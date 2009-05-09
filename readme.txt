
Ahkera readme
=============

Ahkera is a RestMS implementation based on the Python/Django web framework.
It primarely focuses on rapid prototyping new functionality into RestMS.

Ahkera is developed and maintained by the people listed in contributors.txt.


Related documents
-----------------

coding-style.txt - self explanatory
todo.txt - things which need to be done

RestMS related information can be found at http://www.restms.org.
The RestMS specification drafts are there as well.

Extensive Django documentation and tutorials are at 
http://www.djangoproject.com. We currently use Django 1.0.

Python documentation is at http://docs.python.org. We currently use 
python 2.x (as supported by django).


Getting started
---------------
- install python and django
- go to your Ahkera source direcorty, run "python manage.py testserver restms/fixtures/simple_test.json"
  This will start a django test web server on localhost
- You now have a RestMS development server running at localhost:8000
- look into todo.txt and start hacking :)
  OR
- run all the tests by typing
  ./manage.py test restms
  Some of the tests will fail with NOT IMPLEMENTED where work needs to be done.

Remark: Most changes to the code will take effect immediately. If you keep 
   the dev web server running you can test your implmentation right away.
Remark II: "testserver" works on an in-memory db. All changes will be lost
   when the test server shuts down. You need to create a real database via
   "python manage.py syncdb" to work on persistent data.



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
            join/       #    definitions for RestMS resources
            message/    #    and their relations as well as
            pipe/       #    get(), put(), post(), and delete() implementations.
            domain/     #    
        templates/      # HTTP response templates
            feed/       #   Specific templates for rendering XML returned by
            join/       #    HTTP request actions. Used by the handlers.
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
database ID, e.g. a message is represented by /restms/resources/message_19. This is
purely an implementation issue, not a design decision.
