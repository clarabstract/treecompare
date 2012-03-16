from __future__ import absolute_import

from .implementations import ChildDiffingMixing, ImplementationBase
from .differ import make_differ

import xml.dom.minidom as dom
import re

class DiffXMLDocument(ChildDiffingMixing, ImplementationBase):
	diffs_types = dom.Document

	def path_and_child(self, doc):
		yield "?xml@version", doc.version
		yield "?xml@encoding", doc.encoding
		yield "?xml@standalone", doc.standalone

		for i, child in enumerate(doc.childNodes):
			if hasattr(child, 'tagName'):
				yield "/%d<%s>" % (i, child.tagName), child
			else:
				yield "/%d:text" % i, child.data


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
				




def diff_xml(expected, actual, *args, **kw):
	xmls = map(dom.parseString, (expected,actual))
	return make_differ(
			DiffXMLDocument,
			DiffXMLElement
		)(*(tuple(xmls) + args), **kw)