import requests
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.timezone import now

from controller.models.fields import URIField
from controller.utils.apps import is_installed
from nodes.models import Node, Server

from . import settings


# Hook Community Network support for related models
# This must be at the begining in order to avoid wired import problems
related_models = [Node, Server]


class CnHost(models.Model):
    """ Describes a host in the Community Network """
    app_url = models.URLField('community network URL', blank=True,
            help_text='Optional URL pointing to a description of this host/device '
                      'in its CN\'s node DB web application.')
    cndb_uri = URIField('community network database URI', blank=True, unique=True,
            help_text='Optional URI for this host/device in its CN\'s CNDB REST API')
    cndb_cached_on = models.DateTimeField('CNDB cached on', null=True, blank=True,
            help_text='Last date that CNDB information for this host/device was '
                      'successfully retrieved.')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    
    content_object = generic.GenericForeignKey()
    
    class Meta:
        unique_together = ('content_type', 'object_id')
    
    def __unicode__(self):
        return unicode(self.pk)
    
    def save(self, *args, **kwargs):
        """ Setting cndb_uri resets cndb_cached_on to null. """
        if self.pk:
            db_host = CnHost.objects.get(pk=self.pk)
            if self.cndb_uri != db_host.cndb_uri:
                self.cndb_cached_on = None
        super(CnHost, self).save(*args, **kwargs)
    
    def auth_cndb(self):
        """ Get auth cookie for the nodeDB API """
        ca_bundle = settings.COMMUNITYNETWORKS_CNDB_CA_BUNDLE
        url_auth = settings.COMMUNITYNETWORKS_CNDB_URL_AUTH
        username = settings.COMMUNITYNETWORKS_CNDB_USER
        password = settings.COMMUNITYNETWORKS_CNDB_PASS
        if not username or not password:
            raise ImproperlyConfigured(
                    "No CNDB credentials defined, are COMMUNITYNETWORKS_CNDB_USER"
                    " and COMMUNITYNETWORKS_CNDB_PASS at settings?"
            )
        data = {
            'username': username,
            'password': password }
        try:
            auth = requests.post(url_auth, data, verify=ca_bundle)
        except Exception as e:
            raise CnHost.CNDBFetchError(str(e))
        return auth

    def fetch_cndb(self):
        """
        Queries the nodeDB using cndb_uri.
        @CNDB API: http://ffm.gg32.com/Doc/FFM/
        """
        try:
            # python-requests uses its own cacert file (e.g. Debian 
            # /usr/local/lib/python2.6/dist-packages/requests/cacert.pem)
            # cause it not contains cacert.org certificate, we include it
            # with the app source 
            # http://hearsum.ca/blog/python-and-ssl-certificate-verification/#comment-443
            ca_bundle = settings.COMMUNITYNETWORKS_CNDB_CA_BUNDLE
            cookies = self.auth_cndb().json()
            resp = requests.get(self.cndb_uri, cookies=cookies, verify=ca_bundle)
        except ImproperlyConfigured as e:
            raise ImproperlyConfigured(str(e))
        except Exception as e:
            raise CnHost.CNDBFetchError(str(e))
        
        if resp.status_code != requests.codes.ok:
            raise CnHost.CNDBFetchError("%i - %s" % (resp.status_code, resp.json().get('description')))
        
        return resp.json()
    
    def cache_cndb(self, *fields):
        """ fetches fields from cndb and stores it into the database """
        cndb = self.fetch_cndb()
        
        for field in fields:
            node = self.content_object
            if field == 'gis':
                if not is_installed('gis'):
                    raise ImproperlyConfigured("'%s' field cannot be cached from CNDB (gis app is not installed)." % field)
                from gis.models import NodeGeolocation
                position = cndb.get('attributes').get('position')
                lat, lon = position.get('lat'), position.get('lon')
                # update the node info
                try:
                    gis = node.gis # exist related object?
                except NodeGeolocation.DoesNotExist:
                    gis = NodeGeolocation.objects.create(node=node)
                gis.geolocation = "%s,%s" % (lat, lon)
                gis.save()
            else:
                raise NotImplementedError("'%s' field cannot be cached from CNDB." % field)
                # TODO How to get other info from CNDB API?
                # can be generic? (proposal)
#                value = cndb.get(CNDB_FIELD_MAP[field])
#                setattr(node, field, value)
#                node.save()
#               # another generalization proposal:
#                CNDB_FIELD_MAP = {
#                    'arch': lambda j: j.get('machine').get('architecture'),
#                    'sliver_pub_ipv4': lambda j: j.get('sliver_pub_ipv4'),
#                    'sliver_pub_ipv4_range': lambda j: '#%d' % len(j.get('ips'))
#                }
#                value = CNDB_FIELD_MAP[field](cndb)
        
        # update last cached time
        # use timezone aware datetime
        self.cndb_cached_on = now()
        self.save()
    
    class CNDBFetchError(Exception):
        pass


# Hook Community Network support for related models
@property
def cn(self):
    try:
        return self.cn_generic.get()
    except CnHost.DoesNotExist:
        return None

for model in related_models:
    model.add_to_class('cn_generic', generic.GenericRelation('communitynetworks.CnHost'))
    model.cn = cn
