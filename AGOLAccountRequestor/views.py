from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
        recipient_email = 'tmckennon@innovateteam.com'  # TODO: Switch to 'GIS_Team@epa.gov' or a new EPA email
        email_context = request.data['result']
        html_msg = render_to_string('../templates/field_coord_request_email.html', email_context)
        plain_msg = strip_tags(html_msg)
        result = send_mail(
            subject="Field Coordinator Request",
            message=plain_msg,
            from_email=recipient_email,
            recipient_list=[recipient_email],
            html_message=html_msg,
        )
        return Response(bool(result))
    except Exception as e:
        return Response({'message': 'There was an error emailing the Field Coordinator Request for ' +
                                    'AGOL user {}.'.format(request.data['result']['agol_user'])})
