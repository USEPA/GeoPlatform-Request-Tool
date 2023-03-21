from django.core.management.base import BaseCommand, no_translations
from accounts.models import AccountRequests, AGOLUserFields
from django.db.models import Count
from django.core.mail import send_mail


class Command(BaseCommand):
    help = 'Notify sponsors of new account requests'

    def handle(self, *args, **options):
        pending_notifications = AccountRequests.objects.filter(sponsor_notified=False).values('sponsor__email').annotate(
            total=Count('sponsor__email'))

        for notification in pending_notifications:
            to_emails = list(AGOLUserFields.objects.values_list('delegates__email', flat=True))
            to_emails.append(notification['sponsor__email'])
            results = send_mail(
                'Pending Account Requests',
                f'{notification["total"]} Account Request(s) is pending your approval in the Account Request Tool.'
                f'Please log in to the <a href="https://r9data.response.epa.gov/request/accounts/list">Account Request Tool Approval List</a> to configure new accounts and notify the users when configuration is complete.',
                'GIS_Team@epa.gov',
                list(set(to_emails)),
                fail_silently=False,
                html_message=f'{notification["total"]} Account Request(s) is pending your approval in the Account Request Tool.'
                f'Please log in to the <a href="https://r9data.response.epa.gov/request/accounts/list">Account Request Tool Approval List</a> to configure new accounts and notify the users when configuration is complete.',
            )
            if results == 1:
                AccountRequests.objects.filter(
                    sponsor_notified=False,
                    sponsor__email=notification['sponsor__email']
                ).update(sponsor_notified=True)
