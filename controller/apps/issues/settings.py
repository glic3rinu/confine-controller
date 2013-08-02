from django.conf import settings


ISSUES_SUPPORT_EMAIL = getattr(settings, 'ISSUES_SUPPORT_EMAIL', [])
