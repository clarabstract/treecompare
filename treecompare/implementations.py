from __future__ import absolute_import, with_statement

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
                if re.search(pattern, self.path_string):
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
    
    def get_diffs(self, expected, actual):
        """
        Calls out to self.diff(), performaing some global processing:
            - always return a list (handle None-return)
            - check for 'ignore' option
            - handle 'assert_includes' option
        """
        #print self.path_string, self.options, expected, actual
        if 'ignore' in self.options:
            return []
        if 'assert_includes' in self.options and isinstance(expected, tuple):
            if any([self.matches(option, actual) for i, option in enumerate(expected)]):
                # At least one match, no diff!
                return []
            else:
                return self.different("%r not included in %r" % (actual,expected))

        return self.diff(expected, actual) or []

    
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
        return self.differ.diff(expected, actual, self.differ_options, self.path + [new_path])

    def continue_diff(self, expected, actual):
        return self.differ.diff(expected, actual, self.differ_options, self.path)

    def matches(self, expected, actual):
        return not self.continue_diff(expected, actual)

    def path_context(self, new_path):
        return self.__class__(self.differ, self.differ_options, self.path+[new_path])

    @contextmanager
    def diffing_child(self, new_path):
        yield self.path_context(new_path)

    @property
    def path_string(self):
        return ''.join(self.path)
    
class DiffPrimitives(ImplementationBase):
    diffs_types = (type(None), bool)
    
    def diff(self, expected, actual):
        if expected != actual:
            return self.different("expected %r, got %r" % (expected, actual))

class DiffNumbers(DiffPrimitives):
    diffs_types = (int, long, float)
    

class DiffText(DiffPrimitives):
    NDIFF_THRESHOLD = 32
    diffs_types = basestring
    def diff(self, expected, actual):
        if not isinstance(expected, basestring):
            return self.different("expected %r, got %r" % (expected, actual))
        expected_comparable, actual_comparable = expected, actual
        if 'ignore_case' in self.options:
            expected_comparable, actual_comparable = expected_comparable.lower(), actual_comparable.lower()
        if 'ignore_spacing' in self.options:
            expected_comparable, actual_comparable = self.normalize_spacing(expected_comparable), self.normalize_spacing(actual_comparable)
        elif 'ignore_line_whitespace' in self.options:
            expected_comparable, actual_comparable = self.normalize_line_spacing(expected_comparable), self.normalize_line_spacing(actual_comparable)
        if expected_comparable != actual_comparable:
            try:
                import difflib
            except ImportError:
                difflib = False
            else:
                if difflib and len(expected) + len(actual) > self.NDIFF_THRESHOLD:
                    diffs = difflib.ndiff(expected_comparable.splitlines(True)+[], actual_comparable.splitlines(True)+[],)
                    return self.different("expected %r, got %r - diff:\n%s" % (expected, actual, '\n'.join(diffs)))
                else:
                    return self.different("expected %r, got %r" % (expected, actual))
    
    def normalize_spacing(self, text):
        normalized = re.sub(r'([^\w])', ' \\1 ', text)
        normalized = re.sub(r'[\s\n\r]+', ' ', normalized)
        return normalized

    def normalize_line_spacing(self, text):
        # Remove CRs
        normalized = re.sub(r'\r', '', text)
        # Remove leading/trailing whitespace
        normalized = re.sub(r'\s*\n\s*', '\n', normalized)
        # Remove leading/trailing newlines
        normalized = re.sub(r'^\n|\n$', '', normalized)
        return normalized


class ChildDiffingMixing(object):
    def path_and_child(self, diffable):
        """For each child item, yield the the child path and child object"""
        raise NotImplementedError

    
    def split_keyed_unkeyed(self, children):
        """
        Turn given children into two lists:
            - the first is the original child list, with nodes for
              whom ignore_key applies replaced with True
            - the second is the list of all nodes for whom ignore_key
              applies
        (i.e. the first list has all items from the second list 
        replaced with True)
        """
        unkeyed = []
        def get_keyd(path_and_child):
            path, child = path_and_child
            with self.diffing_child(path) as node:
                if 'ignore_key' in node.options:
                    unkeyed.append((path, child))
                    return False
                else:
                    return path, child


        return filter(None, map(get_keyd, children)), unkeyed
    
    def filtered_path_and_child(self, diffable):
        for path, child in self.path_and_child(diffable):
            with self.diffing_child(path) as node:
                if 'ignore' not in node.options:
                    yield path, child

    def diff(self, expected, actual):
        diffs = []
        if not isinstance(actual, type(expected)):
            return self.different("expected %r, got %r" % (expected, actual))
        expected_children = list(self.filtered_path_and_child(expected))
        actual_children = list(self.filtered_path_and_child(actual))

        keyed_expected, unkeyed_expected = self.split_keyed_unkeyed(expected_children)
        keyed_actual, unkeyed_actual = self.split_keyed_unkeyed(actual_children)
        # First check keyed elements in lockstep, based on actual:
        # (unkeyed elements are all 'True', so they'll never be different)


        expected_lookup = dict(keyed_expected)
        for path, actual_object in keyed_actual:
            with self.diffing_child(path) as child:
                if path in expected_lookup:
                    diffs += child.continue_diff(expected_lookup[path], actual_object)
                else:
                    diffs += child.different("unexpected value: %r" % actual_object)

        # Now check unekeyed elements using broad search...
        # Attempt to match each actual to each expected, keeping track
        # of unmatched elements
        unmatched_expected = dict(unkeyed_expected)
        def no_match(path_and_child):
            path, actual_child = path_and_child
            with self.diffing_child(path) as node:
                for path, expected_child in unmatched_expected.iteritems():
                    if node.matches(expected_child, actual_child):
                        del unmatched_expected[path]
                        return False
                return True
        unmatched_actual = filter(no_match, unkeyed_actual)
         
        # Now for each unmatched element we try to get the 'deepest'
        # difference and report that (presumably it's the more useful
        # one)
        for path, ua in unmatched_actual:
            with self.diffing_child(path) as node:
                if unmatched_expected:
                    diffs_to_all = [(p, node.continue_diff(ue, ua)) for p, ue in unmatched_expected.iteritems()]
                    bdf, best_diff = max(diffs_to_all, key= lambda diffs: sum([len(d.path) for d in diffs[1]]))
                    del unmatched_expected[bdf]
                    diffs += best_diff
                else:
                    diffs += node.different("unexpected value: %r" % ua)

        # And finally, add all missing expectations:
        for path in set(unmatched_expected.keys() + dict(keyed_expected).keys()) - set(dict(unmatched_actual + keyed_actual).keys()):
            with self.diffing_child(path) as node:
                expected_object = dict(expected_children)[path]
                diffs += node.different("expected %r, got nothing" % (expected_object,))
            

        return diffs




class DiffLists(ChildDiffingMixing, ImplementationBase):
    diffs_types = (list, tuple)

    def path_and_child(self, diffable):
        for i, child in enumerate(diffable):
            yield "[%r]" % i, child


class DiffDicts(ChildDiffingMixing, ImplementationBase):
    diffs_types = dict

    def path_and_child(self, diffable):
        for key, child in diffable.iteritems():
            yield "[%r]" % key, child
