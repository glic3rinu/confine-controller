from django.core.exceptions import ValidationError

from controller.core.validators import validate_prop_name

from . import exceptions


def validate_properties(obj, attrs, source):
    """ Check if properties has been provided and all has valid names. """
    properties = attrs.get(source, None)
    if properties is None:
       raise exceptions.ParseError(detail='Properties is a mandatory field.')
    else:
        # check properties name matchs regular expresion!
        for prop in properties:
            try:
                validate_prop_name(prop.name)
            except ValidationError as e:
                raise exceptions.ParseError(detail='; '.join(e.messages))
    return attrs
