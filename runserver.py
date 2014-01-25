'''
This python file is the main control
component for all web requests from
the client to the server.
This file shall import from
the "app" module and run it.
The "host" and "port" values are
needed to allow remote access
(non-localhost) and reachable from
localhost/IP address of the machine
running this file.
'''
if __name__ == '__main__':
    from web.app import app
    app.run(host='0.0.0.0', debug=True, port=80)
