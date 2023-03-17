from django.db.models import Q
from django.utils.timezone import now
from .models import AccountRequests, AGOL, GroupMembership, AGOLGroup, Notification
from uuid import UUID
import logging

logger = logging.getLogger('AGOLAccountRequestor')


def create_account(account_request, password: str = None):
    agol = account_request.response.portal

    if account_request.agol_id is None:
        # double check if username already exists, but we are out of sync
        username_valid, agol_id, groups, existing_account_enabled, created = agol.check_username(account_request.username)
        if agol_id:
            account_request.agol_id = agol_id
            account_request.existing_account_enabled = existing_account_enabled
            account_request.created=created
            account_request.save()

            # account already exists since we already grabbed their user id from agol
            return True

    # invite user since they don't exist yet
    if agol.create_user_account(account_request, password):
        # account was created successfully
        account_request.created=now()
        account_request.save()
        return True

    # account creation failed, return false
    return False


def add_account_to_groups(account_request):
    # add users to groups for either existing or newly created
    agol = account_request.response.portal
    groups = AGOLGroup.objects.filter(groupmembership__request=account_request, groupmembership__is_member=False)
    success_list = []
    for group in groups:
        if agol.add_to_group(account_request.username, group.id):
            GroupMembership.objects.filter(request=account_request, group=group).update(is_member=True)
            success_list.append(group.pk)
    return success_list


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


def enable_account(account_request, password):
    if account_request.existing_account_enabled:
        return True

    agol = account_request.response.portal

    enable_success = agol.enable_user_account(account_request.username)
    if enable_success:
        account_request.existing_account_enabled = True
        account_request.save()

    if password is not None:
        password_update_success = agol.update_user_account(account_request.username, {"password": password})

    template = "enabled_account_email.html"
    if password is not None and password_update_success:
        template = "enabled_account_email_with_password.html"
    Notification.create_new_notification(template=template,
                                         context={"username": account_request.username,
                                                  "response": account_request.response.name,
                                                  "approved_by": account_request.approved_by},
                                         subject="Your EPA Geoplatform Account has been enabled",
                                         to=[account_request.email],
                                         content_object=account_request)
    return True
