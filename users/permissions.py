import inspect, functools


class Permission(object):
    """ 
    Base class for defining class and instance permissions.
    Enabling an intuitive interface for checking permissions:
        
        # Define permissions
        class NodePermission(Permission):
            def change(self, caller, user):
                return caller.user == user
        
        # Provide permissions
        Node.has_perm = NodePermission()
        
        # Check class permission by passing it as string
        Node.has_perm(user, 'change')
        
        # Check class permission by calling it
        Node.has_perm.change(user)
        
        # Check instance permissions
        node = Node()
        node.has_perm(user, 'change')
        node.has_perm.change(user)
    """
    def __get__(self, instance, clas):
        if instance is not None:
            caller = instance
        elif clas is not None:
            caller = clas
        else: 
            raise TypeError('WTF are you doing dude?')
        def call(user, perm):
            return getattr(self, perm)(caller, user)
        for func in inspect.getmembers(type(self), predicate=inspect.ismethod):
            setattr(call, func[0], functools.partial(func[1], self, caller))
        return call

