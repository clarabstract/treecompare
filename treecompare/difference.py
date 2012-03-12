class Difference(object):
    def __init__(self, path, message):
        self.path = path
        self.message = message
    
    def __unicode__(self):
        return u"%s: %m" % (self.path, self.message)