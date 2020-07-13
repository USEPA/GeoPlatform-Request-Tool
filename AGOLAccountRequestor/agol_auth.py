from social_core.backends.oauth import BaseOAuth2
from django.contrib.auth.models import User
from social_core.exceptions import AuthException


class AGOLOAuth2(BaseOAuth2):
    name = 'agol'
    ID_KEY = 'username'
    _AUTHORIZATION_URL = 'https://{}/sharing/rest/oauth2/authorize'
    _ACCESS_TOKEN_URL = 'https://{}/sharing/rest/oauth2/token'
    REQUIRES_EMAIL_VALIDATION = False
    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False
    EXTRA_DATA = [
        ('refresh_token', 'refresh_token'),
        ('expires_in', 'expires'),
        ('username', 'username'),
        ('email', 'email')
    ]

    def _base_url(self):
        _domain = self.setting('DOMAIN')
        domain = _domain if _domain else 'www.arcgis.com'
        return domain

    def authorization_url(self):
        return self._AUTHORIZATION_URL.format(self._base_url())

    def access_token_url(self):
        return self._ACCESS_TOKEN_URL.format(self._base_url())

    def get_user_details(self, response):
        if 'error' in response:
            return {}

        return {
            'username': response.get('username'),
            'email': response.get('email'),
            'fullname': response.get('fullName'),
            'first_name': response.get('firstName'),
            'last_name': response.get('lastName'),
            'agol_groups': [x.get('id') for x in response.get('groups')] # get list of group ids user is a member of
        }

    def user_data(self, access_token, *args, **kwargs):
        return self.get_json(
            'https://{}/sharing/rest/community/self'.format(self._base_url()),
            params={
                'token': access_token,
                'f': 'json'
            }
        )
    # # api does support state... need to remove this and test
    # def validate_state(self):
    #     return None
    #
    # # added so we can verify redirect_uri without having to actually redirect there
    # # a slight hack to allow us to redirect to frontend oauthcallback page
    # def get_redirect_uri(self, state=None):
    #     return self.setting('REDIRECT_URI')


def associate_by_username(backend, details, user=None, *args, **kwargs):
    """
    Associate current auth with a user with the same email address in the DB.

    This pipeline entry is not 100% secure unless you know that the providers
    enabled enforce email verification on their side, otherwise a user can
    attempt to take over another user account by using the same (not validated)
    email address on some provider.  This pipeline entry is disabled by
    default.
    """
    if user:
        return None

    username = details.get('username')
    if username:
        # Try to associate accounts registered with the same email address,
        # only if it's a single object. AuthException is raised if multiple
        # objects are returned.
        users = list(User.objects.filter(agol_info__agol_username=username))
        if len(users) == 0:
            return None
        elif len(users) > 1:
            raise AuthException(
                backend,
                'The given username is associated with another account'
            )
        else:
            return {'user': users[0],
                    'is_new': False}
