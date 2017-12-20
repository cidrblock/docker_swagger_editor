#!/usr/bin/env python

""" Simple swagger backend (backend.py)
"""

import argparse
from flask import Flask, request

# pylint: disable=invalid-name
port = None
app = Flask(__name__, static_url_path='', static_folder="/swagger_editor")

@app.route('/')
def root():
    """ The swagger editor entry point
    """
    return app.send_static_file('index.html')

@app.route('/<filename>', methods=['GET', 'PUT'])
def spec(filename):
    """ The route for swagger
    """
    if request.method == 'GET':
        try:
            with open("/working/%s" % filename) as file_contents:
                data = file_contents.read()
                return data
        except IOError:
            return '', 400
    if request.method == 'PUT':
        try:
            with open("/working/%s" % filename, 'w') as outfile:
                outfile.write(request.data.decode("utf-8"))
            return '', 200
        except IOError:
            return '', 400

def main():
    """ The main entry point
    """
    # pylint: disable=global-statement
    global port
    parser = argparse.ArgumentParser(description='Simple swagger backend')
    parser.add_argument('-p', '--port', action="store", dest="port", type=int,
                        required=True)
    args = parser.parse_args()
    port = args.port
    app.run(port=port, host='0.0.0.0')

if __name__ == "__main__":
    main()
