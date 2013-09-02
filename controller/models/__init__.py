try:
    # psycopg2 needs us to register the uuid type
    import psycopg2.extras
    psycopg2.extras.register_uuid()
except (ImportError, AttributeError):
    pass


## Add South introspect rules for privatefiles.PrivateField
from django.conf import settings
if 'privatefiles' and 'south' in settings.INSTALLED_APPS:
    from privatefiles import PrivateFileField
    from south.modelsinspector import add_introspection_rules
    rules = [((PrivateFileField,), [], {"attachment" : ["attachment", {"default": True}],},)]
    add_introspection_rules(rules, ["^privatefiles\.models\.fields\.PrivateFileField"])

