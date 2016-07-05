         _______ _________ _______  _______  _______  ______  _________
        (       )\__   __/(  ____ \(  ____ )(  ___  )(  __  \ \__    _/
        | () () |   ) (   | (    \/| (    )|| (   ) || (  \  )   )  (
        | || || |   | |   | |      | (____)|| |   | || |   ) |   |  |
        | |(_)| |   | |   | |      |     __)| |   | || |   | |   |  |
        | |   | |   | |   | |      | (\ (   | |   | || |   ) |   |  |
        | )   ( |___) (___| (____/\| ) \ \__| (___) || (__/  )|\_)  )
        |/     \|\_______/(_______/|/   \__/(_______)(______/ (____/

        -----------------------------------------------------------------


[![License](https://img.shields.io/badge/license-GPL3-blue.svg)]()
[![License](https://img.shields.io/badge/python->%3D2.7-green.svg)]()


Introduction
------------

-> What the user of the framework (a developper) will write :

    class Person(microdj.Magic):
        name = ""
        age = 0
        sexe = ""


-> The framework will be able to :

1. Generates instance attributes for all static attributes

2. an __init__ method with all attributes as keyword arguments
   so the user can writes :
        p1 = Person(name="toto")
        p2 = Person(name="titi", age=3)

3. The html code that represents a form to create Person objects 
(this is what django.admin do)

4. The html code that represents a list of all Person objects 
(this is what django.admin do also)

5. Saving/loading all Person objects in a file (we will not use a database, but serialization)

6. A simple http server in python with a tiny url dispatcher

        my_url/person
        my_url/admin
        ...

7. A rendering method using a template engine (for example Jinja)

8. Your propositions are welcome ...



Usage
-----
#### 1. Create a new web app

    python microdj startapp app_name

This wil creates a folder called app_name with :

    database/   : the database folder that contains all serialized objects
    templates/  : the templates folder that contains all templates files
    models.py   : models file that contains user's classes
    views.py    : views file that contains user's views
    urls.py     : urls file that will be used by the dispatcher
    __init__.py : an empty init file to tels to python that this is a module


To clean the app use :

        python microdj delapp app_name


#### 2. Write your models in : app_name/models.py

    class YourClassName(microdj.Magic):
        attribute1 = default_value
        attribute2 = default_value
        ........

create instances of your class using :

    instance1 = YourClassName(attribute1=value, attribute2=value, ....)

Don't forget to save created objects using :

    YourClassName.save()


#### 3. Generate the database :

    python microdj syncdb app_name

This will creates a file "class_name.db" in the database folder for each Class
(that has Meta_Magic as metaclass) you have in your model.


To clean the database use :

    python microdj cleandb app_name

#### 4. Generate the admin views :

    python microdj genadmin app_name


#### 5. Write your templates in : app_name/templates

We use jinja2 templates engine : http://jinja.pocoo.org/docs/dev/


#### 6. Write your Views in :  app_name/views.py

Return a response using a template :

    def index(req):
        return microdj.render("template_name.html", { "key" : var })

Return a simple text response :

    def index(req):
        return "balbalbalba"

Don't forget to load the needed classes :

    YourClassName.load()

#### 7. Write your urls in : app_name/urls.py

    urls = {
        'path1' : views.view1,
        'path2' : views.view2,
        .....
    }

#### 8. Run the server :

    python microdj runserver app_name port_number
