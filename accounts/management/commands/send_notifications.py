from django.core.management.base import BaseCommand, no_translations
from accounts.models import Notification


class Command(BaseCommand):
    help = 'Send unsent notifications'

    def add_arguments(self, parser):
        parser.add_argument('--error-test', action='store_true')

    def handle(self, *args, **options):
        if options.get('error_test', False):
            raise Exception('this should log')

        for notification in Notification.objects.filter(sent__isnull=True):
            notification.send()
