from rest_framework import permissions
from rest_framework.permissions import DjangoModelPermissions


class IsSponsor(DjangoModelPermissions):

    def has_permission(self, request, view):
        # must be sponsor or superuser to edit

        if request.user.is_superuser:
            return True

        is_sponsor = request.user.groups.filter(name='Sponsors').exists()
        return is_sponsor

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

