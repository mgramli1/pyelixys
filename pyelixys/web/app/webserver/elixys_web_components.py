"""
Handles all component related operations
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

from pyelixys.web.app.webserver.elixys_web_sequences import NoSequenceFound,\
                                            TooManySeqFound


class NoComponentFound(Exception):
    pass

class TooManyComponentFound(Exception):
    pass

class InvalidId(Exception):
    pass

elixys_web_components = Blueprint('elixys_web_components', __name__,
        template_folder = 'templates')

class ElixysComponentHandler(object):
    """ This provides routes for Elixys/sequence/id/*
    It handles GET,POST and DELETE
    """

    @elixys_web_components.route(
            '/component/<component_id>',
            methods=['GET'])
    def getcomp(component_id):
        """ Return a component for a given id """
        current_app.logger.debug("GetComp:%s", component_id)
        auth = request.authorization
        username = auth.username

        session = Session()

        user = session.query(User).\
                    filter_by(Username=username).one()

        try:
            comp = session.query(Component).\
                    filter(Component.ComponentID==int(component_id)).\
                    one()
            current_app.logger.debug(
                    "Request Component %d",
                    component_id)

        except MultipleResultsFound:
            raise TooManyComponentFound
        except NoResultFound:
            raise NoComponentFound
        except ValueError:
            raise InvalidId


        return jsonify(comp.as_dict(), indent=4, sort_keys=True)



    @elixys_web_components.route(
            '/sequence/<sequence_id>/component/<component_id>',
            methods=['GET'])
    @elixys_web_components.route(
            '/Elixys/sequence/<sequence_id>/component/<component_id>',
            methods=['GET'])
    @requires_auth
    @requires_auth
    def getcompinseq(sequence_id, component_id):
        '''
        Funciton shall take in a sequence id as a
        parameter.
        Function shall return the sequence object
        as a jSON object.
        Function shall try to obtain the sequence based
        on the id or try to handle the unknown sequence id.
        All components shall be added to the return object
        as a part of a sequence's components.
        '''
        current_app.logger.debug("REQ:%s", request)
        auth = request.authorization
        username = auth.username

        session = Session()

        user = session.query(User).\
                    filter_by(Username=username).one()

        try:
            seq = session.query(Sequence).\
                    filter_by(SequenceID=int(sequence_id)).one()
        except MultipleResultsFound:
            raise TooManySeqFound
        except NoResultFound:
            raise NoSequenceFound

        try:
            comp = session.query(Component).\
                    filter(Component.SequenceID==seq.SequenceID).\
                    filter(Component.ComponentID==int(component_id)).\
                    one()
            current_app.logger.debug(
                    "Request Component %d",
                    component_id)

        except MultipleResultsFound:
            raise TooManyComponentFound
        except NoResultFound:
            raise NoComponentFound
        except ValueError:
            raise InvalidId


        return jsonify(comp.as_dict(), indent=4, sort_keys=True)

    @elixys_web_components.errorhandler(NoSequenceFound)
    def noseqfound(error):
        return "No Seq found"

    @elixys_web_components.errorhandler(TooManySeqFound)
    def toomanyfound(error):
        return "Too many seq found"


    @elixys_web_components.errorhandler(NoComponentFound)
    def noseqfound(error):
        return "No comp found"

    @elixys_web_components.errorhandler(TooManyComponentFound)
    def toomanyfound(error):
        return "Too many comp found"


    @elixys_web_components.errorhandler(InvalidId)
    def toomanyfound(error):
        return "In correct id parameters"


