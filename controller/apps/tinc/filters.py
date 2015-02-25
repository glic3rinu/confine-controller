from controller.admin.filters import MySimpleListFilter

from .helpers import get_user_tinchosts


class MyHostsListFilter(MySimpleListFilter):
    """ Filter hosts by admin according to request.user """
    title = 'hosts'
    parameter_name = 'my_hosts'
    
    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            return (
                ('True', 'My hosts'),
                ('False', 'All'),
            )
        return (
            ('True', 'My hosts'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(owner=request.user)


class MyTincAddressListFilter(MySimpleListFilter):
    """ Filter tinc address by admin according to request.user """
    title = 'tinc address'
    parameter_name = 'my_tinc_addresses'
    
    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            return (
                ('True', 'My tinc addresses'),
                ('False', 'All'),
            )
        return (
            ('True', 'My tinc addresses'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(host__pk__in=get_user_tinchosts(request.user))
