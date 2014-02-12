"""
Handles all reagent related operations
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
from pyelixys.web.app.webserver.elixys_web_components import NoComponentFound,\
                                            TooManyComponentFound




class NoReagentFound(Exception):
    pass

class TooManyReagentFound(Exception):
    pass

class InvalidReagentId(Exception):
    pass


elixys_web_reagents = Blueprint('elixys_web_reagents', __name__,
        template_folder = 'templates')

class ElixysReagentHandler(object):
    """ This provides routes for
    Elixys/sequence/[seqid]/component/[compid]/reagent/[rid0].[rid1].*
    It handles GET,POST and DELETE
    """

    @elixys_web_reagents.route(
            '/sequence/<sequence_id>/reagents')
    @elixys_web_reagents.route(
            '/Elixys/sequence/<sequence_id>/reagents')
    def getAllReagentsForSeq(sequence_id):
        """ Get all reagents for a given sequence """
        current_app.logger.debug("Get All Reagents for seq %s",
                sequence_id)

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

        rs = []

        for comp in seq.components:
            rs += comp.reagents

        rs_dict = {'type':'reagents',
                   'reagents':[r.as_dict() for r in rs]}

        return jsonify(rs_dict)

    @elixys_web_reagents.route(
            '/component/<component_id>/reagents')
    @elixys_web_reagents.route(
            '/Elixys/component/<component_id>/reagents')
    def getAllReagentsForComp(component_id):
        """ Get all reagents for a given sequence """
        current_app.logger.debug("Get All Reagents for component %s",
                component_id)

        auth = request.authorization
        username = auth.username

        session = Session()

        user = session.query(User).\
                    filter_by(Username=username).one()

        try:
            comp = session.query(Component).\
                    filter_by(ComponentID=int(component_id)).one()
        except MultipleResultsFound:
            raise TooManyComponentFound
        except NoResultFound:
            raise NoComponentFound

        rs_dict = {'type':'reagents',
                   'reagents':[r.as_dict() for r in comp.reagents]}

        return jsonify(rs_dict)
    @elixys_web_reagents.route(
            '/Elixys/sequence/<sequence_id>/reagent/<reagent_ids>')
    @elixys_web_reagents.route(
            '/sequence/<sequence_id>/reagent/<reagent_ids>')
    @requires_auth
    def reagent_index(sequence_id, reagent_ids):
        '''
        Accept in a sequence,and reagent id as a
        parameter.

        Return the reagent data
        as a jSON object.
        '''
        current_app.logger.debug("Get Reagents:%s", reagent_ids)
        auth = request.authorization
        username = auth.username

        session = Session()

        user = session.query(User).\
                    filter_by(Username=username).one()


        reagent_ids = reagent_ids.split(".")
        try:
            reagent_ids = [int(rid) for rid in reagent_ids]
        except ValueError:
            raise InvalidReagentId

        try:
            seq = session.query(Sequence).\
                    filter_by(SequenceID=int(sequence_id)).one()
        except MultipleResultsFound:
            raise TooManySeqFound
        except NoResultFound:
            raise NoSequenceFound

        try:
            reagents = session.query(Reagent).\
                    filter(Reagent.ReagentID.in_(reagent_ids)).\
                    all()
        except NoResultFound:
            raise NoReagentFound
        except ValueError:
            raise InvalidReagentId

        rs = {'type':'reagents',
                'reagents': [r.as_dict() for r in reagents]}

        return jsonify(rs)

    @elixys_web_reagents.errorhandler(NoReagentFound)
    def noreagentfound(error):
        return "No Seq found"

    @elixys_web_reagents.errorhandler(TooManyReagentFound)
    def toomanyreagentfound(error):
        return "Too many seq found"

    @elixys_web_reagents.errorhandler(InvalidReagentId)
    def invalidreagentid(error):
        return "Reagent id should be integer"

    @elixys_web_reagents.errorhandler(TooManySeqFound)
    def toomanyseqfound(error):
        return "Found too many sequences"

    @elixys_web_reagents.errorhandler(NoSequenceFound)
    def noseqfound(error):
        return "No sequence found"

    @elixys_web_reagents.errorhandler(TooManyComponentFound)
    def toomanycompfound(error):
        return "Found too many sequences"

    @elixys_web_reagents.errorhandler(NoComponentFound)
    def nocompfound(error):
        return "No component found"
