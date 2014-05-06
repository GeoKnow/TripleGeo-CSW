#!/usr/bin/env python

import os
import tempfile
from flask import Flask, abort, url_for, request, make_response

import config
import query

app = Flask(__name__)

@app.route('/query', methods=['GET', 'POST'])
def execute_query():
    #raise Exception('Break')
    
    # Read query from input
    q = None 
    if request.method == 'POST':
        q = request.form.get('query')
    else:
        q = request.args.get('query')
    if not q:
        app.logger.info('Rejected an empty query')
        abort(400)
    else:
        app.logger.debug('Received query: %s', repr(q))
        
    # Create a temporary copy
    f = None
    fp = tempfile.NamedTemporaryFile(mode='w', delete=False)
    try: 
        fp.write(q)
        f = fp.name
    except Exception as ex:
        app.logger.error('Failed to create temporary file: %s', str(ex))
        abort(500)
    finally:
        fp.close()
    
    # Invoke query and cleanup
    result = None
    try: 
        result = query.invoke(f)
    except Exception as ex:
        app.logger.error('Failed to execute query: %s', str(ex))
        abort(400)
    finally:
        os.remove(f)
    
    response = make_response(result, 200)
    response.headers['Content-Type'] = 'application/rdf+xml'
    return response


if __name__ == '__main__':
    app.run(
        host = str(config.get('wsgi', 'host', '127.0.0.1')), 
        port = int(config.get('wsgi', 'port', 5001)), 
        debug = True)

