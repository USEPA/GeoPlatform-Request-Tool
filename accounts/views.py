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
from .func import create_accounts, add_accounts_to_groups, update_requests_groups
from natsort import natsorted


def format_username(data):
    username_extension = 'EPAEXT' if '@epa.gov' not in data['email'] else 'EPA'
    username = f'{data["last_name"].capitalize()}.{data["first_name"].capitalize()}_{username_extension}'
    return username.replace(' ', '')


class AccountRequestViewSet(CreateModelMixin, GenericViewSet):
    queryset = AccountRequests.objects.none()
    serializer_class = AccountRequestSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def perform_create(self, serializer):
        agol = AGOL.objects.first()
        username = format_username(self.request.data)
        username_valid, agol_id, groups = agol.check_username(username)
        possible_accounts = agol.find_accounts_by_email(self.request.data['email'])
        is_existing_account = True if agol_id is not None else False
        # try to capture reason here but proceed if we can't
        try:
            reason = ResponseProject.objects.get(id=self.request.data['response']).default_reason
        except ObjectDoesNotExist:
            reason = None
        account_request = serializer.save(username_valid=username_valid, agol_id=agol_id, username=username,
                                          is_existing_account=is_existing_account,
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

    def perform_update(self, serializer):
        agol = AGOL.objects.first()
        username_valid, agol_id, existing_groups = agol.check_username(self.request.data['username'])
        is_existing_account = True if agol_id is not None else False
        account_request = serializer.save(username_valid=username_valid, agol_id=agol_id,
                                          is_existing_account=is_existing_account)
        update_requests_groups(account_request, existing_groups, self.request.data['groups'])

    # create account (or queue up creation?)
    @action(['POST'], detail=False)
    def approve(self, request):
        account_requests = AccountRequests.objects.filter(pk__in=request.data['accounts'])
        if not account_requests:
            return Http404

        # verify user has permission on each request submitted.
        for x in account_requests:
            self.check_object_permissions(request, x)

        # create accounts that don't exist
        create_success = create_accounts(account_requests, request.data.get('password', None))

        # add accounts to groups
        group_success = add_accounts_to_groups(account_requests)

        success = [x.pk for x in account_requests if x.pk in create_success and x.pk in group_success]
        AccountRequests.objects.filter(pk__in=success).update(created=now())

        # todo: this whole things needs more testing
        if len(create_success) == len(account_requests) and len(group_success) == len(account_requests):
            return Response()
        if len(create_success) != len(account_requests):
            return Response("Error creating and updating accounts")
        if len(group_success) != len(account_requests):
            return Response("Accounts created. Existing account NOT updated.")

        return Response(status=400)

    # possible to setup email to request with reason
    @action(['POST'], detail=True)
    def reject(self, request):
        pass

    @action(['GET'], detail=False)
    def roles(self, request):
        options = list()
        for value, display in AccountRequests.ROLE_CHOICES:
            options.append({'display': display, 'value': value})
        return Response(options)

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
        return AccountSerializer

    @action(['GET'], detail=True)
    def preview_invitation_email(self, request, pk=None):
        account_request = get_object_or_404(AccountRequests, pk=pk)
        return TemplateResponse(request, 'invitation_email_body.html', {"account_request": account_request})


class AGOLGroupViewSet(ReadOnlyModelViewSet):
    queryset = AGOLGroup.objects.none()
    serializer_class = AGOLGroupSerializer
    ordering = ['title']
    pagination_class = None
    filter_fields = ['response', 'is_auth_group']
    search_fields = ['title']

    # only show groups for which the user the user has access per agol group fields assignable groups
    def get_queryset(self):
        # if self.request.query_params:
        #     if 'all' in self.request.query_params and self.request.query_params['all'] == 'true':
        #         return AGOLGroup.objects.all()
            # elif 'search' in self.request.query_params:
            #     search_text = self.request.query_params['search']
            #     return AGOLGroup.objects.filter(title__contains=search_text)
            # elif 'is_auth_group' in self.request.query_params:
            #     is_auth_group = False
            #     if self.request.query_params.get('is_auth_group').lower() == 'true':
            #         is_auth_group = True
            #     elif self.request.query_params.get('is_auth_group').lower() == 'false':
            #         is_auth_group = False
            #     return AGOLGroup.objects.filter(is_auth_group=is_auth_group)

        sponsors = User.objects.filter(agol_info__delegates=self.request.user)
        return AGOLGroup.objects.filter(Q(response__users=self.request.user) | Q(response__users__in=sponsors))

    def get_permissions(self):
        if self.action == 'all':
            return [AllowAny()]
        return super(AGOLGroupViewSet, self).get_permissions()

    @action(['GET'], detail=False)
    def all(self, request):
        groups = self.filter_queryset(AGOLGroup.objects.all())
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


    def get_serializer_class(self):
        if not self.request.user.is_anonymous:
            return FullResponseProjectSerializer
        return ResponseProjectSerializer


class SponsorsViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.filter(agol_info__sponsor=True)
    serializer_class = SponsorSerializer
    ordering = ['last_name']
    permission_classes = [IsAuthenticated]
    search_fields = ['last_name', 'first_name', 'email']
    filter_fields = ['response', 'agol_info__delegates']


class AGOLRoleViewSet(ReadOnlyModelViewSet):
    queryset = AGOLRole.objects.all()
    serializer_class = AGOLRoleSerializer
    ordering = ['system_default', 'name']
    search_fields = ['name', 'description']
    filter_fields = ['system_default', 'is_available']


class PendingNotificationViewSet(ReadOnlyModelViewSet):
    queryset = Notification.objects.filter(sent__isnull=True)
    serializer_class = PendingNotificationSerializer

    @action(['PUT'], detail=True)
    def mark_sent(self, request, pk=None):
        notification = get_object_or_404(Notification, pk=pk)
        notification.sent = now()
        notification.save()
        return Response('')
