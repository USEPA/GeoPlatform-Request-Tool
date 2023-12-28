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
from django.conf import settings

from accounts import views as account_views
from django.contrib.auth import views as auth_views
from .views import current_user, error_test
from .views import email_field_coordinator_request
import debug_toolbar

router = routers.DefaultRouter()

router.register('portals', account_views.PortalsViewSet)
router.register('account/request', account_views.AccountRequestViewSet)
router.register('account/approvals', account_views.AccountViewSet)
router.register('responses', account_views.ResponseProjectViewSet)
router.register('sponsors', account_views.SponsorsViewSet)
router.register('agol/groups', account_views.AGOLGroupViewSet)
router.register('agol/roles', account_views.AGOLRoleViewSet)
# router.register('notifications', account_views.PendingNotificationViewSet)

admin.site.site_header = "EPA Account Request Tool"
admin.site.site_title = "Account Request Tool"
admin.site.index_title = "Tool Administration"
admin.site.site_url = f"/{settings.URL_PREFIX}"

urlpatterns = [
    path(f'{settings.URL_PREFIX}api/admin/', admin.site.urls),
    # path('api/oauth2/', include('rest_framework_social_oauth2.urls')),
    path(f'{settings.URL_PREFIX}api/v1/', include(router.urls)),
    path(f'{settings.URL_PREFIX}api/v1/error_test/', error_test),
    path(f'{settings.URL_PREFIX}api/v1/email_field_coordinator_request/', email_field_coordinator_request),
    # path('api/rest-auth/', include('rest_auth.urls')),
    path(f'{settings.URL_PREFIX}api/oauth2/', include('social_django.urls', namespace='social_django')),
    path(f'{settings.URL_PREFIX}api/current_user/', current_user),
    path(f'{settings.URL_PREFIX}api/auth/logout/', auth_views.LogoutView.as_view(), name='logout'),
]

if settings.DEBUG:
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls)),]

if not settings.DISABLE_PASSWORD_AUTH:
    urlpatterns += [path(f'{settings.URL_PREFIX}api/auth/', include('rest_framework.urls', namespace='rest_framework'))]
