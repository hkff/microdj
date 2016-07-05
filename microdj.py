# @Author : Walid Benghabrit
# @on     : 07/10/15

##########################################
### Imports
##########################################
import pickle
import imp
import os, sys, inspect
from BaseHTTPServer import *
import urlparse
import jinja2


##########################################
### Config
##########################################

DEBUG = False

def P(args):
    if DEBUG:
        print(args)


APP_NAME = "." 

def DB_PATH(): 
    return APP_NAME + "/database/"

def VIEWS_PATH(): 
    return APP_NAME + "/"

def MODELS_PATH():
    return APP_NAME + "/"
    
def URLS_PATH(): 
    return APP_NAME + "/"

def TEMPLATES_PATH():
    return APP_NAME + "/templates/"    


URLS = None


##########################################
### Dispatcher
##########################################
class HTTPRequestHandler(BaseHTTPRequestHandler):

    # Simple dispatcher
    def dispatch(self, path, args):
        res = None 
        # TODO : can be extended using regexp
        if path in URLS:            # Lookup for view
            res = URLS[path](args)  # Call the view passing the args of the req

        return res


    def do_GET(self):
        # Handle request
        p = self.path
        k = urlparse.urlparse(p).query
        args = urlparse.parse_qs(k)
        
        res = self.dispatch(p, args)
        if res is None:
            res = "URL not found"
            self.send_response(404)
        else:
            self.send_response(200)

        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        self.wfile.write(res.encode("utf-8"))


