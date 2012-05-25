from django.forms import CheckboxSelectMultiple, CheckboxInput
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.forms.widgets import flatatt
from itertools import chain
from django.utils.html import escape, conditional_escape

from nodes import models
from slices import forms as slices_forms
from slices import models as slices_models

from django.forms.models import modelformset_factory

class NodeWithInterfacesWidget(CheckboxSelectMultiple):
    """
    """

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul>']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                final_attrs['class'] = "node_item"
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            
            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))

            child_cpu, child_storage, child_memory, child_network, rendered_child_network = self.get_childs(option_value)
 
            output.append(u'%s<li><label%s>%s %s</label><div id="network_%s" class="network_%s node_extra"><a href="#" onclick="add_new_form_element(\'id_node_%s_nr-TOTAL_FORMS\',\'network_%s\'); return false;">New network request</a><h4>Network Requests</h4><div><h5>Network request</h5>%s</div></div><div class="cpu_%s node_extra"><h4>CPU Requests</h4>%s</div><div class="storage_%s node_extra"><h4>Storage Requests</h4>%s</div><div class="memory_%s node_extra"><h4>Memory Requests</h4>%s</div></li>' % (
                child_network.management_form.__unicode__(),
                label_for,
                rendered_cb,
                option_label,
                option_value,
                option_value,
                option_value,
                option_value,
                rendered_child_network,
                option_value,
                child_cpu,
                option_value,
                child_storage,
                option_value,
                child_memory)
                          )
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))

    def set_retented_data(self, node_id, data_id, data_value):
        try:
            retented_data[node_id][data_id] = data_value 
        except:
            try:
                retented_data[node_id] = {}
                retented_data[node_id][data_id] = data_value
            except:
                retented_data = {}
                retented_data[node_id] = {}
                retented_data[node_id][data_id] = data_value                
    
    def get_childs(self, option_value):
        NetworkFormset = modelformset_factory(slices_models.NetworkRequest,
                                              extra = 1,
                                              form = slices_forms.NetworkRequestForm)
        try:
            child_network = retented_data[option_value]['network']
        except:
            child_network = NetworkFormset(prefix = "node_%s_nr" % option_value,
                                           queryset = slices_models.NetworkRequest.objects.none())
        
        rendered_child_network = ""
        for c_form in child_network:
            rendered_child_network += c_form.as_p()

        try:
            child_cpu = retented_data[option_value]['cpu']
        except:
            child_cpu = slices_forms.CPURequestForm(prefix = "node_%s_c" % option_value).as_p()

        try:
            child_storage = retented_data[option_value]['storage']
        except:
            child_storage = slices_forms.StorageRequestForm(prefix = "node_%s_s" % option_value).as_p()

        try:
            child_memory = retented_data[option_value]['memory']
        except:            
            child_memory = slices_forms.MemoryRequestForm(prefix = "node_%s_m" % option_value).as_p()

        return [child_cpu, child_storage, child_memory, child_network, rendered_child_network]
