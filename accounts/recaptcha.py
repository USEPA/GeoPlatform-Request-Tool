from drf_recaptcha.fields import ReCaptchaV3Field
from django.conf import settings


class ReCaptchaV3FieldWithBypass(ReCaptchaV3Field):
    """
    Custom ReCaptcha V3 field that bypasses validation when minimum score is set to 0.0.
    This allows e2e tests to bypass recaptcha by setting DRF_RECAPTCHA_MINIMUM_SCORE to 0.0
    """

    def validate(self, value):
        # If minimum score is 0.0, bypass recaptcha validation entirely
        if settings.DRF_RECAPTCHA_MINIMUM_SCORE == 0.0:
            return
        # Otherwise, perform normal validation
        super().validate(value)

