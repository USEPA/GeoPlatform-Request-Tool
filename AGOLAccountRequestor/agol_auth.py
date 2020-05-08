from social_core.backends.oauth import BaseOAuth2
from django.contrib.auth.models import User
from social_core.exceptions import AuthException


class AGOLOAuth2(BaseOAuth2):
    name = 'agol'
    ID_KEY = 'username'
    AUTHORIZATION_URL = 'https://epa.maps.arcgis.com/sharing/rest/oauth2/authorize'
    ACCESS_TOKEN_URL = 'https://epa.maps.arcgis.com/sharing/rest/oauth2/token'
    REQUIRES_EMAIL_VALIDATION = False
    ACCESS_TOKEN_METHOD = 'POST'
    EXTRA_DATA = [
        ('refresh_token', 'refresh_token'),
        ('expires_in', 'expires'),
        ('username', 'username')
    ]

    def get_user_details(self, response):
        if 'error' in response:
            return {}

        return {
            'username': response['username'],
            'email': response['email'],
            'fullname': response['fullName'],
            'first_name': response['fullName'].split()[0],
            'last_name': response['fullName'].split()[1]
        }

    def user_data(self, access_token, *args, **kwargs):
        return self.get_json(
            'https://epa.maps.arcgis.com/sharing/rest/community/self',
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
