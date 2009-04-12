
Ahkera readme
=============

Ahkera is a RestMS implementation based on the Python/Django web framework.
It primarely focuses on rapid prototyping new functionality into RestMS.

Ahkera is developed and maintained by the people listed in contributors.txt.


Related documents
-----------------

coding-style.txt - self explanatory
todo.txt - things that need to be done

RestMS related information can be found at http://www.restms.org.
The RestMS specification draft is at http://wiki.amqp.org/spec:7.

Extensive Django documentation and tutorials are at 
http://www.djangoproject.com. We currently use Django 1.0.

Python documentation is at http://docs.python.org. We currently use 
python 2.x (as supported by django).



Getting started
---------------
- install python and django
- go to your Ahkera source direcorty, run "python manage.py testserver admin.json restms.json"
  this will start a django test web server on localhost with user/pass admin/admin
  for the database admin interface. It will also add some RestMS resource instances
  (2 feeds, 3 joins, 3 pipes)
- You now have a RestMS development server running at localhost:8000
- look into todo.txt and start hacking :)
  OR
- go ahead to the "Managing Objects" section, and use the admin interface
  to configure some RestMS resources into your database.

Remark: Most changes to the code will take effect immediately. If you keep 
   the dev web server running you can test your implmentation right away.
Remark II: "testserver" works on an in-memory db. All changes will be lost
   when the test server shuts down. You need to create a real database via
   "python manage.py syncdb" to work on persistent data.


Managing Objects
----------------

So you started the development server but you cannot manage restms
objects because not all methods are implemented for all the object types,
e.g. POST won't work on feeds, because nobody implemented it?

Connect to the Django admin interface at http://localhost:8000/admin 
(login: admin, pass: admin). Here you can manipulate the database backend
directly. Try adding a join for a start - the page for adding joins 
will let you create a feed and a pipe inline.


Overview
--------

Ahkera/                 # django site directory
    Ahkera              # Ahkera sqlite development database (holds all restms objects)
    ...
    urls.py             # maps urls to functions
    ...
    restms/             # restms web application
        ...
        views.py        # trampoline functions for calling handlers
                        #  (get, put, post, delete) of restms resource objects (feed, join, ...)
        ...
        handlers/       # handler models and actions 
            feed/       #   These subdirs contain database
            join/       #   definitions for RestMS resources
            message/    #   and their relations as well as
            pipe/       #   get(), put(), post(), and delete() implementations.
        templates/      # HTTP response templates
            feed/       #   Specific templates for rendering XML returned by
            join/       #   HTTP request actions. Used by the handlers.
            message/    
            pipe/


Design issues
-------------
The Ahkera design breaks with the MTV (Model, Template, View) pattern 
suggested by django. It does so in favour of having consistent RestMS
resource type classes in the handlers/ subdirectory.

Templates are in a separate subdirectory so we can use the "app directories" 
template loader.


RestMS resource hashes
----------------------
At the time of writing resource hashes contain the resource type and its
database ID, e.g. a feed is represented by /restms/resources/feed_19. This is
purely an implementation issue, no design decision.
