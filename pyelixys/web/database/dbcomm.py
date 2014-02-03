"""
Elixys MySQL database communication layer
This python class uses Model's ORM classes
to represent the fields/tables on the database.


"""
# Imports
# Basic imports
import json
import datetime
import time
import sys
import os

# Import the DB connection object from SQLAlchemy
from pyelixys.web.database.model import engine

# Import from Model all ORM objects
from model import Component
from model import Reagents
from model import Roles
from model import RunLog
from model import SystemLog
from model import Sequence
from model import User
from model import loadSession

# Import config object to be used for
# system configurations
from dbconf import config
# Old imports (might remove some)
# Import from 'Core/'
sys.path.append('/opt/elixys/core')
# import Exceptions
# import Utilities
#import TimedLock

#import MySQLdb
import threading
import logging
# Suppress MySQLdb's annoying warnings
import warnings
warnings.filterwarnings("ignore", "Unknown table.*")
import traceback
log = logging.getLogger("elixys.db")

# Error log levels
LOG_ERROR = 0
LOG_WARNING = 1
LOG_INFO = 2
LOG_DEBUG = 3

# Helper Functions
def parse_log_level(log_level):
    '''
    Function shall parse the log level string into
    an integer.
    Function expects a string parameter to be passed
    in for the log level to set.
    Function shall return an integer for the log
    level representation.
    '''
    if log_level == "error":
        return LOG_ERROR
    elif log_level == "warning":
        return LOG_WARNING
    elif log_level == "info":
        return LOG_INFO
    elif log_level == "debug":
        return LOG_DEBUG
    else:
        return -1

def parse_point(s_point):
    """
    Parses a point from the configuration file
    Function expects to be passed in a string parameter
    for the point value.
    Function returns a dictionary list item.
    """
    point = {}
    p_array = s_point.split(",")
    point["x"] = int(p_array[0])
    point["y"] = int(p_array[1])
    return point

def __CallStoredProcedure(self, sProcedureName, pArguments):
    """Calls the given SQL stored procedure"""
    pRows = None
    error_string = ""
    locked_state = False
    try:
        # Acquire the database lock
        self.database_lock.Acquire(10)
        locked_state = True

        # Acquire the cursor and internal database reference
        cursor = self.__pDatabase.cursor()
        pInternalDB = cursor._get_db()

        # Format the argument list
        sArguments = ""
        for pArgument in pArguments:
            if len(sArguments) != 0:
                sArguments += ", "
            sArguments += pInternalDB.literal(pArgument)

        # Invoke the stored procedure
        sQuery = "CALL " + sProcedureName + "(" + sArguments + ")"
        cursor._query(sQuery)
        cursor._executed = sQuery
        pRows = cursor.fetchall()
        cursor.close()
    except Exception, ex:
        # Remember error
        error_string = str(ex)
    finally:
        # Release the database lock
        if locked_state:
            self.database_lock.Release()

    # Raise an exception if an error occurred
    if error_string != "":
        self.__pDatabase = None
        raise Exception(error_string)

    # Return the result
    return pRows

