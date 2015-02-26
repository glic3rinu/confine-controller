from django.contrib.admin import SimpleListFilter
from django.utils.encoding import force_text


class MyNodesListFilter(SimpleListFilter):
    """ Filter Nodes by group according to request.user """
    title = 'Nodes'
    parameter_name = 'my_nodes'
    
    def lookups(self, request, model_admin):
        return (
            ('True', 'My Nodes'),
            ('False', 'All'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(group__users=request.user)
    
    def choices(self, cl):
        """ Enable default selection different than All """
        for lookup, title in self.lookup_choices:
            # workaround for NodeListAdmin
            selected = self.value() == force_text(lookup)
            if not selected and title == 'All' and self.value() is None:
                selected = True
            # end of workaround
            yield {
                'selected': selected,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }


class NodesPub4IfaceListFilter(SimpleListFilter):
    """Filter nodes which have support for public IPv4 sliver interfaces."""
    title = 'public IPv4 iface support'
    parameter_name = 'pub4iface'
    
    def lookups(self, request, model_admin):
        return (
            ('True', 'Nodes that support public IPv4 ifaces'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(
                resources__name='pub_ipv4').filter(
                resources__max_req__gt=0
            )
