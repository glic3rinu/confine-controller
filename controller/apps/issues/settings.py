from django.conf import settings


ISSUES_SUPPORT_EMAILS = getattr(settings, 'ISSUES_SUPPORT_EMAILS', [])
