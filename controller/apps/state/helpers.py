from controller.models.utils import get_field_value

def break_headers(header):
    header = header.replace(', <', ',\n                 <')
    return header.replace(' (', '\n                  (')


def break_lines(text, every=150):
    result = []
    for line in text.split('\n'):
        every = text.find('\\n')
        if every != -1:
            distance = line.find(':') + 3
            line = line.replace('\\n', '\n' + ' '*distance)
        result.append(line)
    return '\n'.join(result)


def conditional_colored(field_name, colours, description=''):
    def colored_field(obj, field=field_name, colors=colours):
        value = get_field_value(obj, field)
        color = colors.get(field, "black")
        if value == 0:
            return value
        return '<span style="color:%s">%s</span>' % (color, value)
    colored_field.allow_tags = True
    if description:
        colored_field.short_description = description
    else:
        colored_field.short_description = field_name
    return colored_field

