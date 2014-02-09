"""
Display user information
"""

import sys
import time
import copy
# import flask components
from flask import Blueprint
from flask import render_template
from flask import jsonify
from flask import current_app
from flask import request

import werkzeug.exceptions as ex
from flask import Flask, abort

from sqlalchemy.orm.exc import MultipleResultsFound,\
                               NoResultFound
#
# import flask class struct implmentation
# import basic user auth
from pyelixys.web.app.userauth.basicauth import requires_auth

from pyelixys.web.database.model import Session
from pyelixys.web.database.model import Sequence,\
                                        Reagent,\
                                        Component,\
                                        User,\
                                        Role


class NoUserFound(Exception):
    pass

elixys_web_users = Blueprint('elixys_web_users', __name__,
        template_folder = 'templates')

class ElixysUserHandler(object):
    """ This provides routes for Elixys/sequence/id/*
    It handles GET,POST and DELETE
    """
    @elixys_web_users.route(
            '/users',
            methods=['GET'])
    @elixys_web_users.route(
            '/Elixys/users',
            methods=['GET'])
    @requires_auth
    def getusers():
        '''
        Return all system users and roles
        '''
        current_app.logger.debug("REQ:%s", request)
        auth = request.authorization
        username = auth.username

        session = Session()

        users = session.query(User).\
                    filter_by(Username=username).all()

        users = {"users":
                    [user.as_dict() for user in users]}


        return jsonify(users)



    @elixys_web_users.errorhandler(NoUserFound)
    def nouserfound(error):
        return "Username was not found"


