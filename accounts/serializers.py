from rest_framework.serializers import ModelSerializer, CharField, PrimaryKeyRelatedField, ChoiceField, JSONField
from .models import *
from rest_framework.decorators import api_view
from rest_framework_recaptcha.fields import ReCaptchaField
from .func import has_outstanding_request


class AccountRequestSerializer(ModelSerializer):
    recaptcha = ReCaptchaField()
    response = PrimaryKeyRelatedField(required=True, queryset=ResponseProject.objects.all())

    def validate(self, attrs):
        # check for outstanding requests and reject if so
        if has_outstanding_request(attrs):
            raise ValidationError({'details': 'Outstanding request found.'})

        return super().validate(attrs)

    class Meta:
        model = AccountRequests
        fields = ['first_name', 'last_name', 'email', 'organization', 'response', 'recaptcha']


class SponsorSerializer(ModelSerializer):
    phone_number = CharField(source='agol_info.phone_number')

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number']


# do NOT user with Sponsor viewset b/c that is unsecured and this exposes username
class SponsorWithUsernameSerializer(SponsorSerializer):
    username = CharField(source='agol_info.agol_username')

    class Meta(SponsorSerializer.Meta):
        fields = SponsorSerializer.Meta.fields + ['username']


class AccountSerializer(ModelSerializer):
    response = PrimaryKeyRelatedField(required=True, queryset=ResponseProject.objects.all())
    reason = ChoiceField(required=True, allow_null=False, allow_blank=False, choices=REASON_CHOICES)

    class Meta:
        model = AccountRequests
        exclude = ['recaptcha', 'user_type', 'sponsor_notified']


class AccountWithSponsorSerializer(AccountSerializer):
    sponsor = SponsorWithUsernameSerializer(many=False, read_only=True)

    class Meta(AccountSerializer.Meta):
        pass


class AGOLGroupSerializer(ModelSerializer):
    class Meta:
        model = AGOLGroup
        fields = ['id', 'title']


class ResponseProjectSerializer(ModelSerializer):
    class Meta:
        model = ResponseProject
        fields = ['id', 'name']


class FullResponseProjectSerializer(ModelSerializer):
    class Meta:
        model = ResponseProject
        fields = ['users', 'name', 'assignable_groups', 'authoritative_group', 'default_reason', 'role', 'requester']


class AGOLRoleSerializer(ModelSerializer):
    class Meta:
        model = AGOLRole
        fields = '__all__'


class PendingNotificationSerializer(ModelSerializer):
    to_emails = JSONField()

    class Meta:
        model = Notification
        fields = ['id', 'subject', 'content', 'to_emails']
