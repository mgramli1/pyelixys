'''
This python file sets up a web micro framework
called Flask. Flask provides easy usability by
using "route()" decorators. This allows easy-to-navigate
classes and modular code by using a combination of
Flask and class structures.
This python file imports Flask and each web request
handler for GET, POST, and DELETE requests.
This python file creates a new Flask instance for
the webserver and uses blueprints. Blueprints are
used to divide the code into sections for each
request. Here, this file registers each GET, POST,
and DELETE class.
'''
from flask import Flask
# import the elixys web GET handler
# import the elixys web POST handler
# import the elixys web DELETE handler
from webserver.elixys_web_get import elixys_web_get
from webserver.elixys_web_get import elixys_web_get_sequence
from webserver.elixys_web_post import elixys_post
from webserver.elixys_web_delete import elixys_delete

app = Flask('Elixys Web Server')
app.debug = True
app.register_blueprint(elixys_web_get)
app.register_blueprint(elixys_web_get_sequence)
app.register_blueprint(elixys_post)
app.register_blueprint(elixys_delete)
