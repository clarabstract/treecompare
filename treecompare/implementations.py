from __future__ import absolute_import

from contextlib import contextmanager
import re

from .difference import Difference

class ImplementationBase(object):
    def __init__(self, differ, options, path):
        self.differ = differ
        if isinstance(options, (dict, tuple)):
            self.differ_options = options
        else:
            self.differ_options = (options,)
        self.path = path


    @property
    def options(self):
        options = self.differ_options
        if isinstance(self.differ_options, dict):
            options = ()
            for pattern, opts in self.differ_options.iteritems():
                if re.match(pattern, self.path):
                    options += opts if isinstance(opts, tuple) else (opts,)
        return options
    
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
    
    def different(self, message_or_path, message=None):
        """
        Call as either:
            self.different(message)         returns a difference for the current node
            self.different(path, message)   returns a difference added to the current path
        """
        if message is None:
            message = message_or_path
            path = self.path
        else:
            path = self.path + message_or_path
        return [Difference(path, message)]

    def diff_child(self, new_path, expected, actual):
        return self.differ.diff(expected, actual, self.differ_options, self.path + new_path)

    def continue_diff(self, expected, actual):
        return self.differ.diff(expected, actual, self.differ_options, self.path)

    @contextmanager
    def diffing_child(self, new_path):
        yield self.__class__(self.differ, self.differ_options, self.path+new_path)
    
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

    def diff(self, expected, actual):
        diffs = []
        for i, obj in enumerate(expected):
            with self.diffing_child("[%s]" % i) as child:
                if len(actual) < (i+1):
                    diffs += self.different("expected %r, got nothing" % obj)
                else:
                    if 'assert_includes' in child.options:
                        if not any([not child.continue_diff(possible, actual[i]) for possible in obj]):
                            diffs += child.different("%r not included in %r" %(actual[i], obj))

                    else:
                        diffs += child.continue_diff(obj, actual[i])
        return diffs



class DiffDicts(ImplementationBase):
    diffs_types = dict
    def diff(self, expected, actual):
        diffs = []
        for key, obj in expected.iteritems():
            with self.diffing_child("[%r]" % key) as child:
                if key not in actual:
                    diffs += self.different("expected %r, got nothing" % obj)
                else:
                    if 'assert_includes' in child.options:
                        if not any([not child.continue_diff(possible, actual[key]) for possible in obj]):
                            diffs += child.different("%r not included in %r" %(actual[key], obj))

                    else:
                        diffs += child.continue_diff(obj, actual[key])
        return diffs




