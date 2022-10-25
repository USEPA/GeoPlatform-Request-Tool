from django.db.models import Q
from .models import AccountRequests, AGOL, GroupMembership, AGOLGroup, Notification
from uuid import UUID
import logging

logger = logging.getLogger('AGOLAccountRequestor')


def create_accounts(account_requests: [AccountRequests], password: str = None):
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

    # return all accounts whose group requests have been fulfilled or doesn't have any group requests
    return account_requests.filter(Q(groupmembership__is_member=True) |
                                   Q(groupmembership__isnull=True)).values_list('pk', flat=True).distinct()


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


def has_outstanding_request(request_data):
    print(request_data)
    return AccountRequests.objects.filter(email=request_data['email'],
                                          response=request_data['response'],
                                          approved__isnull=True).exists()


def enable_accounts(account_requests, password):
    success_total = [x.pk for x in account_requests if x.existing_account_enabled]
    agol = AGOL.objects.first()
    disabled_accounts = [x for x in account_requests if not x.existing_account_enabled]
    if len(disabled_accounts) > 0:
        for account in disabled_accounts:
            success = agol.enable_user_account(account.username)
            if success:
                account.existing_account_enabled = True
                account.save()
                password_update_success = agol.update_user_account(account.username, {"password": password})
                success_total += [account]

                template = "enabled_account_email.html"
                if password is not None and password_update_success:
                    template = "enabled_account_email_with_password.html"
                Notification.create_new_notification(template=template,
                                                     context={"username": account.username,
                                                              "response": account.response.name,
                                                              "approved_by": account.approved_by},
                                                     subject="Your EPA Geoplatform Account has been enabled",
                                                     to=[account.email],
                                                     content_object=account)
    return success_total
