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

from webserver.elixys_web_index import elixys_web_index
from webserver.elixys_web_sequences import elixys_web_sequences
from webserver.elixys_web_components import elixys_web_components
from webserver.elixys_web_users import elixys_web_users
from webserver.elixys_web_reagents import elixys_web_reagents

app = Flask('Elixys Web Server')
app.debug = True

app.register_blueprint(elixys_web_index)
app.register_blueprint(elixys_web_sequences)
app.register_blueprint(elixys_web_components)
app.register_blueprint(elixys_web_reagents)
app.register_blueprint(elixys_web_users)
