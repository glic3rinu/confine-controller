from django.contrib.admin.helpers import AdminReadonlyField

from controller.admin.options import *


# Monkey-patch AdminReadonlyField in order to support help_text deffinitions
old_init = AdminReadonlyField.__init__
def __init__(self, form, field, is_first, model_admin=None):
    old_init(self, form, field, is_first, model_admin=model_admin)
    if not self.field['help_text'] and not callable(field):
        method = getattr(model_admin, field, None)
        self.field['help_text'] = getattr(method, 'help_text', '')
AdminReadonlyField.__init__ = __init__
