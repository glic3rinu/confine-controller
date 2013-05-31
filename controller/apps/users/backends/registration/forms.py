from captcha.fields import CaptchaField
from registration.forms import RegistrationFormUniqueEmail

class RegistrationCaptchaForm(RegistrationFormUniqueEmail):
    """ Registration form with captcha based on django-simple-captcha """
    captcha = CaptchaField(help_text="Type the characters you see in the picture.")
