'''
Return the index of the
Elixys server
'''
# import basic components
import time
import copy
# import flask components
from flask import Blueprint
from flask import render_template
from flask import jsonify
from flask import current_app
from flask import request
import sys
# import flask class struct implmentation
# import basic user auth
from pyelixys.web.app.userauth.basicauth import requires_auth


elixys_web_index = Blueprint('elixys_web_index', __name__,
        template_folder = 'templates')

class ElixysIndex:
    '''
    This class handles the "Main" page for
    the web browser. If the user has yet to
    be authenticated, they will be prior to
    visiting the Homepage.
    Class represents the GET / web requests.
    '''
    @elixys_web_index.route('/')
    @requires_auth
    def main_index():
        '''
        Function requires authentication.
        Upon valid authentication, function shall
        render a HTML page stored in the 'templates'
        folder.
        '''
        current_app.logger.debug(str(request))
        return render_template('main_elixys.html')
