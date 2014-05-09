csw2rdf-middleware
==================

A draft implementation of a CSW-to-RDF middleware application.

Requirements
------------

Make sure all requirements are properly installed. This applies to both command-line usage and the WSGI application.

    pip install -r pip-requirements.txt

Start Middleware
----------------

Edit your configuration at `config.ini` and adjust to your needs (host, port, CSW endpoints etc.).  
Afterwards, you just have to start the WSGI application:

    python wsgi.py

Examples
--------

An example command-line invocation would be:

    python query.py input/q1.txt
    
To keep error/output streams separated, invoke as:

    python query.py input/q1.txt 2>err.log 1>out.rdf

To send a query to the WSGI service running at 127.0.0.1:5000:

    curl -X POST http://localhost:5000/query -d @input/q1-post.txt

