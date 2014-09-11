from __future__ import absolute_import

from django.contrib import admin
from registration.admin import RegistrationAdmin
from registration.models import RegistrationProfile


class CustomRegistrationAdmin(RegistrationAdmin):
    # Override registration admin that fails with custom user model (#518)
    search_fields = ('user__username', 'user__name')


admin.site.unregister(RegistrationProfile)
admin.site.register(RegistrationProfile, CustomRegistrationAdmin)
