
class Facts(object):

    def __init__(self):
        self.facts = {}

    def set(self,*args):
        path = args[:-1]
        value = args[-1]
        cd = self.facts
        for i,key in enumerate(path[:-1]):
            if not key in cd or not isinstance(cd[key],dict) and i < len(path)-2:
                cd[key] = {}
            cd = cd[key]
        cd[path[-1]] = value

    def get(self,*args):
        cd = self.facts
        partial_path = []
        for key in args:
            partial_path.append(key)
            if not isinstance(cd,dict) or not key in cd:
                raise KeyError("key path %s not found" % ".".join(partial_path))
            cd = cd[key]
        return cd