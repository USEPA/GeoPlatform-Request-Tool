from django.core.management.base import BaseCommand, no_translations
from accounts.models import AccountRequests
from django.db.models import Count
from django.core.mail import send_mail


class Command(BaseCommand):
    help = 'Notify sponsors of new account requests'

    def handle(self, *args, **options):
        pending_notifications = AccountRequests.objects.filter(sponsor_notified=False).values('sponsor__email').annotate(
            total=Count('sponsor__email'))

        for notification in pending_notifications:
            results = send_mail(
                'Pending GeoPlatform Account Requests',
                f'You have {notification["total"]} pending account requests. '
                f'Please go to https://r9.ercloud.org/request/accounts/list to review',
                'GIS_Team@epa.gov',
                [notification['sponsor__email']],
                fail_silently=False,
                html_message=f'You have {notification["total"]} pending account requests. Please go to '
                f'<a href="https://r9.ercloud.org/request/accounts/list">https://r9.ercloud.org/request/accounts/list</a> to review',
            )
            if results == 1:
                AccountRequests.objects.filter(
                    sponsor_notified=False,
                    sponsor__email=notification['sponsor__email']
                ).update(sponsor_notified=True)
