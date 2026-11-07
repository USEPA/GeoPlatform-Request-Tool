"""Adding a user through the admin as a non-superuser (GH #196)."""

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import AGOL, AGOLUserFields


class AdminAddUserPortalTest(TestCase):
    """A request tool administrator who is not a superuser adds a user.

    ``portal`` is made read-only for them by
    ``AGOLUserFieldsInline.get_readonly_fields``. Django does not render a
    read-only field as an input and does not read one back off the POST, so
    nothing set ``portal`` on the new row and the not-null column rejected the
    insert with an IntegrityError.
    """

    def setUp(self):
        self.portal = AGOL.objects.create(portal_name="geosecure", portal_url="https://example.test")
        self.other_portal = AGOL.objects.create(portal_name="other", portal_url="https://other.test")

        self.admin = User.objects.create_user(
            username="portal-admin", password="pw", is_staff=True, is_superuser=False
        )
        AGOLUserFields.objects.create(user=self.admin, portal=self.portal)
        # Staff need the add/change permissions the real administrators hold.
        from django.contrib.auth.models import Permission

        self.admin.user_permissions.add(
            *Permission.objects.filter(
                content_type__app_label__in=("auth", "accounts"),
                codename__in=(
                    "add_user", "change_user", "view_user",
                    "add_agoluserfields", "change_agoluserfields", "view_agoluserfields",
                ),
            )
        )

        self.client = Client()
        self.client.force_login(self.admin)

    def _add_user_post(self, username):
        return {
            "username": username,
            "password1": "sufficiently-long-pw-1",
            "password2": "sufficiently-long-pw-1",
            "agol_info-TOTAL_FORMS": "1",
            "agol_info-INITIAL_FORMS": "0",
            "agol_info-MIN_NUM_FORMS": "0",
            "agol_info-MAX_NUM_FORMS": "1",
            "agol_info-0-agol_username": "new.user",
            "agol_info-0-sponsor": "",
        }

    def test_non_superuser_can_add_a_user(self):
        url = reverse("admin:auth_user_add")
        response = self.client.post(url, self._add_user_post("new.user"), follow=False)

        # A successful admin add redirects; a re-rendered form means it failed.
        self.assertIn(response.status_code, (301, 302), msg=getattr(response, "content", b"")[:400])
        self.assertTrue(User.objects.filter(username="new.user").exists())

    def test_added_user_gets_the_administrators_portal(self):
        url = reverse("admin:auth_user_add")
        self.client.post(url, self._add_user_post("new.user2"), follow=False)

        created = User.objects.get(username="new.user2")
        self.assertEqual(created.agol_info.portal, self.portal)
        self.assertNotEqual(created.agol_info.portal, self.other_portal)


class AdminAddUserPortalSuperuserTest(TestCase):
    """A superuser still chooses the portal explicitly, as before."""

    def setUp(self):
        self.portal = AGOL.objects.create(portal_name="geosecure", portal_url="https://example.test")
        self.other_portal = AGOL.objects.create(portal_name="other", portal_url="https://other.test")
        self.superuser = User.objects.create_superuser(
            username="root", password="pw", email="root@example.test"
        )
        self.client = Client()
        self.client.force_login(self.superuser)

    def test_superuser_choice_is_honoured(self):
        url = reverse("admin:auth_user_add")
        self.client.post(
            url,
            {
                "username": "picked.user",
                "password1": "sufficiently-long-pw-1",
                "password2": "sufficiently-long-pw-1",
                "agol_info-TOTAL_FORMS": "1",
                "agol_info-INITIAL_FORMS": "0",
                "agol_info-MIN_NUM_FORMS": "0",
                "agol_info-MAX_NUM_FORMS": "1",
                "agol_info-0-agol_username": "picked.user",
                "agol_info-0-portal": str(self.other_portal.pk),
                "agol_info-0-sponsor": "",
            },
            follow=False,
        )

        created = User.objects.get(username="picked.user")
        self.assertEqual(created.agol_info.portal, self.other_portal)
