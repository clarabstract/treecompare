import unittest

from treecompare import diff
from treecompare.difference import Difference
import pprint

class TestTreeCompare(unittest.TestCase):
    
    def assertNotDifferent(self, expected, actual, options={}):
        diffs = diff(expected, actual, options)
        if diffs:
            message = """Expected object
%s
and actual object
%s
should be considered equal, but the the following differences were reported:"
%s\n""" % (pprint.pformat(expected), pprint.pformat(actual), '\n'.join(diffs))
            self.fail(message)
    
    def assertDifferent(self, expected_diffs, expected, actual, options={}):
        diffs = diff(expected, actual, options)
        #Let's get meta!
        diff_diffs = diff([Difference(path, message) for path, message in expected_diffs.iteritems()], diffs,)
        if diff_diffs:
            message = """Expected object
%s
and actual object
%s
failed to produce the expected differences:"
%s\n""" % (pprint.pformat(expected), pprint.pformat(actual), '\n'.join(diff_diffs))
            self.fail(message)

    def test_trivial_equal(self):
        self.assertNotDifferent(42,42)
        
    def test_equal_trees(self):
        
        self.assertNotDifferent({
            'foo': ['bar', 3L, 1.2],
            'bipples': None
        },{
            'foo': ['bar', 3L, 1.2],
            'bipples': None
        })
    
    def test_equal_lists(self):
        
        self.assertNotDifferent(
            [(1,2,'3'), dict(foo=3)],
            [(1,2,'3'), dict(foo=3)]
        )
        
    def test_equal_with_different_type(self):
        self.assertNotDifferent(
            (1, "fafa"),
            (1L, u"fafa")
        )
    
    def test_ignore_key_option(self):
        self.assertNotDifferent(
            options = {
                r'^\[\d+\]$' : 'ignore_key'
            },
            expected=['apples', 'oranges', 'starfruit', [1,2,3]],
            actual=  ['oranges', 'starfruit', [1,2,3],  'apples'],
        )
        
        self.assertDifferent(
            {
              '[2][1]': 'expected 2, got 3',
              '[2][2]': 'expected 3, got 2'  
            },
            options = {
                r'^\[\d+\]$' : 'ignore_key'
            },
            expected=['apples', 'oranges', 'starfruit', [1,2,3]],
            actual=  ['oranges', 'starfruit', [1,3,2],  'apples'],
        )
        
    
    def test_assert_includes_option(self):
        self.assertNotDifferent(
            options = {
                r'^\[2\]': 'assert_includes'
            },
            expected = [
                'ninjas',
                ('apple', 'orange', 'watermelon'),
                'orchards'
            ],
            actual = [
                'ninjas',
                'orange',
                'orchards'
            ]
        )
        
    def test_assert_includes_option_failure(self):
        self.assertDifferent(
            {
                '[1]': '"pear" not included in ("apple", "orange", "watermelon")'
            },
            options = {
                r'^\[2\]': 'assert_includes'
            },
            expected = [
                'ninjas',
                ('apple', 'orange', 'watermelon'),
                'orchards'
            ],
            actual = [
                'ninjas',
                'pear',
                'orchards'
            ]
        )
    
    def test_assert_includes_option_with_ignore_key(self):
        self.assertNotDifferent(
            options = {
                r'^\[2\]\[whatever\]': ('assert_includes', 'ignore_key')
            },
            expected = [
                'ninjas',
                dict(whatever=('apple', 'orange', 'watermelon')),
                'orchards'
            ],
            actual = [
                'ninjas',
                dict(whatever='orange'),
                'orchards'
            ]
        )
    
    
    def test_ignore_option(self):
        self.assertNotDifferent(
            options = {
                r'\[papaya\]': 'ignore'
            },
            expected = {
                'banana': 'republic',
            },
            actual = {
                'bana': 'republic',
                'papaya': 'republic'
            }
        )
    def test_ignore_option_failure(self):
        self.assertDifferent(
            {
              '[pineapple]': 'expected something, got nothing'  
            },
            options = {
                r'\[(pineapple|papaya)\]': 'ignore'
            },
            expected = {
                'banana': 'republic',
                'pineapple': 'commonwealth',
            },
            actual = {
                'bana': 'republic',
                'papaya': 'republic'
            }
        )
    
        
if __name__ == '__main__':
    unittest.main()
