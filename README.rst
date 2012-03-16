================
``treecompare``
================
----------
Compare large trees of arbitrary objects
----------

``treecompare`` is a library for comparing trees of various objects in a way that yields useful "paths" to each difference. Simply knowing that two object blobs differ is hardly useful without knowing where exactly the differences are located. For text blobs, text-diff utilities can solve this problem, but they are ill suited for dealing with arbitrary data structures such as dictionaries where key order doesn't matter.

Major features:

* Can point to exact location of each difference
* Works with the major python builtin types
* Very easy to extend to handle new classes
* Optional support for comparing XML trees
* String differences reported with ``difflib``
* Configurable "fuzzy" matching:
	- ignore certain miss-matches 
	- match certain ordered structures in any order
	- assert inclusion instead of straight-up equality
	- case insensitive matching for certain nodes
	- whitespace normalization for text nodes


Usage
===============

Basic usage::

	>>> from treecompare import diff

	>>> differences = diff(
	...     expected = {
	...         "glossary": {
	...             "title": "example glossary",
	...                     "GlossDiv": {
	...                 "title": "S",
	...                             "GlossList": {
	...                     "GlossEntry": {
	...                         "ID": "SGML",
	...                                             "SortAs": "SGML",
	...                                             "GlossTerm": "Standard Generalized Markup Language",
	...                                             "Acronym": "SGML",
	...                                             "Abbrev": "ISO 8879:1986",
	...                                             "GlossDef": {
	...                             "para": "A meta-markup language, used to create markup languages such as DocBook.",
	...                                                     "GlossSeeAlso": ["GML", "XML"]
	...                         },
	...                                             "GlossSee": "markup"
	...                     }
	...                 }
	...             }
	...         }
	...     },
	...     actual = {
	...         "glossary": {
	...             "title": "example glossary",
	...                     "GlossDiv": {
	...                 "title": "S",
	...                             "GlossList": {
	...                     "GlossEntry": {
	...                         "ID": "SGML",
	...                                             "SortAs": "SGML",
	...                                             "GlossTerm": "Standard Generalized Markup Language",
	...                                             "Acronym": "SGML",
	...                                             "Abbrev": "ISO 8879:1986",
	...                                             "GlossDef": {
	...                             "para": "A meta-markup language, used to create markup leenguages such as DocBook.",
	...                                                     "GlossSeeAlso": ["GML", "XML"]
	...                         },
	...                                             "GlossSee": "markup"
	...                     }
	...                 }
	...             }
	...         }
	...     }
	... )
	>>> print '\n'.join(map(str,differences))
	['glossary']['GlossDiv']['GlossList']['GlossEntry']['GlossDef']['para']: expected 'A meta-markup language, used to create markup languages such as DocBook.', got 'A meta-markup language, used to create markup leenguages such as DocBook.' - diff:
	- A meta-markup language, used to create markup languages such as DocBook.
	?                                                ^

	+ A meta-markup language, used to create markup leenguages such as DocBook.
	?                                                ^^

	>>> 

``['glossary']['GlossDiv']['GlossList']['GlossEntry']['GlossDef']['para']`` is the "path" of the difference,
it shows exactly how one can navigate the objects to get to the differing parts. As the difference is inside a reasonably large block of text, the difference is highlifhted even further using text-diffs.


Matching options
-------------------

You can configure different matching strategies using the options argument::

	>>> diff(['A','b'], ['a','B'])
	[Difference([0]: "expected 'A', got 'a'"), Difference([1]: "expected 'b', got 'B'")]
	>>> diff(['A','b'], ['a','B'], options='ignore_case')
	[]

You can also pass multiple matching options using a tuple of strings.

Scoped options
~~~~~~~~~~~~~~~~~~~~~~

As each 'node' in a tree of objects has a "path" it is easy to refer to specific sections in your tree using nothign more complicated then regex. You can use this to specify matching options for only parts of your tree::

	>>> diff(
	...     options = {
	...         r'^\[1\]\[\'whatever\'\]': ('assert_includes', 'ignore_case')
	...     },
	...     expected = [
	...         'ninjas',
	...         dict(whatever=('apple', 'ORANGE', 'watermelon')),
	...         'orCHards'
	...     ],
	...     actual = [
	...         'ninjas',
	...         dict(whatever='orAnGe'),
	...         'orchards'
	...     ]
	... )
	[Difference([2]: "expected 'orCHards', got 'orchards'")]

