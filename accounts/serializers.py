from rest_framework.serializers import ModelSerializer, CharField, PrimaryKeyRelatedField
from .models import *
from rest_framework.decorators import api_view
from rest_framework_recaptcha.fields import ReCaptchaField


class AccountRequestSerializer(ModelSerializer):
    recaptcha = ReCaptchaField()
    response = PrimaryKeyRelatedField(required=True, queryset=ResponseProject.objects.all())

    class Meta:
        model = AccountRequests
        fields = ['first_name', 'last_name', 'email', 'organization', 'response', 'reason', 'description', 'recaptcha']


class AccountSerializer(ModelSerializer):
    response = PrimaryKeyRelatedField(required=True, queryset=ResponseProject.objects.all())

    class Meta:
        model = AccountRequests
        exclude = ['recaptcha', 'user_type']


class AGOLGroupSerializer(ModelSerializer):
    class Meta:
        model = AGOLGroup
        fields = ['id', 'title']


class ResponseProjectSerializer(ModelSerializer):
    class Meta:
        model = ResponseProject
        fields = ['id', 'name']


class SponsorSerializer(ModelSerializer):
    phone_number = CharField(source='agol_info.phone_number')

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number']
