csw2rdf-middleware
==================

A draft implementation of a CSW-to-RDF middleware application

Examples
--------

An example invocation would be:

    python search.py input/q1.txt
    
To keep error/output streams separated, invoke as:

    python search.py input/q1.txt 2>err.log 1>out.rdf

Todo
----

 * Wrap as a WSGI application (malex)
