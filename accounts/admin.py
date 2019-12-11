from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django import forms
from django.contrib.auth.models import User

# hack to make full name show up in autocomplete b/c nothing else worked
User.__str__ = lambda x: f"{x.first_name} {x.last_name}"


@admin.register(AGOL)
class AGOLAdmin(admin.ModelAdmin):
    fields = ['portal_url', 'user']


admin.site.unregister(User)
admin.site.unregister(Group)


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


class AGOLGroupFieldsInline(admin.StackedInline):
    model = AGOLGroupFields


@admin.register(Group)
class AGOLGroupAdmin(GroupAdmin):
    inlines = (AGOLGroupFieldsInline,)


def toggle_show(self, request, queryset):
    for group in queryset:
        group.show = not group.show
        group.save(update_fields=['show'])


toggle_show.short_description = "Toggle Show in multi-select"


@admin.register(AGOLGroup)
class AGOLGroupAdmin(admin.ModelAdmin):
    ordering = ['title']
    search_fields = ['title']
    list_display = ['title', 'show']
    fields = ['title', 'show']
    actions = [toggle_show]


@admin.register(AccountRequests)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'email', 'username', 'submitted']
    search_fields = list_display
    ordering = ['-submitted']
    list_filter = ['approved']
