from __future__ import absolute_import
"""

ignore                  Don't bother matching objects at path.

ignore_unexpected       Allow object at path to include unexpected child items 
                        (all expected items must still match however)

assert_includes         Instead of regular equality matching, verify that 
                        object at path matches list/tuple/etc at corresponding
                        path of expected object
                        
ignore_key              Ignore 'key' (e.g. index for lists, string key for 
                        dicts) when comparing nodes at path

ignore_case             When comparing strings, ignore case

ignore_whitespace       When comparing strings, ignore all whitespace except
                        for single spaces, including newlines

ignore_line_whitespace  When comparing strings, normalize line endings and ignore
                        any leading or trailing whitespace

"""

from .differ import Differ
from . import implementations

diff = Differ(
		implementations.DiffPrimitives,
		implementations.DiffNumbers,
		implementations.DiffText,
                implementations.DiffLists,
                implementations.DiffDicts
	)