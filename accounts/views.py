from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import BaseFilterBackend

from django.shortcuts import get_list_or_404, get_object_or_404, Http404
from django_filters.rest_framework import FilterSet, BooleanFilter, DateFilter, NumberFilter, BaseCSVFilter
from django.db.models import Q, Count
from django.template.response import TemplateResponse
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist

from .models import *
from .serializers import *
from .permissions import IsSponsor
from .func import create_account, add_account_to_groups, update_requests_groups, enable_account
from natsort import natsorted


def format_username(data):
    if data['email'].split('@')[1].lower() in settings.ENTERPRISE_USER_DOMAINS:
        username = data['email']
    else:
        username_extension = 'EPAEXT' if '@epa.gov' not in data['email'] else 'EPA'
        username = f'{data["last_name"].capitalize()}.{data["first_name"].capitalize()}_{username_extension}'
    return username.replace(' ', '')


class AccountRequestViewSet(CreateModelMixin, GenericViewSet):
    queryset = AccountRequests.objects.none()
    serializer_class = AccountRequestSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def perform_create(self, serializer):
        agol = ResponseProject.objects.get(id=self.request.data['response']).portal
        username = format_username(self.request.data)
        username_valid, agol_id, groups, existing_account_enabled, created = agol.check_username(username)
        possible_accounts = agol.find_accounts_by_email(self.request.data['email'])
        is_existing_account = True if agol_id is not None else False
        # try to capture reason here but proceed if we can't
        try:
            reason = ResponseProject.objects.get(id=self.request.data['response']).default_reason
        except ObjectDoesNotExist:
            reason = None
        account_request = serializer.save(username_valid=username_valid, agol_id=agol_id, username=username,
                                          is_existing_account=is_existing_account,
                                          existing_account_enabled=existing_account_enabled,
                                          possible_existing_account=possible_accounts, reason=reason)
        update_requests_groups(account_request, groups)


class AccountFilterSet(FilterSet):
    approved_and_created = BooleanFilter(method='approved_and_created_func')
    approved = BooleanFilter(field_name='approved', lookup_expr='isnull', exclude=True)
    approved_gte = DateFilter(field_name='approved', lookup_expr='gte')
    created = BooleanFilter(field_name='created', lookup_expr='isnull', exclude=True)

    def approved_and_created_func(self, queryset, name, value):
        return queryset.exclude(created__isnull=value).exclude(approved__isnull=value)

    class Meta:
        model = AccountRequests
        fields = ['approved_and_created', 'approved', 'response']


class SponsorFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser or request.user.has_perm('accounts.view_all_accountrequests'):
            return queryset
        else:
            # get list of users that current user is a delegate for
            sponsors = set([x.user for x in request.user.delegate_for.all()])
            # add current user into list of potential sponsors for the filter in case they are both a sponsor and a delegate
            sponsors.add(request.user)
            return queryset.filter(response__users__in=sponsors)


