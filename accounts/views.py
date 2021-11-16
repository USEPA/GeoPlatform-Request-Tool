from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet
from rest_framework.mixins import CreateModelMixin
from .serializers import *
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated, DjangoModelPermissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import BaseFilterBackend

from django.shortcuts import get_list_or_404, get_object_or_404
from django_filters.rest_framework import FilterSet, BooleanFilter, DateFilter, NumberFilter
from django.db.models import Q, Count
from django.template.response import TemplateResponse

from .models import *


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
        account_request = serializer.save(username_valid=username_valid, agol_id=agol_id, username=username,
                                          possible_existing_account=possible_accounts)
        if groups:
            account_request.groups.set(groups)

    # @action(['GET'], detail=False, )
    # def field_coordinators(self, request):
    #     sponsors = User.objects.filter(agol_info__sponsor=True)
    #     sponsors_list = list()
    #     for sponsor in sponsors:
    #         sponsors_list.append({
    #             'first_name': sponsor.first_name,
    #             'last_name': sponsor.last_name,
    #             'display': f'{sponsor.first_name} {sponsor.last_name}',
    #             'email': sponsor.email,
    #             'phone_number': sponsor.agol_info.phone_number,
    #             'authoritative_group': sponsor.agol_info.authoritative_group,
    #             'value': sponsor.pk
    #         })
    #     return Response({"results": sponsors_list})


