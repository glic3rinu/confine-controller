def has_permission(action, user):
    """
    This function will return True if user has enought permissions to perform
    action to the given object.
    action is formed as following:
    objecttype_objectid_action
    """
    if user.is_superuser:
        return True
    objecttype, objectid, action = action.split("_")
