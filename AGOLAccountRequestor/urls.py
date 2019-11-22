"""AGOLAccountRequestor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from accounts import views as account_views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

router = routers.DefaultRouter()

router.register('account/request', account_views.AccountRequestViewSet)
router.register('account/approvals', account_views.AccountViewSet)
router.register('agol/groups', account_views.AGOLGroupViewSet)

admin.site.site_header = "EPA GeoPlatform Account Request Tool"
admin.site.site_title = "GeoPlatform Account Request Tool"
admin.site.index_title = "Tool Administration"


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

urlpatterns = [
    path('api/admin/', admin.site.urls),
    # path('api/oauth2/', include('rest_framework_social_oauth2.urls')),
    path('api/v1/', include(router.urls)),
    path('api/rest-auth/', include('rest_auth.urls')),
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/oauth2/', include('rest_framework_social_oauth2.urls')),
    path('api/current_user/', current_user),

]
