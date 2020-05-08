from django.core.management.base import BaseCommand, no_translations
from accounts.models import AGOL


class Command(BaseCommand):
    help = 'Notify sponsors of new account requests'

    def handle(self, *args, **options):
        agol = AGOL.objects.get(portal_url='https://epa.maps.arcgis.com')
        agol.get_all_groups()
        # todo: determine what happens if a group is removed but our tool has someone linked to it

