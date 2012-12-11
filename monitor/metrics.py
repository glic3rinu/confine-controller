
import requests
import gevent
from gevent import monkey

class Metric(object):
    pass



class REST(Metric):
    def __call__(self, queryset=None, url=None, member=None):
        """ 
        Example:
            targets: NodeQuerySet
            url: "http://[{{ node.tinc.address }}]/confine/api/node"
            member: "state"
        """
        from nodes.models import *
        from django.template import Context, Template
        
        #### Test parameters
        queryset=Node.objects.all()
        url = Template('http://controller.confine-project.eu/api/nodes/{{ node.id }}')
        member = 'set_state'
        ######
        
        model = queryset.model._meta.verbose_name
        monkey.patch_all(thread=False, select=False)
        
        # create grenlets
        glets = [gevent.spawn(requests.get, url.render(Context({model:obj})), prefetch=True) for obj in queryset] 

        # wait for all the greenlets to finish
        gevent.joinall(glets)

        # store the results
        for (glet, node) in zip(glets, queryset):
            print node.id, glet.get().json['id']
