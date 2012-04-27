
def activate_user(modeladmin, request, queryset):
    for item in queryset:
        user = item.user
        user.is_active = True
        user.save()
        item.delete()

def delete_user(modeladmin, request, queryset):
    for item in queryset:
        user = item.user
        user.delete()
        item.delete()
