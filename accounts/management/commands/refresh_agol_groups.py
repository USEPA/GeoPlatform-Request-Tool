from django.core.management.base import BaseCommand, no_translations
from accounts.models import AGOL


class Command(BaseCommand):
    help = 'Update groups and roles from all portals/agols'

    def handle(self, *args, **options):
        #agol = AGOL.objects.get(portal_url='https://epa.maps.arcgis.com')
        for agol in AGOL.objects.all():
            agol.get_all_groups()
            agol.get_all_existing_user_group_memberships()
            agol.get_all_roles()
            # todo: determine what happens if a group is removed but our tool has someone linked to it
