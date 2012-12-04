from django.contrib.admin import SimpleListFilter


class MyNodesListFilter(SimpleListFilter):
    """ Filter slices by group according to request.user """
    title = 'Nodes'
    parameter_name = 'my_nodes'
    
    def lookups(self, request, model_admin):
        return (
            ('True', 'My Nodes'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(group__user=request.user)
