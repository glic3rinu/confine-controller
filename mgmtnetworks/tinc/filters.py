from django.contrib.admin import SimpleListFilter


class MyHostsListFilter(SimpleListFilter):
    """ Filter hosts by admin according to request.user """
    title = 'Hosts'
    parameter_name = 'my_hosts'
    
    def lookups(self, request, model_admin):
        return (
            ('True', 'My Hosts'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(admin=request.user)
