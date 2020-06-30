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
    REASON_CHOICES = (('Emergency Response', 'Emergency Response'),
                      ('Other Federal Agency', 'Other Federal Agency'),
                      ('State Agency', 'State Agency'),
                      ('University', 'University'),
                      ('Long Term GIS Support', 'Long Term GIS Support'),
                      ('Non Government Organization', 'Non Government Organization'),
                      ('Tribal Government', 'Tribal Government'),
                      ('Citizen Advisor', 'Citizen Advisor'),
                      ('Other', 'Other'))

    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    possible_existing_account = models.CharField(max_length=300, blank=True, null=True)
    organization = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    username_valid = models.BooleanField(default=False)
    user_type = models.CharField(max_length=200, choices=USER_TYPE_CHOICES, default='creatorUT')
    role = models.ForeignKey('AGOLRole', on_delete=models.DO_NOTHING, blank=True, null=True)
    groups = models.ManyToManyField('AGOLGroup', blank=True, related_name='account_requests')
    auth_group = models.ForeignKey('AGOLGroup', on_delete=models.DO_NOTHING, blank=True, null=True)
    sponsor = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    sponsor_notified = models.BooleanField(default=False)
    reason = models.CharField(max_length=200, choices=REASON_CHOICES, default='Emergency Response')
    recaptcha = models.TextField()
    submitted = models.DateTimeField(auto_now_add=True)
    approved = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(null=True, blank=True)
    agol_id = models.UUIDField(blank=True, null=True)
    response = models.ForeignKey('ResponseProject', on_delete=models.PROTECT, blank=True, null=True)

    def save(self, *args, **kwargs):
        # this resets role and auth_group if the response changes
        self.role = self.response.role
        self.auth_group = self.response.authoritative_group
        super().save(*args, **kwargs)

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
    requests = models.ManyToManyField('AccountRequests')
    is_auth_group = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class AGOLRole(models.Model):
    id = models.CharField(primary_key=True, max_length=16)
    name = models.CharField(max_length=200)
    description = models.TextField()
    is_available = models.BooleanField(default=False)
    agol = models.ForeignKey('AGOL', on_delete=models.CASCADE, related_name='roles')

    def __str__(self):
        return self.name


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
                                         'num': '100', 'start': next_record, 'sortField': 'created', 'sortOrder': 'asc'})
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
        if r.status_code == requests.status_codes.ok:
            response_json = r.json(strict=False)
            AGOLGroup.objects.update_or_create(id=response_json.get('id'), defaults={
                "title": response_json['title'],
                "agol": self
            })

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
                "role": account_request.role.id,
                "userLicenseType": account_request.user_type,
                "fullname": f"{account_request.first_name} {account_request.last_name}",
                "userType": "creatorUT",
                "groups": ",".join(str(x) for x in set(list(account_request.groups.all().values_list('id', flat=True)) + [account_request.auth_group.id])),
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
            success = []
            for account in AccountRequests.objects.filter(pk__in=[x.pk for x in account_requests])\
                .exclude(username__in=response_json['notInvited']):
                success.append(account.pk)
                user_url = f'{self.portal_url}/sharing/rest/community/users/{account.username}'
                user_response = requests.get(user_url, params={'token': token, 'f': 'json'})
                user_response_json = user_response.json()
                if 'error' in user_response_json:
                    return False, None, None
                else:
                    account.agol_id = user_response_json['id']
                    account.save(update_fields=['agol_id'])
            return success
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

    phone_number = models.CharField(max_length=20, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agol_info')
    delegates = models.ManyToManyField(User, related_name='delegate_for', blank=True)

    def clean(self):
        super().clean()
        if self.sponsor and not self.user.email:
            raise ValidationError('Email can not be blank if user is a sponsor.')


class ResponseProject(models.Model):
    users = models.ManyToManyField(User, related_name='response', verbose_name='Sponsors',
                                   limit_choices_to={'agol_info__sponsor': True})
    name = models.CharField('Name', max_length=500)
    assignable_groups = models.ManyToManyField('AGOLGroup', related_name='response',
                                               verbose_name='GeoPlatform Assignable Groups')
    role = models.ForeignKey('AGOLRole', on_delete=models.PROTECT, verbose_name='GeoPlatform Role',
                             limit_choices_to={'is_available': True})
    authoritative_group = models.ForeignKey('AGOLGroup', on_delete=models.PROTECT,
                                            verbose_name='Geoplatform Authoritative Group',
                                            limit_choices_to={'is_auth_group': True})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Responses/Projects'
        verbose_name = 'Response/Project'

    #     max_length=200,
    #     choices=[
    #         ('', 'Unknown'),
    #         ('R01', 'Region 1 - New England'),
    #         ('R02', 'Region 2 - NJ, NY, Puerto Rico, US Virgin Islands'),
    #         ('R03', 'Region 3 - Mid Atlantic'),
    #         ('R04', 'Region 4 - Southeast'),
    #         ('R05', 'Region 5 - Great Lakes'),
    #         ('R06', 'Region 6 - Central South'),
    #         ('R07', 'Region 7 - IA, KS, MO, NE'),
    #         ('R08', 'Region 8 - CO, MT, ND, SD, UT, WY'),
    #         ('R09', 'Region 9 - Pacific Southwest'),
    #         ('R10', 'Region 10 - Pacific Northwest'),
    #         ('OARM', 'EPA Office of Administration and Resources Management'),
    #         ('OAR', 'EPA Office of Air and Radiation'),
    #         ('OSCPP', 'EPA Office of Chemical Safety and Pollution Prevention'),
    #         ('OECA', 'EPA Office of Enforcement and Compliance Assurance'),
    #         ('OEI', 'EPA Office of Environmental Information'),
    #         ('OGC', 'EPA Office of General Counsel'),
    #         ('OIG', 'EPA Office of Inspector General'),
    #         ('OITA', 'EPA Office of International and Tribal Affairs'),
    #         ('OLEM', 'EPA Office of Land and Emergency Management'),
    #         ('ORD', 'EPA Office of Research and Development'),
    #         ('OW', 'EPA Office of Water'),
    #         ('OA', 'EPA Office of the Administrator'),
    #         ('OCFO', 'EPA Office of the Chief Financial Officer'),
    #         ('ER', 'OLEM - ER Program Support')
    #     ],
    #     default='',
    # )