# DB class
class DBComm:
    '''
    This class shall represent the Elixys MySQL database communication
    between from the server to the database. This class expects a .ini
    file for the System Configuration prior to being able to connect.

    '''
    ### Constructor, DB Connect and DB Disconnect ###

    def __init__(self):
        '''
        Constructor for the DBComm object.
        Function expects a string for a configuration .ini filename
        to be passed in as a parameter. If no config or an invalid
        filename is provided, function will raise an exception.
        Function doesn't return an object.
        Function shall store various values from the .ini file
        to values on the DBComm object.
        '''

        self.database = None
        #self.database_lock = TimedLock.TimedLock()

        # Open the system configuration
        self.system_configuration = config

        # Create the configuration object
        self.configuration = {}
        self.configuration["name"] = self.system_configuration["Name"]
        self.configuration["version"] = self.system_configuration["Version"]
        self.configuration["debug"] = (
                self.system_configuration["Debug"] == "True")
        self.configuration["reactors"] = (
                int(self.system_configuration["Reactors"]))

        self.configuration["reagentsperreactor"] = int(
                self.system_configuration["ReagentsPerReactor"])
        self.configuration["elutepositionsperreactor"] = int(
                self.system_configuration["ElutePositionsPerReactor"])
        self.configuration["deliverypositionsperreactor"] = int(
                self.system_configuration["DeliveryPositionsPerReactor"])
        self.configuration["reactorlayoutdimensions"] = (
                parse_point(self.system_configuration["ReactorLayoutDimensions"]))

        self.configuration["reactorreagentpositions"] = []
        for index in range(1, self.configuration["reagentsperreactor"] + 1):
            self.configuration["reactorreagentpositions"].append(
                    parse_point(self.system_configuration["ReactorReagent" +
                            str(index)]))

        self.configuration["reactordeliverypositions"] = []
        for index in range(1, self.configuration["deliverypositionsperreactor"] + 1):
            self.configuration["reactordeliverypositions"].append(
                    parse_point(self.system_configuration["ReactorDelivery" +
                            str(index)]))

        self.configuration["reactorelutepositions"] = []
        for index in range(1, self.configuration["elutepositionsperreactor"] + 1):
            self.configuration["reactorelutepositions"].append(
                    parse_point(self.system_configuration["ReactorElute" +
                            str(index)]))

        # Interpret the log level
        self.log_level = parse_log_level(self.system_configuration["LogLevel"])
        if self.log_level == -1:
            raise Exception("Invalid log level in system configuration file")

        # Create the Twilio configuration
        self.twilio_configuration = {}
        self.twilio_configuration["account"] = (
                self.system_configuration["TwilioAccount"])
        self.twilio_configuration["token"] = (
                self.system_configuration["TwilioToken"])
        self.twilio_configuration["fromphone"] = (
                self.system_configuration["TwilioFromPhone"])

    def connect(self, host = 'localhost'):
        """
        Function shall connect to the database via SQLAlchemy.
        Function expects an optional parameter, host. If given
        a host, function shall attempt to connect to that host name.
        If no parameters (host) is passed in, function shall attempt
        to connect via 'localhost'. If function is unable to connect
        to the database, it shall log it and raise an exception.
        Note that SQLAlchemy will auto commit for us.
        """
        self.database = engine.connect()

    def disconnect(self):
        """
        Function shall disconnect from the database.
        Function expects no parameters.
        Function returns no objects.
        Function shall check if there exists a
        database object attached to the DBComm class
        and close the connection.

        """
        # Disconnect from the database
        if self.database != None:
            self.database.close()
            self.database = None

    ### Configuration functions ###

    def get_configuration(self):
        """
        Function shall get the configuration object
        attached to the DBComm object/class.
        Function expects no parameters to be passed in.
        Function returns the system configuration object
        as a dictionary object.
        """
        log.debug("DBComm.GetConfiguration()")
        return self.configuration

    def get_supported_operations(self):
        """
        Function shall get the support unit operations from
        the configuration object.
        Function expects no parameters to be passed in.
        Function returns the supported operations as
        a dictionary object.
        """
        log.debug("DBComm.GetSupportedOperations()")
        return self.system_configuration["UnitOperations"]

    def get_reactor_positions(self):
        """
        Function gets the reactor poistions available
        from the configuration object.
        Function expects no parameters to be passed in.
        Function returns the reactor positions as a
        dictionary object.
        """
        log.debug("DBComm.GetReactorPositions()")
        return self.system_configuration["ReactorPositions"]

    def get_twilio_configuration(self):
        """
        Function gets the twilio congfurations from the
        configuration object.
        Function expects no parameters to be passed in.
        Funciton returns the Twilio configuration
        as a dictionary object.
        """
        log.debug("DBComm.GetTwilioConfiguration()")
        return self.twilio_configuration

    ### Logging functions ###

    def get_log_level(self):
        '''
        Function returns the log level that
        was set by the config file.
        Function expects no parameters.
        Function returns an integer for
        the logging level.
        '''
        return self.log_level

    def system_log(self, username, level, message):
        '''
        Function shall take in the message
        passed in and log the mssage to
        the database.

        Function expects a string for the
        username and message, and a integer
        for the level.
        Function shall return a string for
        the message sent.
        '''
        # check if the passed in level is
        # above the logging level
        if int(level) > self.log_level:
            raise Exception('Invalid level')
        # load a new session
        session = loadSession()
        # obtain the user id from the username
        user_id = session.query(User).filter_by(
                Username = str(username))
        if user_id.first() == None:
            session.close()
            raise Exception('Unable to find username')
        user_id = int(user_id.first().UserID)
        system_log = SystemLog(
                datetime.datetime.now(),
                int(level),
                int(user_id),
                str(message))
        session.add(system_log)
        session.commit()
        session.close()
        return str(message)

    def run_log(self, level, username, sequence_id, component_id, message):
        '''
        Function shall take in the message
        passed in and log the mssage to
        the RunLog table.

        Function expects a string for the
        username and message, and an integer
        for the level, sequence id, and component
        id.
        Function shall return a string for
        the message sent.
        '''
        # check if the passed in level is
        # above the logging level
        if int(level) > self.log_level:
            raise Exception('Invalid level')
        # load a new session
        session = loadSession()
        # obtain the user id from the username
        user_id = session.query(User).filter_by(
                Username = str(username))
        if user_id.first() == None:
            session.close()
            raise Exception('Unable to find username')
        user_id = int(user_id.first().UserID)
        run_log = RunLog(
                datetime.datetime.now(),
                int(level),
                int(user_id),
                int(sequence_id),
                int(component_id),
                str(message))
        session.add(run_log)
        session.commit()
        session.close()
        return str(message)

    def status_log(self,
            vacuum_system_on,
            vacuum_system_pressure,
            cooling_system_on,
            prssure_regulator1_set_pressure,
            pressure_regulator1_actual_pressure,
            pressure_regulator2_set_pressure,
            pressure_regulator2_actual_pressure,
            gas_transfer_valve_open,
            f18_load_valve_open,
            hplc_load_valve_open,
            reagent_robot_position_set,
            reagent_robot_position_actual,
            reagent_robot_position_set_x,
            reagent_robot_position_set_y,
            reagent_robot_position_actual_x,
            reagent_robot_position_actual_y,
            reagent_robot_status_x,
            reagent_robot_status_y,
            reagent_robot_error_x,
            reagent_robot_error_y,
            reagent_robot_control_x,
            reagent_robot_control_y,
            reagent_robot_check_x,
            reagent_robot_check_y,
            gripper_set_up,
            gripper_set_down,
            gripper_set_open,
            gripper_set_close,
            gas_transfer_set_up,
            gas_transfer_set_down,
            gripper_up,
            gripper_down,
            gripper_open,
            gripper_close,
            gas_transfer_up,
            gas_transfer_down,

            reactor1_set_position,
            reactor1_actual_position,
            reactor1_set_y,
            reactor1_actual_y,
            reactor1_robot_status,
            reactor1_robot_error,
            reactor1_robot_control,
            reactor1_robot_check,
            reactor1_set_up,
            reactor1_set_down,
            reactor1_up,
            reactor1_down,
            reactor1_stopcock1_position,
            reactor1_stopcock2_position,
            reactor1_stopcock3_position,
            reactor1_collet1_on,
            reactor1_collet1_set_temperature,
            reactor1_collet1_actual_temperature,
            reactor1_collet2_on,
            reactor1_collet2_set_temperature,
            reactor1_collet2_actual_temperature,
            reactor1_collet3_on,
            reactor1_collet3_set_temperature,
            reactor1_collet3_actual_temperature,
            reactor1_stir_motor,
            reactor1_raditation_detector,

            reactor2_set_position,
            reactor2_actual_position,
            reactor2_set_y,
            reactor2_actual_y,
            reactor2_robot_status,
            reactor2_robot_error,
            reactor2_robot_control,
            reactor2_robot_check,
            reactor2_set_up,
            reactor2_set_down,
            reactor2_up,
            reactor2_down,
            reactor2_stopcock1_position,
            reactor2_stopcock2_position,
            reactor2_stopcock3_position,
            reactor2_collet1_on,
            reactor2_collet1_set_temperature,
            reactor2_collet1_actual_temperature,
            reactor2_collet2_on,
            reactor2_collet2_set_temperature,
            reactor2_collet2_actual_temperature,
            reactor2_collet3_on,
            reactor2_collet3_set_temperature,
            reactor2_collet3_actual_temperature,
            reactor2_stir_motor,
            reactor2_raditation_detector,

            reactor3_set_position,
            reactor3_actual_position,
            reactor3_set_y,
            reactor3_actual_y,
            reactor3_robot_status,
            reactor3_robot_error,
            reactor3_robot_control,
            reactor3_robot_check,
            reactor3_set_up,
            reactor3_set_down,
            reactor3_up,
            reactor3_down,
            reactor3_stopcock1_position,
            reactor3_stopcock2_position,
            reactor3_stopcock3_position,
            reactor3_collet1_on,
            reactor3_collet1_set_temperature,
            reactor3_collet1_actual_temperature,
            reactor3_collet2_on,
            reactor3_collet2_set_temperature,
            reactor3_collet2_actual_temperature,
            reactor3_collet3_on,
            reactor3_collet3_set_temperature,
            reactor3_collet3_actual_temperature,
            reactor3_stir_motor,
            reactor3_raditation_detector):
        '''
        '''
        # Load a new session and create the StatusLog
        # object. Then add and commit to DB.
        session = loadSession()
        status_log = StatusLog(
                vacuum_system_on,
                vacuum_system_pressure,
                cooling_system_on,
                prssure_regulator1_set_pressure,
                pressure_regulator1_actual_pressure,
                pressure_regulator2_set_pressure,
                pressure_regulator2_actual_pressure,
                gas_transfer_valve_open,
                f18_load_valve_open,
                hplc_load_valve_open,
                reagent_robot_position_set,
                reagent_robot_position_actual,
                reagent_robot_position_set_x,
                reagent_robot_position_set_y,
                reagent_robot_position_actual_x,
                reagent_robot_position_actual_y,
                reagent_robot_status_x,
                reagent_robot_status_y,
                reagent_robot_error_x,
                reagent_robot_error_y,
                reagent_robot_control_x,
                reagent_robot_control_y,
                reagent_robot_check_x,
                reagent_robot_check_y,
                gripper_set_up,
                gripper_set_down,
                gripper_set_open,
                gripper_set_close,
                gas_transfer_set_up,
                gas_transfer_set_down,
                gripper_up,
                gripper_down,
                gripper_open,
                gripper_close,
                gas_transfer_up,
                gas_transfer_down,

                reactor1_set_position,
                reactor1_actual_position,
                reactor1_set_y,
                reactor1_actual_y,
                reactor1_robot_status,
                reactor1_robot_error,
                reactor1_robot_control,
                reactor1_robot_check,
                reactor1_set_up,
                reactor1_set_down,
                reactor1_up,
                reactor1_down,
                reactor1_stopcock1_position,
                reactor1_stopcock2_position,
                reactor1_stopcock3_position,
                reactor1_collet1_on,
                reactor1_collet1_set_temperature,
                reactor1_collet1_actual_temperature,
                reactor1_collet2_on,
                reactor1_collet2_set_temperature,
                reactor1_collet2_actual_temperature,
                reactor1_collet3_on,
                reactor1_collet3_set_temperature,
                reactor1_collet3_actual_temperature,
                reactor1_stir_motor,
                reactor1_raditation_detector,

                reactor2_set_position,
                reactor2_actual_position,
                reactor2_set_y,
                reactor2_actual_y,
                reactor2_robot_status,
                reactor2_robot_error,
                reactor2_robot_control,
                reactor2_robot_check,
                reactor2_set_up,
                reactor2_set_down,
                reactor2_up,
                reactor2_down,
                reactor2_stopcock1_position,
                reactor2_stopcock2_position,
                reactor2_stopcock3_position,
                reactor2_collet1_on,
                reactor2_collet1_set_temperature,
                reactor2_collet1_actual_temperature,
                reactor2_collet2_on,
                reactor2_collet2_set_temperature,
                reactor2_collet2_actual_temperature,
                reactor2_collet3_on,
                reactor2_collet3_set_temperature,
                reactor2_collet3_actual_temperature,
                reactor2_stir_motor,
                reactor2_raditation_detector,

                reactor3_set_position,
                reactor3_actual_position,
                reactor3_set_y,
                reactor3_actual_y,
                reactor3_robot_status,
                reactor3_robot_error,
                reactor3_robot_control,
                reactor3_robot_check,
                reactor3_set_up,
                reactor3_set_down,
                reactor3_up,
                reactor3_down,
                reactor3_stopcock1_position,
                reactor3_stopcock2_position,
                reactor3_stopcock3_position,
                reactor3_collet1_on,
                reactor3_collet1_set_temperature,
                reactor3_collet1_actual_temperature,
                reactor3_collet2_on,
                reactor3_collet2_set_temperature,
                reactor3_collet2_actual_temperature,
                reactor3_collet3_on,
                reactor3_collet3_set_temperature,
                reactor3_collet3_actual_temperature,
                reactor3_stir_motor,
                reactor3_raditation_detector)
        session.add(status_log)
        session.commit()
        session.close()

    def get_recent_logs_by_timestamp(self, username, level, timestamp):
        '''
        '''
        pass

    def get_recent_logs_by_count(self, username, level, count):
        '''
        '''
        pass

    ### Role functions ###

    def get_all_roles(self):
        """
        Function shall return all user roles on the database.
        Function expects no parameters to be passed in.

        Function returns an array of dictionary objects for
        all roles on the database.

        Function shall check if the resultset of the query
        is valid (non-null) and return the resultset. If
        the queried resultset is empty, function shall raise
        an expcetion
        """
        log.debug("DBComm.GetAllRoles()")
        # Create a new session, query for all roles, and close session.
        session = loadSession()
        # Query for all roles
        roles = session.query(Roles)

        # Verify that it is valid resultset, then format to
        # a dictionary.
        if roles.all() != None or roles.all() != []:
            session.close()
            roles_array = []
            for role in roles:
                roles_array.append(
                        role.as_dict())
        return roles_array

        # Raise an exception since role name was invalid.
        session.close()
        log.error("Couldn't get all roles - raising Exception.")
        raise Exception("Role " + str(role_name) + " not found")

        # OLD: roles_raw = self.call_stored_procedure("GetAllRoles", ())

    def get_role(self, role_name):
        """
        Function returns a specified role.
        Function expects a string to be passed in
        as a parameter from a role name.

        Function returns the role as an array of the
        dictionary object from the Roles row on the
        database.

        Function shall check if the passed in role
        name is an element on the database. If role
        name is not an element on the column on the database,
        the function shall raise an exception.
        """
        # Create a new session & query for the role
        session = loadSession()
        role = session.query(Roles).filter_by(
                        RoleName = str(role_name)).first()
        # Check if resultset is valid (Non-null)
        if role != None and role != []:
            session.close()
            return role.as_dict()
        # Raise an exception since role name was invalid.
        session.close()
        log.error("Couldn't get the role for '" + str(role_name) + "'.")
        raise Exception("Role " + str(role_name) + " not found")
        #OLD: roles = roles.filter_by(Roles.RoleName = role_name).first()

    def create_role(self, role_name, flags):
        """
        Function shall create a new specified role
        with the given parameters passed in.
        Function expects a string to be passed in
        as a parameter from a role name and an integer
        flags.

        Function returns the newly created role as
        an array of the dictionary object of the new
        role object.

        Function shall check if the passed in role
        name is an element on the database. If role
        name is not an element on the column on the database,
        the function shall raise an exception.
        """
        log.debug("DBComm.CreateRole(%s, %i)" % (role_name, flags))
        # Check if values to insert are valid
        if str(role_name) == '':
            raise Exception("Invalid Role name.")
        if int(flags) < 1:
            raise Exception("Invalid Flag value.")

        # Create a new session & query for the role
        session = loadSession()
        new_role = Roles(
                str(role_name),
                int(flags),
                self.get_last_role_id(session) + 1)
        session.add(new_role)
        session.commit()
        # Check if resultset is valid (Non-null)
        # If non null, then insertion was successful
        # and return the role object that was inserted.
        # If not, raise an exception.
        role = session.query(Roles).filter_by(
                    RoleName = str(role_name),
                    Flags = int(flags)).first()
        if role != None:
            session.close()
            return role.as_dict()
        # Raise an exception since role name was invalid.
        session.rollback()
        session.close()
        log.error("Couldn't create role with -" +
            "\nRole name: " + str(role_name) + \
            "\nFlags: " + str(flags))
        raise Exception("Role " + str(role_name) + " not found")
        # OLD: return self.call_stored_procedure("CreateRole", (role_name, flags))

    def update_role(self, role_name, updated_role_name, updated_flags):
        """
        Function shall updated the specified role
        with the given parameters passed in.
        Function expects a string to be passed in
        as a parameter from the role name to update,
        a string for the new role name and an integer
        for the new flags value.
        Function returns the newly created role as
        a JSON object.

        Function shall check if the passed in role
        name is an element on the database. If role
        name is not an element on the column on the database,
        the function shall raise an exception.
        """
        log.debug("DBComm.UpdateRole(%s, %s, %i)"
                %(role_name, updated_role_name, updated_flags))
        # Create a new session & query for the role
        session = loadSession()
        role = session.query(Roles).filter_by(
                    RoleName = str(role_name))
        # Check if resultset is valid (Non-null)
        if role.first() == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't get the role for '" + str(role_name) + "'.")
            raise Exception("Role " + str(role_name) + " not found")

        # If no error, then update row with new values via ORM
        role.update(
                {'RoleName': str(updated_role_name),
                'Flags': int(updated_flags)})
        session.commit()

        # Verify there exists the new element on the DB
        role = session.query(Roles).filter_by(
                    RoleName = str(updated_role_name),
                    Flags = str(updated_flags)).first()
        if role != None:
            session.close()
            return role.as_dict()

        # Raise an exception since role name was invalid.
        session.rollback()
        session.close()
        log.error("Couldn't get the updated role for '" + str(updated_role_name) + "'.")
        raise Exception("Role " + str(updated_role_name) + " not found")

        # OLD: return self.call_stored_procedure("UpdateRole",
        # (role_name, update_role_name, updated_flags))

    def delete_role(self, role_name):
        """
        Function shall delete the specified role
        with the given parameter passed in.
        Function expects a string to be passed in
        as a parameter from the role name to delete.
        Function returns the no object.

        Function shall check if the passed in role
        name is an element on the database before deleting the
        row. If role name is not an element on the column
        on the database, the function shall raise an exception.
        """
        log.debug("DBComm.DeleteRole(%s)" % (role_name))
        # Create a new session & query for the role
        session = loadSession()
        role = session.query(Roles).filter_by(
                    RoleName = str(role_name))
        # Check if resultset is valid (Non-null)
        if role.first() == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't get the role for '" + str(role_name) + "'.")
            raise Exception("Role " + str(role_name) + " not found")

        # Delete the role
        role.delete()
        session.commit()
        # old: return self.call_stored_procedure("DeleteRole", (role_name, ))

    def get_last_role_id(self, session):
        '''
        Function shall obtain the last id of
        the roles table and return it.
        Function takes in a session object for
        the DB connection and returns an integer
        for the last id on the role table.
        '''
        roles = session.query(Roles).all()
        last_role_id = 1
        for role in roles:
            last_role_id = int(role.RoleID)
        return last_role_id

    ### User functions ###

    def get_all_users(self):
        """
        Returns details of all system users

        Function shall return all users on the database.
        Function expects no parameters to be passed in.

        Function returns an array of dictionary objects for
        all users on the database.

        Function shall check if the resultset of the query
        is valid (non-null) and return the resultset. If
        the queried resultset is empty, function shall raise
        an exception.
        """
        log.debug("DBComm.GetAllUsers()")
        # Create a new session, query for all users, and close session.
        session = loadSession()
        users = session.query(User).all()
        # Check if query was successful
        if users == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't get all roles - raising Exception.")
            raise Exception("Users not found")

        # The query is valid, but the RoleID is an index
        # and not a RoleName. We shall first convert a user
        # row to a dictionary then query for the RoleID and
        # add it to 'accesslevel' on the dictionary object.
        user_array = []
        for user in users:
            user_dict = user.as_dict()
            role_id = int(user_dict['accesslevel'])
            # Obtain the information from RoleID in the
            # Roles table and get the RoleName.
            user_role_name = session.query(Roles).filter_by(
                        RoleID = role_id).first().RoleName
            user_dict['accesslevel'] = user_role_name
            user_array.append(user_dict)
        session.close()
        return user_array

        # OLD: pUsersRaw = self.__CallStoredProcedure("GetAllUsers", ())

    def get_user(self, username):
        """
        Returns details of the specified user.

        Function shall return a users on the database based
        on the parameters passed into the function.
        Function expects a string username to look up
        on the database.

        Function returns an array of dictionary objects for
        the user on the database.

        Function shall check if the resultset of the query
        is valid (non-null) and return the resultset. If
        the queried resultset is empty, function shall raise
        an exception.
        """
        log.debug("DBComm.GetUser()")
        # Create a new session & query for a user
        session = loadSession()
        user = session.query(User).filter_by(
                        Username = str(username)).first()
        # Check if query was successful
        if user == None:
            # Raise an exception since user was invalid.
            session.close()
            log.error("Couldn't get user '" + str(username) + \
                    "'  - raising Exception.")
            raise Exception("User not found")

        # The query is valid, but the RoleID is an index
        # and not a RoleName. We shall first convert a user
        # row to a dictionary then query for the RoleID and
        # add it to 'accesslevel' on the dictionary object.
        user_dict = user.as_dict()
        role_id = int(user_dict['accesslevel'])
        # Obtain the information from RoleID in the
        # Roles table and get the RoleName.
        user_role_name = session.query(Roles).filter_by(
                    RoleID = role_id).first().RoleName
        user_dict['accesslevel'] = user_role_name
        session.close()
        return user_dict
        #OLD : pUserRaw = self.__CallStoredProcedure("GetUser", (sUsername, ))

    def get_user_password_hash(self, username):
        """
        Returns the password hash of the specified user

        Function shall return a user's password on the database
        based on the parameters passed into the function. The
        returned password will be hashed for security.

        Function expects a string username to look up
        on the database.

        Function returns a string for the user's password
        as a hash on the database.

        Function shall check if the resultset of the query
        is valid (non-null) and return the resultset. If
        the queried resultset is empty, function shall raise
        an exception.
        """
        log.debug("DBComm.GetUserPasswordHash()")
        # Create a new session & query for a user
        session = loadSession()
        user_pw = session.query(User).filter_by(
                        Username = str(username))
        # Check if query was successful
        if user_pw.first() == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't get all roles - raising Exception.")
            raise Exception("Users not found")
        # Close session and return password hash
        user_pw = str(user_pw.first().Password)
        session.close()
        return user_pw
        # OLD: pPasswordHash = self.__CallStoredProcedure(
        #       "GetUserPasswordHash", (sUsername, ))

    def create_user(self, new_username, new_password_hash, new_first_name, new_last_name,
            new_role_name, new_email, new_phone, new_message_level):
        """
        Creates a new user

        Function shall create a new specified user
        with the given parameters passed in.
        Function expects:
        -a string to be passed in as a parameter for a
        username, hashed password, first name, last name,
        role name, and phone number.
        -an integer to be passed in as a parameter for
        the message level.

        Function returns the newly created user as
        an array of the dictionary object of the new
        user object.

        Function shall check if the passed in user
        name is an element on the database. If user
        name is not an element on the column on the database,
        the function shall raise an exception.
        """
        # Check if vital values to insert are valid
        if str(new_username) == '':
            raise Exception("Invalid Username.")
        if str(new_role_name) == '':
            raise Exception("Invalid Rolename.")
        if type(new_message_level) != int:
            raise Exception("Invalid New Message Level type.")

        log.debug("DBComm.CreateUser(%s, %s, %s, %s, %s, %s, %s, %i)"
               % (new_username, new_password_hash,
                    new_first_name, new_last_name,
                    new_role_name, new_email,
                    new_phone, new_message_level))

        default_client_state = (
        {"type":"clientstate",
            "screen":"HOME",
            "sequenceid":0,
            "componentid":0,
            "lastselectscreen":"SAVED",
            "prompt":{"type":"promptstate",
                "screen":"",
                "title":"",
                "show":False,
                "text1":"",
                "edit1":False,
                "edit1default":"",
                "edit1validation":"",
                "text2":"",
                "edit2":False,
                "edit2default":"",
                "edit2validation":"",
                "buttons":[]},
            "selectsequencesort":{"type":"sort",
                "column":"name",
                "mode":"down"},
            "runhistorysort":{"type":"sort",
                "column":"date&time",
                "mode":"down"}})
        # Before inserting the new user, need to
        # take the 'new_role_name' value and convert
        # it into a RoleID for the attribute of the
        # User class.
        # Create a new session
        session = loadSession()
        new_role_id = session.query(Roles).filter_by(
                        RoleName = str(new_role_name)).first()
        # Check if query was successful
        if new_role_id == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't get all roles - raising Exception.")
            raise Exception("Users not found")
        new_role_id = int(new_role_id.RoleID)

        # Create a new user
        # Add and commit to database.
        new_user = User(
            str(new_username), str(new_password_hash),
            str(new_first_name), str(new_last_name),
            str(new_role_id), str(new_email),
            str(new_phone), int(new_message_level),
            str(default_client_state))
        session.add(new_user)
        session.commit()
        # Check if resultset is valid (Non-null)
        # Check if new role is non null.
        # If non null, then insertion
        # was successful and return the role object
        # that was inserted. If not, raise an exception.
        username = session.query(User).filter_by(
                    Username = str(new_username)).first().Username
        if username != None:
            session.close()
            return self.get_user(username)

        # Raise an exception since role name was invalid.
        session.rollback()
        session.close()
        log.error("Couldn't create user." +
            "Couldn't find new username on database")
        raise Exception("User " + str(username) + " not found")
        # OLD: return self.__CallStoredProcedure(
        # "CreateUser", (sUsername, sPasswordHash,

    def update_user(self, username,
            new_username, firstname,
            lastname, rolename, email,
            phone, message_level):
        """
        Function shall update an existing user
        with the given parameters passed in.
        Function expects:
        -A string for username, firstname,
        lastname, rolename, email, and
        phone number.
        -An integer for the message level

        Function returns the newly created user as
        a dictionary object.

        Function shall check if the passed in user
        name is an element on the database. If user
        name is not an element on the column on the database,
        the function shall raise an exception.
        """
        # Check if vital values to insert are valid
        if str(new_username) == '':
            raise Exception("Invalid Username.")
        if str(rolename) == '':
            raise Exception("Invalid Rolename.")
        if type(message_level) != int:
            raise Exception("Invalid New Message Level type.")

        log.debug("DBComm.UpdateUser(%s, %s, %s, %s, %s, %s, %i)"
                % (username, firstname, lastname, rolename,
                    email, phone, message_level))

        # Before inserting the new user, need to
        # take the 'new_role_name' value and convert
        # it into a RoleID for the attribute of the
        # User class. First, create a new session
        session = loadSession()
        role_id = session.query(Roles).filter_by(
                        RoleName = str(rolename)).first()
        # Check if query was successful
        if role_id == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't get all roles - raising Exception.")
            raise Exception("Users not found")

        role_id = role_id.RoleID
        # Create a query for the User
        user = session.query(User).filter_by(
                    Username = str(username))
        # Check if resultset is valid (Non-null)
        if user.first() == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't get the user for '" + str(username) + "'.")
            raise Exception("User " + str(username) + " not found")

        # If no error, then update row with new values via ORM
        # Obtain the row object and perform an update
        user.update(
                {'Username': str(new_username),
                'FirstName': str(firstname),
                'LastName': str(lastname),
                'RoleID': int(role_id),
                'Email': str(email),
                'Phone': str(phone),
                'MessageLevel': int(message_level)})
        session.commit()
        # Verify there exists the new element on the DB
        user = session.query(User).filter_by(
                    Username = str(new_username)).first()
        # Check if resultset is valid (Non-null)
        if user == None:
            # Raise an exception since role name was invalid.
            session.rollback()
            session.close()
            log.error("Couldn't get the updated user for '" + str(updated_role_name) + "'.")
            raise Exception("User " + str(updated_role_name) + " not found")
        # Close session and return formatted dict
        session.close()
        return user.as_dict()
        #old: return self.__CallStoredProcedure("UpdateUser", (sUsername,

    def update_user_password(self, username, password_hash):
        """
        Updates an existing user's password
        as a Hash.
        Function shall update an existing user's
        password as a hash with the given parameters
        passed in.

        Function expects a string for the username
        and the password to update on the database.

        Function returns the new updated password.

        Function shall check if the passed in user
        name is an element on the database. If user
        name is not an element on the column on the database,
        the function shall raise an exception.
        """
        log.debug("DBComm.UpdateUserPassword(%s, %s)" % (username, password_hash))

        # Check if vital values to insert are valid
        if str(username) == '':
            raise Exception("Invalid Username.")

        session = loadSession()

        # Query for the new object and check it.
        # If no error, then update row with new values via ORM
        # Obtain the row object and perform an update
        new_user = session.query(User).filter_by(
                    Username = str(username))
         # Check if resultset is valid (Non-null)
        if new_user.first() == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't get the user for '" + str(username) + "'.")
            raise Exception("User " + str(username) + " not found")

       # Update the password & commit to database.
        new_user.update({'Password': str(password_hash)})
        session.commit()
        # Verify there exists the new element on the DB
        user = session.query(User).filter_by(
                    Username = str(username)).first()
        # Check if the password is updated
        if user.Password != str(password_hash):
            # Raise an exception since password name was invalid.
            session.rollback()
            session.close()
            log.error("Couldn't get the updated user's password for '" + str(password_hash) + "'.")
            raise Exception("Coudln't find password" + str(password) +
                    " for user " + str(username))

        # Close session, obtain new user object,
        # and return formatted dict
        session.close()
        user = session.query(User).filter_by(
                    Username = str(username)).first()
        return user.as_dict()
        # old: self.__CallStoredProcedure(
        # "UpdateUserPassword", (sUsername, sPasswordHash))

    def delete_user(self, username):
        """
        Function shall delete an existing user
        with the given parameter passed in.

        Function expects a string to be passed in
        as a parameter from the username to delete.
        Function returns the no object.

        Function shall check if the passed in user
        name is an element on the database before deleting the
        row. If username is not an element on the column
        on the database, the function shall raise an exception.
        """
        log.debug("DBComm.DeleteUser(%s)" % (username))

        # Create a new session & query for the role
        session = loadSession()
        user = session.query(User).filter_by(
                    Username = str(username))
        # Check if resultset is valid (Non-null)
        if user.first() == None:
            # Raise an exception since username was invalid.
            session.close()
            log.error("Couldn't get the username for '" + str(username) + "'.")
            raise Exception("Username " + str(username) + " not found")

        # If not, delete the user
        user.delete()
        session.commit()

        # Verify row was deleted.
        user = session.query(User).filter_by(
                    Username = str(username)).first()
        if user != None:
            # Raise an exception since username
            session.rollback()
            session.close()
            log.error("Username '" + str(username) + "' wasn't deleted..rolling back")
            raise Exception("Username " + str(username) + " not found")

        #old : return self.__CallStoredProcedure("DeleteUser", (sUsername, ))

    def get_user_client_state(self, username):
        """
        Returns the client state of a user

        Function shall return a user's clientstate from
        the database.
        Function expects a string for the username to be
        passed in as a parameter.

        Function returns the client state as a dictionary object.

        Function shall check if the resultset of the query
        is valid (non-null) and return the resultset. If
        the queried resultset is empty, function shall raise
        an exception.
        """
        log.debug("DBComm.GetUserClientState(%s)" % (username))
        # Create a new session, query for a user's client state
        session = loadSession()
        user_clientstate = session.query(User).filter_by(
                Username = str(username)).first()

        # Check if query was successful
        if user_clientstate == None:
            # Raise an exception since username was invalid.
            session.close()
            log.error("Couldn't get user '" + str(username) + "'" + \
                    " from the database.")
            raise Exception("User not found")
        # If query is not empty, close session and return clientstate
        session.close()
        return json.loads(user_clientstate.ClientState)
        #old: pUserClientState = self.__CallStoredProcedure(
        #"GetUserClientState", (sUsername, ))

    def update_user_client_state(self, username, new_client_state):
        """
        Updates the client state of a user

        Function shall update an existing user's
        client state with the given parameters passed in.
        Function expects a string for username
        and a dictionary for the new client state to
        be passed in.

        Function returns the newly updated client state as
        a dictionary object.

        Function shall check if the passed in user's client
        state is an element on the database. If the client state
        is not an element on the column on the database,
        the function shall raise an exception.
        """

        # Check if vital values to insert are valid
        if str(username) == '':
            raise Exception("Invalid Username.")

        log.debug("DBComm.UpdateUserClientState(%s, %s)" % (username, new_client_state))
        session = loadSession()
        # Create a query for the User
        user = session.query(User).filter_by(
                    Username = str(username))
        # Check if resultset is valid (Non-null)
        if user.first() == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't get the user for '" + str(username) + "'.")
            raise Exception("User " + str(username) + " not found")

        # If no error, then update row with new values via ORM
        # Obtain the row object and perform an update to
        # the client state.
        user.update({'ClientState': json.dumps(new_client_state)})
        session.commit()

        # Verify there exists the new element on the DB
        user = session.query(User).filter_by(
            Username = str(username)).first()

        # Check if resultset is valid (Non-null)
        if user == None:
            # Raise an exception since username was invalid.
            session.rollback()
            session.close()
            log.error("Couldn't get the updated user for '" + str(username) + "'.")
            raise Exception("User " + str(username) + " not found")

        # Close session and return formatted dict
        session.close()
        return user.ClientState

        #old: return self.__CallStoredProcedure("UpdateUserClientState", (sUsername, sClientState))

    # Added new functions - Luis #
    def is_a_user(self, username):
        '''
        Function shall check if the username
        passed in is a username on the database.
        Function expects a string for the username
        to be passed in.
        Function shall return True or False, true
        if the username exists and false otherwise.
        '''
        # Check for empty strings
        if str(username) == '':
            return False
        # load session and query for user
        session = loadSession()
        user = session.query(User).filter_by(
                Username = str(username)).first()
        # if the query returns a username
        if user != None:
            return True
        # if not, then not on the database
        return False

    def is_valid_login(self, username, password_hash):
        '''
        Function shall check if the username and
        password combination is valid.
        Function expects a string for the username
        and the password as a hash.
        Function shall return a boolean, true
        if the username-password combination is valid
        or false otherwise.
        '''
        # load session and query for the user
        username = str(username).lower()
        session = loadSession()
        user = session.query(User).filter_by(
                Username = str(username),
                Password = str(password_hash)).first()
        # Check if query is valid
        if user != None:
            session.close()
            return True

        # If user is Null, then user-password
        # is invalid
        session.close()
        return False

    ### Sequence functions ###

    def get_sequences_by_name(self, sequence_name):
        '''
        Function returns sequence data based on sequence_name.
        Returns all sequences with the same name field as
        sequence_name that are of type 'Saved'

        Function shall return all 'Saved' sequences on the
        database based on the parameters passed into the
        function.
        Function expects a string sequence_name to look up
        on the database.

        Function returns an array of dictionary objects for
        the user on the database.

        Function shall check if the resultset of the query
        is valid (non-null) and return the resultset. If
        the queried resultset is empty, function shall raise
        an exception.
        '''
        log.debug("DBComm.GetUser()")
        # Create a new session & query for all sequences
        # for matching names.
        session = loadSession()
        sequences = session.query(Sequence).filter_by(
                        Name = str(sequence_name),
                        Type = 'Saved').all()

        # Check if query was successful
        if sequences == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't find any sequences '" + str(sequence_name) + \
                    "'  - raising Exception.")
            raise Exception("No Sequences found")

        # The query is valid, We shall first convert a seq
        # row to a dictionary.
        seq_array = []
        for sequence in sequences:
            sequence_dict = sequence.as_dict()
            # Need to obtain the user name from the UserID
            seq_user_name = session.query(User).filter_by(
                    UserID = int(sequence.UserID))
            if seq_user_name.first() == None:
                session.close()
                raise Exception('No User found for Sequence.')
            # Update and append to the new dict object
            sequence_dict['creator'] = str(seq_user_name.first().Username)
            seq_array.append(sequence_dict)
        session.close()
        return seq_array
        # comp_dictsRaw = self.__CallStoredProcedure(
        # "GetAllSequencesByName", (sName, ))

    def get_sequences_history_by_name(self, sequence_name):
        '''
        Function returns sequence data based on the sequence
        name passed into the funciton. This function only returns
        sequences that have been ran previously
        (or have a type of "History")

        Function expects a string as the passed in parameter
        for the sequence name to look up.

        Function shall return the all sequences of type 'History'
        with the same name as 'sequence_name' as a dictionary
        object. Function returns an array of dictionary objects for
        the user on the database.

        Function shall check if the resultset of the query
        is valid (non-null) and return the resultset. If
        the queried resultset is empty, function shall raise
        an exception.

        '''
        log.debug("DBComm.GetAllHistorySequencesByName(%s)" % (sequence_name, ))
        # Create a new session & query for all sequences of type 'History'
        session = loadSession()
        sequences = session.query(Sequence).filter_by(
                        Type = 'History',
                        Name = str(sequence_name)).all()

        # Check if query was successful
        if sequences == None or sequences == []:
            # Raise an exception since sequence was invalid.
            session.close()
            log.error("Couldn't find any sequences '" + str(sequence_name) + \
                    "'  - raising Exception.")
            raise Exception("No Sequences found")

        # The query is valid, We shall first convert a seq
        # row to a dictionary.
        seq_array = []
        for sequence in sequences:
            print str(sequences)
            comp_dict = sequence.as_dict()
            # Need to obtain the user name from the UserID
            seq_user_name = session.query(User).filter_by(
                    UserID = sequence.UserID).first().Username
            # Update and append to the new dict object
            comp_dict['creator'] = str(seq_user_name)

            seq_array.append(comp_dict)
        session.close()
        return seq_array
        # comp_dictsRaw = self.__CallStoredProcedure(
        # "GetAllHistorySequencesByName", (sName, ))

    def get_all_sequences(self, sequence_type):
        """
        Function returns all sequences data based on the sequence
        type passed into the funciton. This function shall only return
        sequences of either type 'Saved' or 'History'.

        Function expects a string as the passed in parameter
        for the sequence type to query on.

        Function shall return the all sequences of the same type
        as 'sequence_type as a dictionary object.
        Function returns an array of dictionary objects for
        the sequences on the database.

        Function shall check if the resultset of the query
        is valid (non-null) and return the resultset. If
        the queried resultset is empty, function shall raise
        an exception.
        """
        # Check if valid params
        if str(sequence_type) != 'Saved' and str(sequence_type) != 'History':
            raise Exception('Invalid sequence type passed in')
        # Create a new session & query for all sequences
        # for matching types.
        log.debug("DBComm.GetAllSequences(%s)" % (sequence_type))

        session = loadSession()
        sequences = session.query(Sequence).filter_by(
                        Type = str(sequence_type)).all()

        # Check if query was successful
        if sequences == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't find any sequences '" + str(sequence_name) + \
                    "'  - raising Exception.")
            raise Exception("No Sequences found")

        # The query is valid, We shall first convert a seq
        # row to a dictionary.
        seq_array = []
        for sequence in sequences:
            print str(sequences)
            comp_dict = sequence.as_dict()
            # Need to obtain the user name from the UserID
            seq_user_name = session.query(User).filter_by(
                UserID = sequence.UserID).first().Username

            # Update and append to the new dict object
            comp_dict['creator'] = str(seq_user_name)
            seq_array.append(comp_dict)
        session.close()
        return seq_array

    def get_sequence_metadata(self, sequence_id):
        """
        Function returns a sequence's metadata based on sequence_id
        that is passed into the function.

        Function expects an integer sequence_id to look up
        on the database.

        Function returns an array of the dictionary object for
        the sequnece's metadata on the database.

        Function shall check if the resultset of the query
        is valid (non-null) and return the resultset. If
        the queried resultset is empty, function shall raise
        an exception.
        """

        # Log the function call and get the sequence data
        log.debug("DBComm.GetSequenceMetadata(%i)" % (sequence_id ))

        # Create a new session & query for all sequences of type 'History'
        session = loadSession()
        sequence = session.query(Sequence).filter_by(
                        SequenceID = int(sequence_id)).first()

        # Check if query was successful
        if sequence == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't find any sequences id:'" + str(sequence_id) + \
                    "'  - raising Exception.")
            raise Exception("No Sequences found")

        # The query is valid, We shall first convert a seq
        # row to a dictionary.
        comp_dict = sequence.as_dict()

        # Need to obtain the user name from the UserID
        seq_user_name = session.query(User).filter_by(
            UserID = sequence.UserID).first().Username

        # Update and append to the new dict object
        comp_dict['creator'] = str(seq_user_name)
        # Removed undeed keys
        comp_dict['timestamp'] = sequence.CreationDate.strftime("%Y-%m-%d %H:%M:%S")
        comp_dict['sequencetype'] = str(sequence.Type)
        comp_dict['type'] = 'sequencemetadata'
        del(comp_dict['time'])
        del(comp_dict['date'])

        session.close()
        return comp_dict
        # pSequenceRaw = self.__CallStoredProcedure(
        # "GetSequence", (nSequenceID, ))

    def get_sequence(self, sequence_id):
        """
        Function returns a sequence's data based on sequence_id
        that is passed into the function.

        Function expects an integer sequence_id to look up
        on the database.

        Function returns a dictionary object for
        the sequnece's data on the database.

        Function shall check if the resultset of the query
        is valid (non-null) and return the resultset. If
        the queried resultset is empty, function shall raise
        an exception.
        """
        # Create a new session & query for a sequence with
        # the name matching the parameter passed in.
        session = loadSession()
        sequence = session.query(Sequence).filter_by(
            SequenceID = int(sequence_id)).first()

        # Check if query was successful
        if sequence == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't find any sequences '" + str(sequence_name) + \
                    "'  - raising Exception.")
            raise Exception("No Sequences found")

        # The query is valid, We shall first convert a seq
        # row to a dictionary.Query for the sequence's components
        # Append metadata and components to the dict
        seq_dict = {'type': 'sequence'}
        seq_dict['metadata'] = self.get_sequence_metadata(
                int(sequence_id))
        seq_dict['components'] = self.get_components_by_sequence(
                int(sequence_id))

        session.close()
        return seq_dict

        #pSequenceRaw = self.__CallStoredProcedure("GetSequence", (nSequenceID, ))
        # Load the sequence
        #pSequence = {"type":"sequence"}
        #pSequence["metadata"] = self.GetSequenceMetadata(sCurrentUsername, nSequenceID)
        #pSequence["components"] = self.GetComponentsBySequence(sCurrentUsername, nSequenceID)

    def create_sequence(self, seq_name, username, comment, seq_type, cassettes, reagents):
        '''
        Function shall create a new sequence and
        return the newly created sequence as a dictionary
        object.

        Function expects parameters to be passed in:
        -strings for sequence name, user, comment, type
        -integers for number of cassettes and reagents to
        append to the sequence

        Function shall return newly created sequences' ID as
        an integer.

        Function shall check if the resultset of the query
        is valid (non-null) and return the resultset. If
        the queried resultset is empty, function shall raise
        an exception.
        '''
        # Check if vital values to insert are valid
        if str(seq_name) == '':
            raise Exception("Invalid Sequence name.")
        if int(cassettes) <= 0:
            raise Exception("Invalid number of Cassettes.")
        if int(reagents) <= 0:
            raise Exception("Invalid number of Reagents.")

        log.debug("DBComm.CreateSequence(%s, %s, %s, %s, %i, %i)" %
                (seq_name, username, comment,
                seq_type, cassettes, reagents))
        # Start a new session
        session = loadSession()
        # Create a new sequence, but first obtain the
        # userID for the username passed in.
        user_id = session.query(User).filter_by(
            Username = str(username)).first().UserID
        # Now, Create a new sequence. We shall update
        # the new sequence with the new components
        # and reagents later.
        new_sequence = Sequence(
                str(seq_name),
                str(comment),
                str(seq_type),
                time.strftime("%Y-%d-%m %H:%M.%S "),
                int(user_id),
                0,
                0,
                True,
                False)
        # add and commit to db
        session.add(new_sequence)
        session.commit()
        # save the new sequence's ID
        new_sequence_id = int(new_sequence.SequenceID)

        # Create components with the sequence id
        # Loop through the number of cassettes
        # and create each component for the cassettte.
        # Save the first component ID.
        first_component_id = 0
        for cassette_num in range(0, int(cassettes)):
            component_id = self.create_component(
                    int(new_sequence_id),
                    'CASSETTE',
                    '',
                    '')
            # Save the first reagent it to update component's details
            first_reagent_id = 1
            # Now insert the number of reagents passed in
            for reagent_position in range(0, int(reagents)):
                if first_reagent_id == 1:
                    first_reagent_id = self.create_reagent(
                        int(new_sequence_id),
                        int(component_id),
                        int(reagent_position) + 1,
                        '',
                        '')
                else:
                    self.create_reagent(
                        int(new_sequence_id),
                        int(component_id),
                        int(reagent_position) + 1,
                        '',
                        '')
            session.commit()
            print 'Component ID: ' + str(component_id)
            # Now update the cassette component's details
            component = session.query(Component).filter_by(
                    ComponentID = component_id)
            print 'Component: ' + str(component)
            component.update(
                    {'Details': str(self.create_default_component_details(
                        new_sequence_id, component_id,
                        first_reagent_id, cassette_num))})
            session.commit()

        session.close()
        return new_sequence_id

    def update_sequence(self, username, sequence_id, sequence_name, comment, valid):
        '''
        Function shall update a row with the
        same sequence id as the passed in.
        Function expects:
        -a string for the username,
        sequence name, and comment.
        -an integer for the sequence id
        -a boolean for the valid flag.

        Function doesn't return an object.
        '''
        # Check the values to be valid

        # load a new session
        session = loadSession()

        # obtain the sequence
        sequence = session.query(Sequence).filter_by(
                SequenceID = int(sequence_id))
        # obtain the user's id using the username
        user = session.query(User).filter_by(
                Username = str(username))

        # check if querys are valid
        if sequence.first() == None:
            # Raise an exception since sequence was invalid.
            session.close()
            log.error("Couldn't find sequence ID:'" + str(sequence_id) + \
                    "'  - raising Exception.")
            raise Exception("No Sequences found")
        if user.first() == None:
            # Raise an exception since username was invalid.
            session.close()
            log.error("Couldn't find username:'" + str(username) + \
                    "'  - raising Exception.")
            raise Exception("No Username found")

        # update the sequence's values
        sequence.update(
                {'UserID': int(user.first().UserID),
                'Name': str(sequence_name),
                'Comment': str(comment),
                'Valid': bool(valid)})

        # update and commit
        session.commit()
        session.close()

    def update_sequence_dirty_flag(self, sequence_id, dirty_flag):
        '''
        Function shall update the dirty flag value
        for a sequence.
        Function expects an intger for the sequence id
        and a boolean for the dirty flag.
        '''
        # load a new session
        session = loadSession()

        # obtain the sequence
        sequence = session.query(Sequence).filter_by(
                SequenceID = int(sequence_id))

        # check if querys are valid
        if sequence.first() == None:
            # Raise an exception since sequence was invalid.
            session.close()
            log.error("Couldn't find sequence ID:'" + str(sequence_id) + \
                    "'  - raising Exception.")
            raise Exception("No Sequences found")

        # update the sequence's values
        sequence.update({'Dirty': bool(dirty_flag)})

        # update and commit
        session.commit()
        session.close()

    def delete_sequence(self, sequence_id):
        '''
        Function shall delete a sequence from the sequence
        table.
        Function expects an integer for the sequence
        id to delete.
        Function shall return True if the query successfully
        deleted the sequence or False if not.
        '''
        session = loadSession()
        sequence = session.query(Sequence).filter_by(
                SequenceID = int(sequence_id))
        # Check if resultset is valid (Non-null)
        if sequence.first() == None:
            # Raise an exception since username was invalid.
            session.close()
            log.error("Couldn't get the sequence id for '" + str(sequence_id) + "'.")
            raise Exception("Sequence " + str(sequence_id) + " not found")

        sequence.delete()
        session.commit()

        # Verify that the deletion was valid.
        sequence = session.query(Sequence).filter_by(
                SequenceID = int(sequence_id))
        if sequence.first() == None:
            return True
        else:
            return False

    def get_last_sequence_id(self, session):
        '''
        Function shall return the last index/id on
        the sequence table.
        Function takes in a session
        Function returns an integer.
        '''
        sequences = session.query(
                Sequence).all()

        last_sequence_id = 1
        for sequence in sequences:
            last_sequence_id = sequence.SequenceID

        return last_sequence_id

   ### Component functions ###

    def get_component(self, component_id):
        '''
        Function shall get the component and
        return the object as a dictionary.
        Function expects an integer for the component
        id to be passed in.
        Function shall return a component as a dictionary
        object.
        '''
        session = loadSession()
        component = session.query(Component).filter_by(
                        ComponentID = int(component_id)).first()
        # Check if query was successful.
        if component == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't find any components '" + str(component_id) + \
                    "'  - raising Exception.")
            raise Exception("No Components found")

        # return as a dictionary object
        # format it
        session.close()
        return component.as_dict()

    def get_previous_component(self, component_id):
        '''
        Function shall get the component, obtain the
        previous component's information, and return
        the object as a dictionary.
        Function expects an integer for the component
        id to be passed in.
        Function shall return a component as a dictionary
        object.
        '''
        # load session
        session = loadSession()
        # obtain component
        prev_component_id = session.query(
                Component).filter_by(
                        ComponentID = int(component_id)).first()

        # Check if query was successful.
        if prev_component_id == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't find any components '" + str(prev_component_id) + \
                    "'  - raising Exception.")
            raise Exception("No Components found")
        # store the prev comp id & query for it
        prev_component_id = int(prev_component_id.PreviousComponentID)
        prev_component = session.query(Component).filter_by(
                        ComponentID = prev_component_id).first()

        # Check if query was successful.
        if prev_component == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't find any components '" + str(prev_component_id) + \
                    "'  - raising Exception.")
            raise Exception("No Components found")

        # return as a dictionary object
        # format it
        session.close()
        return prev_component.as_dict()

    def get_next_component(self, component_id):
        '''
        Function shall get the component, obtain the
        next component's information, and return
        the object as a dictionary.
        Function expects an integer for the component
        id to be passed in.
        Function shall return a component as a dictionary
        object.
        '''
        # load session
        session = loadSession()
        # obtain component
        next_component_id = session.query(
                Component).filter_by(
                        ComponentID = int(component_id)).first()
        # Check if query was successful.
        if next_component_id == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't find any components '" + str(next_component_id) + \
                    "'  - raising Exception.")
            raise Exception("No Components found")
        next_component_id = int(next_component_id.NextComponentID)

        next_component = session.query(Component).filter_by(
                        ComponentID = next_component_id).first()

        # Check if query was successful.
        if next_component == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't find any components '" + str(next_component_id) + \
                    "'  - raising Exception.")
            raise Exception("No Components found")

        # return as a dictionary object
        # format it
        session.close()
        return next_component.as_dict()

    def get_components_by_sequence(self, sequence_id):
        '''
        Function shall obtain all components associated
        with the given sequence id that is passed in.

        Function expects an integer for the sequence id
        to query on all components on to be passed into
        the function.

        Function shall return an array of dictionary objects
        for all components that have the same sequence id.

        Function shall check if the resultset of the query
        is valid (non-null) and return the resultset. If
        the queried resultset is empty, function shall raise
        an exception.
        '''
        log.debug("DB.GetComponentBySequence(%s)" % (sequence_id))
        # Create a new session & query for components with
        # the name matching the sequence id
        session = loadSession()
        components = session.query(Component).filter_by(
                        SequenceID = int(sequence_id)).all()

        # Check if query was successful
        if components == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't find any sequences '" + str(sequence_name) + \
                    "'  - raising Exception.")
            raise Exception("No Sequences found")

        # The query is valid, We shall first convert a comp
        # row to a dictionary.
        comp_array = []
        for component in components:
            print str(component.Details) + '\n'
            comp_dict = {}
            comp_dict["id"] = int(component.ComponentID)
            comp_dict["sequenceid"] = int(component.SequenceID)
            comp_dict["note"] = str(component.Note)
            # obtain data from 'Details' column via
            # a dict lookup
            # Check if Details contains several elements (might not)
            details = json.loads(str(component.Details))
            comp_dict.update(details)

            comp_array.append(comp_dict)
        session.close()
        return comp_array

    def create_component(self, sequence_id, component_type, note, content):
        '''
        Function shall create a new component and shall update
        the component count for a sequence to relect the newly added
        component.

        Function expects:
        -an integer for the sequence id.
        -strings for the component type, sequence note
        -a string for content but the format of the string
        should be in a dictionary-like format

        Function shall return the Component ID of the newly
        created component.

        Function shall check if the resultset of the query
        is valid (non-null) and return the resultset. If
        the queried resultset is empty, function shall raise
        an exception.
        '''
        if int(sequence_id) <= 0:
            raise Exception('Sequence id is not valid.')
        log.debug("DBComm.CreateComponent(%i, %s, %s, %s)" %
                (sequence_id, component_type, note, content))

        # Create new session
        session = loadSession()
        # Need to obtain the last component of the sequence
        # First, get a sequence object with a matching sequence id
        sequence = session.query(Sequence).filter_by(
                SequenceID = int(sequence_id))

        # Check if query was successful
        if sequence.first() == None:
            # Raise an exception since sequence id was invalid.
            session.close()
            log.error("Couldn't find any sequences ID '" + str(sequence_id) + \
                    "'  - raising Exception.")
            raise Exception("No Sequences found")

        # Save the first component id
        seq_first_component_id = int(sequence.first().FirstComponentID)
        # If the sequence's first component id is 0, then
        # this is the first component being added.
        if seq_first_component_id == 0:
            # Create a new component object
            new_component = Component(
                int(sequence_id),
                0,
                0,
                str(component_type),
                str(note),
                str(content),
                str(self.get_last_component_id(session) + 1) )
            # add new element to database
            session.add(new_component)

            # Update component count for the sequence
            sequence.update(
                    {'ComponentCount': int(sequence.first().ComponentCount) + 1})
            # Map the first component id to sequence's 'FirstComponentID'
            # Update the component count to the number of cassettes/components
            # that were added.
            sequence.update(
                    {'FirstComponentID': int(new_component.ComponentID)})
            session.commit()

            new_component_id = str(new_component.ComponentID)
            session.close()
            return new_component_id

        # else, there's a previous component
        # Query for a componenet with a matching sequence ID
        # and no next component ID (this would be the last component).
        prev_component = session.query(Component).filter_by(
                SequenceID = int(sequence.first().SequenceID),
                NextComponentID = 0)
        # Store the last component's ID.
        last_component_id = int(prev_component.first().ComponentID)

        # Create a new component object
        new_component = Component(
            int(sequence_id),
            int(last_component_id),
            0,
            str(component_type),
            str(note),
            str(content),
            str(self.get_last_component_id(session) + 1))
        # add and commit to database
        session.add(new_component)

        # Update the last (previous) component's next component id
        # to the newly added component.
        prev_component = session.query(Component).filter_by(
                ComponentID = last_component_id)
        prev_component.update(
                {'NextComponentID': int(new_component.ComponentID)})
        # Update component count for the sequence
        sequence.update(
                {'ComponentCount': int(sequence.first().ComponentCount) + 1})
        session.commit()
        new_comp_id = int(new_component.ComponentID)
        session.close()
        return new_comp_id

    def insert_component(self, sequence_id, component_type, note, details, previous_id):
        '''
        Function shall insert a component and map it to the sequence.
        This is useful for arranging unit operations in a certain order.

        Function expects:
        -an integer for the sequence id and a previous id
        (the previous id would be the value for previous
        component id)
        -a string for the component type, note, and details

        Function shall return an integer for the component
        id of the newly created component.
        '''
        # check for valid values
        if int(sequence_id) <= 0:
            raise Exception('Invalid sequence id')
        # load session and create new component
        session = loadSession()
        # Check if the sequence exists
        sequence = session.query(Sequence).filter_by(
                SequenceID = int(sequence_id))
        if sequence.first() == None:
            # Raise an exception since sequence id was invalid.
            session.close()
            log.error("Couldn't find any sequence '" + str(sequence_id) + \
                    "'  - raising Exception.")
            raise Exception("No Sequence found")
        # Create a new component object to insert
        component = Component(
                int(sequence_id),
                int(previous_id),
                0,
                str(component_type),
                str(note),
                str(details),
                self.get_last_component_id(session) + 1)
        session.add(component)
        session.commit()

        # Update the sequence's component count
        sequence = session.query(Sequence).filter_by(
                SequenceID = int(sequence_id))
        sequence.update({'ComponentCount': sequence.first().ComponentCount + 1})
        session.commit()

        return_comp_id = int(component.ComponentID)
        session.close()
        return return_comp_id

    def update_component(self, component_id, comp_type, note, details):
        '''
        Function shall update a row with the
        same component id as the passed in
        parameters.

        Function expects:
        -a string for the component type
        and note
        -an integer for the component id
        -a dictionary for the details (can
        be passed in as a string in a dictionary
        format)
        Function doesn't return an object.
        '''
        # Check the values to be valid
        if int(component_id) <= 0:
            raise Exception('Invalid component id')
        # load a new session & query for the component
        session = loadSession()
        component = session.query(Component).filter_by(
                ComponentID = int(component_id))

        # check if query are valid
        if component.first() == None:
            # Raise an exception since component was invalid.
            session.close()
            log.error("Couldn't find component with ID:'" + str(component_id) + \
                    "'  - raising Exception.")
            raise Exception("No Components found")

        # update the component's values
        component.update(
                {'Type': str(comp_type),
                'Note': str(note),
                'Details': str(details)})

        # update and commit
        session.commit()
        session.close()

    def move_component(self, component_id, previous_id):
        '''
        Function shall move a component and change its previous id
        to the passed in parameter.

        Function expects:
        -an integer for the component id and a previous id
        (the previous id would be the value for previous
        component id)
        -a string for the component type, note, and details

        Function shall not return any object.
        '''
        # check for valid values
        if int(component_id) <= 0:
            raise Exception('Invalid component id')
        if int(previous_id) < 0:
            raise Exception('Invalid previous id')
        # load session and query for the component with
        # matching IDs
        session = loadSession()
        component = session.query(Component).filter_by(
                ComponentID = int(component_id))

        # Check if valid query
        if component.first() == None:
            # Raise an exception since component id was invalid.
            session.close()
            log.error("Couldn't find any components'" + str(component_id) + \
                    "'  - raising Exception.")
            raise Exception("No Components found")

        # Update the components previous component id
        component.update({'PreviousComponentID': int(previous_id)})
        session.commit()
        session.close()

    def delete_component(self, component_id):
        '''
        Function shall delete a component from the
        component table. Function shall also update
        the component count of the sequence and remap
        the previous index.

        Function expects an integer for the component's
        ID to delete from the table.
        Function doesn't return an object.
        '''
        if int(component_id) <= 0:
            raise Exception('Invalid component ID.')
        log.debug("DBComm.DeleteComponent(%i)" % (component_id))
        # Create a new session & query for the component
        session = loadSession()
        component = session.query(Component).filter_by(
                ComponentID = int(component_id))
        # Check if resultset is valid (Non-null)
        if component.first() == None:
            # Raise an exception since component was invalid.
            session.close()
            log.error("Couldn't get the component for id'" + str(component_id) + "'.")
            raise Exception("Component " + str(component_id) + " not found")

        # Save the previous & next component id of the deleted component
        previous_component_id = int(component.first().PreviousComponentID)
        next_component_id = int(component.first().NextComponentID)
        # query for those components
        previous_component = session.query(Component).filter_by(
                ComponentID = int(previous_component_id))
        next_component = session.query(Component).filter_by(
                ComponentID = int(next_component_id))

        # check if we need to update the previous component or
        # the next component.
        if previous_component.first() != None:
            # there exists a previous comp, update/remap it.
            previous_component.update({'NextComponentID': next_component_id})
        if next_component.first() != None:
            # there exists a next comp, update/remap it.
            next_component.update({'PreviousComponentID': previous_component_id})

        # update the sequence's component count, first try to obtain
        # a matching sequence with the id
        sequence = session.query(Sequence).filter_by(
                SequenceID = int(component.first().SequenceID))
        # check if query was successful
        if sequence == None:
            # Raise an exception since sequence was invalid.
            session.close()
            log.error("Couldn't get the component's sequence id'" +
                    str(component_id) + "'.")
            raise Exception("Component " + str(component_id) + " not found")
        # update the count by -1
        sequence.update({'ComponentCount': int(sequence.first().ComponentCount)-1})
        # finally, delete component and commit to db
        component.delete()
        session.commit()
        session.close()

    def get_cassette(self, sequence_id, cassette_number):
        '''
        Function shall return a dictionary of a sequence's
        cassette component.
        Function expects an integer for the sequence ID and
        the cassete number to obtain (there exists cassettes
        0, 1, and 2)
        Function shall return the cassette as a dictionary object.
        '''
        # verify valid values
        if int(sequence_id) <= 0:
            raise Exception('Invalid sequence id')
        if int(cassette_number) > 2 or int(cassette_number) <= 0:
            raise Exception('Invalid cassette number')

        # Load new session and query for component on sequence id.
        session = loadSession()
        component = session.query(
                Component.ComponentID,
                Component.SequenceID,
                Component.Note,
                Component.Type,
                Component.Details).filter_by(
                        SequenceID = int(sequence_id)).all()
        # Check if query was successful.
        if component == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't find any components '" + str(component_id) + \
                    "'  - raising Exception.")
            raise Exception("No Components found")
        # Obtain the cassette value by the number passed in.
        component = component[int(cassette_number)]
        # return as a dictionary object & format it
        session.close()
        return component.as_dict()

    def get_last_component_id(self, session):
        '''
        Function shall return the last index/id on
        the components table.
        Function takes in a session
        Function returns an integer.
        '''
        components = session.query(
                Component).all()

        last_component_id = 1
        for component in components:
            last_component_id = int(component.ComponentID)

        return last_component_id

    def create_default_component_details(self,
            sequence_id, component_id,
            first_reagent_id, cassette_num):
        '''
        Funciton shall create the default component
        details to be saved onto the 'Detail's column.
        Function expects an integer for the
        sequence id, component id, the
        reagent id of the first reagent created,
        and the cassette number to represent the
        reactor the cassette is located in.
        Function returns a dictionary of the
        newly created component's details (default details)
        '''
        # load new session
        session = loadSession()
        # obtain component
        component = session.query(Component).filter_by(
                ComponentID = component_id).first()

        # create a Details dictionary
        component_details = {}
        component_details['sequenceid'] = int(component.SequenceID)
        component_details['note'] = str(component.Note)
        component_details['validationerror'] = False
        component_details['reactor'] = int(cassette_num)
        component_details['componenttype'] = 'CASSETTE'
        component_details['type'] = 'component'
        component_details['reagentids'] = []
        for reagent_id in range(int(first_reagent_id), int(first_reagent_id) + 12):
            component_details['reagentids'].append(reagent_id)

        return component_details

    ### Reagent functions ###

    def get_reagent(self, reagent_id):
        '''
        Function shall get the reagent and
        return the object as a dictionary.
        Function expects an integer for the reagent
        id to be passed in.
        Function shall return a reagent as a dictionary
        object.
        '''
        if reagent_id <= 0:
            raise Exception('Invalid reagent id')
        session = loadSession()
        reagent = session.query(Reagents).filter_by(
                        ReagentID = int(reagent_id)).first()
        # Check if query was successful.
        if reagent == None:
            # Raise an exception since role name was invalid.
            session.close()
            log.error("Couldn't find any reagents with id'" + str(reagent_id) + \
                    "'  - raising Exception.")
            raise Exception("No Reagent found")

        # return as a dictionary object
        # format it
        # TODO: call component.as_dict()

        session.close()
        return reagent.as_dict()

    def get_reagents_by_sequence(self, sequence_id):
        '''
        Function shall obtain all reagents based on
        the sequence id that shall be provided.
        Function expects an integer for the
        sequence id to be passed in.
        Function shall return all reagents with
        the same sequence id as an array of dictionary
        objects.
        '''
        if sequence_id <= 0:
            raise Exception('Invalid sequecne id')
        # load session and get all reagents by sequence id
        session = loadSession()
        reagents = session.query(Reagents).filter_by(
                SequenceID = int(sequence_id)).all()

        if reagents == None:
            # Raise an exception since reagents was invalid.
            session.close()
            log.error("Couldn't find any reagents with sequence id '" +
                    str(component_id) + "'  - raising Exception.")
            raise Exception("No Reagents found")
        # add each reagent dictionary to an array
        reagent_array = []
        for reagent in reagents:
            reagent_array.append(reagent.as_dict())

        session.close()
        return reagent_array

    def get_reagents_by_name(self, sequence_id, name):
        '''
        Function shall obtain all reagents based on
        the sequence id and name that shall be provided.
        Function expects an integer for the
        sequence id and a string for the sequence name
        to be passed in.
        Function shall return all reagents as an array
        of dictionary objects.
        '''
        if int(sequence_id) <= 0:
            raise Exception('Invalid sequecne id')
        # load session and get all reagents by sequence id
        session = loadSession()
        reagents = session.query(Reagents).filter_by(
                SequenceID = int(sequence_id),
                Name = str(name)).all()

        if reagents == None:
            # Raise an exception since reagents was invalid.
            session.close()
            log.error("Couldn't find any reagents with sequence id '" +
                    str(component_id) + "' and reagent name '" + str(name) +
                    "' - raising Exception.")
            raise Exception("No Reagents found")
        # add each reagent dictionary to an array
        reagent_array = []
        for reagent in reagents:
            reagent_array.append(reagent.as_dict())

        session.close()
        return reagent_array

    def get_reagent_by_position(self, sequence_id, cassette_number, position_number):
        '''
        Function shall obtain a specific reagent
        at a position based on the parameters passed in.
        Function shall look for all reagents with the sequence
        id and filter then by which cassette number and the
        position number location on the cassette.

        Function expects integers for the sequence id,
        a cassette number to select (only cassettes 1-3),
        and a position number for the position location on
        the cassette.

        Function shall return a dictionary object for the
        reagent.
        '''
        # Verify valid search criteria
        if int(sequence_id) <= 0:
            raise Exception('Invalid sequence id')
        if int(cassette_number) < 1 or int(cassette_number) > 3:
            raise Exception('Invalid cassette number')
        if int(position_number) < 1 or int(position_number) > 12:
            raise Exception('Invalid position number')

        # Load session and obtain all CASSETTE components based by
        # sequence id.
        session = loadSession()
        components = session.query(Component).filter_by(
                SequenceID = int(sequence_id),
                Type = 'CASSETTE').all()
        # Check for a valid resultset
        if components == None or components == []:
            # Raise an exception since components was invalid.
            session.close()
            log.error("Couldn't find any cassette components with sequence id '" +
                    str(sequence_id) + "' - raising Exception.")
            raise Exception("No Components found")
        # Obtain the cassette
        component_id = components[ int(cassette_number) - 1].ComponentID
        reagent = session.query(Reagents).filter_by(
                ComponentID = component_id,
                Position = int(position_number)).first()
        # Check for a valid resultset
        if reagent == None:
            # Raise an exception since reagent was invalid.
            session.close()
            log.error("Couldn't find any reagents with component id '" +
                    str(component_id) + "' - raising Exception.")
            raise Exception("No Reagents found")

        return reagent.to_dict()

    def get_reagent_cassette(self, sequence_id, reagent_id):
        '''
        Function shall obtain the cassette number from the
        sequence id and reagent id. Function shall return the
        cassette number (1-3) of the sequence's reagent id.

        Function expects integers for the sequence id and
        a reagent id to look up.

        Function shall return a integer value that represents
        which cassette number.
        '''
        # Verify valid search criteria
        if int(sequence_id) <= 0:
            raise Exception('Invalid sequence id')
        if int(reagent_id) <= 0:
            raise Exception('Invalid reagent id')

        # Load session and obtain all CASSETTE components based by
        # sequence id.
        session = loadSession()
        components = session.query(Component).filter_by(
                SequenceID = int(sequence_id),
                Type = 'CASSETTE').all()
        # Check for a valid resultset
        if components == None or components == []:
            # Raise an exception since components was invalid.
            session.close()
            log.error("Couldn't find any cassette components with sequence id '" +
                    str(sequence_id) + "' - raising Exception.")
            raise Exception("No Components found")

        # Obtain cassettes
        reagents_array = []
        for component in components:
            reagents_array.append(
                    session.query(Reagents).filter_by(
                        ComponentID = int(component.ComponentID)).all())
        # Check for a valid resultset
        if reagents_array == None or reagents_array == []:
            # Raise an exception since reagent was invalid.
            session.close()
            raise Exception("No Reagents found")

        # Loop through each of the 3 cassettes and their 12 reagents
        # Check if there's a match in reagent id
        # Here, keep track of which cassette and reagent position
        # we are in
        cassette_counter = 1
        reagent_counter = 1
        for reagent in reagents_array:
            for reag in reagent:
                if reag.ReagentID == int(reagent_id):
                    session.close()
                    return cassette_counter
                if reagent_counter == 12:
                    cassette_counter += 1
                    reagent_counter = 1
                else:
                    reagent_counter += 1
        # If no match is found, raise exception
        session.close()
        log.error("Couldn't find any reagents with reagent id '" +
                    str(reagent_id) + "' - raising Exception.")
        raise Exception('No matching reagent id found')

    def update_reagent(self, reagent_id, name, description):
        '''
        Function shall update a reagent with the
        new information passed in. Function shall
        update a row with the same reagent id as
        the passed in parameter.

        Function expects:
        -an integer for the reagent id to look up.
        -a string for the name and description.

        Function doesn't return an object.
        '''
        # load a new session
        session = loadSession()

        # obtain the reagent
        reagent = session.query(Reagents).filter_by(
                ReagentID = int(reagent_id))

        if reagent.first() == None:
            # Raise an exception since reagent was invalid.
            session.close()
            log.error("Couldn't find reagent id:'" + str(reagent_id) + \
                    "'  - raising Exception.")
            raise Exception("No Reagent found")

        # update the reagent values
        reagent.update(
                {'Name': str(name),
                'Description': str(description)})

        # update and commit
        session.commit()
        session.close()

    def update_reagent_by_position(self, sequence_id,
            cassette_number, position, name, description):
        '''
        Function shall update a reagent with the
        new information passed in. Function shall
        update a row with the same reagent id as
        the passed in parameter.

        Function expects:

        -an integer for the reagent id to look up.
        -a string for the name and description.

        Function doesn't return an object.
        '''
        # Load session and obtain all components based by
        # sequence id.
        session = loadSession()
        components = session.query(Component).filter_by(
                SequenceID = int(sequence_id)).all()
        # Check for a valid resultset
        if components == None or components == []:
            # Raise an exception since components was invalid.
            session.close()
            log.error("Couldn't find any components with sequence id '" +
                    str(sequence_id) + "' - raising Exception.")
            raise Exception("No Components found")

        # Obtain components with
        reagents_array = []
        for component in components:
            reagents_array.append(
                    session.query(Reagents).filter_by(
                        ComponentID = int(component.ComponentID),
                        Position = int(position)))
        # Check for a valid resultset
        if reagents_array == None or reagents_array == []:
            # Raise an exception since reagent was invalid.
            session.close()
            raise Exception("No Reagents found")
        # Obtain the reagent position to be updated.
        reagent = reagents_array[int(cassette_number) - 1]
        reagent.update(
                {'Name': str(name),
                'Description': str(description)})

        # load a new session
        # update and commit
        session.commit()
        session.close()

    def create_reagent(self, sequence_id, component_id,
            reagent_position, name, description):
        '''
        Function shall create a new reagent and add
        it to the reagent table.

        Function expects the following parameters:
        -An integer for the sequence id, component id,
        and reagent position.
        -A string for the name and description of the
        reagent to be inserted.

        Function shall return the 'ReagentID' value
        of the newly inserted reagent.
        '''

        session = loadSession()
        new_reagent = Reagents(
                int(sequence_id),
                int(component_id),
                int(reagent_position),
                str(name),
                str(description),
                int(self.get_last_reagent_id(session) + 1))
        session.add(new_reagent)
        session.commit()
        new_reagent_id = int(new_reagent.ReagentID)
        session.close
        return new_reagent_id

    def get_last_reagent_id(self, session):
        '''
        Function shall get the last reagent id
        from the reagents table and return it.
        Function expects a session object
        to be passed in.
        Function returns an integer.
        '''
        reagents = session.query(
                Reagents).all()

        last_reagent_id = 1
        for reagent in reagents:
            last_reagent_id = int(reagent.ReagentID)

        return last_reagent_id

def main():
    '''Main function is called only when
    this file is executed as a Python script
    '''
    db = DBComm()
    return db

if __name__ == '__main__':
    db = main()
    from IPython import embed
    embed()
