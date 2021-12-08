from django.db import models
from django.core.exceptions import ValidationError
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

import sys
import requests
from django.db.models import UniqueConstraint
from social_django.utils import load_strategy
import time
from django.contrib.auth.models import User, Group
from urllib.parse import urlencode
import json

import logging

logger = logging.getLogger('AGOLAccountRequestor')

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
    USER_TYPE_CHOICES = (('creatorUT', 'Creator'),)
    # ROLE_CHOICES = (('jmc1ObdWfBTH6NAN', 'EPA Publisher'),
    #                 ('71yacZLdeuDirQ6K', 'EPA Viewer'))

    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    possible_existing_account = models.CharField(max_length=300, blank=True, null=True)
    is_existing_account = models.BooleanField(default=False)
    organization = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    username_valid = models.BooleanField(default=False)
    user_type = models.CharField(max_length=200, choices=USER_TYPE_CHOICES, default='creatorUT')
    role = models.ForeignKey('AGOLRole', on_delete=models.DO_NOTHING, blank=True, null=True)
    groups = models.ManyToManyField('AGOLGroup', blank=True, related_name='account_requests', through='GroupMembership')
    auth_group = models.ForeignKey('AGOLGroup', on_delete=models.DO_NOTHING, blank=True, null=True)
    sponsor = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    # sponsor_notified = models.BooleanField(default=False)
    reason = models.CharField(max_length=200, choices=REASON_CHOICES, blank=True, null=True)
    recaptcha = models.TextField()
    submitted = models.DateTimeField(auto_now_add=True)
    approved = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(null=True, blank=True)
    agol_id = models.UUIDField(blank=True, null=True)
    response = models.ForeignKey('ResponseProject', on_delete=models.PROTECT, blank=True, null=True,
                                 related_name='requests')
    notifications = GenericRelation('Notification')

    @property
    def sponsor_notified(self):
        return self.notifications.count() > 0

    def create_new_notification(self):
        n = Notification.objects.create(
            subject='New GeoPlatform Account Request',
            content=render_to_string("new_account_request_email.html", {"HOST_ADDRESS": settings.HOST_ADDRESS}),
            content_object=self
        )
        n.to.set(self.response.get_email_recipients())

    def save(self, *args, **kwargs):
        # this resets role and auth_group if the response changes
        if self.response:
            self.role = self.response.role
            self.auth_group = self.response.authoritative_group

        send_notification = self.pk is None
        super().save(*args, **kwargs)
        if send_notification:
            self.create_new_notification()

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
    is_auth_group = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class GroupMembership(models.Model):
    group = models.ForeignKey('AGOLGroup', on_delete=models.CASCADE)
    request = models.ForeignKey('AccountRequests', on_delete=models.CASCADE)
    is_member = models.BooleanField(default=False)


class AGOLRole(models.Model):
    id = models.CharField(primary_key=True, max_length=16)
    name = models.CharField(max_length=200)
    description = models.TextField()
    is_available = models.BooleanField(default=False)
    agol = models.ForeignKey('AGOL', on_delete=models.CASCADE, related_name='roles')
    system_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def clean(self):
        if self.system_default:
            if (self.pk and AGOLRole.objects.filter(system_default=True).exclude(pk=self.pk).exists()) or \
                    AGOLRole.objects.filter(system_default=True).exists():
                raise ValidationError({'system_default': 'You cannot have more than one system default.'})


