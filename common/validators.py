from uuid import UUID

from django.core.exceptions import ValidationError


def UUIDValidator(value):
    try: 
        UUID(value)
    except:
        raise ValidationError('%s is a badly formed hexadecimal UUID string' % value)