class AccountViewSet(ModelViewSet):
    queryset = AccountRequests.objects.all()
    serializer_class = AccountSerializer
    search_fields = ['first_name', 'last_name', 'username', 'organization']
    filterset_class = AccountFilterSet
    filter_backends = ModelViewSet.filter_backends + [SponsorFilterBackend]
    permission_classes = [IsSponsor]

    def get_queryset(self):
        user_portal = self.request.user.agol_info.portal_id
        # return self.queryset.filter(sponsor__agol_info__portal_id=user_portal)
        return self.queryset.filter(response__portal_id=user_portal)

    def perform_update(self, serializer):
        # agol of the logged in approver/admin
        # agol = self.request.user.agol_info.portal

        # agol of the user request from response/project
        agol = ResponseProject.objects.get(pk=self.request.data['response']).portal

        username_valid, agol_id, existing_groups, existing_account_enabled, created = agol.check_username(self.request.data['username'])
        is_existing_account = True if agol_id is not None else False
        account_request = serializer.save(username_valid=username_valid, agol_id=agol_id,
                                          is_existing_account=is_existing_account,
                                          existing_account_enabled=existing_account_enabled)
        update_requests_groups(account_request, existing_groups, self.request.data['groups'])

    # create account (or queue up creation?)
    @action(['POST'], detail=False)
    def approve(self, request):
        account = AccountRequests.objects.get(pk=request.data['account_id'])
        if not account:
            return Response({
                'id': request.data['account_id'],
                'error': f"Account not {request.data['account_id']} found"
            }, status=404)

        # verify user has permission on each request submitted.
        self.check_object_permissions(request, account)

        # marked approved and capture who dun it (do we want to do this here, or after it's actually created?)
        account.approved=now()
        account.approved_by=request.user
        account.save()

        password = request.data.get('password', None)

        # create accounts that don't exist
        create_success = create_account(account, password)
        if not create_success:
            return Response({
                'id': account.pk,
                'error': f"Error creating {account.username} at {account.response.portal.portal_name}."
            }, status=500)

        # re-enabled disabled accounts
        enabled_success = enable_account(account, password)
        if not enabled_success:
            return Response({
                'id': account.pk,
                'error': f"Error enabling {account.username} at {account.response.portal.portal_name}."
            }, status=500)

        # add account to groups
        if account.groupmembership_set.count() > 0:
            group_success = add_account_to_groups(account)
            if not group_success:
                return Response({
                    'id': account.pk,
                    'warning': f"Warning, {account.username} created but groups not added at {account.response.portal.portal_name}"
                }, status=200)
        else:
            #no groups to add
            group_success = True

        #success = [x.pk for x in account_requests if x.pk in create_success and x.pk in group_success]
        if create_success and enabled_success and group_success:
            return Response({
                'id': account.pk,
                'success': f"Successfully approved {account.username} at {account.response.portal.portal_name}"
            }, status=200)

        # return unknown error if for some reason previous error checks didn't return an error but was not successful
        return Response({
            'id': account.pk,
            'error': f"Unknown error with {account.username} at {account.response.portal.portal_name}"
        }, status=400)

    # possible to setup email to request with reason
    @action(['POST'], detail=True)
    def reject(self, request):
        pass

    # @action(['GET'], detail=False)
    # def roles(self, request):
    #     options = list()
    #     for value, display in AccountRequests.ROLE_CHOICES:
    #         options.append({'display': display, 'value': value})
    #     return Response(options)

    @action(['GET'], detail=False)
    def user_types(self, request):
        options = list()
        for value, display in AccountRequests.USER_TYPE_CHOICES:
            options.append({'display': display, 'value': value})
        return Response(options)

    # @action(['GET'], detail=False)
    # def sponsors(self, request):
    #     sponsors = User.objects.filter(agol_info__sponsor=True)
    #     sponsors_list = list()
    #     for sponsor in sponsors:
    #         if sponsor.last_name:
    #             display = f'{sponsor.first_name} {sponsor.last_name}'
    #         else:
    #             display = None
    #         username = sponsor.agol_info.agol_username if sponsor.agol_info.agol_username else sponsor.username
    #         sponsors_list.append({
    #             'value': sponsor.pk,
    #             'display': display,
    #             'username': username,
    #             'email': sponsor.email,
    #         })
    #     return Response(sponsors_list)

    # @action(['GET', 'PUT'], detail=False)
    # def pending_notifications(self, request):
    #     # if get send pending notifications with emails
    #     if request.method == 'GET':
    #         pending_notifications = AccountRequests.objects.filter(sponsor_notified=False,
    #                                                                approved__isnull=True,
    #                                                                created__isnull=True)\
    #             .values('response__users')\
    #             .annotate(total_pending=Count('response__users'))\
    #             .filter(total_pending__gt=0)
    #
    #         for i, notification in enumerate(pending_notifications):
    #             delegate_emails = User.objects.filter(delegate_for__user=notification['response__users']) \
    #                 .values_list('email', flat=True)
    #             pending_notifications[i]['sponsor'] = User.objects.get(pk=notification['response__users']).email
    #             pending_notifications[i]['delegates'] = list(filter(None, delegate_emails))
    #             pending_notifications[i].pop('response__users')
    #
    #         return Response(pending_notifications)
    #
    #     # post expects array of sponsor emails that have been notified successfully
    #     if request.method == 'PUT':
    #         AccountRequests.objects.filter(response__users__email__in=request.data.get('notified_sponsors', []))\
    #             .update(sponsor_notified=True)
    #         return Response()

    def get_serializer_class(self):
        if self.request.query_params.get('include_sponsor_details', False):
            return AccountWithSponsorSerializer
        if self.request.query_params.get('include_all_details', False):
            return AccountWithNestedDataSerializer
        return AccountSerializer

    @action(['GET'], detail=True)
    def preview_invitation_email(self, request, pk=None):
        account_request = get_object_or_404(AccountRequests, pk=pk)
        return TemplateResponse(request, 'invitation_email_body.html', {"account_request": account_request, "PORTAL": account_request.response.portal})