class IsSponsor(DjangoModelPermissions):
    """
    Object-level permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # must be sponsor or superuser to edit

        if request.user.is_superuser:
            return True

        sponsors = set([x.user.pk for x in request.user.delegate_for.all()])
        # add current user into list of potential sponsors for the filter in case
        # they are both a sponsor and a delegate
        sponsors.add(request.user.pk)

        if obj.response.users.filter(pk__in=sponsors).exists():
            return True

        return False


class AccountFilterSet(FilterSet):
    approved_and_created = BooleanFilter(method='approved_and_created_func')
    approved = BooleanFilter(field_name='approved', lookup_expr='isnull', exclude=True)
    approved_gte = DateFilter(field_name='approved', lookup_expr='gte')
    created = BooleanFilter(field_name='created', lookup_expr='isnull', exclude=True)

    def approved_and_created_func(self, queryset, name, value):
        return queryset.exclude(created__isnull=value).exclude(approved__isnull=value)

    class Meta:
        model = AccountRequests
        fields = ['approved_and_created', 'approved', 'sponsor_notified']


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
    permission_classes = (IsSponsor,)

    def perform_update(self, serializer):
        agol = AGOL.objects.first()
        username_valid, agol_id, groups = agol.check_username(self.request.data['username'])

        # removed due to changes in how notification are handled and how relationships to sponsors work
        # '''check if sponsor changing and mark sponsor_notified to true but if sponsor_notified is false it should stay false'''
        # existing_record = AccountRequests.objects.get(pk=self.request.data['id'])
        #
        # sponsor_notified = existing_record.sponsor_notified
        # if sponsor_notified:
        #     sponsor_notified = existing_record.sponsor.pk == self.request.data['sponsor'] and existing_record.sponsor_notified

        account_request = serializer.save(username_valid=username_valid, agol_id=agol_id)
        new_groups = AGOLGroup.objects.filter(pk__in=list(set(groups + self.request.data['groups'])))
        account_request.groups.set(new_groups)

    # create account (or queue up creation?)
    @action(['POST'], detail=False)
    def approve(self, request):
        account_requests = get_list_or_404(AccountRequests, pk__in=request.data['accounts'])
        success = []
        # verify user has permission on each request submitted.
        for x in account_requests:
            self.check_object_permissions(request, x)
        AccountRequests.objects.filter(pk__in=request.data['accounts']).update(approved=now())
        agol = AGOL.objects.first()
        create_accounts = [x for x in account_requests if x.agol_id is None]
        create_success = len(create_accounts) == 0
        if len(create_accounts) > 0:
            success += agol.create_users_accounts(account_requests, request.data.get('password', None))
            if len(success) == len(create_accounts):
                create_success = True

        else:
            create_success = True

        # add users to groups for either existing or newly created
        group_requests = [x for x in AccountRequests.objects.filter(pk__in=request.data['accounts'], agol_id__isnull=False)]
        group_success = len(group_requests) == 0
        for g in group_requests:
            if g.groups.count() > 0:
                group_success = agol.add_to_group([g.username], [str(x) for x in g.groups.values_list('id', flat=True)])
                if group_success:
                    success.append(g.pk)
            else:
                group_success = True

        AccountRequests.objects.filter(pk__in=success).update(created=now())
        if create_success and group_success:
            return Response()
        if not create_success:
            return Response("Error creating and updating accounts", status=500)
        if not group_success:
            return Response("Accounts created. Existing account NOT updated.", status=500)

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

    @action(['GET', 'PUT'], detail=False)
    def pending_notifications(self, request):
        # if get send pending notifications with emails
        if request.method == 'GET':
            pending_notifications = AccountRequests.objects.filter(sponsor_notified=False,
                                                                   approved__isnull=True,
                                                                   created__isnull=True)\
                .values('response__users')\
                .annotate(total_pending=Count('response__users'))\
                .filter(total_pending__gt=0)

            for i, notification in enumerate(pending_notifications):
                delegate_emails = User.objects.filter(delegate_for__user=notification['response__users']) \
                    .values_list('email', flat=True)
                pending_notifications[i]['sponsor'] = User.objects.get(pk=notification['response__users']).email
                pending_notifications[i]['delegates'] = list(filter(None, delegate_emails))
                pending_notifications[i].pop('response__users')

            return Response(pending_notifications)

        # post expects array of sponsor emails that have been notified successfully
        if request.method == 'PUT':
            AccountRequests.objects.filter(response__users__email__in=request.data.get('notified_sponsors', []))\
                .update(sponsor_notified=True)
            return Response()

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
    filter_fields = ['response']

    # only show groups for which the user the user has access per agol group fields assignable groups
    def get_queryset(self):
        sponsors = User.objects.filter(agol_info__delegates=self.request.user)
        return AGOLGroup.objects.filter(Q(response__users=self.request.user) | Q(response__users__in=sponsors))

    @action(['GET'], detail=False)
    def all(self, request):
        groups = AGOLGroup.objects.all()
        groups_list = list()
        for group in groups:
            groups_list.append({
                'value': group.pk,
                'title': group.title.lstrip('​')
            })
        sorted_group_list = sorted(groups_list, key=lambda x: x['title'])
        return Response(sorted_group_list)


class ResponseProjectFilterSet(FilterSet):
    for_approver = BooleanFilter(method='for_approver_func')

    def for_approver_func(self, queryset, name, value):
        if not value:
            return queryset

        sponsors = User.objects.filter(agol_info__delegates=self.request.user)
        return queryset.filter(Q(users=self.request.user) | Q(users__in=sponsors))


class ResponseProjectViewSet(ReadOnlyModelViewSet):
    queryset = ResponseProject.objects.all()
    serializer_class = ResponseProjectSerializer
    ordering = ['name']
    permission_classes = [AllowAny]
    pagination_class = None
    filterset_class = ResponseProjectFilterSet

    # todo: disable response
    # def filter_queryset(self, queryset):
    #     if 'status' not in self.request.query_params:
    #         queryset = queryset.exclude(status_in=['cancled', 'etc.'])
    #     return super(ResponseProjectViewSet, self).filter_queryset(queryset)

class SponsorsViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.filter(agol_info__sponsor=True)
    serializer_class = SponsorSerializer
    ordering = ['last_name']
    permission_classes = [AllowAny]
    search_fields = ['last_name', 'first_name', 'email']
    filter_fields = ['response', 'agol_info__delegates']


