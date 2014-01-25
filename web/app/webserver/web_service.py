'''
This python file allows the Elixys webserver to
access component objects:
    -sequence manager
    -core server
    -database
'''
# import the coreserver, database comm,
# and sequence manager
import sys
sys.path.append("/opt/elixys/core")
sys.path.append("/opt/elixys/database")
sys.path.append("/var/www/wsgi")

# Import proxy from wsgi
# Import initialrunstate, sequence manager,
# and Exceptions from core
# Import DBComm from database
import CoreServerProxy
from CoreServer import InitialRunState
import DBComm as DBComm_old
from web.database.dbcomm import DBComm
import SequenceManager
import Exceptions

def coreServerFactory():
    coreServer = CoreServerProxy.CoreServerProxy()
    coreServer.Connect()
    return coreServer

def databaseFactory():
    db = DBComm()
    return db

def getCurrentClientState(username):
    db = DBComm()
    client = db.get_user_client_state(
            str(username))
    return client

def getSequenceManager(db):
    return SequenceManager.SequenceManager(db)

def databaseFactoryOld():
    db = DBComm_old.DBComm()
    db.Connect()
    return db

# assign variables to be used for handlers
core_server = coreServerFactory()
db = databaseFactory()
sequence_manager = getSequenceManager(databaseFactoryOld())
