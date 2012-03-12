import re

def tplify(obj):
    if isinstance(obj, list):
        return tuple(obj)
    elif isinstance(obj, tuple):
        return obj
    else:
        return (obj,)    

class Differ(object):
    def __init__(self, *implementations):
        self.implementations = implementations
    
    
    def __call__(self, *args, **kw):
        return self.diff(*args, **kw)
    
    def diff(self, expected, actual, options={}, path=""):
        if not options and actual == expected:
            return []
        for impl_class in self.implementations:
            if impl_class.can_diff(actual):
                impl_options = options
                if isinstance(options, dict):
                    impl_options = ()
                    for pattern, opts in options.iteritems():
                        if re.match(pattern, path):
                            impl_options += tplify(options)
                impl = impl_class(self, tplify(impl_options), path)
                return impl.get_diffs(expected, actual)
        raise Exception("No diff implementation found for %r" %
                actual)
        
            
        