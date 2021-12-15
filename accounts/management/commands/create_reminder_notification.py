from django.core.management.base import BaseCommand, no_translations
from accounts.models import AccountRequests, AGOLUserFields, Notification
from django.db.models import Count
from django.conf import settings
from django.template.loader import render_to_string


class Command(BaseCommand):
    help = 'Notify sponsors of pending account requests on daily basis'

    def handle(self, *args, **options):
        pending_accounts = AGOLUserFields.objects.filter(sponsor=True, user__response__requests__approved__isnull=True)\
            .annotate(total_pending=Count('user__response__requests'))\
            .filter(total_pending__gt=0)

        for pending in pending_accounts:
            n = Notification.objects.create(
                subject='Pending GeoPlatform Account Requests',
                content=render_to_string("reminder_pending_account_request_email.html", {
                    "HOST_ADDRESS": settings.HOST_ADDRESS,
                    "count": pending.total_pending
                })
            )
            n.to.set(pending.get_email_recipients())
