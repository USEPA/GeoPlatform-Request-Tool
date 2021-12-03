from django.conf import settings
from django.contrib import admin
from django.forms import ModelForm
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from django.http.response import HttpResponse

from .models import *
from .func import email_response_project_disabled


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
    inlines = [GroupAdminInline]


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


class AccountRequestsInline(admin.TabularInline):
    model = AccountRequests
    readonly_fields = fields = ['first_name', 'last_name', 'email', 'organization', 'username', 'approved', 'created',
                                'is_existing_account']
    extra = 0
    show_change_link = True

    def has_delete_permission(self, request, obj=None):
        # unable to control delete permissions per account request so disable all in this view
        return False


@admin.register(ResponseProject)
class ResponseProjectAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']
    fields = ['name', 'assignable_groups', 'role', 'authoritative_group', 'users', 'is_disabled', 'disable_users_link']
    readonly_fields = ['disable_users_link']
    autocomplete_fields = ['users', 'assignable_groups']
    inlines = [AccountRequestsInline]
    list_filter = ['is_disabled']

    def save_model(self, request, obj, form, change):
        if change and not obj._is_disabled and obj.is_disabled:
            email_response_project_disabled(obj)
        super(ResponseProjectAdmin, self).save_model(request, obj, form, change)

    def disable_users_link(self, obj):
        return mark_safe(f'<a target=_blank href="{obj.disable_users_link}">Relevant Response/Project GeoPlatform Accounts List</a>')

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        urls = [
            path('preview_disable_email/<int:pk>/', self.preview_disable_response_email)
        ] + urls
        return urls

    def preview_disable_response_email(self, request, pk):
        r = get_object_or_404(ResponseProject, pk=pk)
        to, subject, message = email_response_project_disabled(r, False)
        return HttpResponse(f'''
            TO: {','.join(to)}<br/>
            SUBJECT: {subject}<br/>
            BODY: <br/>{message}
        ''')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj is None:
            readonly_fields += ['is_disabled']
        elif not obj.can_be_disabled():
            readonly_fields += ['is_disabled']
            field = [f for f in obj._meta.fields if f.name == 'is_disabled'][0]
            field.help_text = 'Can not disable response/project while there are pending account requests.'
        return readonly_fields
