from __future__ import absolute_import

from .difference import Difference

class ImplementationBase(object):
    def __init__(self, differ, options, path):
        self.differ = differ
        self.options = options
        self.path = path
    
    @classmethod
    def can_diff(cls, object):
        if not hasattr(cls, 'diffs_types'):
            raise NotImplementedError("""Either provide the 'diffs_types'
            class-attribute, or implement your own 'can_diff' method.""")
        return isinstance(object, cls.diffs_types)
    
    def diff(self, expected, actual):
        raise NotImplementedError
    
    def get_diffs(self, *args, **kw):
        """Just like diff(), except always returns a list"""
        return self.diff(*args, **kw) or []
    
    def different(self, message):
        return [Difference(self.path, message)]
    
class DiffPrimitives(ImplementationBase):
    diffs_types = (type(None), bool)
    
    def diff(self, expected, actual):
        if expected != actual:
            return self.different("expected %r, got %r" % (expected, actual))

class DiffNumbers(DiffPrimitives):
    diffs_types = (int, long, float)
    

class DiffText(DiffPrimitives):
    diffs_types = basestring
    
class DiffLists(ImplementationBase):
    diffs_types = list

