from django.contrib import admin
from models import Slice, Sliver, MemoryRequest, StorageRequest, CPURequest, NetworkRequest
from confine_utils.widgets import ShowText
from confine_utils.admin import admin_link_factory
from django import forms 
import settings 
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.html import escapejs

STATE_COLORS = { settings.ALLOCATED: "darkorange",
                 settings.DEPLOYED: "magenta",
                 settings.STARTED: "green" 
               }

def colored_state(self):
    state = escape(self.state)
    color = STATE_COLORS.get(self.state, "black")
    return "<b><span style='color: %s;'>%s</span></b>" % (color, state)
colored_state.short_description = "State" 
colored_state.allow_tags = True
colored_state.admin_order_field = 'state'


class MemoryRequestInline(admin.TabularInline):
    model = MemoryRequest
    max_num = 0
    
class StorageRequestInline(admin.TabularInline):
    model = StorageRequest
    max_num = 0
    
class CPURequestInline(admin.TabularInline):
    model = CPURequest
    max_num = 0

class NetworkRequestInline(admin.TabularInline):
    model = NetworkRequest
    extra = 0


class SliverAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'slice', 'node', 'cpurequest', 'memoryrequest', 'storagerequest', colored_state]
    list_filter = ['storagerequest__type', 'cpurequest__type', 'networkrequest__type', 'state']
    inlines = [CPURequestInline, MemoryRequestInline, StorageRequestInline, NetworkRequestInline]


    def response_change(self, request, obj):
        """
        Hack that closes browser window after SliverForm popup edition (emulating behaviour of popup addition).
        """
        # Semi-copypasta of django ModelAdmin
        opts = obj._meta
        verbose_name = opts.verbose_name
        if obj._deferred:
            opts_ = opts.proxy_for_model._meta
            verbose_name = opts_.verbose_name

        pk_value = obj._get_pk_val()
        msg = 'The %(name)s "%(obj)s" was changed successfully.' % {'name': force_unicode(verbose_name), 'obj': force_unicode(obj)}
        
        if "_continue" in request.POST:
            self.message_user(request, msg + ' ' + _("You may edit it again below."))
            if "_popup" in request.REQUEST:
                return HttpResponseRedirect(request.path + "?_popup=1")
            else:
                return HttpResponseRedirect(request.path)
        # end of copypasta
        elif "_popup" in request.POST:
            return HttpResponse(
                '<!DOCTYPE html><html><head><title></title></head><body>'
                '<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script></body></html>' % \
                # escape() calls force_unicode.
                (escape(pk_value), escapejs(obj)))        

        return super(SliverAdmin, self).response_change(request, obj)


class SliverForm(forms.ModelForm):
    """ 
    Read-only form for displaying slivers in slice admin change form.
    Also it provides popup links to each sliver admin change form.
    """
    #FIXME: js needed: when save popup the main form is not updated with the new/changed slivers
    #TODO: possible reimplementation when nested inlines support becomes available on django.contrib.admin

    sliver = forms.CharField(label="Sliver", widget=ShowText(bold=True))
    node = forms.CharField(label="Node", widget=ShowText(bold=True))
    url = forms.CharField(label="Node URL", widget=ShowText(bold=True))
    state = forms.CharField(label="State", widget=ShowText(bold=True))
    
    class Meta:
        # reset model field order
        fields = []
    
    def __init__(self, *args, **kwargs):
        super(SliverForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs['instance']
            sliver_change = reverse('admin:slices_sliver_change', args=(instance.pk,))
            self.initial['sliver'] = mark_safe("<a href='%s' id='add_id_user' onclick='return showAddAnotherPopup(this);'>%s </a>" % (sliver_change, instance))
            node_change = reverse('admin:nodes_node_change', args=(instance.node.pk,))
            self.initial['node'] = mark_safe("<a href='%s'>%s</a>" % (node_change, instance.node))
            self.initial['url'] = mark_safe("<a href='%s'>%s</a>" % (instance.node.url, instance.node.url))
            self.initial['state'] = mark_safe(colored_state(instance))

    

class SliverInline(admin.TabularInline):
    model = Sliver
    form = SliverForm
    max_num = 0    

def users(slice):
    return slice.user.username
    # for now only one user x slice: replace with the following when we allow more:
    #return ",".join(self.user.all().values_list('username', flat=True))

class SliceAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', users, colored_state, 
                    admin_link_factory('template', base_url='/static/'), 
                    admin_link_factory('code', base_url='/static/')
                   ]
    list_filter = ['state']
    inlines = [SliverInline]


admin.site.register(Slice, SliceAdmin)
admin.site.register(Sliver, SliverAdmin)
