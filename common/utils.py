def get_field_value(obj, field_name):
    names = field_name.split('__')
    rel = getattr(obj, names.pop(0))
    for name in names:
        rel = getattr(rel, name)
    return rel

