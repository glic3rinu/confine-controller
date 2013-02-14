from django.contrib.admin import SimpleListFilter
from django.utils.encoding import force_text


class MySimpleListFilter(SimpleListFilter):
    """ Filter slices by group according to request.user """
    def choices(self, cl):
        """ Enable default selection different than All """
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == force_text(lookup),
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }
