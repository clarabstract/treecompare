from __future__ import absolute_import



class Difference(object):
    def __init__(self, path, message):
        self.path = path
        self.message = message
    
    def __unicode__(self):
        return u"%s: %s" % (self.path_string, self.message)

    def __str__(self):
    	return str(unicode(self))

    def __repr__(self):
    	return "Difference(%s: %r)" % (self.path_string, self.message)

    

    @property
    def __diff_implementation__(self):
    	from .implementations import ImplementationBase, ChildDiffingMixing
    	class DiffImplementation(ChildDiffingMixing, ImplementationBase):
    	    def path_and_child(self, diffable):
    	        yield ".path", diffable.path_string
    	        yield ".message", diffable.message
    	return DiffImplementation

    @property
    def path_string(self):
        return ''.join(self.path)