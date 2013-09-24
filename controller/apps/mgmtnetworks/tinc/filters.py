from controller.admin.filters import MySimpleListFilter


class MyHostsListFilter(MySimpleListFilter):
    """ Filter hosts by admin according to request.user """
    title = 'Hosts'
    parameter_name = 'my_hosts'
    
    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            return (
                ('True', 'My Hosts'),
                ('False', 'All'),
            )
        return (
            ('True', 'My Hosts'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(owner=request.user)
