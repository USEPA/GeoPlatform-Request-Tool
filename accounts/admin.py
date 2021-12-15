from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.forms import ModelForm
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib.messages import WARNING
from django.utils.timezone import now


from .models import *


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
    list_filter = ['response', 'submitted', 'approved', 'created']
    fields = ['first_name', 'last_name', 'email', 'possible_existing_account', 'organization', 'username',
              'username_valid', 'user_type', 'role', 'auth_group', 'sponsor', 'sponsor_notified', 'reason',
              'approved', 'created', 'response', 'is_existing_account']
    readonly_fields = ['possible_existing_account', 'username_valid', 'sponsor_notified', 'approved', 'created',
                       'is_existing_account']
    inlines = [GroupAdminInline, PendingNotificationInline]


def set_system_default(modeladmin, request, queryset):
    if queryset.count() > 1:
        modeladmin.message_user(request, 'Only select one role for system default.', WARNING)
    else:
        AGOLRole.objects.all().update(system_default=False)
        queryset.update(system_default=True)


@admin.register(AGOLRole)
class AGOLRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_available', 'system_default']
    search_fields = ['name', 'description']
    ordering = ['-is_available', 'name']
    list_filter = ['is_available']
    fields = ['name', 'id', 'description', 'agol', 'is_available', 'system_default']
    readonly_fields = ['name', 'id', 'description', 'agol']
    actions = [set_system_default]

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
        self.fields['users'].required = True

    class Meta:
        model = ResponseProject
        fields = '__all__'


@admin.register(ResponseProject)
class ResponseProjectAdmin(admin.ModelAdmin):

    list_display = ['name', 'requester', 'sponsors', 'approved', 'disabled']
    search_fields = ['name']
    ordering = ['name']
    fields = ['name', 'requester', 'users', 'assignable_groups', 'role', 'authoritative_group', 'default_reason',
              'approved', 'approved_by',
              'disabled', 'disabled_by', 'disable_users_link']
    readonly_fields = ['approved', 'approved_by', 'disabled', 'disabled_by', 'disable_users_link']
    autocomplete_fields = ['users', 'assignable_groups']
    inlines = [AccountRequestsInline, PendingNotificationInline]
    list_filter = ['disabled', 'approved']
    form = ResponseProjectForm

    def change_view(self, request, object_id, form_url='', extra_context=None):
        response = super(ResponseProjectAdmin, self).change_view(request, object_id, form_url, extra_context)
        if type(response) == HttpResponseRedirect:
            if 'approve' in request.POST:
                return redirect('../approve/')
            if 'disable' in request.POST:
                return redirect('../disable/')
        return response

    def disable_users_link(self, obj):
        return mark_safe(f'<a target=_blank href="{obj.disable_users_link}">Relevant Response/Project GeoPlatform Accounts List</a>')

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
        object = self.get_object(request, object_id)
        to, subject, message = object.generate_approval_email()

        if request.POST:
            object.approved = now()
            object.approved_by = request.user
            object.save()
            notification = Notification.objects.create(
                subject=subject,
                content=message,
                content_object=object
            )
            notification.to.set(to)
            return redirect('../change')
        opts = self.model._meta
        app_label = opts.app_label

        return TemplateResponse(request, 'admin/confirmation.html', {
            'title': 'Are you sure?',
            "object": object,
            "opts": opts,
            "app_label": app_label,
            "type": "Approve",
            "to": ', '.join(set([x.email.lower() for x in to])),
            "subject": subject,
            "email_content": message,
            'site_header': 'EPA GeoPlatform Account Request Tool',
            'site_title': 'GeoPlatform Account Request Tool',
        })

    def disable_view(self, request, object_id):
        object = self.get_object(request, object_id)
        to, subject, message = object.generate_disable_email()

        if request.POST:
            object.disabled = now()
            object.disabled_by = request.user
            object.save()
            n = Notification.objects.create(
                subject=subject,
                content=message,
                content_object=object
            )
            n.to.set(to)
            return redirect('../change/')
        opts = self.model._meta
        app_label = opts.app_label

        return TemplateResponse(request, 'admin/confirmation.html', {
            'title': 'Are you sure?',
            "object": object,
            "opts": opts,
            "app_label": app_label,
            "type": "Disable",
            "to": ', '.join(set([x.email.lower() for x in to])),
            "subject": subject,
            "email_content": message,
            'site_header': 'EPA GeoPlatform Account Request Tool',
            'site_title': 'GeoPlatform Account Request Tool',
        })


    # def get_readonly_fields(self, request, obj=None):
    #     readonly_fields = super().get_readonly_fields(request, obj)
    #     if obj is None:
    #         readonly_fields += ['is_disabled']
    #     elif not obj.can_be_disabled():
    #         readonly_fields += ['is_disabled']
    #         field = [f for f in obj._meta.fields if f.name == 'is_disabled'][0]
    #         field.help_text = 'Can not disable response/project while there are pending account requests.'
    #     return readonly_fields

@admin.register(Notification)
class PendingNotificationAdmin(admin.ModelAdmin):
    list_display = ['to_emails', 'subject', 'sent']
    fields = ['to', 'subject', 'content', 'sent']
    readonly_fields = ['sent']
    autocomplete_fields = ['to']
