from twisted.internet import reactor, defer
from twisted.web.server import Site
from twisted.web.resource import Resource
from txroutes import Dispatcher
import uuid

class Base(Resource):

    def __init__(self, *args, **kwargs):
        Resource.__init__(self, *args, **kwargs)

        self.sessions = {}
    
    def getChild(self, name, request):
        """
        Initial state.
        Check the request headers for a cookie, &c
        """
        c = request.getCookie("libevil")
        print "c: %s" % c
        if not c:
            print "Setting up a cookie"
            id = uuid.uuid4().hex
            request.addCookie("libevil", id )
            self.sessions[ id ] = self._generator()
            begin = self.sessions[ id ].next()
            return String(begin)

        if c in self.sessions:
            return Running(self.sessions, c)
        else:
            print "Couldn't find generator in session"
            self.sessions[c] = self._generator()
            begin = self.sessions[c].next()
            print "Got %s" % begin
            return String(begin)
        
class String(Resource):
    def __init__(self, string):
        Resource.__init__(self)
        self.string = string

    #def render(self, request):
    #    return self.string

    def render_GET(self, request):
        return str( self.string )
    def render_POST(self, request):
        return str( self.string )

class Running(Resource):
    
    isLeaf=True
    def __init__(self, sessions, id):
        Resource.__init__(self)
        self.sessions = sessions
        self.id = id
    def render_GET(self, request):
        """
        the user sent us data here too, clicked a link or something.
        """
        print "Running sessions is %s" % self.sessions
        val = self.sessions[ self.id ].send(request)
        print "Got val"
        return val
        
    def render_POST(self, request):
        """
        The user sent us data.
        """
        pass

def generates():
    count = 1
    string = "I have hit the site %s times!"
    request = yield string % count
    yield
    while 1:
        count = count + 1
        request = yield string % count
        print "Got yielded into. Incrementing count."
        yield



c = Base()
c._generator = generates

factory = Site(c)
reactor.listenTCP(8000, factory)
reactor.run()
