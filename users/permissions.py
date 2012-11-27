import inspect, functools

from .models import User, AuthToken, Group, Roles


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
    def __get__(self, instance, cls):
        if instance is not None:
            caller = instance
        elif cls is not None:
            caller = cls
        else: 
            raise TypeError('WTF are you doing dude?')
        def call(user, perm):
            return getattr(self, perm)(caller, user)
        for func in inspect.getmembers(type(self), predicate=inspect.ismethod):
            if func[1].im_class is not type(self):
                # aggregated methods
                setattr(call, func[0], functools.partial(func[1], caller))
            else:
                # self methods
                setattr(call, func[0], functools.partial(func[1], self, caller))
        return call
    
    def _aggregate(self, caller, perm):
        """ Aggregates cls methods to self class"""
        for method in inspect.getmembers(perm, predicate=inspect.ismethod):
            if not method[0].startswith('_'):
                setattr(type(self), method[0], method[1])


class ReadOnlyPermission(Permission):
    def view(self, caller, user):
        return True


class UserPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        if inspect.isclass(caller):
            return True
        return caller == user
    
    def change(self, caller, user):
        return self.add(caller, user)
    
    def delete(self, caller, user):
        return self.add(caller, user)


class RolesPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        if inspect.isclass(caller):
            return user.has_roles(('admin',))
        return caller.group.has_role(user, 'admin')
    
    def change(self, caller, user):
        return self.add(caller, user)
    
    def delete(self, caller, user):
        return self.add(caller, user)


class GroupPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        return True
    
    def change(self, caller, user):
        if inspect.isclass(caller):
            return False
        return caller.has_role(user, 'admin')
    
    def delete(self, caller, user):
        if inspect.isclass(caller):
            return True
        else:
            return caller.has_role(user, 'admin')


User.has_permission = UserPermission()
Roles.has_permission = RolesPermission()
Group.has_permission = GroupPermission()
