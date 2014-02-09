from functools import wraps
from flask import request, Response

# import hashing library
import hashlib
# import logging
from flask import current_app
from pyelixys.web.database.model import Session,\
                                        User

from sqlalchemy.orm.exc import MultipleResultsFound,\
                               NoResultFound
# import db comm layer
#from pyelixys.web.database.dbcomm import DBComm

def check_auth(username, password):
    """
    Function checks is username and password is valid.
    Funciton shall make a database call to verify the
    username and password exists on the database via
    hashing.
    """
    session = Session()
    password_hash = hashlib.md5(str(password)).hexdigest()
    try:
        user = session.query(User).filter(User.Username==username).\
            filter(User.Password==password_hash).one()
    except (MultipleResultsFound, NoResultFound):
        return False

    if user:
        return True
    return False

def authenticate():
    """
    Sends a 401 response that enables basic auth
    """
    #log.info("Authenticate")
    return Response(
            'Could not verify your access level for elixys\n'
            'You must have proper credentials', 401,
            {'WWW-Authenticate':'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            #log.debug("Requires auth")
            return authenticate()
        #log.debug("username:%s" % auth.username)
        return f(*args, **kwargs)
    return decorated

