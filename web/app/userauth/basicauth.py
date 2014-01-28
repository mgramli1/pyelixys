from functools import wraps
from flask import request, Response

# import hashing library
import hashlib
# import logging
from flask import current_app
# import db comm layer
from web.database.dbcomm import DBComm

def check_auth(username, password):
    """
    Function checks is username and password is valid.
    Funciton shall make a database call to verify the
    username and password exists on the database via
    hashing.
    """
    # create new DB communication object
    # and check for a valid login
    db = DBComm()
    # Check if user exists
    if db.is_a_user(str(username)):
        # Convert string password to md5 hash format
        password_hash = hashlib.md5(str(password)).hexdigest()
        # Check username with password
        return (db.is_valid_login(
           str(username),
           str(password_hash)))
    # The file doesn't exist, the user doesn't exist,
    # or the username-password combination isn't valid.
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

