from django.conf import settings
from django.contrib import admin
from django.forms import ModelForm
from django import forms
from django.core.mail import send_mail

import urllib
import logging

from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User
from .models import *


logger = logging.getLogger('AGOLAccountRequestor')

# hack to make full name show up in autocomplete b/c nothing else worked
User.__str__ = lambda x: f"{x.first_name} {x.last_name}"


@admin.register(AGOL)
class AGOLAdmin(admin.ModelAdmin):
    fields = ['portal_url', 'user']


admin.site.unregister(User)
# admin.site.unregister(Group)


# class AGOLModelMultipleChoiceField(forms.ModelMultipleChoiceField):
#     def label_from_instance(self, obj):
#         return f"{obj.first_name} {obj.last_name}"


# class AGOLUserFieldsForm(forms.ModelForm):
#     delegates = forms.ModelMultipleChoiceField(queryset=User.objects.all())
#
#     class Meta:
#         model = AGOLUserFields
#         fields = '__all__'


class AGOLUserFieldsInline(admin.StackedInline):
    model = AGOLUserFields
    autocomplete_fields = ['delegates']
    # form = AGOLUserFieldsForm


@admin.register(User)
class AGOLUserAdmin(UserAdmin):
    inlines = (AGOLUserFieldsInline,)

    # hacky solution b/c of https://code.djangoproject.com/ticket/29707
    def get_search_results(self, request, queryset, search_term):
        if 'responseproject' in request.META.get('HTTP_REFERER', ''):
            queryset = queryset.filter(agol_info__sponsor=True)
        return super().get_search_results(request, queryset, search_term)
# class AGOLGroupFieldsInline(admin.StackedInline):
    # model = AGOLGroupFields
    # autocomplete_fields = ['assignable_groups']


# @admin.register(Group)
# class AGOLGroupAdmin(GroupAdmin):
#     inlines = (AGOLGroupFieldsInline,)


@admin.register(AGOLGroup)
class AGOLGroupAdmin(admin.ModelAdmin):
    ordering = ['-is_auth_group', 'title']
    search_fields = ['title']
    list_display = ['title', 'is_auth_group']
    fields = ['title', 'is_auth_group']
    readonly_fields = ['title']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AccountRequests)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'email', 'username']
    search_fields = list_display
    ordering = ['-submitted']
    list_filter = ['response', 'submitted', 'approved', 'created']
    fields = ['first_name', 'last_name', 'email', 'possible_existing_account', 'organization', 'username',
              'username_valid', 'user_type', 'role', 'groups', 'auth_group', 'sponsor', 'sponsor_notified', 'reason',
              'approved', 'created', 'response']
    autocomplete_fields = ['groups']


@admin.register(AGOLRole)
class AGOLRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_available']
    search_fields = ['name', 'description']
    ordering = ['-is_available', 'name']
    list_filter = ['is_available']
    fields = ['name', 'id', 'description', 'agol', 'is_available']
    readonly_fields = ['name', 'id', 'description', 'agol']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ResponseProjectAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ResponseProjectAdminForm, self).__init__(*args, **kwargs)
        self.fields['is_disabled'].help_text = 'Setting this will send an email notification to ' \
                                               'assigned sponsors and their delegates.'


@admin.register(ResponseProject)
class ResponseProjectAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']
    fields = ['name', 'assignable_groups', 'role', 'authoritative_group', 'users', 'is_disabled']
    autocomplete_fields = ['users', 'assignable_groups']
    form = ResponseProjectAdminForm

    def save_model(self, request, obj, form, change):
        if change and obj.is_disabled and AccountRequests.objects.filter(response=obj, agol_id__isnull=False).exists():
            email_response_project_disabled(obj)
        super(ResponseProjectAdmin, self).save_model(request, obj, form, change)


def email_response_project_disabled(response_project):
    try:
        from_email_account = settings.GPO_REQUEST_EMAIL_ACCOUNT
        recipient_emails = set()
        for sponsor in response_project.users.all():
            recipient_emails.add(sponsor.email)
            delegate_emails = set()
            for delegate in sponsor.agol_info.delegates.all():
                if hasattr(delegate, 'email'):
                    delegate_emails.add(delegate.email)
            recipient_emails.update(delegate_emails)
        # define link to relevant user accounts
        url = 'https://{domain}/home/organization.html?'.format(domain=settings.SOCIAL_AUTH_AGOL_DOMAIN)
        query_params = {'showFilters': 'false', 'view': 'table', 'sortOrder': 'asc', 'sortField': 'fullname'}
        # get account request AGOL IDs to define in link
        agol_ids = list(str(acct.agol_id).replace('-', '') for acct in AccountRequests.objects.filter(response=response_project,
                                                                                                      agol_id__isnull=False))
        agol_ids_param = ' OR '.join(agol_ids)
        query_params['searchTerm'] = agol_ids_param
        link = url + urllib.parse.urlencode(query_params) + '#members'
        email_subject = "GeoPlatform Account Response/Project has been disabled"
        msg = f'GeoPlatform Account Request Tool Response/Project <b>{response_project.name}</b> has been disabled. '\
              f'Please go to this GeoPlatform dashboard link <a href="{link}">Relevant Response/Project GeoPlatform Accounts List</a> ' \
              f'to make appropriate account changes and notify the users of your changes.'
        send_mail(
            subject=email_subject,
            message=msg,
            from_email=from_email_account,
            recipient_list=recipient_emails,
            html_message=msg,
        )
    except Exception as e:
        logger.error("Email Error: There was an error emailing the disabled Response Project's assigned sponsors and their delegates.")
