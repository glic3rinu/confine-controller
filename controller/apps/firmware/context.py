import os, re


class Context(object):
    """
    Registration class used for register arbitrary methods available during
    build uci and file evaluation
    """
    def __init__(self):
        self._registry = {}
    
    def register(self, **kwargs):
        self._registry.update(**kwargs)
    
    def unregister(self, obj):
        if obj in self._registry:
            self._registry.pop(obj)
    
    def get(self):
        return self._registry

context = Context()


# Define some context methods used for firmware evaluation

def get_ssh_pubkey(user):
    file_name = os.path.expanduser('~%s/.ssh/id_rsa.pub' % user)
    try:
        with file(file_name) as pubkey_file:
            pubkey = pubkey_file.read().strip()
    except:
        pubkey = ''
    return pubkey


# Register some methods
context.register(get_ssh_pubkey=get_ssh_pubkey)
context.register(re=re)
