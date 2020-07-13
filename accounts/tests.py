from django.test import TestCase
from unittest.mock import patch, MagicMock
from .models import AGOL, AccountRequests
from django.contrib.auth.models import User
from .views import format_username
import json


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


class TestAccounts(TestCase):
    fixtures = ['fixtures.json']

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

    def test_invitations(self):
        agol = AGOL.objects.get(pk=1)
        agol.get_token = MagicMock(return_value='token')
        requests = AccountRequests.objects.all()
        invitations = agol.generate_invitations(requests, 'password')
        self.assertTrue('000b6ee121bb4739a5021e0f0241ff01' in invitations[0]["groups"])
        self.assertTrue('00237b674c3347a18e0fb2bfcdb248e1' in invitations[0]["groups"])

