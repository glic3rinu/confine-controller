from django.conf.urls import patterns, url
from registration.views import register
from registration.urls import urlpatterns as registration_urlpatterns

from controller.utils import is_installed
from . import BackendFactory

if is_installed('captcha'):
    from .forms import RegistrationCaptchaForm as RegistrationForm
else:
    from registration.forms import RegistrationFormUniqueEmail as RegistrationForm


urlpatterns = patterns('',
    url(r'^register/$',
    register,
    { 'form_class': RegistrationForm, 'backend': BackendFactory.create() },
    name='registration_register'),
) + registration_urlpatterns
