"""
URLconf for registration and activation, using django-registration's
default backend.

If the default behavior of these views is acceptable to you, simply
use a line like this in your root URLconf to set up the default URLs
for registration::

    (r'^accounts/', include('groupregistration.backends.default.urls')),

This will also automatically set up the views in
``django.contrib.auth`` at sensible default locations.

If you'd like to customize the behavior (e.g., by passing extra
arguments to the various views) or split up the URLs, feel free to set
up your own URL patterns for these views instead.

"""


from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

from groupregistration.views import register_group#, complete

urlpatterns = patterns('',
   url(r'^register/group/$',
       register_group,
       {'backend': 'groupregistration.backends.default.UserGroup'},
       name='registration_group_register'),
   url(r'^register/group/complete/$',
       TemplateView.as_view(template_name='registration_group_complete.html'),
       name='registration_group_complete'),
)
                       
