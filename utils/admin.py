from django.contrib import admin

def insert_inline(model, inline, head=False):
    """ Insert model inline into an existing model_admin """
    model_admin = admin.site._registry[model]
    if not model_admin.inlines: 
        # Avoid inlines defined on parent class be shared between subclasses
        # Seems that if we use tuples they are lost in some conditions like changing the tuple in modeladmin.__init__ 
        model_admin.__class__.inlines = []
    if head:
        model_admin.inlines = [inline] + model_admin.inlines
    else:
        model_admin.inlines.append(inline)
        
        
def insert_list_filter(model, filter):
    model_admin = admin.site._registry[model]
    if not model_admin.list_filter: model_admin.__class__.list_filter = []
    model_admin.list_filter += (filter,)

def insert_list_display(model, field):
    model_admin = admin.site._registry[model]
    if not model_admin.list_display: model_admin.__class__.list_display = []
    model_admin.list_display += (field,)    
