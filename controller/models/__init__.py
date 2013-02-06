try:
    # psycopg2 needs us to register the uuid type
    import psycopg2.extras
    psycopg2.extras.register_uuid()
except (ImportError, AttributeError):
    pass


## Add South introspect rules for private_files.PrivateField
from django.conf import settings
if 'private_files' and 'south' in settings.INSTALLED_APPS:
    from private_files import PrivateFileField
    from south.modelsinspector import add_introspection_rules
    rules = [((PrivateFileField,), [], {"attachment" : ["attachment", {"default": True}],},)]
    add_introspection_rules(rules, ["^private_files\.models\.fields\.PrivateFileField"])

