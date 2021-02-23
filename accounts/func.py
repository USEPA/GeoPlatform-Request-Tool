from .models import AccountRequests, AGOL, GroupMembership, AGOLGroup
from django.utils.timezone import now
from typing import Optional
from uuid import UUID


def create_accounts(account_requests: [AccountRequests], password: str = None):
    account_requests.update(approved=now())
    # return existing accounts ass successful since they already exist
    success = [x.pk for x in account_requests if x.agol_id is not None]
    agol = AGOL.objects.first()
    create_accounts = [x for x in account_requests if x.agol_id is None]
    if len(create_accounts) > 0:
        success += agol.create_users_accounts(create_accounts, password)
        # if len(success) == len(create_accounts):
        #     AccountRequests.objects.filter(pk__in=success).update(created=now())
        #     return True
        # else:
        #     return False

    return success


def add_accounts_to_groups(account_requests: [AccountRequests]):
    # add users to groups for either existing or newly created
    agol = AGOL.objects.first()
    group_account_requests = [x for x in account_requests.filter(agol_id__isnull=False)]
    total_group_requests = 0

    for account_request in group_account_requests:
        groups = AGOLGroup.objects.filter(groupmembership__request=account_request, groupmembership__is_member=False)
        for group in groups:
            success = agol.add_to_group(account_request.username, group.id)
            if success:
                GroupMembership.objects.filter(request=account_request, group=group).update(is_member=True)

    # return all accounts who's group requests have been fulfilled
    return account_requests.filter(groupmembership__is_member=True).values_list('pk', flat=True).distinct()


def update_requests_groups(account_request: AccountRequests, existing_groups: [str], requested_groups=None):
    # in order to ensure users are not incorrectly add to groups reevaluate groups through here
    if requested_groups is None:
        requested_groups = []
    account_request.groups.set([])
    # force set everything requested back to is_member False and only set to True if they are currently set to the group
    if len(requested_groups) > 0:
        for group in requested_groups:
            # confirm group is part of related response
            if UUID(group) in account_request.response.assignable_groups.values_list('id', flat=True):
                GroupMembership.objects.update_or_create(group_id=group, request=account_request,
                                                         defaults={'is_member': False})

    if len(existing_groups) > 0:
        # capture groups they are already part of
        for group in existing_groups:
            GroupMembership.objects.update_or_create(group_id=group, request=account_request,
                                                     defaults={'is_member': True})