class AGOL(models.Model):
    portal_url = models.URLField()
    org_id = models.CharField(max_length=50, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        if not self.org_id:
            self.org_id = self.get_org_id()

        if not self.pk:
            super().save(*args, **kwargs)
            if self.groups.count() == 0:
                self.get_all_groups()

            if self.roles.count() == 0:
                self.get_all_roles()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.portal_url

    def get_token(self):
        social = self.user.social_auth.get(provider='agol')
        return social.get_access_token(load_strategy())

    def get_org_id(self):
        if not self.org_id:
            r = requests.get('{}/sharing/rest/portals/self'.format(self.portal_url),
                             params={'f': 'json', 'token': self.get_token()})
            return r.json()['id']

    def get_list(self, url, results_key='results'):
        try:

            sys.stdout.write(f'\nGetting All {url}... \n')

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

                if response_json['nextStart'] == -1 or response_json['nextStart'] == 0:
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
            sys.stdout.write('\nCreating/updating groups...\n')

            for group in all_groups:
                AGOLGroup.objects.update_or_create(id=group['id'], defaults={'title': group['title'], 'agol': self})

        except:
            sys.stdout.write('\nError encountered. Stopping update.\n')
            raise

    def get_all_roles(self):
        all_roles = self.get_list('portals/self/roles', 'roles')
        sys.stdout.write('\nCreating/updating roles...\n')
        for role in all_roles:
            AGOLRole.objects.update_or_create(id=role['id'], defaults={'name': role['name'],
                                                                       'description': role['description'],
                                                                       'agol': self})

    def get_group(self, group_id):
        r = requests.get(f'{self.portal_url}/sharing/rest/community/groups/{group_id}',
                         params={'token': self.get_token(), 'f': 'json'})
        if r.status_code == requests.codes.ok:
            response_json = r.json(strict=False)
            AGOLGroup.objects.update_or_create(id=response_json.get('id'), defaults={
                "title": response_json['title'],
                "agol": self
            })

    def generate_invitation(self, account_request, initial_password=None):
        invitation = {
            "email": account_request.email,
            "firstname": account_request.first_name,
            "lastname": account_request.last_name,
            "username": account_request.username,
            "role": account_request.role.id,
            "userLicenseType": account_request.user_type,
            "fullname": f"{account_request.first_name} {account_request.last_name}",
            "userType": "creatorUT",
            "userCreditAssignment": 2000
        }
        if initial_password:
            invitation["password"] = initial_password

        return invitation

    def create_users_accounts(self, account_requests: [AccountRequests], initial_password=None):
        token = self.get_token()
        success = []
        url = f'{self.portal_url}/sharing/rest/portals/self/invite/'
        for account_request in [x for x in account_requests if x.agol_id is None]:
            invitation = self.generate_invitation(account_request, initial_password)

            # goofy way of encoding data since requests library does not seem to appreciate the nested structure.
            data = {
                "invitationList": json.dumps({"invitations": [invitation]}),
                "f": "json",
                "token": token
            }

            if initial_password is None:
                template = get_template('invitation_email_body.html')
                data["message"] = template.render({"account_request": account_request})

            # pre-encode to ensure nested data isn't lost
            data = urlencode(data)
            response = requests.post(url, data=data, headers={'Content-type': 'application/x-www-form-urlencoded'})

            response_json = response.json()

            if 'success' in response_json and response_json['success'] \
                    and account_request.username not in response_json['notInvited']:
                # success = []
                # for account in AccountRequests.objects.filter(pk__in=[x.pk for x in account_requests])\
                #     .exclude(username__in=response_json['notInvited']):
                success.append(account_request.pk)
                user_url = f'{self.portal_url}/sharing/rest/community/users/{account_request.username}'
                user_response = requests.get(user_url, params={'token': token, 'f': 'json'})
                user_response_json = user_response.json()
                if 'error' in user_response_json:
                    return False, None, None
                else:
                    account_request.agol_id = user_response_json['id']
                    account_request.save(update_fields=['agol_id'])
        return success

    def check_username(self, username):
        token = self.get_token()
        url = f'{self.portal_url}/sharing/rest/community/checkUsernames'

        data = {
            'usernames': username,
            'f': 'json',
            'token': token
        }

        r = requests.post(url, data=data)

        response = r.json()
        if 'error' in response:
            return False, None, []

        if 'usernames' in response:
            # if it suggested matches requested...great this is normal for new accounts
            if response['usernames'] and response['usernames'][0]['requested'] == response['usernames'][0]['suggested']:
                return True, None, []
            # if list is blank the account appears to not exist but may have been previously deleted
            elif len(response['usernames']) == 0:
                return True, None, []
            else:
                user_url = f'{self.portal_url}/sharing/rest/community/users/{username}'

                user_response = requests.get(user_url, params={'token': token, 'f': 'json'})
                user_response_json = user_response.json()
                if 'error' in user_response_json:
                    return False, None, []
                else:
                    # fixes issue #34
                    group_ids = list(x['id'] for x in user_response_json.get('groups', []))
                    for id in (x for x in group_ids if not AGOLGroup.objects.filter(id=x).exists()):
                        self.get_group(id)
                    return False, user_response_json['id'], group_ids

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


class AGOLUserFields(models.Model):
    agol_username = models.CharField(max_length=200, null=True, blank=True)
    sponsor = models.BooleanField(default=False)

    phone_number = models.CharField(max_length=20, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agol_info')
    delegates = models.ManyToManyField(User, related_name='delegate_for', blank=True)

    def get_email_recipients(self):
        to = set()
        to.add(self.user)
        for delegate in self.delegates.all():
            to.add(delegate)
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

    users = models.ManyToManyField(User, related_name='response', verbose_name='Sponsors',
                                   limit_choices_to={'agol_info__sponsor': True}, blank=True)
    name = models.CharField('Name', max_length=500)
    assignable_groups = models.ManyToManyField('AGOLGroup', related_name='response',
                                               verbose_name='GeoPlatform Assignable Groups')
    role = models.ForeignKey('AGOLRole', on_delete=models.PROTECT, verbose_name='GeoPlatform Role',
                             limit_choices_to={'is_available': True}, null=True, blank=True,
                             help_text='System default will be used if left blank.')
    authoritative_group = models.ForeignKey('AGOLGroup', on_delete=models.PROTECT,
                                            verbose_name='Geoplatform Authoritative Group',
                                            limit_choices_to={'is_auth_group': True})
    disabled = models.DateTimeField(null=True, blank=True)
    disabled_by = models.ForeignKey(User, models.PROTECT, 'disabled_responses', null=True, blank=True)
    default_reason = models.CharField(max_length=200, choices=REASON_CHOICES,
                                      verbose_name='Default Reason / Affiliation')
    approved = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, models.PROTECT, 'approved_responses', null=True, blank=True)
    requester = models.ForeignKey(User, models.PROTECT, 'requested_responses')
    notifications = GenericRelation('Notification')

    def __str__(self):
        return self.name

    @property
    def sponsors(self):
        return ','.join([f'{u.first_name} {u.last_name}' for u in self.users.all()])

    @property
    def disable_users_link(self):
        # define link to relevant user accounts
        agol = AGOL.objects.first()
        url = f'{agol.portal_url}/home/organization.html?'
        query_params = {'showFilters': 'false', 'view': 'table', 'sortOrder': 'asc', 'sortField': 'fullname'}
        # get account request AGOL IDs to define in link
        agol_ids = list(
            str(acct.agol_id).replace('-', '') for acct in self.requests.filter(agol_id__isnull=False,
                                                                                is_existing_account=False))
        agol_ids_param = '&searchTerm=' + '%20OR%20'.join(agol_ids)
        return f'{url}{urlencode(query_params)}{agol_ids_param}#members'

    def can_be_disabled(self):
        return not self.requests.filter(approved__isnull=True).exists()

    def save(self, *args, **kwargs):
        if self.role is None:
            self.role = AGOLRole.objects.get(system_default=True)
        send_notification = self.pk is None
        super().save(*args, **kwargs)
        if send_notification:
            self.create_new_notification()

    def create_new_notification(self):
        REQUEST_URL = f"{settings.HOST_ADDRESS}/api/admin/accounts/responseproject/{self.pk}"
        n = Notification.objects.create(
            subject='New Response/Project Request for Review in GeoPlatform Account Request Tool',
            content=render_to_string("new_response_request_email.html", {"REQUEST_URL": REQUEST_URL}),
            content_object=self
        )
        n.to.set(User.objects.filter(groups__name="Coordinator Admin"))

    def get_email_recipients(self):
        recipients = set()
        for sponsor in self.users.all():
            recipients.update(sponsor.agol_info.get_email_recipients())
        return recipients

    def generate_approval_email(self):
        try:
            # from_email_account = settings.GPO_REQUEST_EMAIL_ACCOUNT

            recipients = self.get_email_recipients()
            request_url = f"{settings.HOST_ADDRESS}?id_in={self.pk}"
            approval_url = f"{settings.HOST_ADDRESS}/accounts/list"
            email_subject = f"GeoPlatform Account Response/Project {self.name} has been approved"
            msg = render_to_string('response_approval_email.html', {
                "response_project": self,
                "request_url": request_url,
                "approval_url": approval_url
            })
            return recipients, email_subject, msg

        except Exception as e:
            logger.error(
                "Email Error: There was an error emailing the disabled Response Project's assigned sponsors and their delegates.", e)

    def generate_disable_email(self):
        try:
            # from_email_account = settings.GPO_REQUEST_EMAIL_ACCOUNT
            recipients = self.get_email_recipients()
            email_subject = f"GeoPlatform Account Response/Project {self.name} has been disabled"
            msg = render_to_string('response_disable_email.html', {"response_project": self})
            return recipients, email_subject, msg

        except Exception as e:
            logger.error(
                "Email Error: There was an error emailing the disabled Response Project's assigned sponsors and their delegates.")

    class Meta:
        verbose_name_plural = 'Responses/Projects'
        verbose_name = 'Response/Project'


class Notification(models.Model):
    to = models.ManyToManyField(User)
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
        return set([x.email.lower() for x in self.to.all()])
