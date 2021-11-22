from django.test import RequestFactory, TestCase
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models import Q

import os
from urllib.parse import parse_qs
import json

from .models import AGOL, AGOLUserFields, AccountRequests
from .views import format_username, SponsorsViewSet, AccountViewSet
from .permissions import IsSponsor
from .func import *

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


def mock_create_user(url, data, headers, *args, **kwargs):
    json_data = parse_qs(data)
    email_address = [x['email'] for x in json.loads(json_data['invitationList'][0])['invitations']]
    response = {"success": email_address, "notInvited": []}

    class MockRequest:
        body = 'nothing'

    class MockResponse:
        text = ''
        request = MockRequest()

        def json(self):
            return response

    return MockResponse()


def mock_fail_create_user(url, data, headers, *args, **kwargs):
    json_data = parse_qs(data)
    email_address = [x['email'] for x in json.loads(json_data['invitationList'][0])['invitations']]
    response = {"success": [], "notInvited": email_address}

    class MockRequest:
        body = 'nothing'

    class MockResponse:
        request = MockRequest()

        def json(self):
            return response

    return MockResponse()


def mock_add_to_group(response, *args, **kwargs):
    class MockRequest:
        body = 'nothing'

    class MockResponse:
        status_code = 200

        def json(self):
            return response
    return MockResponse()


class TestAccounts(TestCase):
    fixtures = ['fixtures.json']

    def setUp(self):
        self.agol = AGOL.objects.get(pk=1)
        self.agol.get_token = MagicMock(return_value='token')
        self.factory = RequestFactory()

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

        # only test with non existing accounts
        requests = AccountRequests.objects.filter(agol_id=None)
        result = agol.create_users_accounts(requests, 'password')
        expected_output = [x.pk for x in requests]
        result.sort()
        self.assertEqual(result, expected_output)
        exists = AccountRequests.objects.filter(agol_id='ffffffff-ffff-ffff-ffff-ffffffffffff').exists()
        self.assertTrue(exists)
        exists = AccountRequests.objects.filter(agol_id='69ac034ef09e4abca2fe67fda9cf6bda').exists()
        self.assertTrue(exists)


    @patch('accounts.models.AGOL.create_users_accounts')
    def test_create_multiple_accounts_without_password(self, create_users_accounts):
        # get all requests
        requests = AccountRequests.objects.all()
        # mock create_users_accounts to return only account pks that don't have agol_id
        requested_pks = [x.pk for x in requests if x.agol_id is None]
        create_users_accounts.return_value = requested_pks
        results = create_accounts(requests)
        # sort results so we can compare
        results.sort()
        self.assertEqual([x.pk for x in requests], results)


    @patch('accounts.models.AGOL.add_to_group')
    def test_add_to_group_with_multiple_accounts_without_password(self, mock_add_to_group):
        # get all requests
        AccountRequests.objects.filter(agol_id__isnull=True).update(agol_id='ffffffffffffffffffffffffffffffff')
        requests = AccountRequests.objects.all()
        # mock create_users_accounts to return only account pks that don't have agol_id

        mock_add_to_group.return_value = False
        results = add_accounts_to_groups(requests)
        self.assertEqual([2], list(results))

        mock_add_to_group.return_value = True
        results = add_accounts_to_groups(requests)
        self.assertEqual([1, 2], list(results))


    @patch('requests.post')
    def test_add_to_group(self, mock_post):
        mock_response = MagicMock()

        mock_post.return_value = mock_response
        agol = AGOL.objects.first()
        agol.get_token = MagicMock(return_value='token')

        mock_response.json.return_value = {"error": None}
        result = agol.add_to_group('username', 'group')
        self.assertFalse(result)

        mock_response.json.return_value = {"notAdded": ['username']}
        result = agol.add_to_group('username', 'group')
        self.assertFalse(result)

        mock_response.json.return_value = {"notAdded": []}
        result = agol.add_to_group('username', 'group')
        self.assertTrue(result)




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

    def test_invitations(self):
        agol = AGOL.objects.get(pk=1)
        agol.get_token = MagicMock(return_value='token')
        requests = AccountRequests.objects.filter(agol_id=None)
        invitations = agol.generate_invitations(requests, 'password')
        self.assertTrue(requests[0].email in invitations[0]["email"])
        self.assertTrue(requests[0].first_name in invitations[0]["firstname"])
        self.assertTrue(requests[0].last_name in invitations[0]["lastname"])

    def test_user_has_account_request_permission(self):
        request = self.factory.get('/account/approvals')

        # does sponsor have permission
        sponsor = User.objects.get(pk=1)

        request.user = sponsor
        for ac in AccountRequests.objects.all():
            result = IsSponsor().has_object_permission(request, SponsorsViewSet, ac)
            self.assertTrue(result)

        # does unrelated user have permission
        unrelated_user = User.objects.get(pk=2)
        request.user = unrelated_user
        for ac in AccountRequests.objects.all():
            result = IsSponsor().has_object_permission(request, SponsorsViewSet, ac)
            self.assertFalse(result)

        # after making delegate does user have permission
        sponsor.agol_info.delegates.set([unrelated_user])
        for ac in AccountRequests.objects.all():
            result = IsSponsor().has_object_permission(request, SponsorsViewSet, ac)
            self.assertTrue(result)


