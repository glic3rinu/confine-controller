class FuncAttrWrapper():
    """ wrapper class for access function attributes on django templates """
    def __init__(self, actions):
        for attr in dir(actions):
            if not attr.startswith('_'):
                setattr(self, attr, getattr(actions, attr))


class SortableField(object):
    """ Helper class for easier inline sorting """
    ASC = 'ascending'
    DESC = 'descending'
    
    def __init__(self, name, order_value, sortable=True, is_sorted=False):
        self.name = name
        self.order_value = str(order_value)
        self.sortable = sortable
        self.is_sorted = is_sorted

    def order_type(self):
        return self.DESC if self.is_reverse() else self.ASC

    def sort_by(self):
        return "-%s" % self.name if self.is_reverse() else self.name

    def update(self, order_value):
        self.is_sorted = True
        self.order_value = order_value

    def is_reverse(self):
        return self.order_value.startswith('-')

    def order(self):
        if self.is_sorted:
            return self.reverse_order_value()
        return self.order_value

    def reverse_order_value(self):
        if self.is_reverse():
             return self.order_value.lstrip('-')
        else:
            return "-%s" % self.order_value

    def serialize(self):
        dump = self.__dict__
        dump.update({
            'order_type': self.order_type(),
            'sort_by': self.sort_by(),
            'is_reverse': self.is_reverse(),
            'order': self.order(),
            'reverse_order_value': self.reverse_order_value(),
        })
        return dump
