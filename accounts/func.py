from django.urls import resolve
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import AccountRequests, AGOL, GroupMembership, AGOLGroup, Notification, ResponseProject, AGOLRole
from uuid import UUID
import logging
import re
from django.utils.timezone import now

logger = logging.getLogger('django')


def add_account_to_groups(account_request):
    # add users to groups for either existing or newly created
    agol = account_request.response.portal
    groups = AGOLGroup.objects.filter(groupmembership__request=account_request, groupmembership__is_member=False)
    success_list = []
    for group in groups:
        if agol.add_to_group(account_request.username, group.id):
            GroupMembership.objects.filter(request=account_request, group=group).update(is_member=True)
            success_list.append(str(group.pk))
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
    return AccountRequests.objects.filter(email=request_data['email'],
                                          response=request_data['response'],
                                          approved__isnull=True).exists()


def email_allowed_for_portal(request_data):
    portal = request_data['response'].portal
    if portal.allow_external_accounts:
        return True
    email_domain = request_data['email'].split('@')[1]
    return email_domain in portal.enterprise_precreate_domains_list


def enable_account(account_request, password):
    if account_request.existing_account_enabled:
        return True

    agol = account_request.response.portal

    enable_success = agol.enable_user_account(account_request.username)
    if enable_success:
        account_request.existing_account_enabled = True
        account_request.save()

    # default process is assumed to be "invite user",
    template = "enabled_account_email_invited.html"

    # if user has epa email address and enterprise authentication is enabled, account needs to be pre-created
    if account_request.is_enterprise_account():
        template = "enabled_account_email_precreated.html"

    # not an enterprise account request and password has been manually set
    elif password is not None:
        password_update_success = agol.update_user_account(account_request.username, {"password": password})
        if password_update_success:
            template = "enabled_account_email_with_password.html"

    Notification.create_new_notification(template=template,
                                         context={
                                             "PORTAL": agol,
                                             "portal_url": agol.portal_url,
                                             "username": account_request.username,
                                             "response": account_request.response.name,
                                             "approved_by": account_request.approved_by
                                         },
                                         subject=f"Your EPA {account_request.response.portal} Account has been enabled",
                                         to=[account_request.email],
                                         content_object=account_request)
    return True


def get_object_id_from_request(request):
    referrer = request.META.get('HTTP_REFERER')
    host = request.META.get('HTTP_HOST')
    path = referrer.split(host)[1].split('?')[0]
    r = resolve(path)
    return r.kwargs.get('object_id', None)


def get_response_from_request(request):
    object_id = get_object_id_from_request(request)
    return ResponseProject.objects.get(id=object_id) if object_id else None


def format_username(data, enterprise_domains=None):
    if enterprise_domains is None:
        enterprise_domains = []
    if data['email'].split('@')[1].lower() in enterprise_domains:
        username = data['email']
    else:
        username_extension = 'EPAEXT' if '@epa.gov' not in data['email'] else 'EPA'
        last_name = re.sub(r'\W+', '', data["last_name"])
        first_name = re.sub(r'\W+', '', data["first_name"])
        username = f'{last_name.capitalize()}.{first_name.capitalize()}_{username_extension}'
    return username.replace(' ', '')


def get_role_from_request(request):
    object_id = get_object_id_from_request(request)
    return AGOLRole.objects.get(id=object_id) if object_id else None


# false if not existing or username not in associated_usernames (based on email)
def email_associated_with_existing_account(account_request: AccountRequests):
    associated_usernames = account_request.possible_existing_account.split(',')
    return account_request.username in associated_usernames


def verify_account_can_be_approved(account):
    if account.is_existing_account and not email_associated_with_existing_account(account):
        raise PermissionDenied(
            {'details': 'Provided email address is not associated with this existing username.'},
        )

def approve_account(account, password, approved_by):
    # marked approved and capture who dun it (do we want to do this here, or after it's actually created?)
    account.approved = now()
    account.approved_by = approved_by
    account.save()

    # create accounts that don't exist
    if account.agol_id is None:
        create_success = account.create_account(password)

        if not create_success:
            return Response({
                'id': account.pk,
                'error': f"Error creating {account.username} at {account.response.portal.portal_name}."
            }, status=500)
    else:
        create_success = True  # fake it for existing accounts

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
        # no groups to add
        group_success = True

    # success = [x.pk for x in account_requests if x.pk in create_success and x.pk in group_success]
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
