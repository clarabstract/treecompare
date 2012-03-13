from __future__ import absolute_import



class Difference(object):
    def __init__(self, path, message):
        self.path = path
        self.message = message
    
    def __unicode__(self):
        return u"%s: %s" % (self.path, self.message)

    def __str__(self):
    	return str(unicode(self))

    def __repr__(self):
    	return "Difference(%s: %r)" % (self.path, self.message)

    

    
    def __diff_implementation__(self):
    	from .implementations import ImplementationBase
    	class DiffImplementation(ImplementationBase):
	    	def diff(self, expected, actual):
	    		return 	self.diff_child(".path", expected.path, actual.path) + \
	    				self.diff_child(".message", expected.message, actual.message)
    	return DiffImplementation