from django_ckeditor_5.fields import CKEditor5Field
from django.core.mail import send_mail
from django.db import models
from django.core.exceptions import ValidationError
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.urls import reverse

import sys
import requests
from django.db.models import UniqueConstraint
from social_django.utils import load_strategy
import time
from datetime import datetime
from django.contrib.auth.models import User, Group
from urllib.parse import urlencode
import json
from django.utils.timezone import now

import logging

logger = logging.getLogger('django')

REASON_CHOICES = (('Emergency Response', 'Emergency Response'),
                  ('Other Federal Agency', 'Other Federal Agency'),
                  ('State Agency', 'State Agency'),
                  ('University', 'University'),
                  ('Long Term GIS Support', 'Long Term GIS Support'),
                  ('Non Government Organization', 'Non Government Organization'),
                  ('Tribal Government', 'Tribal Government'),
                  ('Citizen Advisor', 'Citizen Advisor'),
                  ('Other', 'Other'))


class AccountRequests(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    possible_existing_account = models.CharField(max_length=300, blank=True, null=True)
    is_existing_account = models.BooleanField(default=False)
    existing_account_enabled = models.BooleanField(default=False)
    organization = models.CharField(max_length=200)
    username = models.CharField(max_length=200, help_text='User frontend to modify username.')
    username_valid = models.BooleanField(default=False)
    user_type = models.ForeignKey('UserType', on_delete=models.DO_NOTHING, blank=True, null=True,
                                  verbose_name='Requested User Type')
    role = models.ForeignKey('AGOLRole', on_delete=models.DO_NOTHING, blank=True, null=True, related_name='account_requests',
                             verbose_name='Requested Role')
    groups = models.ManyToManyField('AGOLGroup', blank=True, related_name='account_requests', through='GroupMembership')
    auth_group = models.ForeignKey('AGOLGroup', on_delete=models.DO_NOTHING, blank=True, null=True)
    sponsor = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    # sponsor_notified = models.BooleanField(default=False)
    reason = models.CharField(max_length=200, choices=REASON_CHOICES, blank=True, null=True)
    recaptcha = models.TextField()
    submitted = models.DateTimeField(auto_now_add=True)
    approved = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True,
                                    related_name='accounts_approved')
    created = models.DateTimeField(null=True, blank=True)
    agol_id = models.UUIDField(blank=True, null=True)
    existing_user_type = models.CharField(max_length=200, blank=True, null=True)
    existing_role = models.CharField(max_length=200, blank=True, null=True)
    response = models.ForeignKey('ResponseProject', on_delete=models.PROTECT, blank=True, null=True,
                                 related_name='requests')
    notifications = GenericRelation('Notification')

    @property
    def sponsor_notified(self):
        return self.notifications.count() > 0

    def is_enterprise_account(self):
        return str(self.email.split('@')[1]).lower() in self.response.portal.enterprise_precreate_domains_list

    def create_new_notification(self):
        Notification.create_new_notification(
            subject=f'New {self.response.portal} Account Request',
            context={
                "REQUEST_ADDRESS": settings.HOST_ADDRESS + "/accounts/list#" + self.response.portal.portal_name,
                "PORTAL": self.response.portal
            },
            template="new_account_request_email.html",
            content_object=self,
            to=self.response.get_email_recipients()
        )

    def disable_account(self):
        if not self.is_enterprise_account() and not self.is_existing_account:
            self.response.portal.disable_user_account(self.username)

    def create_account(self, password=None):
        create_success = self.response.portal.create_user_account(self, password)
        if create_success:
            self.created = now()  # mark created once created or enabled and added to groups
            self.save()
        return create_success

    # def get_required_user_type(self):
        # self.role

    def save(self, *args, **kwargs):
        # this resets role and auth_group if the response changes
        if self.response:
            self.role = self.response.role
            self.user_type = self.response.role.minimum_compatible_user_type
            self.auth_group = self.response.authoritative_group

        send_notification = self.pk is None
        super().save(*args, **kwargs)
        if send_notification:
            self.create_new_notification()

    @property
    def new_user_type(self):
        """
        Determines the user type for the account request based on the existing user type and the response portal's user types.

        Returns:
            UserType: The user type if it meets the required hierarchy, otherwise None.
        """
        if self.agol_id:
            # Check if the existing user type is valid and exists in the portal's user types
            if self.existing_user_type and self.response.portal.user_types.filter(code=self.existing_user_type).exists():
                existing_user_type = self.response.portal.user_types.get(code=self.existing_user_type)
                min_required_user_type = self.response.role.minimum_compatible_user_type
                # Return None if the existing user type is valid and meets the required hierarchy
                if existing_user_type.hierarchy < min_required_user_type.hierarchy:
                    return min_required_user_type

            # Return the user type with the lowest hierarchy if no existing user type is found or valid
        return None

    @property
    def new_role(self):
        """
        Determines the new role for the account request based on the existing role and the response portal's roles.

        Returns:
            AGOLRole: The new role if it meets the required hierarchy, otherwise None.
        """
        if self.agol_id:
            # Check if the existing role is valid and exists in the portal's roles
            if self.existing_role and self.response.portal.roles.filter(role_id=self.existing_role).exists():
                existing_role = self.response.portal.roles.get(role_id=self.existing_role)
                min_required_role = self.response.role
                if existing_role.hierarchy < min_required_role.hierarchy:
                    return min_required_role

        # # Check if the current role meets the required hierarchy
        # if self.role and self.role.hierarchy >= self.response.role.hierarchy:
        #     return None
        # Return the response role if no existing role is found or valid
        return None

    class Meta:
        verbose_name_plural = 'Account Requests'
        verbose_name = 'Account Request'
        permissions = [
            ('view_all_accountrequests', 'Can view ALL Account Requests regardless of Sponsor')
        ]


