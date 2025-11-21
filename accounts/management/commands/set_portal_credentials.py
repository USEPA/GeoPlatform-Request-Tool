import json
from base64 import urlsafe_b64encode
from getpass import getpass
from keyring import set_password
from django.core.management import BaseCommand
from django.conf import settings

from accounts.models import AGOL, get_credential_cypher
from cryptography.fernet import Fernet
from dotenv import load_dotenv, set_key

class Command(BaseCommand):
    help = "Set ArcGIS Online credentials for a user."

    def handle(self, *args, **options):
        print("Select a portal:")
        portals = list(AGOL.objects.all())
        for i, p in enumerate(portals, 1):
            print(f"{i}. {p.get_portal_name_display()}")
        choice = input("Enter the number of your choice: ")
        selected_portal = portals[int(choice) - 1]
        print("Input username and password:")
        username = input("Username: ")
        password = getpass("Password: ")

        # Encrypt credentials
        cypher = get_credential_cypher()
        encrypted_password = cypher.encrypt(json.dumps({
            "username": username,
            "password": password
        }).encode())

        env_path = '.env'
        load_dotenv(dotenv_path=env_path)
        set_key(env_path, f"{selected_portal.portal_name.upper()}_PORTAL_CREDENTIALS",  encrypted_password.decode())
        print(f"Credentials for {selected_portal.get_portal_name_display()} set successfully.")

        if not selected_portal.org_id:
            selected_portal.org_id = selected_portal.get_org_id()
            selected_portal.save()
        if selected_portal.groups.count() == 0:
            selected_portal.get_all_groups()
            selected_portal.get_all_existing_user_group_memberships()
        if selected_portal.roles.count() == 0:
            selected_portal.get_all_roles()
