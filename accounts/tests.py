from django.test import RequestFactory, TestCase
from unittest.mock import patch, MagicMock
from django.shortcuts import get_list_or_404
from django.contrib.auth.models import User
from django.utils.timezone import now

import json

from .models import AGOL, AGOLUserFields, AccountRequests
from .views import format_username, SponsorsViewSet
from .permissions import IsSponsor


def mock_check_username_empty(*args, **kwargs):
    class MockResponse:
        def json(self):
            return {
                'usernames': [],
            }

    return MockResponse()


def mock_check_username(*args, **kwargs):
    class MockResponse:
        def json(self):
            return {
                'usernames': [
                    {'requested': 'same', 'suggested': 'same'}
                ],
            }

    return MockResponse()


def mock_existing_check_username(*args, **kwargs):
    class MockResponse:
        def json(self):
            return {
                'usernames': [
                    {'requested': 'name', 'suggested': 'nope'}
                ],
            }

    return MockResponse()


def mock_get_user(*args, **kwargs):
    class MockResponse:
        def json(self):
            return {
                'id': 'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'groups': []
            }

    return MockResponse()


def mock_create_user(*args, **kwargs):
    class MockRequest:
        body = 'nothing'

    class MockResponse:
        text = '''{"success": ["name.a@epa.gov"], "notInvited": []}'''
        request = MockRequest()

        def json(self):
            return json.loads(self.text)

    return MockResponse()


def mock_fail_create_user(*args, **kwargs):
    class MockRequest:
        body = 'nothing'

    class MockResponse:
        text = '''{"success": [], "notInvited": ["name.a@epa.gov"]}'''
        request = MockRequest()

        def json(self):
            return json.loads(self.text)

    return MockResponse()


def mock_add_to_group(*args, **kwargs):
    class MockRequest:
        body = 'nothing'

    class MockResponse:
        status_code = 200

        def json(self):
            return {
                "notAdded": [""]
            }
    return MockResponse()


