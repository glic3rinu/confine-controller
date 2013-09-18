from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

from controller.utils.apps import is_installed
from registration.backends.default.urls import urlpatterns as registration_urlpatterns

from . import BackendFactory

if is_installed('captcha'):
    from .forms import RegistrationCaptchaForm as RegistrationForm
else:
    from .forms import RegistrationFormUniqueEmail as RegistrationForm


backend = BackendFactory.create()
ActivationView = backend.get_activation_view()
RegistrationView = backend.get_registration_view()

urlpatterns = patterns('',
   url(r'^activate/complete/$',
       TemplateView.as_view(template_name='registration/activation_complete.html'),
       name='registration_activation_complete'),
    url(r'^activate/(?P<activation_key>\w+)/$',
       ActivationView.as_view(),
       name='registration_activate'),
    url(r'^register/$',
        RegistrationView.as_view(form_class=RegistrationForm),
        name='registration_register'),
) + registration_urlpatterns
