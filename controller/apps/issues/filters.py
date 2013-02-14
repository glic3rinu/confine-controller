from controller.admin.filters import MySimpleListFilter


class MyTicketsListFilter(MySimpleListFilter):
    """ Filter tickets by created_by according to request.user """
    title = 'Tickets'
    parameter_name = 'my_tickets'
    
    def lookups(self, request, model_admin):
        return (
            ('True', 'My Tickets'),
            ('False', 'All'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            if request.user.is_superuser:
                return queryset.filter(owner=request.user)
            return queryset.filter(created_by=request.user)
