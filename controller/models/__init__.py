from django.conf import settings
from django.core import validators
from django.db import models

from controller.settings import MGMT_IPV6_PREFIX
from controller.utils.singletons.models import SingletonModel

try:
    # psycopg2 needs us to register the uuid type
    import psycopg2.extras
    psycopg2.extras.register_uuid()
except (ImportError, AttributeError):
    pass

## Add South introspect rules for privatefiles.PrivateField
if 'privatefiles' and 'south' in settings.INSTALLED_APPS:
    from privatefiles import PrivateFileField
    from south.modelsinspector import add_introspection_rules
    rules = [((PrivateFileField,), [], {"attachment" : ["attachment", {"default": True}],},)]
    add_introspection_rules(rules, ["^privatefiles\.models\.fields\.PrivateFileField"])


class Testbed(SingletonModel):
    """
    Groups testbed-wide parameters and resources and provides the
    API URIs to navigate to other resources in the testbed.

    """
    def __unicode__(self):
        return "testbed"


class TestbedParams(models.Model):
    """ Describes testbed-wide parameters. """
    testbed = models.OneToOneField(Testbed, primary_key=True, related_name='testbed_params')
    mgmt_ipv6_prefix = models.CharField(max_length=128,
            help_text='An IPv6 /48 network used as the testbed management '
                      'IPv6 prefix. See addressing for legal values. This '
                      'member can only be changed if all nodes are in the '
                      'safe set state (/set_state=safe).',
            default=MGMT_IPV6_PREFIX,
            validators=[validators.validate_ipv6_address])

    def __unicode__(self):
        return "testbed_params"

