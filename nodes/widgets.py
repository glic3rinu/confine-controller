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
    This is a custom widget to display a list of nodes with hierarchical
    forms inside, with storagerequest, cpurequest, memoryrequest, and interfaces
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

            child_cpu, child_storage, child_memory, child_ii, rendered_child_ii, child_pubi, rendered_child_pubi, child_privi, rendered_child_privi = self.get_childs(option_value)
 
            output.append(u"""
            %s
            %s
            %s
            <li>
            <label%s>%s %s</label>

            <div id=\"ii_%s\" class=\"ii_%s node_extra\">
            <a href=\"#\" onclick=\"add_new_form_element('id_node_%s_nr-TOTAL_FORMS','ii_%s'); return false;\">New Isolated Interface</a>
            <h4>Isolated Interfaces</h4>
            <div>
            <h5>Isolated Interface</h5>
            %s
            </div>
            </div>

            <div id=\"pubi_%s\" class=\"pubi_%s node_extra\">
            <a href=\"#\" onclick=\"add_new_form_element('id_node_%s_nr-TOTAL_FORMS','pubi_%s'); return false;\">New Public Interface</a>
            <h4>Public Interfaces</h4>
            <div>
            <h5>Public Interface</h5>
            %s
            </div>
            </div>

            <div id=\"privi_%s\" class=\"privi_%s node_extra\">
            <a href=\"#\" onclick=\"add_new_form_element('id_node_%s_nr-TOTAL_FORMS','privi_%s'); return false;\">New Private Interface</a>
            <h4>Private Interfaces</h4>
            <div>
            <h5>Private Interface</h5>
            %s
            </div>
            </div>

            
            <div class=\"cpu_%s node_extra\">
            <h4>CPU Requests</h4>
            %s
            </div>
            <div class=\"storage_%s node_extra\">
            <h4>Storage Requests</h4>
            %s
            </div>
            <div class=\"memory_%s node_extra\">
            <h4>Memory Requests</h4>
            %s
            </div>
            </li>
            """ % (
                              child_ii.management_form.__unicode__(),
                              child_pubi.management_form.__unicode__(),
                              child_privi.management_form.__unicode__(),
                              label_for,
                              rendered_cb,
                              option_label,
                              option_value,
                              option_value,
                              option_value,
                              option_value,
                              rendered_child_ii,
                              option_value,
                              option_value,
                              option_value,
                              option_value,
                              rendered_child_pubi,
                              option_value,
                              option_value,
                              option_value,
                              option_value,
                              rendered_child_privi,
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
        IsolatedifaceFormset = modelformset_factory(slices_models.IsolatedIface,
                                              extra = 1,
                                              form = slices_forms.IsolatedIfaceForm)
        try:
            child_isolatediface = retented_data[option_value]['isolatediface']
        except:
            child_isolatediface = IsolatedifaceFormset(prefix = "node_%s_ii" % option_value,
                                           queryset = slices_models.IsolatedIface.objects.none())
        
        rendered_child_isolatediface = ""
        for c_form in child_isolatediface:
            rendered_child_isolatediface += c_form.as_p()

        
        PublicIfaceFormset = modelformset_factory(slices_models.PublicIface,
                                              extra = 1,
                                              form = slices_forms.PublicIfaceForm)
        try:
            child_PublicIface = retented_data[option_value]['publiciface']
        except:
            child_PublicIface = PublicIfaceFormset(prefix = "node_%s_pubi" % option_value,
                                           queryset = slices_models.PublicIface.objects.none())
        
        rendered_child_PublicIface = ""
        for c_form in child_PublicIface:
            rendered_child_PublicIface += c_form.as_p()
            

        PrivateIfaceFormset = modelformset_factory(slices_models.PrivateIface,
                                              extra = 1,
                                              form = slices_forms.PrivateIfaceForm)
        try:
            child_PrivateIface = retented_data[option_value]['privateiface']
        except:
            child_PrivateIface = PrivateIfaceFormset(prefix = "node_%s_privi" % option_value,
                                           queryset = slices_models.PrivateIface.objects.none())
        
        rendered_child_PrivateIface = ""
        for c_form in child_PrivateIface:
            rendered_child_PrivateIface += c_form.as_p()

            
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

        return [child_cpu, child_storage, child_memory, child_isolatediface, rendered_child_isolatediface, child_PublicIface, rendered_child_PublicIface, child_PrivateIface, rendered_child_PrivateIface]
