from django.contrib.admin import SimpleListFilter
from django.utils.encoding import force_text


class MyHostsListFilter(SimpleListFilter):
    """ Filter hosts by admin according to request.user """
    title = 'Hosts'
    parameter_name = 'my_hosts'
    
    def lookups(self, request, model_admin):
        return (
            ('True', 'My Hosts'),
            ('False', 'All'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(owner=request.user)
    
    def choices(self, cl):
        # TODO make this reusable in a basefilterclass
        """ Enable default selection different than All """
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == force_text(lookup),
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