##########################################
### Server
##########################################
def Server(port):
    # Loading the urls.py for dispatcher
    global URLS
    urls = imp.load_source("urls", URLS_PATH() + "urls.py") 
    URLS = urls.urls
    import nom
    # Load classes
    CLASSES = microdj.get_model_classes()

    server_address = ('', int(port))
    httpd = HTTPServer(server_address, HTTPRequestHandler)
    print("Server start on port %s" % port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server...")
    httpd.server_close()


##########################################
### Rendering
##########################################

def render(template_name, template_vars):
    """
    Render template file using jinja2
    """
    templateLoader = jinja2.FileSystemLoader(searchpath=TEMPLATES_PATH())
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(template_name)
    return template.render(template_vars)



def admin(req):
    """ Admin view """
    CLASSES = microdj.get_model_classes()
    return render("admin.html", { "classes" : CLASSES})

	
    
##########################################
###  Framework Commands
##########################################
class microdj(object):
    
    @staticmethod
    def startapp(app_name):
        """
        Start a new app
        """
        global APP_NAME
        APP_NAME = app_name
        folders = [APP_NAME, TEMPLATES_PATH(), DB_PATH()]
        for f in folders:
            if not os.path.exists(f): 
                os.makedirs(f)
        
        # Create __init__.py
        open(APP_NAME + "/__init__.py", 'w+').close()
        
        # Create models.py
        with open(MODELS_PATH() + "models.py", 'w+') as f:
            f.write("import microdj\n")
            f.write("microdj.APP_NAME = '%s'\n" % APP_NAME)
            f.write("\n# Write your models here")
            
        # Create views.py
        with open(MODELS_PATH() + "views.py", 'w+') as f:
            f.write("import microdj\n")
            f.write("microdj.APP_NAME = '%s'\n" % APP_NAME)
            f.write("from %s.models import *\n" % APP_NAME)
            f.write("\n# Write your views here")
            f.write("\ndef index(req):\n\treturn 'It works !'\n")
            f.write("\ndef admin(req):\n\treturn microdj.admin(req)\n")
        
        # Create urls.py
        with open(URLS_PATH() + "urls.py", 'w+') as f:
            f.write("import %s.views as views\n\n" % APP_NAME)
            f.write("urls = {\n\t'/admin' : views.admin,\n\t'/' : views.index,\n}")
            

    @staticmethod
    def delapp(app_name):
        """
        Delete an application
        """
        import shutil
        if os.path.exists(app_name):
            shutil.rmtree(app_name + "/")
        else:
             print("Application %s not found ! " % app_name)   
    
    
    @staticmethod
    def syncdb(app_name):
        """
        Sync db 
        """
        global APP_NAME
        APP_NAME = app_name
        
        classes = microdj.get_model_classes()
        for obj in classes:
            obj.objects = []
            obj.save()


    @staticmethod
    def cleandb(app_name):
        """
        Delete database files
        """
        global APP_NAME
        APP_NAME = app_name
        
        import shutil
        if os.path.exists(DB_PATH()):
            shutil.rmtree(DB_PATH())
            os.makedirs(DB_PATH())
        else:
             print("Application %s not found ! " % app_name)   
    
    
    @staticmethod
    def genadmin(app_name):
        """
        Generate views
        """
        global APP_NAME
        APP_NAME = app_name

        template_file = TEMPLATES_PATH() + "admin.html"
        
        with open(template_file, "w+") as f:
            f.write("""
                {% for c in classes %}
                <hr>
                <h2> {{ c.__name__ }} objects : </h2>
                <ul style='list-style-type:square'>
                    {% for x in c.objects %}
                        <li> {{ x|e }} </li>
                    {% endfor %}
                </ul>
                <hr>
                {% endfor %}
                """)



    @staticmethod
    def runserver(app_name, port):
        """
        Run simple HTTP server
        """
        global APP_NAME
        APP_NAME = app_name
        Server(int(port))
        

    @staticmethod
    def get_model_classes():
        res = []
        # Load the module models.py
        models = imp.load_source("models", MODELS_PATH() + "models.py") 
        
        # Get all classes in the module
        for name, obj in inspect.getmembers(models):
            if inspect.isclass(obj):
                # Get only classes that are defined in models.py
                if obj.__module__ == "models":
                    # Get only classes that have Meta_Magic as metaclass
                    if type(obj).__name__ is "Meta_Magic":
                        # Loading objects of the class from the db
                        obj.load()
                        res.append(obj)
        return res


##########################################
###  Meta 
##########################################

# Meta Magic class
class Meta_Magic(type):
    
    def __new__(cls, *args, **kargs):
        """ 
        new method 
        """
        P("Meta_Magic new method called with : { cls : %s ; args : %s }\n" % (cls, args))
        return super(Meta_Magic, cls).__new__(cls, *args)
        
    
        
    def __init__(self, *args, **kargs):
        """ 
        init method 
        """
        P("Meta_Magic init called with : { self : %s ; args : %s }\n" % (self, args))
        
        # Add an objects attribute in the class that will contains all instances
        setattr(self, 'objects', [])
        
        ##
        # Generating instane attributes
        ##
        def meta_init(self, **kargs):
            for arg in kargs:
                if arg in self.__class__.__dict__:  # Check if arg is an attribute
                    setattr(self, arg, kargs[arg])
                else:
                    print("Attribute error : %s doesn't exsits in %s" %(arg, self.__class__))

        # add the method to the class        
        setattr(self, '__init__', meta_init)


# Magic class
class Magic(object):
    
    __metaclass__ = Meta_Magic

    ##
    # Saving instanes in objects attribute
    ##
    def __new__(cls, *args, **kargs):
        obj = super(Magic, cls).__new__(cls, *args)
        obj.__class__.objects.append(obj)  
        return obj
        
    ##
    # Serialization
    ##
    @classmethod
    def save(cls):
        """ Save a list of all objects of this class """
        P("Saving all objects of type %s " % cls)
        with open(DB_PATH() + cls.__name__ + ".db", "wb") as f:
            pickle.dump(cls.objects, f, pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls):
        """ Load a list of all objects of this class """
        P("Loading all objects of type %s " % cls)
        with open(DB_PATH() + cls.__name__ + ".db", "rb") as f:
            cls.objects = pickle.load(f)



###################################
### Main
###################################

HELP = """ Read the md file :P """
if __name__ == "__main__":
    if len(sys.argv) > 2:
        if hasattr(microdj, sys.argv[1]):
            obj = getattr(microdj, sys.argv[1])
            if len(sys.argv) == 3:
                obj(sys.argv[2])
            elif len(sys.argv) == 4:
                obj(sys.argv[2], sys.argv[3])
    else:
        print(HELP)


###################################
### Framework usage
###################################

# class Person(Magic):
#     name = "name"
#     age = 0
#     sexe = "?"
    
#     def __str__(self):
#         return "Name : %s Age : %s Sexe : %s" %(self.name, self.age, self.sexe)
        
# p1 = Person(name="titi")
# p2 = Person(name="toto", age = 20)
# Person.save()

