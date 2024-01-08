from django_filters.rest_framework import FilterSet, BooleanFilter, BaseCSVFilter
from django.contrib.auth.models import User
from django.db.models import Q
from .models import ResponseProject


from accounts.models import AGOLGroup


class AGOLGroupFilterSet(FilterSet):
    role_in = BaseCSVFilter(field_name='roles', lookup_expr='in')

    class Meta:
        model = AGOLGroup
        fields = ['response', 'is_auth_group', 'role_in']


class ResponseProjectFilterSet(FilterSet):
    for_approver = BooleanFilter(method='for_approver_func')
    id_in = BaseCSVFilter(field_name='pk', lookup_expr='in')
    is_disabled = BooleanFilter(field_name='disabled', lookup_expr='isnull', exclude=True)

    def for_approver_func(self, queryset, name, value):
        if not value:
            return queryset

        if self.request.user.is_superuser:
            return queryset

        sponsors = User.objects.filter(agol_info__delegates=self.request.user)
        return queryset.filter(Q(users=self.request.user) | Q(users__in=sponsors))

    class Meta:
        model = ResponseProject
        fields = ['disabled']