# class AGOLGroupThrough(models.Model):
#     NEW_OR_EXISTING_CHOICES = (('new', 'New'),
#                                ('existing', 'Existing'))
#     group = models.ForeignKey('AGOLGroup', on_delete=models.CASCADE)
#     request = models.ForeignKey('AccountRequests', on_delete=models.CASCADE)
#     new_or_existing = models.CharField(max_length=200, choices=NEW_OR_EXISTING_CHOICES, default='new')


class AGOLGroup(models.Model):
    id = models.UUIDField(primary_key=True)
    title = models.CharField(max_length=500)
    agol = models.ForeignKey('AGOL', on_delete=models.CASCADE, related_name='groups')
    requests = models.ManyToManyField('AccountRequests', through='GroupMembership')
    users = models.ManyToManyField('AGOLUserFields', through='GroupMembership')
    is_auth_group = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def name(self):
        return self.title

    class Meta:
        verbose_name = 'AGOL/Portal Group'
        verbose_name_plural = 'AGOL/Portal Groups'

class GroupMembership(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey('AGOLGroup', on_delete=models.CASCADE)
    request = models.ForeignKey('AccountRequests', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey('AGOLUserFields', on_delete=models.CASCADE, null=True, blank=True)
    is_member = models.BooleanField(default=False)


class AGOLRole(models.Model):
    role_id = models.CharField(max_length=16)
    name = models.CharField(max_length=200)
    description = models.TextField()
    is_available = models.BooleanField(default=False)
    agol = models.ForeignKey('AGOL', on_delete=models.CASCADE, related_name='roles')
    system_default = models.BooleanField(default=False)
    auth_groups = models.ManyToManyField(AGOLGroup, verbose_name='Allowed Authoritative Groups',
                                         related_name='roles', limit_choices_to={'is_auth_group': True})
    minimum_compatible_user_type = models.ForeignKey('UserType', on_delete=models.PROTECT, null=True, blank=True, related_name='roles')
    hierarchy = models.IntegerField(default=0, help_text='This controls if a users account needs to be given a higher role when approved than what they currently have so that it is compatible with the groups they are assigned to.')

    def __str__(self):
        return self.name

    @property
    def auth_group_required(self):
        return self.agol.requires_auth_group

    def clean(self):
        if self.system_default:
            if (self.pk and AGOLRole.objects.filter(system_default=True, agol=self.agol).exclude(pk=self.pk).exists()):
                raise ValidationError({'system_default': 'You cannot have more than one system default. Remove current default to select a new one.'})

    class Meta:
        verbose_name = 'AGOL/Portals Role'
        verbose_name_plural = 'AGOL/Portals Roles'


class UserType(models.Model):
    code = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    portal = models.ForeignKey('AGOL', related_name='user_types', on_delete=models.PROTECT)
    hierarchy = models.IntegerField(default=0, help_text='This controls if a users account needs to be given a higher user type when approved than what they currently have so that it is compatible with the roles they are assigned to.')

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = 'AGOL/Portal User Type'
        verbose_name_plural = 'AGOL/Portal User Types'


class AGOL(models.Model):
    id = models.AutoField(primary_key=True)
    portal_name = models.CharField(max_length=50, blank=True, null=True, choices=[('geosecure', 'GeoSecure'),
                                                                                  ('geoplatform', 'GeoPlatform')])
    portal_url = models.URLField()
    org_id = models.CharField(max_length=50, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    allow_external_accounts = models.BooleanField(default=False, help_text='Allow external (non-enterprise) accounts to be created.')
    enterprise_precreate_domains = models.TextField(null=True, blank=True, verbose_name='Email domains for enterprise accounts',
                                                    help_text='Separate email domains with comma (e.g. gmail.com,hotmail.com). Value required if external account creation is not allowed')
    requires_auth_group = models.BooleanField(default=True)
    email_signature_content = CKEditor5Field()

    @property
    def enterprise_precreate_domains_list(self):
        if self.enterprise_precreate_domains:
            return self.enterprise_precreate_domains.split(',')
        return []


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.user:
            if not self.org_id:
                self.org_id = self.get_org_id()
                super().save(*args, **kwargs)
            if self.groups.count() == 0:
                self.get_all_groups()
                self.get_all_existing_user_group_memberships()
            if self.roles.count() == 0:
                self.get_all_roles()

    def __str__(self):
        return self.get_portal_name_display()

    def get_token(self):
        social = self.user.social_auth.get()
        return social.get_access_token(load_strategy())

    def get_org_id(self):
        if not self.org_id:
            r = requests.get('{}/sharing/rest/portals/self'.format(self.portal_url),
                             params={'f': 'json', 'token': self.get_token()})
            return r.json()['id']

    def get_list(self, url, results_key='results', use_query=True):
        try:
            sys.stdout.write(f'\nGetting All from {self.portal_url}... \n')

            next_record, total_records, update_total = 0, 1, True
            all_records = []
            org_query = 'orgid:{}'.format(self.org_id)
            q = org_query
            while total_records != len(all_records) and total_records > len(all_records):
                r = requests.get(f'{self.portal_url}/sharing/rest/{url}',
                                 params={'token': self.get_token(), 'f': 'json', 'q': q,
                                         'num': '100', 'start': next_record, 'sortField': 'created',
                                         'sortOrder': 'asc'})
                response_json = r.json(strict=False)

                if update_total:
                    total_records = len(all_records) + response_json['total']
                    update_total = False

                next_record = response_json['nextStart']
                all_records += response_json[results_key]
                sys.stdout.flush()
                sys.stdout.write('\rFetched {} of {}\r'.format(len(all_records), total_records))

                if (response_json['nextStart'] == -1 or response_json['nextStart'] == 0) and use_query:
                    next_record = 1
                    q = 'uploaded: [000000{} TO 000000{}000] AND {}'.format(all_records[-1]['created'] + 1,
                                                                            int(time.time()),
                                                                            org_query)
                    update_total = True

            return all_records

        except:
            sys.stdout.write('\nError encountered. Stopping update.\n')
            # logger.exception('Error in refreshAllAGOL refresh_catalog')
            raise

    def get_all_groups(self):
        try:
            all_groups = self.get_list('community/groups')
            sys.stdout.write(f'\nCreating/updating groups from {self.portal_url}...\n')

            for group in all_groups:
                AGOLGroup.objects.update_or_create(id=group['id'], defaults={'title': group['title'], 'agol': self})

        except:
            sys.stdout.write('\nError encountered. Stopping update.\n')
            raise

    def get_all_existing_user_group_memberships(self):
        GroupMembership.objects.filter(user__isnull=False).delete()
        for user in AGOLUserFields.objects.filter(portal=self):
            r = requests.get(f'{self.portal_url}/sharing/rest/community/users/{user.agol_username}',
                             params={'token': self.get_token(), 'f': 'json'})
            response_json = r.json(strict=False)
            if 'error' in response_json:
                continue
            for group in response_json.get('groups', []):
                if AGOLGroup.objects.filter(id=group['id'], agol=self).exists():
                    GroupMembership.objects.create(group_id=group['id'], user=user, is_member=True)


    def get_all_roles(self):
        all_roles = self.get_list('portals/self/roles', 'roles')
        sys.stdout.write(f'\nCreating/updating roles from {self.portal_url}...\n')
        for role in all_roles:
            AGOLRole.objects.update_or_create(role_id=role['id'], agol=self,
                                              defaults={
                                                  'name': role['name'],
                                                  'description': role['description']})

    def get_group(self, group_id):
        r = requests.get(f'{self.portal_url}/sharing/rest/community/groups/{group_id}',
                         params={'token': self.get_token(), 'f': 'json'})
        if r.status_code == requests.codes.ok:
            response_json = r.json(strict=False)
            AGOLGroup.objects.update_or_create(id=response_json.get('id'), defaults={
                "title": response_json['title'],
                "agol": self
            })

    def generate_user_request_data(self, account_request, initial_password=None):
        user_request_data = {
            "email": account_request.email,
            "firstname": account_request.first_name,
            "lastname": account_request.last_name,
            "username": account_request.username,
            "role": account_request.role.role_id,
            "userLicenseType": account_request.user_type.code,
            "fullname": f"{account_request.first_name} {account_request.last_name}",
            "userCreditAssignment": 2000
        }
        if initial_password:
            user_request_data["password"] = initial_password

        return user_request_data

    def create_user_account(self, account_request, initial_password=None):
        # fail if the account already exists (don't send an invite)
        if account_request.agol_id is not None:
            return False

        token = self.get_token()

        user_request_data = self.generate_user_request_data(account_request, initial_password)

        # if user has enterprise email address and is using enterprise authentication, account needs to be pre-created
        if account_request.is_enterprise_account():
            url = f'{self.portal_url}/portaladmin/security/users/createUser'
            user_request_data.update({
                "provider": "enterprise",
                "userLicenseTypeId": "creatorUT",
                "f": "json",
                "token": token,
            })
            data = user_request_data

        elif account_request.response.portal.allow_external_accounts:  # Invite user
            url = f'{self.portal_url}/sharing/rest/portals/self/invite/'

            # goofy way of encoding data since requests library does not seem to appreciate the nested structure.
            data = {
                "invitationList": json.dumps({"invitations": [user_request_data]}),
                "f": "json",
                "token": token
            }

            if initial_password is None:
                template = get_template('invitation_email_body.html')
                data["message"] = template.render({
                    "account_request": account_request,
                    "PORTAL": self
                })

        else:
            # should not get here
            raise Exception('Portal does not allow external accounts and request email does not have a preapproved domain')

        # pre-encode to ensure nested data isn't lost
        data = urlencode(data)
        response = requests.post(url, data=data, headers={'Content-type': 'application/x-www-form-urlencoded'})

        response_json = response.json()

        if 'success' in response_json and response_json['success'] or response_json.get('status', False) == 'success':
            # and account_request.username not in response_json['notInvited']:
            user_url = f'{self.portal_url}/sharing/rest/community/users/{account_request.username}'
            user_response = requests.get(user_url, params={'token': token, 'f': 'json'})
            user_response_json = user_response.json()
            if 'error' in user_response_json:
                logger.error(response_json)
                return False
            else:
                account_request.agol_id = user_response_json['id']
                account_request.save(update_fields=['agol_id'])

            return True
        else:
            logger.error(response_json)
            return False

    def disable_user_account(self, username):
        url = f"{self.portal_url}/sharing/rest/community/users/{username}/disable"
        token = self.get_token()
        r = requests.post(url, data={'token': token, 'f': 'json'})
        r_json = r.json()
        if 'error' in r_json:
            raise Exception(r_json)


    def _username_check(self, username: list[str], token: str):
        url = f'{self.portal_url}/sharing/rest/community/checkUsernames'

        data = {
            'usernames': username,
            'f': 'json',
            'token': token
        }

        r = requests.post(url, data=data)

        return r.json()

    def check_username(self, username: list[str]):
        token = self.get_token()
        response = self._username_check(username, token)

        # error or missing usernames will fail everything so bail here and mark invalid
        if 'error' in response or 'usernames' not in response:
            return False, None, [], False, None, None, None

        # if it suggested matches requested...great this is normal for new accounts
        if response['usernames'] and response['usernames'][0]['requested'] == response['usernames'][0]['suggested']:
            return True, None, [], False, None, None, None
        # if list is blank the account appears to not exist but may have been previously deleted
        elif len(response['usernames']) == 0:
            return True, None, [], False, None, None, None
        else:
            # else check actual username endpoint and see if user exists
            user_url = f'{self.portal_url}/sharing/rest/community/users/{username}'

            user_response = requests.get(user_url, params={'token': token, 'f': 'json'})
            user_response_json = user_response.json()
            if 'error' in user_response_json or 'disabled' not in user_response_json:
                return False, None, [], False, None, None, None
            else:
                # fixes issue #34
                group_ids = list(x['id'] for x in user_response_json.get('groups', []))
                for group_id in (x for x in group_ids if not AGOLGroup.objects.filter(id=x).exists()):
                    self.get_group(group_id)
                return False, user_response_json['id'], group_ids, \
                    not user_response_json['disabled'], \
                    datetime.utcfromtimestamp(user_response_json['created'] / 1000), \
                    user_response_json['userLicenseTypeId'], \
                    user_response_json.get('roleId', None)

    def add_to_group(self, user, group):
        token = self.get_token()

        url = f'{self.portal_url}/sharing/rest/community/groups/{str(group).replace("-", "")}/addUsers'

        data = {
            'users': user,
            'f': 'json',
            'token': token
        }
        r = requests.post(url, data=data)

        response_json = r.json()

        if 'error' in response_json:
            return False

        if user in response_json['notAdded']:
            return False

        return True

    def find_accounts_by_email(self, email):
        token = self.get_token()
        url = f'{self.portal_url}/sharing/rest/community/users'

        """ email search is case sensitive ?!?! """
        r = requests.get(url, params={'q': f'email:{email}', 'f': 'json', 'token': token})

        usernames = []
        response_json = r.json()
        if 'error' not in response_json and r.status_code == requests.codes.ok:
            for result in response_json['results']:
                usernames.append(result['username'])

        return ",".join(usernames)

    def enable_user_account(self, username):
        token = self.get_token()
        url = f'{self.portal_url}/sharing/rest/community/users/{username}/enable'
        data = {
            'f': 'json',
            'token': token
        }
        r = requests.post(url, data=data)
        response_json = r.json()
        if r.status_code == requests.codes.ok:
            return response_json.get('success', False)
        return False

    def update_user_account(self, username, data):
        token = self.get_token()
        url = f'{self.portal_url}/sharing/rest/community/users/{username}/update'
        data['f'] = 'json'
        data['token'] = token

        r = requests.post(url, data=data)
        response_json = r.json()
        if r.status_code == requests.codes.ok:
            return response_json.get('success', False)
        return False

    def update_user_type(self, username, user_type):
        url = f'{self.portal_url}/sharing/rest/portals/self/updateUserLicenseType'
        data = {
            'users': [username],
            'userLicenseType': user_type,
            'f': 'json',
            'token': self.get_token()
        }
        r = requests.post(url, data=data)

        if 'error' in r.json():
            raise Exception(r.json())

        return r.json().get('success', False)

    def update_user_role(self, username, role):
        url = f'{self.portal_url}/sharing/rest/portals/self/updateUserRole'
        data = {
            'user': username,
            'role': role,
            'f': 'json',
            'token': self.get_token()
        }
        r = requests.post(url, data=data)

        if 'error' in r.json():
            raise Exception(r.json())

        return r.json().get('success', False)

    class Meta:
        verbose_name = 'AGOL/Portal'
        verbose_name_plural = 'AGOL/Portals'

class AGOLUserFields(models.Model):
    id = models.AutoField(primary_key=True)
    agol_username = models.CharField(max_length=200, null=True, blank=True)
    portal = models.ForeignKey(AGOL, models.PROTECT)
    sponsor = models.BooleanField(default=False)

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agol_info')
    delegates = models.ManyToManyField(User, related_name='delegate_for', blank=True)

    def get_email_recipients(self):
        to = set()
        to.add(self.user.email.lower())
        for delegate in self.delegates.all():
            to.add(delegate.email.lower())
        return to

    def clean(self):
        super().clean()
        if self.sponsor and not self.user.email:
            raise ValidationError('Email can not be blank if user is a sponsor.')


class ResponseProject(models.Model):
    def __init__(self, *args, **kwargs):
        super(ResponseProject, self).__init__(*args, **kwargs)
        # capture is_disabled value at init before any changes are made
        self._disabled = self.disabled
        self._approved = self.approved

    id = models.AutoField(primary_key=True)
    users = models.ManyToManyField(User, related_name='response', verbose_name='Sponsors',
                                   limit_choices_to={'agol_info__sponsor': True}, blank=True)
    name = models.CharField('Name', max_length=500)
    portal = models.ForeignKey(AGOL, models.PROTECT, related_name='responses', verbose_name='Portal/AGOL')
    assignable_groups = models.ManyToManyField('AGOLGroup', related_name='response',
                                               verbose_name='Assignable Groups')
    role = models.ForeignKey('AGOLRole', on_delete=models.PROTECT, verbose_name='Role',
                             limit_choices_to={'is_available': True}, related_name='responses')
    authoritative_group = models.ForeignKey('AGOLGroup', on_delete=models.PROTECT,
                                            verbose_name='Authoritative Group', blank=True, null=True,
                                            limit_choices_to={'is_auth_group': True})
    disabled = models.DateTimeField(null=True, blank=True)
    disabled_by = models.ForeignKey(User, models.PROTECT, 'disabled_responses', null=True, blank=True)
    default_reason = models.CharField(max_length=200, choices=REASON_CHOICES,
                                      verbose_name='Default Reason / Affiliation')
    approved = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, models.PROTECT, 'approved_responses', null=True, blank=True)
    requester = models.ForeignKey(User, models.PROTECT, 'requested_responses', null=True, blank=True)
    notifications = GenericRelation('Notification')
    protected_datasets = models.ManyToManyField('ProtectedDataset', null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def sponsors(self):
        return ','.join([f'{u.first_name} {u.last_name}' for u in self.users.all()])

    @property
    def request_url(self):
        return f"{settings.HOST_ADDRESS}?response={self.pk}"

    @property
    def disable_users_link(self):
        # # define link to relevant user accounts using AGOL/portal of response/project being modified
        # agol = self.portal
        # url = f'{agol.portal_url}/home/organization.html?'
        # query_params = {'showFilters': 'false', 'view': 'table', 'sortOrder': 'asc', 'sortField': 'fullname'}
        # # get account request AGOL IDs to define in link
        # agol_ids = list(
        #     str(acct.agol_id).replace('-', '') for acct in self.requests.filter(agol_id__isnull=False,
        #                                                                         is_existing_account=False))
        # agol_ids_param = '&searchTerm=' + '%20OR%20'.join(agol_ids)
        # return f'{url}{urlencode(query_params)}{agol_ids_param}#members'
        # above links to agol/portal but with longer lists this fails b/c the url is too long
        url = f"{reverse('admin:accounts_accountrequests_changelist')}?response__id__exact={self.pk}"
        return url

    @property
    def auth_group_required(self):
        return self.portal.requires_auth_group if self.pk else False

    def can_be_disabled(self):
        return not self.requests.filter(approved__isnull=True).exists()

    def clean(self):
        if self.auth_group_required and not self.role.auth_groups.filter(id=self.authoritative_group_id).exists():
            raise ValidationError({"authoritative_group": "The Authoritative Group must be available under the selected Role. "
                                  "Check the Role's allowed Authoritative Groups."})

    def save(self, *args, **kwargs):
        if self.role is None:
            self.role = self.portal.roles.get(system_default=True)

        send_approved_email = not self._approved and self.approved
        send_disabled_email = not self._disabled and self.disabled

        super().save(*args, **kwargs)
        if send_approved_email:
            to, subject, message = self.generate_approval_email()
        elif send_disabled_email:
            to, subject, message = self.generate_disable_email()

        if send_approved_email or send_disabled_email:
            Notification.create_new_notification(
                to=to,
                subject=subject,
                content=message,
                content_object=self
            )

    def generate_new_email(self):
        REQUEST_URL = f"{settings.HOST_ADDRESS}/api/admin/accounts/responseproject/{self.pk}?{self.portal}"
        to = [x.email.lower() for x in User.objects.filter(groups__pk=settings.COORDINATOR_ADMIN_GROUP_ID)]
        subject = f'New {self.portal} Response/Project Request for Review in Account Request Tool'
        content = render_to_string('new_response_request_email.html', {
            "REQUEST_URL": REQUEST_URL,
            "PORTAL": self.portal
        })
        return to, subject, content

    def get_email_recipients(self):
        recipients = set()
        for sponsor in self.users.all():
            recipients.update(sponsor.agol_info.get_email_recipients())
        return recipients

    def generate_approval_email(self):
        try:
            recipients = self.get_email_recipients()
            request_url = self.request_url
            approval_url = f"{settings.HOST_ADDRESS}/accounts/list?{self.portal}"
            email_subject = f"{self.portal} Account Response/Project {self.name} has been approved"
            msg = render_to_string('response_approval_email.html', {
                "response_project": self,
                "PORTAL": self.portal,
                "request_url": request_url,
                "approval_url": approval_url
            })
            return recipients, email_subject, msg

        except Exception as e:
            logger.error(
                "Email Error: There was an error emailing the disabled Response Project's assigned sponsors and their delegates.",
                e)
            raise e

    def generate_disable_email(self):
        try:
            recipients = self.get_email_recipients()
            email_subject = f"{self.portal} Account Response/Project {self.name} has been disabled"
            msg = render_to_string('response_disable_email.html', {"response_project": self, "PORTAL": self.portal})
            return recipients, email_subject, msg

        except Exception as e:
            logger.error(
                "Email Error: There was an error emailing the disabled Response Project's assigned sponsors and their delegates.")
            raise e


    class Meta:
        verbose_name_plural = 'Responses/Projects'
        verbose_name = 'Response/Project'


class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    to = models.TextField()
    subject = models.TextField()
    content = models.TextField()
    sent = models.DateTimeField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.subject

    @property
    def to_emails(self):
        return set([x.lower() for x in json.loads(self.to)])

    @classmethod
    def create_new_notification(cls, subject, to, content_object, template=None, context=None, content=None):
        if content:
            n = cls.objects.create(
                subject=subject,
                content=content,
                content_object=content_object,
                to=json.dumps(list(to))
            )
        elif template and context:
            n = cls.objects.create(
                subject=subject,
                content=render_to_string(template, context),
                content_object=content_object,
                to=json.dumps(list(to))
            )
        else:
            raise ValueError('Must provide content or template and context')

        return n

    def send(self):
        results = send_mail(
            self.subject,
            self.content,
            settings.EMAIL_FROM,
            list(set(self.to_emails)),
            fail_silently=False,
            html_message=self.content,
        )
        if results == 1:
            self.sent = datetime.now()
            self.save()


class ProtectedDataset(models.Model):
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name
