from django.conf import settings
from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib.messages import WARNING
from django.utils.timezone import now
from rangefilter.filters import DateRangeFilterBuilder
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from django.utils.translation import gettext_lazy as _
import re
import logging
from .func import get_response_from_request

email_domain_regex = re.compile(r"(^[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

from .models import *

logger = logging.getLogger('django')

# hack to make full name show up in autocomplete b/c nothing else worked
# User.__str__ = lambda x: f"{x.first_name} {x.last_name} ({x.agol_info.portal.portal_name if hasattr(x, 'agol_info') and x.agol_info.portal is not None else ''})"
# # make admin panel show full name and portal of currently logged in user
# def _get_short_name_(user_instance):
#     return f"{user_instance.first_name} {user_instance.last_name} ({user_instance.agol_info.portal if hasattr(user_instance, 'agol_info') and user_instance.agol_info.portal is not None else ''})"


# User.get_short_name = _get_short_name_

class AGOLAdminForm(ModelForm):
    def clean_enterprise_precreate_domains(self):
        valid_emails = []
        for email in self.cleaned_data['enterprise_precreate_domains'].split(','):
            stripped_email = email.strip()
            if email_domain_regex.fullmatch(stripped_email):
                valid_emails.append(stripped_email)

        if not self.cleaned_data['allow_external_accounts'] and len(valid_emails) == 0:
            raise ValidationError("Email domain required if external account creation is disabled.")

        return ",".join(valid_emails)

    class Meta:
        model = AGOL
        fields = ['portal_name', 'portal_url', 'user', 'allow_external_accounts',
                  'enterprise_precreate_domains']


@admin.register(AGOL)
class AGOLAdmin(admin.ModelAdmin):
    list_display = ['portal_name', 'portal_url']
    form = AGOLAdminForm


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
    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ['portal']
        return self.readonly_fields
    # form = AGOLUserFieldsForm


@admin.register(User)
class AGOLUserAdmin(UserAdmin):
    inlines = (AGOLUserFieldsInline,)
    # list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(agol_info__portal_id=request.user.agol_info.portal_id)


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
    list_display = ['title', 'agol', 'is_auth_group']
    list_filter = ['agol']
    fields = ['title', 'agol', 'is_auth_group']
    readonly_fields = ['title', 'agol']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(agol=request.user.agol_info.portal_id)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_search_results(self, request, queryset, search_term):
        referrer = request.META.get('HTTP_REFERER', '')
        if 'responseproject' in referrer:
            r = get_response_from_request(request)
            if r:
                queryset = queryset.filter(agol=r.portal)
        return super().get_search_results(request, queryset, search_term)


class GroupAdminInline(admin.TabularInline):
    model = AGOLGroup.requests.through
    readonly_fields = ['group', 'is_member']
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class UserCreateForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False

    # def clean_password2(self):
    #     return None
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ['username']


class UserAdmin(AGOLUserAdmin):
    add_form = UserCreateForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username',),
        }),
    )
    fieldsets = (
        (None, {'fields': ('username',)}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


# only do this if explicit in settings
if getattr(settings, 'DISABLE_PASSWORD_AUTH', False):
    admin.site.unregister(User)
    admin.site.register(User, UserAdmin)


class PendingNotificationInline(GenericTabularInline):
    model = Notification
    fields = ['to_emails', 'subject', 'sent']
    readonly_fields = fields
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(AccountRequests)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'email', 'username']
    search_fields = list_display
    ordering = ['-submitted']
    list_filter = [('response', RelatedDropdownFilter),('approved_by', RelatedDropdownFilter),
                   ('submitted', DateRangeFilterBuilder()), ('approved', DateRangeFilterBuilder()),
                   ('created', DateRangeFilterBuilder())]
    fields = ['first_name', 'last_name', 'email', 'possible_existing_account', 'existing_account_enabled', 'organization', 'username',
              'username_valid', 'user_type', 'role', 'auth_group', 'sponsor', 'sponsor_notified', 'reason',
              'approved', 'approved_by', 'created', 'response', 'is_existing_account']
    readonly_fields = ['possible_existing_account', 'username_valid', 'sponsor_notified', 'approved', 'created',
                       'is_existing_account', 'existing_account_enabled', 'approved_by']
    inlines = [GroupAdminInline, PendingNotificationInline]
    actions = ['disable_account_action']

    @admin.action(description="Disable selected accounts")
    def disable_account_action(modeladmin, request, queryset):
        if not request.user.has_perm('accounts.change_accountrequests'):
            raise PermissionError('You do not have permission to modify accounts')
        try:
            for a in queryset:
                a.disable_account()
            messages.success(request, "If selected accounts were non-enterprise and new it has been disabled")
        except Exception as e:
            messages.error(request, "Error occurred when attempting to disable accounts.")
            logger.error('Error disabling accounts', e)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == "auth_group":
                kwargs["queryset"] = AGOLGroup.objects.filter(response__portal_id=request.user.agol_info.portal_id)

            if db_field.name == "role":
                kwargs["queryset"] = AGOLRole.objects.filter(agol_id=request.user.agol_info.portal_id)

            if db_field.name == "response":
                kwargs["queryset"] = ResponseProject.objects.filter(portal_id=request.user.agol_info.portal_id)

            if db_field.name == "sponsor":
                kwargs["queryset"] = User.objects.filter(agol_info__portal_id=request.user.agol_info.portal_id)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(response__portal_id=request.user.agol_info.portal_id)

# def set_system_default(modeladmin, request, queryset):
#     if queryset.count() > 1:
#         modeladmin.message_user(request, 'Only select one role for system default.', WARNING)
#     else:
#         AGOLRole.objects.filter().update(system_default=False)
#         queryset.update(system_default=True)


@admin.register(AGOLRole)
class AGOLRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_available', 'system_default', 'agol']
    search_fields = ['name', 'description']
    ordering = ['-is_available', 'agol', 'name']
    list_filter = ['is_available', 'agol']
    fields = ['name', 'id', 'description', 'agol', 'is_available', 'system_default']
    readonly_fields = ['name', 'id', 'description', 'agol']
    # actions = [set_system_default] removed b/c its more complicated with multiple agols

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class AccountRequestsInline(admin.TabularInline):
    model = AccountRequests
    readonly_fields = fields = ['first_name', 'last_name', 'email', 'organization', 'username', 'approved', 'created',
                                'is_existing_account']
    extra = 0
    show_change_link = True

    def has_delete_permission(self, request, obj=None):
        # unable to control delete permissions per account request so disable all in this view
        return False

    def has_add_permission(self, request, obj=None):
        return False


class ResponseProjectForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('instance', False):
            self.fields['users'].required = True
            self.fields['requester'].required = True
            self.fields['authoritative_group'].required = True

    class Meta:
        model = ResponseProject
        fields = '__all__'


@admin.register(ResponseProject)
class ResponseProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'portal', 'requester', 'sponsors', 'approved', 'disabled']
    search_fields = ['name']
    ordering = ['name']
    fields = ['name', 'requester', 'users', 'assignable_groups', 'role', 'authoritative_group', 'default_reason',
              'approved', 'approved_by', 'disabled', 'disabled_by', 'disable_users_link', 'portal']
    readonly_fields = ['approved', 'approved_by', 'disabled', 'disabled_by', 'disable_users_link']
    autocomplete_fields = ['users', 'assignable_groups']
    inlines = [AccountRequestsInline, PendingNotificationInline]
    list_filter = ['disabled', 'approved']
    form = ResponseProjectForm

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(portal=request.user.agol_info.portal_id)

    def get_fields(self, request, obj=None):
        if obj is None:
            return ['name']
        return self.fields

    def get_readonly_fields(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return self.readonly_fields + ['portal']
        return self.readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        response_id = request.resolver_match.kwargs.get('object_id', None)
        if db_field.name == "requester":
            kwargs["queryset"] = User.objects.filter(agol_info__portal__responses=response_id)

        if db_field.name == "authoritative_group":
            kwargs["queryset"] = AGOLGroup.objects.filter(agol__responses=response_id, is_auth_group=True)

        if db_field.name == "role":
            kwargs["queryset"] = AGOLRole.objects.filter(agol__responses=response_id, is_available=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        response = super(ResponseProjectAdmin, self).change_view(request, object_id, form_url, extra_context)
        if type(response) == HttpResponseRedirect:
            if 'approve' in request.POST:
                return redirect('../approve/')
            if 'disable' in request.POST:
                return redirect('../disable/')
        return response

    def disable_users_link(self, obj):
        return mark_safe(f'<a target=_blank href="{obj.disable_users_link}">Relevant Response/Project Accounts List</a>')

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        urls = [
            path('<path:object_id>/approve/', self.approve_view, name='%s_%s_approve' % info),
            path('<path:object_id>/disable/', self.disable_view, name='%s_%s_disable' % info),
        ] + urls
        return urls

    def approve_view(self, request, object_id):
        obj = self.get_object(request, object_id)

        if request.POST:
            obj.approved = now()
            obj.approved_by = request.user
            obj.save()
            return redirect('../change')

        opts = self.model._meta
        app_label = opts.app_label
        to, subject, message = obj.generate_approval_email()

        return TemplateResponse(request, 'admin/confirmation.html', {
            'title': 'Are you sure?',
            "object": obj,
            "opts": opts,
            "app_label": app_label,
            "type": "Approve",
            "to": ', '.join(to),
            "subject": subject,
            "email_content": message,
            'site_header': 'EPA Account Request Tool',
            'site_title': 'Account Request Tool',
        })

    def disable_view(self, request, object_id):
        obj = self.get_object(request, object_id)

        if request.POST:
            obj.disabled = now()
            obj.disabled_by = request.user
            obj.save()
            return redirect('../change/')

        opts = self.model._meta
        app_label = opts.app_label
        to, subject, message = obj.generate_disable_email()

        return TemplateResponse(request, 'admin/confirmation.html', {
            'title': 'Are you sure?',
            "object": obj,
            "opts": opts,
            "app_label": app_label,
            "type": "Disable",
            "to": ', '.join(to),
            "subject": subject,
            "email_content": message,
            'site_header': 'EPA Account Request Tool',
            'site_title': 'Account Request Tool',
        })

    def save_model(self, request, obj, form, change):
        if obj.pk is None:
            obj.portal = request.user.agol_info.portal
        super().save_model(request, obj, form, change)
    # def get_readonly_fields(self, request, obj=None):
    #     readonly_fields = super().get_readonly_fields(request, obj)
    #     if obj is None:
    #         readonly_fields += ['is_disabled']
    #     elif not obj.can_be_disabled():
    #         readonly_fields += ['is_disabled']
    #         field = [f for f in obj._meta.fields if f.name == 'is_disabled'][0]
    #         field.help_text = 'Can not disable response/project while there are pending account requests.'
    #     return readonly_fields

    def get_inlines(self, request, obj):
        if not obj:
            return []
        return self.inlines


@admin.register(Notification)
class PendingNotificationAdmin(admin.ModelAdmin):
    list_display = ['to_emails', 'subject', 'sent']
    fields = ['to', 'subject', 'content', 'sent']
    readonly_fields = ['sent']
