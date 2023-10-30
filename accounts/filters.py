from django_filters.rest_framework import FilterSet, BaseCSVFilter

from accounts.models import AGOLGroup


class AGOLGroupFilterSet(FilterSet):
    role_in = BaseCSVFilter(field_name='roles', lookup_expr='in')

    class Meta:
        model = AGOLGroup
        fields = ['response', 'is_auth_group', 'role_in']
