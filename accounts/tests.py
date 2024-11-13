from django.test import RequestFactory, TestCase
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.db.models import Q

import os
from urllib.parse import parse_qs
import json

from AGOLAccountRequestor.agol_auth import get_user_details
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


def mock_request_json(return_value):
    def _(*args, **kwargs):
        class MockResponse:
            def json(self):
                return return_value

        return MockResponse()

    return _


def mock_get_user(*args, **kwargs):
    class MockResponse:
        def json(self):
            return {
                'id': 'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'groups': []
            }

    return MockResponse()


def mock_create_user(url, data, headers, *args, **kwargs):
    if url.endswith('portaladmin/security/users/createUser'):
        response = {"status": "success"}
    else:
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


def mock_precreate_user(url, data, headers, *args, **kwargs):
    response = {"status": "success"}

    class MockRequest:
        body = 'nothing'

    class MockResponse:
        text = ''
        request = MockRequest()

        def json(self):
            return response

    return MockResponse()


def mock_fail_create_user(url, data, headers, *args, **kwargs):
    if url.endswith('portaladmin/security/users/createUser'):
        response = {"status": "failed"}
    else:
        json_data = parse_qs(data)
        email_address = [x['email'] for x in json.loads(json_data['invitationList'][0])['invitations']]
        response = {"account_request": None, "notInvited": email_address}

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
        results = self.agol.check_username('Smo.doesntmatter')
        self.assertTrue(results[0])

    @patch('accounts.models.requests.post', side_effect=mock_existing_check_username)
    @patch('accounts.models.requests.get', side_effect=mock_get_user)
    def test_check_existing_username(self, mock_post, mock_get):
        results = self.agol.check_username('doesntmatter')
        self.assertFalse(results[0])

    @patch('accounts.models.requests.post', side_effect=mock_check_username_empty)
    @patch('accounts.models.requests.get', side_effect=mock_get_user)
    def test_check_existing_username_empty(self, mock_post, mock_get):
        results = self.agol.check_username('doesntmatter')
        self.assertTrue(results[0])

    @patch('requests.post')
    def test_check_username_failure(self, mock_post):
        mock_post.side_effect = mock_request_json({'error': {'details': 'nothing'}})
        results = self.agol.check_username('doesntmatter')
        self.assertFalse(results[0])
        mock_post.side_effect = mock_request_json({})
        results = self.agol.check_username('doesntmatter')
        self.assertFalse(results[0])

    @patch('accounts.models.requests.post', side_effect=mock_fail_create_user)
    @patch('accounts.models.requests.get', side_effect=mock_get_user)
    def test_account_rejection(self, mock_post, mock_get):
        requests = AccountRequests.objects.all()
        for account in requests:
            if not account.is_enterprise_account() and not account.response.portal.allow_external_accounts:
                try:
                    self.agol.create_user_account(account, 'password')
                except Exception as e:
                    self.assertEqual(str(e),
                                     'Portal does not allow external accounts and request email does not have a preapproved domain')
            else:
                result = self.agol.create_user_account(account, 'password')
                self.assertFalse(result)
                exists = AccountRequests.objects.filter(agol_id='ffffffff-ffff-ffff-ffff-ffffffffffff').exists()
                self.assertFalse(exists)

    @patch('accounts.models.requests.post', side_effect=mock_create_user)
    @patch('accounts.models.requests.get', side_effect=mock_get_user)
    def test_create_account_with_passwords(self, mock_post, mock_get):
        # only test with non existing accounts, there should be account requests which already created
        requests = AccountRequests.objects.filter(agol_id=None)
        for account in requests:
            if not account.is_enterprise_account() and account.response.portal.allow_external_accounts:
                self.assertTrue(self.agol.create_user_account(account, 'password'))
        # Any non-existing account requests should have been created with all fs GUID
        self.assertTrue(AccountRequests.objects.filter(agol_id='ffffffff-ffff-ffff-ffff-ffffffffffff').exists())

        # This is our already approved account GUID, which should have already been created
        self.assertTrue(AccountRequests.objects.filter(agol_id='ed5b2bae-7e53-4efe-a8fa-15e5dc230d79').exists())

    @patch('accounts.models.requests.post', side_effect=mock_precreate_user)
    @patch('accounts.models.requests.get', side_effect=mock_get_user)
    def test_create_enterprise_accounts(self, mock_post, mock_get):
        # only test with non existing accounts, there should be account requests which already created
        requests = AccountRequests.objects.filter(agol_id=None)
        for account in requests:
            if account.is_enterprise_account():
                try:
                    self.agol.create_user_account(account, 'password')
                except Exception as e:
                    self.assertEqual(str(e),
                                     'Portal does not allow external accounts and request email does not have a preapproved domain')

        # Any non-existing account requests should have been created with all fs GUID
        self.assertTrue(AccountRequests.objects.filter(agol_id='ffffffff-ffff-ffff-ffff-ffffffffffff').exists())

        # This is our already approved account GUID, which should have already been created
        self.assertTrue(AccountRequests.objects.filter(agol_id='ed5b2bae-7e53-4efe-a8fa-15e5dc230d79').exists())

    @patch('accounts.models.requests.post', side_effect=mock_create_user)
    @patch('accounts.models.requests.get', side_effect=mock_get_user)
    def test_create_account_without_passwords(self, mock_post, mock_get):
        # only test with non existing accounts, there should be account requests which already created
        requests = AccountRequests.objects.filter(agol_id=None)
        for account in requests:
            if account.is_enterprise_account() or (
                    not account.is_enterprise_account() and account.response.portal.allow_external_accounts):
                self.assertTrue(self.agol.create_user_account(account))

        # Any non-existing account requests should have been created with all fs GUID
        self.assertTrue(AccountRequests.objects.filter(agol_id='ffffffff-ffff-ffff-ffff-ffffffffffff').exists())

        # This is our already approved account GUID, which should have already been created
        self.assertTrue(AccountRequests.objects.filter(agol_id='ed5b2bae-7e53-4efe-a8fa-15e5dc230d79').exists())

    @patch('accounts.models.AGOL.add_to_group')
    def test_add_to_group_with_multiple_accounts_without_password(self, mock_add_to_group):
        # get all requests
        AccountRequests.objects.filter(agol_id__isnull=True).update(agol_id='ffffffffffffffffffffffffffffffff')
        requests = AccountRequests.objects.all()

        # there are 4 group requests in fixtures
        # in this test, all add_to_group requests should fail, results should empty
        mock_add_to_group.return_value = False
        results = []
        for account in requests:
            results += add_account_to_groups(account)
        self.assertTrue(len(results) == 0)

        # in this test, 4 groups should be added as defined in fixtures
        # results should be empty to start and finish with 4 GUIDs (len =4)
        mock_add_to_group.return_value = True
        for account in requests:
            results += add_account_to_groups(account)
        self.assertTrue(len(results) == 4)

    @patch('requests.post')
    def test_add_to_group(self, mock_post):
        mock_response = MagicMock()
        mock_post.return_value = mock_response

        for agol in AGOL.objects.all():
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

    def test_invitations(self):
        for agol in AGOL.objects.all():
            agol.get_token = MagicMock(return_value='token')
            requests = AccountRequests.objects.filter(agol_id=None)
            invitation = agol.generate_user_request_data(requests[0], 'password')
            self.assertTrue(requests[0].email in invitation["email"])
            self.assertTrue(requests[0].first_name in invitation["firstname"])
            self.assertTrue(requests[0].last_name in invitation["lastname"])

    def test_user_has_account_request_permission(self):
        for agol in AGOL.objects.all():
            request = self.factory.get('/account/approvals')

            # does sponsor have permission
            sponsor = User.objects.get(agol_info__portal_id=agol.id, last_name="sponsor")

            request.user = sponsor
            for ac in AccountRequests.objects.filter(agol_id=agol.id):
                result = IsSponsor().has_object_permission(request, SponsorsViewSet, ac)
                self.assertTrue(result)

            # does unrelated user have permission
            unrelated_user = User.objects.get(agol_info__portal_id=agol.id, last_name="delegate")
            request.user = unrelated_user
            for ac in AccountRequests.objects.filter(agol_id=agol.id):
                result = IsSponsor().has_object_permission(request, SponsorsViewSet, ac)
                self.assertFalse(result)

            # after making delegate does user have permission
            sponsor.agol_info.delegates.set([unrelated_user])
            for ac in AccountRequests.objects.filter(agol_id=agol.id):
                result = IsSponsor().has_object_permission(request, SponsorsViewSet, ac)
                self.assertTrue(result)

    def test_allow_response_with_unrelated_auth_group(self):
        # at time of writing test most records in the fixture will fail this test
        # thats fine since clean doesn't generally get called outside of form validation
        responseproject = ResponseProject.objects.get(id=1001)
        # this should not error and allow test to pass
        responseproject.clean()

        responseproject = ResponseProject.objects.get(id=1002)
        try:
            responseproject.clean()
            self.fail('Should not get here')
        except ValidationError as e:
            self.assertTrue('authoritative_group' in e.args[0])

    def test_email_associated_with_existing_account(self):
        a = AccountRequests()

        a.username = 'test'
        a.possible_existing_account = ''
        r = email_associated_with_existing_account(a)
        self.assertFalse(r)

        a.possible_existing_account = 'test,test12'
        r = email_associated_with_existing_account(a)
        self.assertTrue(r)

    @patch('accounts.func.email_associated_with_existing_account')
    def test_verify_account_can_be_approved(self, mock_email_association):
        mock_email_association.return_value = False
        a = AccountRequests(is_existing_account=True)
        # this one should fail
        try:
            verify_account_can_be_approved(a)
        except PermissionDenied:
            self.assertTrue(True)

        # this should not throw exception
        mock_email_association.return_value = True
        try:
            verify_account_can_be_approved(a)
        except:
            self.assertTrue(False)

        # this should not throw exception
        a.is_existing_account = False
        try:
            verify_account_can_be_approved(a)
        except:
            self.assertTrue(False)


    @patch('accounts.models.AGOL.create_user_account')
    def test_create_account_from_request(self, mock_create_user_account):
        mock_create_user_account.return_value = False
        a = AccountRequests.objects.get(id=103)
        self.assertFalse(a.create_account())

        mock_create_user_account.return_value = True
        self.assertTrue(a.create_account())
        self.assertTrue(a.created is not None)

    @patch('accounts.models.AGOL.enable_user_account')
    def test_enable_account(self, mock_enable_user_account):
        a = AccountRequests(existing_account_enabled=True)
        self.assertTrue(enable_account(a, None))

        mock_enable_user_account.return_value = True
        a = AccountRequests.objects.get(id=101)
        self.assertFalse(a.existing_account_enabled)
        self.assertTrue(enable_account(a, None))
        self.assertTrue(a.existing_account_enabled)


    @patch('accounts.models.AGOL.create_user_account')
    def test_create_account_from_request(self, mock_create_user_account):
        mock_create_user_account.return_value = False
        a = AccountRequests.objects.get(id=103)
        self.assertFalse(a.create_account())

        mock_create_user_account.return_value = True
        self.assertTrue(a.create_account())
        self.assertTrue(a.created is not None)

    @patch('accounts.func.add_account_to_groups')
    @patch('accounts.func.enable_account')
    @patch('accounts.models.AGOL.create_user_account')
    def test_account_approval(self, mock_create_user_account, mock_enable_account, mock_add_to_groups):
        a = AccountRequests.objects.get(id=101)
        mock_create_user_account.return_value = True
        mock_add_to_groups.return_value = False
        r = approve_account(a, None, User(id=1))
        self.assertTrue('groups not added at' in r.data['warning'])


        a = AccountRequests.objects.get(id=102)
        self.assertTrue(a.approved is None and a.approved_by is None and a.existing_account_enabled)

        mock_create_user_account.return_value = False

        r = approve_account(a, None, User(id=1))
        self.assertEqual(r.data['id'], 102)
        print(r.data['error'])
        self.assertTrue("Error creating" in r.data['error'])

        mock_create_user_account.return_value = True
        mock_enable_account.return_value = False

        r = approve_account(a, None, User(id=1))
        self.assertTrue('Error enabling' in r.data['error'])

        mock_enable_account.return_value = True
        r = approve_account(a, None, User(id=1))
        self.assertTrue('Successfully' in r.data['success'])




