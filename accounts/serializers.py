from rest_framework.serializers import ModelSerializer
from .models import *
from rest_framework.decorators import api_view
from rest_framework_recaptcha.fields import ReCaptchaField


class AccountRequestSerializer(ModelSerializer):
    recaptcha = ReCaptchaField()

    class Meta:
        model = AccountRequests
        fields = ['first_name', 'last_name', 'email', 'organization', 'sponsor', 'reason', 'description', 'recaptcha']


class AccountSerializer(ModelSerializer):
    class Meta:
        model = AccountRequests
        exclude = ['recaptcha']


class AGOLGroupSerializer(ModelSerializer):
    class Meta:
        model = AGOLGroup
        fields = ['id', 'title']