Note how the ``ignore_case`` option allowed ``"orAnGe"`` to match ``"ORANGE"`` but not ``"orchards"`` with ``orCHards`` as ``r'^\[1\]\[\'whatever\'\]'`` does not match the path ``'[2]'``.

Supported options
~~~~~~~~~~~~~~~~~~~~~~

``ignore``
	Don't bother matching objects at this path.

``assert_includes``
	Instead of regular equality matching, verify that object at path is included in tuple at corresponding path of expected object.

``ignore_key``
	Ignore  the 'key' (e.g. order index for lists, string key for dicts when comparing nodes at path. Most useful when performing any-order comparisons.

``ignore_case``
	Use case insensitive compare for strings at this path.

``ignore_spacing``
	Ignore absolutely all whitespace (including line endings) except for purposes of separting words.

``ignore_line_whitespace``
	When comparing strings, normalize line endings and ignore any leading or trailing whitespace.


XML Diff
-------------------

The optional xml diffing module works exactly the same::

	>>> from treecompare.xml import diff_xml
	>>> differences = diff_xml("""<?xml version="1.0" encoding="UTF-8"?>
	...     <menu id="file" value="File">
	...       <popup>
	...         <menuitem value="New" onclick="CreateNewDoc()" />
	...         <menuitem value="Open" onclick="OpenDoc()" />
	...         <menuitem value="Close" onclick="CloseDoc()" />
	...       </popup>
	...     </menu>""",
	...     """<?xml version="1.1" encoding="UTF-8"?>
	...     <menu id="file" value="File">
	...       <popup>
	...         <menuitem value="New" onclick="CreateNewDoc()" />
	...         <menuitem value="Open" onclick="OpenDuck()" />
	...         <menuitem value="Close" onclick="CloseDoc()" />
	...       </popup>
	...     </menu>""")
	>>> print '\n'.join(map(str,differences))
	?xml@version: expected u'1.0', got u'1.1'
	/0<menu>/1<popup>/3<menuitem>@onclick: expected u'OpenDoc()', got u'OpenDuck()'

The numbers before each element in the path refers to the node's index in the parent (including text nodes). You can use the ``ignore_key`` option to match certain elements in any order.


Extending
===============

A ``diff`` function contains a number a list of implementation classes that perform the actual work. The default ``diff`` contains implementations for the major python builtins. ``diff_xml`` adds additional implementations for XML nodes. 

``ImplementationBase`` is, not surprisingly, the base class for Implementations.  Your subclass must be able to answer to:

	1. ``cls.can_diff(obj)`` - are you able to diff this object? Note: a default implementation is provided that simply does an instanceof check on ``cls.diffs_types`` - setting that class attribute should suffice in most cases.

	2. ``self.diff(expected, actual)`` - the acutal implementation, must return a list of ``Difference`` objects. 

For the vast majority of diff implementations one only really needs to recursively diff certain object attributes, and append something to the current "path" for each attribute. The ``ChildDiffingMixing`` allows you to do this very easily - you need only impelment a method that ``yield``s each ``(path,child)`` pair. Everything else including options handling is handled for you. 

The XML differ implementation illustrates how easy this is::

	from treecompare.implementations import ChildDiffingMixing, ImplementationBase

	class DiffXMLElement(ChildDiffingMixing, ImplementationBase):
		diffs_types = dom.Element
		def path_and_child(self, el):
			yield ":tag", el.tagName
			for name, value in el.attributes.items():
				yield "@%s" % name, value

			for i, child in enumerate(el.childNodes):
				if hasattr(child, 'tagName'):
					yield "/%d<%s>" % (i, child.tagName), child
				else:
					yield "/%d:text" % i, child.data


Nothing else to it!

Finally, you have to register your implementation to a differ function. A factory method is provided that can generate your own copy of ``diff()`` (with all the default builtin implementations arleady included), with any of your added::

	from treecompare.differ import make_differ

	custom_diff = make_differ(MyCustomDiff, SomeOtherImplementation)

Note that ``can_diff`` is called for each implemenation in order. Only the first match is used. If you want your custom implementation to override a builtin, you may manipulate the ``custom_diff.implementations`` list directly.