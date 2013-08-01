from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe


class LinkedRelatedFieldWidgetWrapper(RelatedFieldWidgetWrapper):
    def render(self, name, value, *args, **kwargs):
        opts = self.rel.to._meta
        info = (opts.app_label, opts.object_name.lower())
        self.widget.choices = self.choices
        output = [self.widget.render(name, value, *args, **kwargs)]
        link = ''
        if value:
            link = reverse("admin:%s_%s_change" % info, current_app=self.admin_site.name, args=[value])
            link = '<p class="file-upload">Current: <a href="%s">%s</a><br>' % (link, link)
        return mark_safe(link + ''.join(output))
