class PsTree(object):
    def __repr__(self):
        return "roots: %s, tree: %s" % (str(self.roots), str(self.tree))
    
    def __init__(self):
        self.roots = []
        self.attributes = dict()
        self.tree = dict()
    
    def insert(self, pid, ppid, worked, waited):
        self.attributes[pid] = {
            'worked': worked,
            'waited': waited
        }
        if ppid not in self.tree:
            self.tree[ppid] = [pid]
            if ppid not in self.attributes:
                self.roots.append(ppid)
        else:
            self.tree[ppid].append(pid)
        if pid in self.roots:
            self.roots.remove(pid)
    
    def total_ticks(self, *args):
        if not self.roots:
            return None
        if not args:
            return self.total_ticks(self.tree[self.roots[0]][0])
        pid = args[0]
        if pid not in self.tree:
            return self.attributes[pid]['worked'] + self.attributes[pid]['waited']
        child_ticks = 0
        for cpid in self.tree[pid]:
            child_ticks += self.total_ticks(cpid)
        child_ticks = max(self.attributes[pid]['waited'], child_ticks)
        return self.attributes[pid]['worked'] + child_ticks
