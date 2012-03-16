from . import implementations as impl

class Differ(object):
    def __init__(self, *implementations):
        self.implementations = implementations
    
    
    def __call__(self, *args, **kw):
        return self.diff(*args, **kw)
    
    def diff(self, expected, actual, options={}, path=[]):
        if not options and actual == expected:
            return []
        if hasattr(actual, '__diff_implementation__'):
            return actual.__diff_implementation__(self, options, path).get_diffs(expected, actual)
        for impl_class in self.implementations:
            if impl_class.can_diff(actual):
                return impl_class(self, options, path).get_diffs(expected, actual)
        raise Exception("No diff implementation found for %r" % (actual,))
        
            



def make_differ(*implementations):
    """Generate a fancy differ with extra implementations"""
    return Differ(
                    impl.DiffPrimitives,
                    impl.DiffNumbers,
                    impl.DiffText,
                    impl.DiffLists,
                    impl.DiffDicts,
                    *implementations
            )