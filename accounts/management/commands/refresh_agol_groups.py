from django.core.management.base import BaseCommand, no_translations
from accounts.models import AGOL
import logging
logger = logging.getLogger('django')

class Command(BaseCommand):
    help = 'Update groups and roles from all portals/agols'

    def handle(self, *args, **options):
        #agol = AGOL.objects.get(portal_url='https://epa.maps.arcgis.com')
        for agol in AGOL.objects.all():
            try:
                agol.get_all_groups()
                agol.get_all_existing_user_group_memberships()
                agol.get_all_roles()

            except Exception as e:
                logger.error(f'Error updating groups and roles for {agol.portal_name}: {e}')
                continue
            # todo: determine what happens if a group is removed but our tool has someone linked to it