class AGOLGroupViewSet(ReadOnlyModelViewSet):
    queryset = AGOLGroup.objects.none()
    serializer_class = AGOLGroupSerializer
    ordering = ['title']
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filterset_fields = ['response', 'is_auth_group']
    search_fields = ['title']

    # only show groups for which the user has access per agol group fields assignable groups
    def get_queryset(self):
        sponsors = User.objects.filter(agol_info__delegates=self.request.user)
        return AGOLGroup.objects.filter(Q(agol_id=self.request.user.agol_info.portal_id) &  Q(response__users=self.request.user) | Q(response__users__in=sponsors))

    def get_permissions(self):
        if self.action == 'all':
            return [AllowAny()]
        return super(AGOLGroupViewSet, self).get_permissions()

    @action(['GET'], detail=False)
    def all(self, request):
        groups = self.filter_queryset(AGOLGroup.objects.filter(agol_id=self.request.user.agol_info.portal))
        groups_list = list()
        for group in groups:
            groups_list.append({
                'id': group.pk,
                'title': group.title.lstrip('​')
            })
        sorted_group_list = natsorted(groups_list, key=lambda x: x['title'])
        return Response(sorted_group_list)


class ResponseProjectFilterSet(FilterSet):
    for_approver = BooleanFilter(method='for_approver_func')
    id_in = BaseCSVFilter(field_name='pk', lookup_expr='in')
    is_disabled = BooleanFilter(field_name='disabled', lookup_expr='isnull', exclude=True)

    def for_approver_func(self, queryset, name, value):
        if not value:
            return queryset

        sponsors = User.objects.filter(agol_info__delegates=self.request.user)
        return queryset.filter(Q(users=self.request.user) | Q(users__in=sponsors))

    class Meta:
        model = ResponseProject
        fields = ['disabled']


class ResponseProjectViewSet(ModelViewSet):
    queryset = ResponseProject.objects.filter(approved__isnull=False)
    serializer_class = ResponseProjectSerializer
    ordering = ['name']
    pagination_class = None
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_class = ResponseProjectFilterSet

    def perform_create(self, serializer):
        # self.request.portal_id = self.request.user.agol_info.portal_id
        obj = serializer.save()
        to, subject, message = obj.generate_new_email()
        Notification.create_new_notification(
            to=to,
            subject=subject,
            content=message,
            content_object=obj
        )

    def get_serializer_class(self):
        if not self.request.user.is_anonymous:
            return FullResponseProjectSerializer
        return ResponseProjectSerializer

    def get_queryset(self):
        if not self.request.user.is_anonymous:
            user_portal = self.request.user.agol_info.portal_id
            return self.queryset.filter(portal_id=user_portal)
        return self.queryset

class SponsorsViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.filter(agol_info__sponsor=True)
    serializer_class = SponsorSerializer
    ordering = ['last_name']
    permission_classes = [IsAuthenticated]
    search_fields = ['last_name', 'first_name', 'email']
    filterset_fields = ['response', 'agol_info__delegates', 'agol_info__portal__user']

    def get_queryset(self):
        return self.queryset.filter(agol_info__portal=self.request.user.agol_info.portal)


class AGOLRoleViewSet(ReadOnlyModelViewSet):
    queryset = AGOLRole.objects.all()
    serializer_class = AGOLRoleSerializer
    ordering = ['system_default', 'name']
    permission_classes = [IsAuthenticated] # todo: can we remove this adn just assign read permission now?
    search_fields = ['name', 'description']
    filterset_fields = ['system_default', 'is_available']

    def get_queryset(self):
        # filter role options based on currently logged in user association
        return self.queryset.filter(Q(agol=self.request.user.agol_info.portal))

# class PendingNotificationViewSet(ReadOnlyModelViewSet):
#     queryset = Notification.objects.filter(sent__isnull=True)
#     serializer_class = PendingNotificationSerializer
#
#     @action(['PUT'], detail=True)
#     def mark_sent(self, request, pk=None):
#         notification = get_object_or_404(Notification, pk=pk)
#         notification.sent = now()
#         notification.save()
#         return Response('')

class PortalsViewSet(ReadOnlyModelViewSet):
    queryset = AGOL.objects.all()
    serializer_class = PortalsSerializer
    ordering = ['portal_name']
    search_fields = ['portal_name', 'portal_url']