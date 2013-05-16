from django.conf import settings

ISSUES_OPERATORS_EMAIL = getattr(settings, 'ISSUES_OPERATOR_EMAIL', [])