class TestAccounts(TestCase):
    fixtures = ['fixtures.json']

    def setUp(self):
        self.factory = RequestFactory()
        agol_user = AGOLUserFields.objects.first()
        self.user = agol_user.user
        self.account_requests = None
        self.is_sponsor = IsSponsor()

    def test_username_formatting(self):
        data = {'email': 'myname@epa.gov', 'first_name': 'Joe', 'last_name': 'Smo'}
        username = format_username(data)
        self.assertEqual(username, 'Smo.Joe_EPA')

        data['email'] = 'joesmo@compancy.org'
        username = format_username(data)
        self.assertEqual(username, 'Smo.Joe_EPAEXT')

    @patch('accounts.models.requests.post', side_effect=mock_check_username)
    def test_check_username(self, mock_post):
        agol = AGOL.objects.get(pk=1)
        agol.get_token = MagicMock(return_value='token')

        results, idk, idk2 = agol.check_username('Smo.doesntmatter')

        self.assertTrue(results)

    @patch('accounts.models.requests.post', side_effect=mock_existing_check_username)
    @patch('accounts.models.requests.get', side_effect=mock_get_user)
    def test_check_existing_username(self, mock_post, mock_get):
        agol = AGOL.objects.get(pk=1)
        agol.get_token = MagicMock(return_value='token')
        results, idk, idk2 = agol.check_username('doesntmatter')
        self.assertFalse(results)

    @patch('accounts.models.requests.post', side_effect=mock_check_username_empty)
    @patch('accounts.models.requests.get', side_effect=mock_get_user)
    def test_check_existing_username_empty(self, mock_post, mock_get):
        agol = AGOL.objects.get(pk=1)
        agol.get_token = MagicMock(return_value='token')
        results, idk, idk2 = agol.check_username('doesntmatter')
        self.assertTrue(results)

    @patch('accounts.models.requests.post', side_effect=mock_fail_create_user)
    @patch('accounts.models.requests.get', side_effect=mock_get_user)
    def test_account_rejection(self, mock_post, mock_get):
        agol = AGOL.objects.get(pk=1)
        agol.get_token = MagicMock(return_value='token')
        requests = AccountRequests.objects.all()
        result = agol.create_users_accounts(requests, 'password')
        self.assertFalse(result)
        exists = AccountRequests.objects.filter(agol_id='ffffffff-ffff-ffff-ffff-ffffffffffff').exists()
        self.assertFalse(exists)

    @patch('accounts.models.requests.post', side_effect=mock_create_user)
    @patch('accounts.models.requests.get', side_effect=mock_get_user)
    def test_create_account(self, mock_post, mock_get):
        agol = AGOL.objects.get(pk=1)
        agol.get_token = MagicMock(return_value='token')
        requests = AccountRequests.objects.all()
        result = agol.create_users_accounts(requests, 'password')
        self.assertTrue(result)
        exists = AccountRequests.objects.filter(agol_id='ffffffff-ffff-ffff-ffff-ffffffffffff').exists()
        self.assertTrue(exists)

    @patch('accounts.models.requests.post', side_effect=mock_create_user)
    @patch('accounts.models.requests.get', side_effect=mock_get_user)
    def test_create_accounts(self, mock_post, mock_get):
        agol = AGOL.objects.get(pk=1)
        agol.get_token = MagicMock(return_value='token')
        success = []

        account_requests = self.account_requests
        if account_requests is None:
            account_requests = get_list_or_404(AccountRequests)

        AccountRequests.objects.all().update(approved=now())
        create_accounts = [x for x in account_requests if x.agol_id is None]
        create_success = len(create_accounts) == 0
        if len(create_accounts) > 0:
            success += agol.create_users_accounts(account_requests, 'password')
            if len(success) == len(create_accounts):
                create_success = True
        else:
            create_success = True

        if not create_success:
            self.assertFalse("Error creating and updating accounts")
        else:
            self.assertTrue(True)
        return success

    def test_invitations(self):
        agol = AGOL.objects.get(pk=1)
        agol.get_token = MagicMock(return_value='token')
        requests = AccountRequests.objects.all()
        invitations = agol.generate_invitations(requests, 'password')
        self.assertTrue('000b6ee121bb4739a5021e0f0241ff01' in invitations[0]["groups"])
        self.assertTrue('00237b674c3347a18e0fb2bfcdb248e1' in invitations[0]["groups"])

    def test_user_has_account_request_permission(self, account_requests=None):
        request = self.factory.get('/account/approvals')
        request.user = self.user
        if account_requests is None:
            account_requests = get_list_or_404(AccountRequests)
        for ac in account_requests:
            self.is_sponsor.has_object_permission(request, SponsorsViewSet, ac)
        self.assertTrue(1)

    @patch('accounts.models.requests.post', side_effect=mock_add_to_group)
    def test_user_approvals(self, mock_post):
        agol = AGOL.objects.get(pk=1)
        agol.get_token = MagicMock(return_value='token')

        self.account_requests = get_list_or_404(AccountRequests)
        account_requests = self.account_requests
        success = []

        # verify user has permission on each request
        self.test_user_has_account_request_permission(account_requests)

        create_success = False
        created_accounts = self.test_create_accounts()
        if len(created_accounts) > 0:
            success.extend(created_accounts)
            create_success = True

        # add users to groups for either existing or newly created
        group_requests = [x for x in AccountRequests.objects.filter(agol_id__isnull=False)]
        group_success = len(group_requests) == 0
        for g in group_requests:
            if g.groups.count() > 0:
                group_success = agol.add_to_group([g.username], [str(x) for x in g.groups.values_list('id', flat=True)])
                if group_success:
                    success.append(g.pk)
            else:
                group_success = True

        AccountRequests.objects.filter(pk__in=success).update(created=now())
        if create_success and group_success:
            self.assertTrue(1)
        if not create_success:
            self.assertFalse("Error creating and updating accounts")
        if not group_success:
            self.assertFalse("Accounts created. Existing account NOT updated.")
