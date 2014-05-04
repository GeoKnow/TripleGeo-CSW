csw2rdf-middleware
==================

A draft implementation of a CSW-to-RDF middleware application

Examples
--------

An example invocation would be:

    python search.py input/q1.txt

Todo
----

 * Wrap application code into a `main(query_file)` function
 * Replace intermediate XML/RDF outputs with actual temporary files. Use `tempfile.NamedTemporaryFile` to ensure uniqueness.
 * The final output should be written directly to STDOUT. Any informational (logging) messages should be written strictly to STDERR.
  

