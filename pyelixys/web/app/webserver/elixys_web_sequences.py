"""
Handles all sequence related operations
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

import json

from sqlalchemy.orm.exc import MultipleResultsFound,\
                               NoResultFound
#
# import flask class struct implmentation
# import basic user auth
from pyelixys.logs import weblog as log
from pyelixys.web.app.userauth.basicauth import requires_auth

from pyelixys.web.database.model import Session
from pyelixys.web.database.model import Sequence,\
                                        Reagent,\
                                        Component,\
                                        User,\
                                        Role


class NoSequenceFound(Exception):
    pass

class TooManySeqFound(Exception):
    pass

class InvalidId(Exception):
    pass

class InvalidRunReq(Exception):
    pass


elixys_web_sequences = Blueprint('elixys_web_sequences', __name__,
        template_folder = 'templates')

class RunResponse(object):
    """ Accept a run request via post
    parse the data, then return an appropriate response
    """
    def __init__(self):
        self.but_action_dict = {}
        self.but_action_dict['ABORTRUN'] = self.action_abort
        self.but_action_dict['HOME'] = self.action_home
        self.but_action_dict['TIMEROVERRIDE'] = self.action_timer_override
        self.but_action_dict['TIMERCONTINUE'] = self.action_continue_run
        self.but_action_dict['USERINPUT'] = self.action_user_input
        self.but_action_dict['PAUSERUN'] = self.action_pause_run
        self.but_action_dict['CONTINUERUN'] = self.action_continue_run

        self.action_dict = {}
        self.action_dict['BUTTONCLICK'] = self.but_action_dict

    def __call__(self, req_dict):
        """ When called, run a action """
        self.req = req_dict
        log.debug("REQ: %s" % repr(self.req))
        try:
            self.action_type = self.req['action']['type']
            self.action_target_id = self.req['action']['target_id']
        except KeyError:
            raise InvalidRunReq

        log.debug("ACTION:%s|TARGET:%s", self.action_type, self.action_target_id)
        action = self.action_dict.get(self.action_type, dict())
        action_target = action.get(self.action_target_id, self.action_unknown)

        return action_target(self.req)

    def action_unknown(self, req=None):
        """ User sent unknown action """
        raise InvalidRunReq

    def action_abort(self, req=None):
        """ Abort sequence """
        #TODO Implement abort on sequencemanager
        return jsonify({"Abort":None})

    def action_home(self,req=None):
        """ Redirect user to home screen """
        #TODO Implement user client status
        return jsonify({"Home":None})

    def action_timer_override(self,req=None):
        """ Override the currently running timer """
        #TODO Implement timer override on sequencemanager
        return jsonify({"TimerOverride":None})

    def action_timer_continue(self,req=None):
        """ Continue a timer """
        #TODO Implement timer continue on sequencemanager
        return jsonify({"ContinueTimer":None})

    def action_user_input(self,req=None):
        """ Deliver message to from user """
        #TODO Implement user input on sequencemanager
        return jsonify({"UserInput":None})

    def action_pause_run(self,req=None):
        """ Pause a currently running sequence """
        #TODO Implement pause on sequencemanager
        return jsonify({"PauseRun":None})

    def action_continue_run(self,req=None):
        """ Continue a currently paused sequence """
        #TODO Implement continue on sequencemanager
        return jsonify({"ContinueRun":None})



class ElixysSequencesHandler(object):
    """ This provides routes for Elixys/sequneces/*
    It handles GET,POST and DELETE
    """
    @elixys_web_sequences.route(
            '/sequence/<sequence_id>',
            methods=['GET'])
    @elixys_web_sequences.route(
            '/Elixys/sequence/<sequence_id>',
            methods=['GET'])
    @requires_auth
    def getsequence(sequence_id):
        '''
        Retrieve a sequence for a given id
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
        except ValueError:
            raise InvalidId

        return jsonify(seq.as_dict())

    @elixys_web_sequences.route(
            '/sequence/all',
            methods=['GET'])
    @elixys_web_sequences.route(
            '/Elixys/sequence/all',
            methods=['GET'])
    @requires_auth
    def getallsequences():
        '''
        Retrieve all sequences
        '''
        current_app.logger.debug("REQ:%s", request)
        auth = request.authorization
        username = auth.username

        session = Session()

        seqs = session.query(Sequence).all()

        seqs_dict = {"type":"sequences",
                "sequences":[seq.as_dict() for seq in seqs]}

        return jsonify(seqs_dict)


    @elixys_web_sequences.route(
            '/user/sequences',
            methods=['GET'])
    @elixys_web_sequences.route(
            '/Elixys/user/sequence',
            methods=['GET'])
    @requires_auth
    def getusersequences():
        '''
        Retrieve this users sequences
        '''
        current_app.logger.debug("REQ:%s", request)
        auth = request.authorization
        username = auth.username

        session = Session()

        user = session.query(User).\
                    filter_by(Username=username).one()

        seqs_dict = {"type":"sequences",
                "sequences":[seq.as_dict() for seq in user.sequences]}

        return jsonify(seqs_dict)

    @elixys_web_sequences.route(
            '/sequence/selected',
            methods=['GET'])
    @elixys_web_sequences.route(
            '/Elixys/sequence/selected',
            methods=['GET'])
    @requires_auth
    def selected_sequence():
        """ Return the users current selected sequence """
        current_app.logger.debug("REQ:%s", request)
        auth = request.authorization
        username = auth.username

        session = Session()

        user = session.query(User).\
                    filter_by(Username=username).one()

        seq = user.selected_sequence

        if seq:
            return jsonify(seq.as_dict(), indent=4, sort_keys=True)
        raise NoSequenceFound

    @elixys_web_sequences.route(
            '/sequence/running',
            methods=['GET'])
    @elixys_web_sequences.route(
            '/Elixys/sequence/running',
            methods=['GET'])
    @requires_auth
    def running_sequence():
        """ Return a sequence that is currently running """
        raise NoSequenceFound


    @elixys_web_sequences.route('/Elixys/RUN', methods=['POST'])
    @requires_auth
    def run_post():
        '''
        Allows the user to send commands to the running sequence
        '''
        # Get objects



        auth = request.authorization
        username = auth.username
        data = request.data
        log.debug("REC DATA: %s" % data)

        current_app.logger.debug("RUN POST: %s | Body: %s",
                request, data)

        run_resp = RunResponse()
        req_dict = json.loads(data)
        return run_resp(req_dict)



    @elixys_web_sequences.errorhandler(NoSequenceFound)
    def noseqfound(error):
        return "No Seq found"

    @elixys_web_sequences.errorhandler(TooManySeqFound)
    def toomanyfound(error):
        return "Too many found"

    @elixys_web_sequences.errorhandler(InvalidId)
    def invalidid(error):
        return "Invalid Id for sequence"


