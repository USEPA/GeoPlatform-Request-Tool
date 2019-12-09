from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet
from rest_framework.mixins import CreateModelMixin
from .serializers import *
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.decorators import action
from rest_framework.response import Response

from django.shortcuts import get_list_or_404
from django.contrib.auth.models import User
from django.utils.timezone import now
from django_filters.rest_framework import FilterSet, BooleanFilter
from django.db.models import Q

from .models import *


class AccountRequestViewSet(CreateModelMixin, GenericViewSet):
    queryset = AccountRequests.objects.none()
    serializer_class = AccountRequestSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        agol = AGOL.objects.get(portal_url='https://epa.maps.arcgis.com')
        username_extension = 'EPAEXT' if '@epa.gov' not in self.request.data['email'] else 'EPA'
        username = f'{self.request.data["last_name"].capitalize()}.{self.request.data["first_name"].capitalize()}_{username_extension}'
        username_valid, agol_id, groups = agol.check_username(username)
        possible_accounts = agol.find_accounts_by_email(self.request.data['email'])
        account_request = serializer.save(username_valid=username_valid, agol_id=agol_id, username=username,
                                          possible_existing_account=possible_accounts)
        if groups:
            account_request.groups.set(groups)

    @action(['GET'], detail=False)
    def sponsors(self, request):
        sponsors = User.objects.filter(agol_info__sponsor=True)
        sponsors_list = list()
        for sponsor in sponsors:
            sponsors_list.append({
                'display': f'{sponsor.first_name} {sponsor.last_name}',
                'value': sponsor.pk
            })
        return Response(sponsors_list)


class IsSponsor(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # must be sponsor or superuser to edit

        if obj.sponsor == request.user or request.user.is_superuser:
            return True
        else:
            return False


class AccountFilterSet(FilterSet):
    approved_and_created = BooleanFilter(method='approved_and_created_func')
    # created = BooleanFilter(field_name='created', lookup_expr='isnull', exclude=True)

    def approved_and_created_func(self, queryset, name, value):
        return queryset.exclude(created__isnull=value, approved__isnull=value)

    class Meta:
        model = AccountRequests
        fields = ['approved_and_created']


class AccountViewSet(ModelViewSet):
    queryset = AccountRequests.objects.all()
    serializer_class = AccountSerializer
    search_fields = ['first_name', 'last_name', 'username']
    filterset_class = AccountFilterSet
    permission_classes = (IsSponsor,)

    def perform_update(self, serializer):
        agol = AGOL.objects.get(portal_url='https://epa.maps.arcgis.com')
        username_valid, agol_id, groups = agol.check_username(self.request.data['username'])

        '''check if sponsor changing and mark sponsor_notified to false but if sponsor_notified is false it should stay false'''
        existing_record = AccountRequests.objects.get(pk=self.request.data['id'])
        sponsor_notified = existing_record.sponsor.pk == self.request.data['sponsor'] and existing_record.sponsor_notified

        account_request = serializer.save(username_valid=username_valid, agol_id=agol_id, sponsor_notified=sponsor_notified)
        account_request.groups.set(list(set(groups + self.request.data['groups'])))

    def get_queryset(self):
        if self.request.user.is_superuser:
            return super().get_queryset()
        else:
            return super().get_queryset().filter(sponsor=self.request.user)

    # create account (or queue up creation?)
    @action(['POST'], detail=False)
    def approve(self, request):
        account_requests = get_list_or_404(AccountRequests, pk__in=request.data['accounts'])
        AccountRequests.objects.filter(pk__in=request.data['accounts']).update(approved=now())
        agol = AGOL.objects.get(portal_url='https://epa.maps.arcgis.com')
        create_accounts = [x for x in account_requests if x.agol_id is None]
        if len(create_accounts) > 0:
            create_success = agol.create_users_accounts(account_requests, request.data['password'])
        else:
            create_success = True

        group_requests = AccountRequests.objects.filter(pk__in=request.data['accounts'], agol_id__isnull=False)
        groups = [str(g['groups']) for g in group_requests.values('groups') if g['groups']]
        if len(group_requests) > 0 and len(groups) > 0:
            group_success = agol.add_to_group([str(a.username) for a in group_requests], groups)
        else:
            group_success = True

        if create_success and group_success:
            AccountRequests.objects.filter(pk__in=[x.pk for x in account_requests]).update(created=now())
            return Response()
        if not create_success:
            return Response("Error creating and updating accounts")
        if not group_success:
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

    @action(['GET'], detail=False)
    def sponsors(self, request):
        sponsors = User.objects.filter(agol_info__sponsor=True)
        sponsors_list = list()
        for sponsor in sponsors:
            if sponsor.last_name:
                display = f'{sponsor.first_name} {sponsor.last_name}'
            else:
                display = None
            username = sponsor.agol_info.agol_username if sponsor.agol_info.agol_username else sponsor.username
            sponsors_list.append({
                'value': sponsor.pk,
                'display': display,
                'username': username,
                'email': sponsor.email,
            })
        return Response(sponsors_list)


    @action(['GET'], detail=False)
    def field_coordinators(self, request):
        sponsors = User.objects.filter(agol_info__sponsor=True)
        sponsors_list = list()
        for sponsor in sponsors:
            sponsors_list.append({
                'first_name': sponsor.first_name,
                'last_name': sponsor.last_name,
                'display': f'{sponsor.first_name} {sponsor.last_name}',
                'email': sponsor.email,
                'phone_number': sponsor.agol_info.phone_number,
                'authoritative_group': sponsor.agol_info.authoritative_group,
                'value': sponsor.pk
            })
        return Response({"results": sponsors_list})


class AGOLGroupViewSet(ReadOnlyModelViewSet):
    queryset = AGOLGroup.objects.none()
    serializer_class = AGOLGroupSerializer
    ordering = ['title']
    pagination_class = None

    # only show groups for which the user the user has access per agol group fields assignable groups
    def get_queryset(self):
        return AGOLGroup.objects.filter(Q(show=True) | Q(assignable_groups__group__in=self.request.user.groups.all()))

    @action(['GET'], detail=False)
    def all(self, request):
        groups = AGOLGroup.objects.all()
        groups_list = list()
        for group in groups:
            groups_list.append({
                'value': group.pk,
                'title': group.title
            })
        return Response(groups_list)

