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
        diff_diffs = diff([Difference(path, message) for path, message in expected_diffs.iteritems()], diffs, options={r'^\[\d+\]$':'ignore_key'})
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

    def test_lists_not_equal_strings(self):
        
        self.assertDifferent({
                '': "expected 'xyz', got ('x', 'y', 'z')"
            },
            options= 'ignore_case',
            expected= "xyz",
            actual= ('x', 'y', 'z')
        )

        self.assertDifferent({
                '': "expected ('x', 'y', 'z'), got 'xyz'"
            },
            options= 'ignore_case',
            expected= ('x', 'y', 'z'),
            actual= "xyz"
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
    def test_ignore_key_option_with_dict(self):
        self.assertNotDifferent(
            options = 'ignore_key',
            expected=dict(a=1, b=2,c=3),
            actual=  dict(c=1, b=2,a=3)
        )
        
    def test_ignore_key_option_with_difference(self):
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
    def test_ignore_key_option_with_deep_difference(self):
        self.assertDifferent(
            {
              "[2][2]['a']": "expected 1, got 2",
              "[3]": "expected ('a','b','c'), got 'farkles'",
              "4": "expected 'apples', got nothing"
            },
            options = {
                r'^\[\d+\]$' : 'ignore_key'
            },
            expected=['apples', 'oranges', 'starfruit', [1,2,dict(a=1)], "farkle"],
            actual=  ['oranges', 'starfruit', [1,2,dict(a=2)],  ('a','b','c'), 'apples'],
        )

    def test_partial_ignore_key_rule(self):

        self.assertDifferent(
            {
              "[0]": "expected 'apples', got 'pineapple'",
              "[3]": "expected 'pineapple', got 'apples'"
              
            },
            options = {
                r'^\[[1-2]\]$' : 'ignore_key'
            },
            expected=['apples', 'oranges', 'starfruit', 'pineapple'],
            actual=  ['pineapple', 'starfruit', 'oranges', 'apples'],
        )


    def test_ignore_key_option_with_unexpected_values(self):
        self.assertDifferent(
            {
              '[2]': "unexpected value: 'maples'",
            },
            options ='ignore_key',
            expected=['apples', 'oranges', 'starfruit'],
            actual=  ['oranges', 'starfruit', 'maples', 'apples'],
        )
        
    def test_ignore_option_with_missing_value(self):
        self.assertDifferent(
            {
              '[2]': "expected 'poppler', got nothing",
            },
            options = {
                r'^\[\d+\]$' : 'ignore_key'
            },
            expected=['apples', 'oranges', 'poppler', 'starfruit'],
            actual=  ['oranges', 'starfruit', 'apples'],
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
            options = ('assert_includes', 'ignore_key'),
            expected = [
                'ninjas',
                'orchards',
                ('apple', 'orange', 'watermelon'),
            ],
            actual = [
                'ninjas',
                'orange',
                'orchards'
            ]
        )

    def test_assert_includes_option_with_ignore_key_in_dict(self):
        self.assertNotDifferent(
            options = {
                r'^\[1\]': ('assert_includes', 'ignore_key')
            },
            expected = [
                'ninjas',
                dict(whatever=('apple', 'orange', 'watermelon')),
                'orchards'
            ],
            actual = [
                'ninjas',
                dict(whaja='orange'),
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
                r'\[\'papaya\'\]': 'ignore'
            },
            expected = {
                'banana': 'republic',
            },
            actual = {
                'banana': 'republic',
                'papaya': 'republic'
            }
        )
    def test_ignore_option_failure(self):
        self.assertDifferent(
            {
              '[pineapple]': "expected something, got nothing"
            },
            options = {
                r'\[\'(pineapple|papaya)\'\]': 'ignore'
            },
            expected = {
                'banana': 'republic',
                'pineapple': 'commonwealth',
            },
            actual = {
                'banana': 'republic',
                'papaya': 'republic'
            }
        )

    def test_ignore_spacing_option(self):
        self.assertNotDifferent(
            options = 'ignore_spacing',
            expected = "Welcome, you are logged in as <bobo>.",
            actual = """Welcome,
you are logged  \tin as< bobo>
    .
                """
        )

    def test_ignore_line_whitespace_option(self):
        self.assertNotDifferent(
            options = 'ignore_spacing',
            expected = """Welcome,
                you are logged in as <bobo>.
            """,
            actual = """Welcome, \r
\t\tyou are logged in as <bobo>.  
            """
        )
    def test_ignore_line_whitespace_option_failure(self):
            self.assertDifferent(
                {
                    ":": "fasf"
                },
                options = 'ignore_spacing',
                expected = """Welcome,
                    you are logged in as <bobo>.
                """,
                actual = """Welcome, \r
    \t\tyou are logged   in as <bobo>.  
                """
            )
    
        
if __name__ == '__main__':
    unittest.main(verbosity=2)
