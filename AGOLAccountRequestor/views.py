import logging
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

    current_user = {
        'name': '{} {}'.format(request.user.first_name, request.user.last_name) if request.user.first_name else request.user.username,
        'permissions': set(permissions),
        'is_superuser': request.user.is_superuser
    }
    return Response(current_user)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def email_field_coordinator_request(request):
    try:
        gpo_request_email_account = settings.GPO_REQUEST_EMAIL_ACCOUNT
        recipient_emails = settings.RECIPIENT_EMAILS
        if 'result' in request.data:
            email_context = request.data['result']
        else:
            email_context = request.data
        if 'emergency_response_name' in email_context:
            html_msg = render_to_string('../templates/field_coord_er_request_email.html', email_context)
            email_subject = "Response/Project Request for Review in GeoPlatform Account Request Tool"
        else:
            html_msg = render_to_string('../templates/field_coord_request_email.html', email_context)
            email_subject = "Coordinator Request for Review in GeoPlatform Account Request Tool"
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
