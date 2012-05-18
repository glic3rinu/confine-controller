from django.forms import CheckboxSelectMultiple, CheckboxInput
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.forms.widgets import flatatt
from itertools import chain
from django.utils.html import escape, conditional_escape

from nodes import models

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

            childs = models.Node.objects.get(id = option_value).interface_set.all()
            children = [u'<ul class="node_interfaces interfaces_%s">' % option_value]
            for child in childs:
                children_attrs = {
                    'id': u'id_interfaces_%i' % child.id,
                    'name': u'interfaces'
                    }
                children.append(u'<li><label>%s %s</label></li>' %(
                    child.name,
                    CheckboxInput(children_attrs).render(u"interfaces", child.id)))
            children.append(u'</ul>')
            
            output.append(u'<li><label%s>%s %s</label>%s</li>' % (label_for, rendered_cb, option_label, u'\n'.join(children)))
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))
