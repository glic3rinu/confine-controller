
def get_field(obj, field_name):
    names = field_name.split('__')
    rel = getattr(obj, names.pop())
    for name in names:
        rel = getattr(rel, name)
    return rel

