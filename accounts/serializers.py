from rest_framework.serializers import ModelSerializer, CharField, PrimaryKeyRelatedField, ChoiceField, \
    JSONField, BooleanField
from .models import *
from drf_recaptcha.fields import ReCaptchaV2Field
from .func import has_outstanding_request, email_allowed_for_portal, email_not_associated_with_existing_account


class AccountRequestSerializer(ModelSerializer):
    recaptcha = ReCaptchaV2Field()
    response = PrimaryKeyRelatedField(required=True, queryset=ResponseProject.objects.all())

    def validate(self, attrs):
        # check for outstanding requests and reject if so
        if has_outstanding_request(attrs):
            raise ValidationError({'details': 'Outstanding request found.'})

        if not email_allowed_for_portal(attrs):
            raise ValidationError({'details': 'Request can not be accepted at this time.'})

        return super().validate(attrs)

    class Meta:
        model = AccountRequests
        fields = ['first_name', 'last_name', 'email', 'organization', 'response', 'recaptcha']


class SponsorSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']


# do NOT user with Sponsor viewset b/c that is unsecured and this exposes username
class SponsorWithUsernameSerializer(SponsorSerializer):
    username = CharField(source='agol_info.agol_username')

    class Meta(SponsorSerializer.Meta):
        fields = SponsorSerializer.Meta.fields + ['username']


class AccountSerializer(ModelSerializer):
    response = PrimaryKeyRelatedField(required=True, queryset=ResponseProject.objects.all())
    reason = ChoiceField(required=True, allow_null=False, allow_blank=False, choices=REASON_CHOICES)
    existing_account_enabled = BooleanField(read_only=True)
    is_existing_account = BooleanField(read_only=True)

    class Meta:
        model = AccountRequests
        exclude = ['recaptcha', 'user_type']


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
    authoritative_group = PrimaryKeyRelatedField(queryset=AGOLGroup.objects.filter(is_auth_group=True), allow_null=True)
    requester = PrimaryKeyRelatedField(required=True, queryset=User.objects.all())

    class Meta:
        model = ResponseProject
        fields = ['id', 'users', 'name', 'portal', 'assignable_groups', 'authoritative_group', 'default_reason', 'role', 'requester']


class AccountWithNestedDataSerializer(AccountSerializer):
    sponsor = SponsorWithUsernameSerializer(many=False, read_only=True)
    response = FullResponseProjectSerializer(many=False, read_only=True)

    class Meta(AccountSerializer.Meta):
        pass


class AGOLRoleSerializer(ModelSerializer):
    class Meta:
        model = AGOLRole
        fields = '__all__'


class PendingNotificationSerializer(ModelSerializer):
    to_emails = JSONField()

    class Meta:
        model = Notification
        fields = ['id', 'subject', 'content', 'to_emails']

class PortalsSerializer(ModelSerializer):
    class Meta:
        model = AGOL
        fields = ['id', 'portal_name', 'portal_url']
