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

    def setUp(self):
        self.agol = AGOL.objects.get(pk=1)
        self.agol.get_token = MagicMock(return_value='token')

    def test_username_formatting(self):
        data = {'email': 'myname@epa.gov', 'first_name': 'Joe', 'last_name': 'Smo'}
        username = format_username(data)
        self.assertEqual(username, 'Smo.Joe_EPA')

        data['email'] = 'joesmo@compancy.org'
        username = format_username(data)
        self.assertEqual(username, 'Smo.Joe_EPAEXT')

    @patch('accounts.models.requests.post', side_effect=mock_check_username)
    def test_check_username(self, mock_post):
        results, idk, idk2 = self.agol.check_username('Smo.doesntmatter')

        self.assertTrue(results)

    @patch('accounts.models.requests.post', side_effect=mock_existing_check_username)
    @patch('accounts.models.requests.get', side_effect=mock_get_user)
    def test_check_existing_username(self, mock_post, mock_get):
        results, idk, idk2 = self.agol.check_username('doesntmatter')
        self.assertFalse(results)

    @patch('accounts.models.requests.post', side_effect=mock_check_username_empty)
    @patch('accounts.models.requests.get', side_effect=mock_get_user)
    def test_check_existing_username_empty(self, mock_post, mock_get):
        results, idk, idk2 = self.agol.check_username('doesntmatter')
        self.assertTrue(results)

    @patch('accounts.models.requests.post', side_effect=mock_fail_create_user)
    @patch('accounts.models.requests.get', side_effect=mock_get_user)
    def test_account_rejection(self, mock_post, mock_get):
        requests = AccountRequests.objects.all()
        result = self.agol.create_users_accounts(requests, 'password')
        self.assertEqual(result, [])
        exists = AccountRequests.objects.filter(agol_id='ffffffff-ffff-ffff-ffff-ffffffffffff').exists()
        self.assertFalse(exists)


    @patch('accounts.models.requests.post', side_effect=mock_create_user)
    @patch('accounts.models.requests.get', side_effect=mock_get_user)
    def test_create_account(self, mock_post, mock_get):
        requests = AccountRequests.objects.all()
        result = self.agol.create_users_accounts(requests, 'password')
        self.assertEqual(len(result), len(requests))
        exists = AccountRequests.objects.filter(agol_id='ffffffff-ffff-ffff-ffff-ffffffffffff').exists()
        self.assertTrue(exists)



    # todo: fix to test groups from add_to_group
    @patch('accounts.models.requests.post')
    def test_add_to_group(self, mock_post):
        mock_post.return_value = MagicMock()
        mock_post.return_value.json.return_value = {}
        mock_post.return_value.status_code = 200

        request = AccountRequests.objects.first()
        request.agol_id = 'someid'
        success = self.agol.add_to_group([request.agol_id], ['agroup'])
        self.assertTrue(success)
        mock_post.assert_called_with(
            "https://epa.maps.arcgis.com/sharing/rest/community/groups/agroup/addUsers",
            data={'users': 'someid', 'f': 'json', 'token': 'token'}
        )

        # verify non-200 code returns false
        mock_post.return_value.status_code = 400
        success = self.agol.add_to_group([request.agol_id], ['agroup'])
        self.assertFalse(success)