class TestGetUserDetails(TestCase):

    def test_user_details_with_full_name(self):
        response = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'fullName': 'Test User',
            'groups': [{'id': 'group1'}, {'id': 'group2'}]
        }
        expected = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'agol_groups': ['group1', 'group2']
        }
        self.assertEqual(get_user_details(response), expected)

    def test_user_details_with_first_and_last_name(self):
        response = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'firstName': 'Test',
            'lastName': 'User',
            'groups': [{'id': 'group1'}, {'id': 'group2'}]
        }
        expected = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'agol_groups': ['group1', 'group2']
        }
        self.assertEqual(get_user_details(response), expected)

    def test_user_details_with_error(self):
        response = {'error': 'Some error'}
        expected = {}
        self.assertEqual(get_user_details(response), expected)

    def test_user_details_with_empty_response(self):
        response = {}
        expected = {
            'username': None,
            'email': None,
            'first_name': '',
            'last_name': '',
            'agol_groups': []
        }
        self.assertEqual(get_user_details(response), expected)

    def test_user_details_with_partial_name(self):
        response = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'fullName': 'Test',
            'groups': [{'id': 'group1'}, {'id': 'group2'}]
        }
        expected = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': '',
            'agol_groups': ['group1', 'group2']
        }
        self.assertEqual(get_user_details(response), expected)

    def test_user_details_with_comma(self):
        response = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'fullName': ' User,  Test ',
            'groups': [{'id': 'group1'}, {'id': 'group2'}]
        }
        expected = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'agol_groups': ['group1', 'group2']
        }
        self.assertEqual(get_user_details(response), expected)

    def test_user_details_with_space_in_last(self):
        response = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'fullName': 'User Fake,  Test ',
            'groups': [{'id': 'group1'}, {'id': 'group2'}]
        }
        expected = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User Fake',
            'agol_groups': ['group1', 'group2']
        }
        self.assertEqual(get_user_details(response), expected)
