from django.db import models
import sys
import requests
from social_django.utils import load_strategy
import time
from django.contrib.auth.models import User, Group
from urllib.parse import urlencode
import json
from django.utils.timezone import now
from django.core.exceptions import ValidationError


class AccountRequests(models.Model):
    USER_TYPE_CHOICES = (('creatorUT', 'Creator'),)
    ROLE_CHOICES = (('jmc1ObdWfBTH6NAN', 'EPA Publisher'),
                    ('71yacZLdeuDirQ6K', 'EPA Viewer'))

    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    possible_existing_account = models.CharField(max_length=300, blank=True, null=True)
    organization = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    username_valid = models.BooleanField(default=False)
    user_type = models.CharField(max_length=200, choices=USER_TYPE_CHOICES, default='creatorUT')
    role = models.CharField(max_length=200, choices=ROLE_CHOICES, default='jmc1ObdWfBTH6NAN')
    groups = models.ManyToManyField('AGOLGroup', blank=True)
    sponsor = models.ForeignKey(User, on_delete=models.PROTECT)
    sponsor_notified = models.BooleanField(default=False)
    recaptcha = models.TextField()
    submitted = models.DateTimeField(auto_now_add=True)
    approved = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(null=True, blank=True)
    agol_id = models.UUIDField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Account Requests'
        verbose_name = 'Account Request'

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
    show = models.BooleanField(default=False, verbose_name='Show in all multi-selects')
    requests = models.ManyToManyField('AccountRequests')

    def __str__(self):
        return self.title


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

    def get_all_groups(self):
        try:

            sys.stdout.write('\nGetting All Groups... \n')

            next_record, total_records, update_total = 0, 1, True
            all_groups = []
            org_query = 'orgid:{}'.format(self.org_id)
            q = org_query
            while total_records != len(all_groups) and total_records > len(all_groups):
                r = requests.get(self.portal_url + '/sharing/rest/community/groups',
                                 params={'token': self.get_token(), 'f': 'json', 'q': q,
                                         'num': '100', 'start': next_record, 'sortField': 'created', 'sortOrder': 'asc'})
                response_json = r.json(strict=False)

                if update_total:
                    total_records = len(all_groups) + response_json['total']
                    update_total = False

                next_record = response_json['nextStart']
                all_groups += response_json['results']
                sys.stdout.flush()
                sys.stdout.write('\rFetched {} of {}\r'.format(len(all_groups), total_records))

                if response_json['nextStart'] == -1 or response_json['nextStart'] == 0:
                    next_record = 1
                    q = 'uploaded: [000000{} TO 000000{}000] AND {}'.format(all_groups[-1]['created'] + 1,
                                                                            int(time.time()),
                                                                            org_query)
                    update_total = True

            groups = []
            for group in all_groups:
                groups.append(AGOLGroup(id=group['id'], title=group['title'], agol=self))
            sys.stdout.write('\nBulk creating groups...\n')

            AGOLGroup.objects.all().delete()
            AGOLGroup.objects.bulk_create(groups)

        except:
            sys.stdout.write('\nError encountered. Stopping update.\n')
            # logger.exception('Error in refreshAllAGOL refresh_catalog')
            raise

    def create_users_accounts(self, account_requests, initial_password):
        token = self.get_token()

        url = f'{self.portal_url}/sharing/rest/portals/self/invite/'

        invitations = list()

        for account_request in account_requests:
            invitations.append({
                "email": account_request.email,
                "firstname": account_request.first_name,
                "lastname": account_request.last_name,
                "username": account_request.username,
                "password": initial_password,
                "role": account_request.role,
                "userLicenseType": account_request.user_type,
                "fullname": f"{account_request.first_name} {account_request.last_name}",
                "userType": "arcgisonly",
                "groups": ",".join(str(x) for x in account_request.groups.all().values_list('id', flat=True)),
                "userCreditAssignment": 2000
            })

        # goofy way of encoding data since request library does not seem to appreciate the nested structure.
        data = {
            "invitationList": json.dumps({"invitations": invitations}),
            "f": "json",
            "token": token
        }
        data = urlencode(data)
        response = requests.post(url, data=data, headers={'Content-type': 'application/x-www-form-urlencoded'})

        response_json = response.json()

        if 'success' in response_json and response_json['success']:
            for account in AccountRequests.objects.filter(pk__in=[x.pk for x in account_requests])\
                .exclude(username__in=response_json['notInvited']):
                user_url = f'{self.portal_url}/sharing/rest/community/users/{account.username}'
                user_response = requests.get(user_url, params={'token': token, 'f': 'json'})
                user_response_json = user_response.json()
                if 'error' in user_response_json:
                    return False, None, None
                else:
                    account.agol_id = user_response_json['id']
                    account.save(update_fields=['agol_id'])
            return True
        else:
            return False

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
            if response['usernames'][0]['requested'] == response['usernames'][0]['suggested']:
                return True, None, []
            else:
                user_url = f'{self.portal_url}/sharing/rest/community/users/{username}'

                user_response = requests.get(user_url, params={'token': token, 'f': 'json'})
                user_response_json = user_response.json()
                if 'error' in user_response_json:
                    return False, None, []
                else:
                    return False, user_response_json['id'], list(x['id'] for x in user_response_json['groups'])

    def add_to_group(self, accounts, groups):
        token = self.get_token()
        for group in groups:
            url = f'{self.portal_url}/sharing/rest/community/groups/{group.replace("-", "")}/addUsers'

            data = {
                'users': ",".join(accounts),
                'f': 'json',
                'token': token
            }
            r = requests.post(url, data=data)

            response_json = r.json()

        if 'error' in response_json:
            return False

        return r.status_code == requests.codes.ok

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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agol_info')

    def clean(self):
        super().clean()
        if self.sponsor and not self.user.email:
            raise ValidationError('Email can not be blank if user is a sponsor.')


class AGOLGroupFields(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    assignable_groups = models.ManyToManyField('AGOLGroup', blank=True, related_name='assignable_groups')
