from __future__ import absolute_import
"""

ignore                  Don't bother matching objects at path.

assert_includes         Instead of regular equality matching, verify that 
                        object at path matches typle at corresponding
                        path of expected object

ignore_key              Ignore 'key' (e.g. order index for lists, string key for 
                        dicts) when comparing nodes at path

ignore_case             When comparing strings, ignore case.

ignore_spacing          Ignore absolutely all whitespace (including line endings)
                        except for purposes of separting words.

ignore_line_whitespace  When comparing strings, normalize line endings and ignore
                        any leading or trailing whitespace


"""

from .differ import make_differ

diff = make_differ() # Your basic differ