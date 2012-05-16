import itertools

def has_permission(action, user):
    """
    This function will return True if user has enought permissions to perform
    action to the given object.
    action is formed as following:
    objecttype_objectid_action
    """
    if user.is_superuser:
        return True
    objecttype, objectid, perm = action.split("_")
    user_perms = map(lambda a: list(a.permissions.filter(object_id = objectid,
                                                              content_type__model = objecttype.lower(),
                                                              permission = perm.upper())),
                     
                     
                     user.roles.all())
    perms = list(itertools.chain.from_iterable(user_perms))
    if len(perms):
        return True
    return False
