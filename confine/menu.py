from django.core.urlresolvers import reverse
from admin_tools.menu import items, Menu
import confine.settings



class CustomMenu(Menu):
    """
    Custom Menu for ucp admin site.
    """
    def __init__(self, **kwargs):
        Menu.__init__(self, **kwargs)
        self.children += [
            items.MenuItem('Dashboard', reverse('admin:index')),
            items.Bookmarks(),]
            
        self.children.append(items.AppList(
            'Nodes',
            models=('nodes.*',)))
        
        self.children.append(items.AppList(
            'Slices',
            models=('slices.*', )))

        self.children.append(items.AppList(
            'Administration',
            models=('django.contrib.auth.*',)))



