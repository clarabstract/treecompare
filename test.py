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
should be considered equal, but the the following differences were reported:
%s\n""" % ( pprint.pformat(expected), 
            pprint.pformat(actual), 
            '\n'.join([" - %s" % d for d in diffs]))
            self.fail(message)
    
    def assertDifferent(self, expected_diffs, expected, actual, options={}):
        diffs = diff(expected, actual, options)
        #Let's get meta!
        diff_diffs = diff([Difference(path, message) for path, message in expected_diffs.iteritems()], diffs)
        if diff_diffs:
            message = """Expected object
%s
and actual object
%s
failed to produce the expected differences:
%s\n""" % ( pprint.pformat(expected),
            pprint.pformat(actual),
            '\n'.join([" - %s" % d for d in diff_diffs]))
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
    
    def test_unequal_trees(self):
        self.assertDifferent({
                '["b"][0]["y"]': "expected 11, got nothing",
                '["b"][0]["z"]': "unexpected value: 11",
            },
            dict(a=1, b=[dict(x=10, y=11)]),
            dict(a=1, b=[dict(x=10, z=11)])
        )

    def test_unequal_trees_longer_expected(self):
        self.assertDifferent({
                '["b"][0]["z"]': "expected 12, got nothing"
            },
            dict(a=1, b=[dict(x=10, y=11, z=12)]),
            dict(a=1, b=[dict(x=10, y=11)])
        )

    def test_unequal_trees_longer_actual(self):
        self.assertDifferent({
                '["b"][0]["z"]': "unexpected value: 12"
            },
            dict(a=1, b=[dict(x=10, y=11)]),
            dict(a=1, b=[dict(x=10, y=11, z=12)])
        )


    def test_equal_lists(self):
        
        self.assertNotDifferent(
            [(1,2,'3'), dict(foo=3)],
            [(1,2,'3'), dict(foo=3)]
        )

    def test_unequal_lists(self):
        
        self.assertDifferent({
                '[1]': "expected 'b', got 'g'"
            },
            ["a", "g", "c"],
            ["a", "b", "c"]
        )
    def test_unequal_lists_longer_expected(self):
        
        self.assertDifferent({
                '[1]': "expected 'd', got nothing"
            },
            ["a", "b", "c"],
            ["a", "b", "c", "d"]
        )
    def test_unequal_lists_longer_actual(self):
        
        self.assertDifferent({
                '[1]': "unexpected value: 'd'"
            },
            ["a", "b", "c", "d"],
            ["a", "b", "c"]
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
              '[2][1]': "expected 2, got 3",
              '[2][2]': "expected 3, got 2"  
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
                r'^\[1\]': "assert_includes"
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
                '[1]': "'pear' not included in ('apple', 'orange', 'watermelon')"
            },
            options = {
                r'^\[1\]$': 'assert_includes'
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
                r'^\[1\]\["whatever"\]': ('assert_includes', 'ignore_key')
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
    
    def test_assert_includes_option_with_ignore_case(self):
        self.assertNotDifferent(
            options = {
                r'^\[1\]\[\'whatever\'\]': ('assert_includes', 'ignore_case')
            },
            expected = [
                'ninjas',
                dict(whatever=('apple', 'ORANGE', 'watermelon')),
                'orchards'
            ],
            actual = [
                'ninjas',
                dict(whatever='orAnGe'),
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
              '[pineapple]': "expected something, got nothing"
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
    unittest.main(verbosity=2)
