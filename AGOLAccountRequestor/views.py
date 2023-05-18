import logging
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie

logger = logging.getLogger('AGOLAccountRequestor')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
def current_user(request):
    permissions = []
    for permission in request.user.user_permissions.all():
        permissions.append(permission.codename)
    for groups in request.user.groups.all():
        for permission in groups.permissions.all():
            permissions.append(permission.codename)
    delegate_for = request.user.delegate_for.values_list('id', flat=True)
    current_user = {
        'id': request.user.id,
        'portal': request.user.agol_info.portal.get_portal_name_display(),
        'name': '{} {}'.format(request.user.first_name, request.user.last_name) if request.user.first_name else request.user.username,
        'permissions': set(permissions),
        'is_superuser': request.user.is_superuser,
        'is_staff': request.user.is_staff,
        'is_sponsor': request.user.agol_info.sponsor,
        'is_delegate': True if len(delegate_for) > 0 else False,
        'delegate_for': delegate_for,
    }
    return Response(current_user)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def email_field_coordinator_request(request):
    try:
        gpo_request_email_account = settings.GPO_REQUEST_EMAIL_ACCOUNT
        # send request emails to Coordinator Admin group
        recipient_emails = list(User.objects.filter(groups__name='Coordinator Admin').values_list('email', flat=True))
        if 'result' in request.data:
            email_context = request.data['result']
        else:
            email_context = request.data
        if 'emergency_response_name' in email_context:
            html_msg = render_to_string('../templates/field_coord_er_request_email.html', email_context)
            email_subject = "Response/Project Request for Review in Account Request Tool"
        else:
            html_msg = render_to_string('../templates/field_coord_request_email.html', email_context)
            email_subject = "Coordinator Request for Review in Account Request Tool"
        plain_msg = strip_tags(html_msg)
        result = send_mail(
            subject=email_subject,
            message=plain_msg,
            from_email=gpo_request_email_account,
            recipient_list=recipient_emails,
            html_message=html_msg,
        )
        return Response(bool(result))
    except Exception as e:
        logger.error('Email Error: There was an error emailing the Field Coordinator Request.')
        return Response(False)


def error_test(request):
    raise Exception("this should log")