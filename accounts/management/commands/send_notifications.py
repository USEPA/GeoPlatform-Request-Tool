from django.core.management.base import BaseCommand, no_translations
from accounts.models import Notification


class Command(BaseCommand):
    help = 'Send unsent notifications'

    def handle(self, *args, **options):
        for notification in Notification.objects.filter(sent__isnull=True):
            notification.send()
