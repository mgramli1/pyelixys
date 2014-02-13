#Embedded file name: /home/luis/pyelixysweb/new_db/Model.py
from datetime import datetime
import json
# Import hashing for user's password
from hashlib import md5

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import ForeignKeyConstraint

from pyelixys.web.database.dbconf import config
# Import validator for components
from pyelixys.web.app.webserver.validate.validatecomponent import comp_vtor

dburl = config['database_url']
engine = create_engine(dburl, echo=True)
Base = declarative_base(engine)

class Component(Base):
    """
    Component of a Unit operation
    """
    __tablename__ = 'Components'
    ComponentID = Column(Integer, primary_key=True)
    SequenceID = Column(Integer, ForeignKey('Sequences.SequenceID'))
    PreviousComponentID = Column(Integer)
    NextComponentID = Column(Integer)
    Type = Column(String(length=20))
    Note = Column(String(length=64))
    Details = Column(String(length=2048))
    runlogs = relationship('RunLog', backref='runlogs')
    sequence = relationship('Sequence', backref='components',
            foreign_keys=[SequenceID])
    reagents = relationship('Reagents',
            primaryjoin="and_" +
            "(Reagents.ComponentID==Component.ComponentID)",
            uselist=True)

    def __init__(self,
            seqID=None,
            previousCompID=None,
            nextCompID=None,
            seq_type="",
            note="",
            details="",
            componentID = None):
        self.ComponentID = componentID
        self.SequenceID = seqID
        self.PreviousComponentID = previousCompID
        self.NextComponentID = nextCompID
        self.Type = seq_type
        self.Note = note
        self.Details = details

    def __repr__(self):
        return '<Component(%s,%s)>' % (self.ComponentID, self.SequenceID)

    def as_dict(self):
        """
        Function shall return the
        Components class attributes as a
        Python dictionary object.
        Funciton expects no parameters
        Function returns a Component as a
        dictionary object.
        """
        comp_dict = {}
        comp_dict['id'] = int(self.ComponentID)
        comp_dict['sequenceid'] = int(self.SequenceID)
        comp_dict['note'] = str(self.Note)
        comp_dict['componenttype'] = str(self.Type)
        details = json.loads(str(self.Details))
        if 'reactor' in details and 'reagentids' in details:
            comp_dict['reactor'] = str(details['reactor'])
            comp_dict['reagentids'] = details['reagentids']
        else:
            comp_dict.update(details)
        comp_dict['validationerror'] = bool(details['validationerror'])
        comp_dict['type'] = str(details['type'])
        return comp_dict

    def get_details(self):
        return json.loads(self.Details)

    details = property(get_details)

    def update_from_dict(self, comp_dict):
        '''
        Updates the attributes of the component
        with the values of the passed in dict.
        Function expects a dictionary object
        with keys that map to the Component's
        attributes/fields.
        Function returns no output.
        '''
        # First validate the entries
        comp_vtor.check('check_component', comp_dict)
        # Valid, let's update the entries of the Component
        # Grab the session object so we can modify via ORM
        component = session.query(Component).filter_by(\
                ComponentID = self.ComponentID).first()

        for key, value in comp_dict.iteritems():
            if key == "sequence_id":
                component.SequenceID = value
            elif key == "previous_component_id":
                component.PreviousComponentID = value
            elif key == "next_component_id":
                component.NextComponentID = value
            elif key == "type":
                component.Type = value
            elif key == "note":
                component.Note = value
            elif key == "details":
                component.Details = value
            else:
                # Else, we received an unknown key
                # Should flag an error
                print "%s,%s" % (key, value)
        # Update to DB
        session.commit()

class Reagents(Base):
    """
    Reagent Object
    """
    __tablename__ = 'Reagents'
    ReagentID = Column(Integer, primary_key=True)
    SequenceID = Column(Integer, ForeignKey('Sequences.SequenceID'))
    ComponentID = Column(Integer, ForeignKey('Components.ComponentID'))
    Position = Column(String(length=2))
    Name = Column(String(length=64))
    Description = Column(String(length=255))
    components = relationship('Component',
            primaryjoin="Component.ComponentID==Reagents.ComponentID",
            uselist=False)
    sequence = relationship('Sequence',
            primaryjoin="Sequence.SequenceID==Reagents.SequenceID",
            uselist=False)


    def __init__(self,
            seqID=None,
            componentID=None,
            position=None,
            name="",
            description="",
            reagentID = None):

        if reagentID is not None:
            self.ReagentID = reagentID
        self.SequenceID = seqID
        self.ComponentID = componentID
        self.Position = position
        self.Name = name
        self.Description = description

    def __repr__(self):
        return '<Reagent(%s,%s)>' % (self.ReagentID, self.Name)

    def as_dict(self):
        """
        Function shall convert the
        reagent's properties as a
        python dictionary and return the
        dictionary.
        Function expects no parameters.
        Function returns a dictionary object.
        """
        reagent_dict = {}
        reagent_dict['type'] = 'reagent'
        reagent_dict['reagentid'] = int(self.ReagentID)
        reagent_dict['componentid'] = int(self.ComponentID)
        reagent_dict['position'] = int(self.Position)
        reagent_dict['name'] = str(self.Name)
        reagent_dict['namevalidation'] = 'type=string; required=true'
        reagent_dict['description'] = str(self.Description)
        reagent_dict['descriptionvalidation'] = 'type=string'
        return reagent_dict


class Roles(Base):
    """
    Roles Object
    """
    __tablename__ = 'Roles'
    RoleID = Column(Integer, primary_key=True)
    RoleName = Column(String(length=30))
    Flags = Column(Integer)
    users = relationship('User',
            primaryjoin="User.RoleID==Roles.RoleID",
            backref='role')

    def __init__(self,
            roleName="",
            flag=0,
            roleID = None):
        if roleID is not None:
            self.RoleID = roleID
        self.RoleName = roleName
        self.Flags = flag

    def __repr__(self):
        return '<Roles(%s,%s)>' % (self.RoleID, self.RoleName)

    def as_dict(self):
        """
        Function shall format the Roles
        class attributes as a Python dictionary.
        Function expects no parameters to be
        passed in.
        Function returns a dictionary object with
        the Roles variables.
        """
        role_dict = {}
        role_dict = {'type': 'role'}
        role_dict['id'] = int(self.RoleID)
        role_dict['name'] = str(self.RoleName)
        role_dict['flags'] = int(self.Flags)
        return role_dict


class SystemLog(Base):
    """
    SystemLog Object
    """
    __tablename__ = 'SystemLog'
    LogID = Column(Integer, primary_key=True)
    Timestamp = Column(DateTime, default=datetime.now)
    Level = Column(Integer)
    UserID = Column(Integer, ForeignKey('Users.UserID'))
    Message = Column(String(length=1024))

    def __init__(self,
            timestamp=0,
            level=0,
            userID=0,
            message="",
            logID=None):
        self.Timestamp = timestamp
        self.Level = level
        self.UserID = userID
        self.Message = message

    def __repr__(self):
        return '<SystemLog(%s, %s)>' % (self.LogID, self.Timestamp)


class StatusLog(Base):
    """
    StatusLog Object
    """
    __tablename__ = 'StatusLog'
    LogID = Column(Integer, primary_key=True)
    Timestamp = Column(DateTime, default=datetime.now)
    VacuumSystemOn = Column(Boolean)
    VacuumSystemPressure = Column(Float)
    CoolingSystemOn = Column(Boolean)
    PressureRegulator1SetPressure = Column(Float)
    PressureRegulator1ActualPressure = Column(Float)
    PressureRegulator2SetPressure = Column(Float)
    PressureRegulator2ActualPressure = Column(Float)
    GasTransferValveOpen = Column(Boolean)
    F18LoadValveOpen = Column(Boolean)
    HPLCLoadValveOpen = Column(Boolean)
    ReagentRobotPositionSet = Column(String(length=64))
    ReagentRobotPositionActual = Column(String(length=64))
    ReagentRobotPositionSetX = Column(Integer)
    ReagentRobotPositionSetY = Column(Integer)
    ReagentRobotPositionActualX = Column(Integer)
    ReagentRobotPositionActualY = Column(Integer)
    ReagentRobotStatusX = Column(String(length=64))
    ReagentRobotStatusY = Column(String(length=64))
    ReagentRobotErrorX = Column(Integer)
    ReagentRobotErrorY = Column(Integer)
    ReagentRobotControlX = Column(Integer)
    ReagentRobotControlY = Column(Integer)
    ReagentRobotCheckX = Column(Integer)
    ReagentRobotCheckY = Column(Integer)
    GripperSetDown = Column(Boolean)
    GripperSetUp = Column(Boolean)
    GripperSetOpen = Column(Boolean)
    GripperSetClose = Column(Boolean)
    GasTransferSetUp = Column(Boolean)
    GasTransferSetDown = Column(Boolean)
    Reactor1SetPosition = Column(String(length=30))
    Reactor1ActualPosition = Column(String(length=30))
    Reactor1SetY = Column(Integer)
    Reactor1ActualY = Column(Integer)
    Reactor1RobotStatus = Column(String(length=30))
    Reactor1RobotError = Column(Integer)
    Reactor1RobotControl = Column(Integer)
    Reactor1RobotCheck = Column(Integer)
    Reactor1SetUp = Column(Boolean)
    Reactor1SetDown = Column(Boolean)
    Reactor1Up = Column(Boolean)
    Reactor1Down = Column(Boolean)
    Reactor1Stopcock1Position = Column(String(length=4))
    Reactor1Stopcock2Position = Column(String(length=4))
    Reactor1Stopcock3Position = Column(String(length=4))
    Reactor1Collet1On = Column(Boolean)
    Reactor1ColletSetTemperature = Column(Float)
    Reactor1ColletActualTemperature = Column(Float)
    Reactor1Collet2On = Column(Boolean)
    Reactor1Collet2SetTemperature = Column(Float)
    Reactor1Collet2ActualTemperature = Column(Float)
    Reactor1Collet3On = Column(Boolean)
    Reactor1Collet3SetTemperature = Column(Float)
    Reactor1Collet3ActualTemperature = Column(Float)
    Reactor1StirMotor = Column(Integer)
    Reactor1RadiationDetector = Column(Float)
    Reactor2SetPosition = Column(String(length=30))
    Reactor2ActualPosition = Column(String(length=30))
    Reactor2SetY = Column(Integer)
    Reactor2ActualY = Column(Integer)
    Reactor2RobotStatus = Column(String(length=30))
    Reactor2RobotError = Column(Integer)
    Reactor2RobotControl = Column(Integer)
    Reactor2RobotCheck = Column(Integer)
    Reactor2SetUp = Column(Boolean)
    Reactor2SetDown = Column(Boolean)
    Reactor2Up = Column(Boolean)
    Reactor2Down = Column(Boolean)
    Reactor2Stopcock1Position = Column(String(length=4))
    Reactor2Stopcock2Position = Column(String(length=4))
    Reactor2Stopcock3Position = Column(String(length=4))
    Reactor2Collet1On = Column(Boolean)
    Reactor2ColletSetTemperature = Column(Float)
    Reactor2ColletActualTemperature = Column(Float)
    Reactor2Collet2On = Column(Boolean)
    Reactor2Collet2SetTemperature = Column(Float)
    Reactor2Collet2ActualTemperature = Column(Float)
    Reactor2Collet3On = Column(Boolean)
    Reactor2Collet3SetTemperature = Column(Float)
    Reactor2Collet3ActualTemperature = Column(Float)
    Reactor2StirMotor = Column(Integer)
    Reactor2RadiationDetector = Column(Float)
    Reactor3SetPosition = Column(String(length=30))
    Reactor3ActualPosition = Column(String(length=30))
    Reactor3SetY = Column(Integer)
    Reactor3ActualY = Column(Integer)
    Reactor3RobotStatus = Column(String(length=30))
    Reactor3RobotError = Column(Integer)
    Reactor3RobotControl = Column(Integer)
    Reactor3RobotCheck = Column(Integer)
    Reactor3SetUp = Column(Boolean)
    Reactor3SetDown = Column(Boolean)
    Reactor3Up = Column(Boolean)
    Reactor3Down = Column(Boolean)
    Reactor3Stopcock1Position = Column(String(length=4))
    Reactor3Stopcock2Position = Column(String(length=4))
    Reactor3Stopcock3Position = Column(String(length=4))
    Reactor3Collet1On = Column(Boolean)
    Reactor3ColletSetTemperature = Column(Float)
    Reactor3ColletActualTemperature = Column(Float)
    Reactor3Collet2On = Column(Boolean)
    Reactor3Collet2SetTemperature = Column(Float)
    Reactor3Collet2ActualTemperature = Column(Float)
    Reactor3Collet3On = Column(Boolean)
    Reactor3Collet3SetTemperature = Column(Float)
    Reactor3Collet3ActualTemperature = Column(Float)
    Reactor3StirMotor = Column(Integer)
    Reactor3RadiationDetector = Column(Float)

    def __init__(self, LogID,
            Timestamp,
            VacuumSystemOn,
            VacuumSystemPressure, CoolingSystemOn,
            PressureRegulator1SetPressure,
            PressureRegulator1ActualPressure,
            PressureRegulator2SetPressure,
            PressureRegulator2ActualPressure,
            GasTransferValveOpen,
            F18LoadValveOpen,
            HPLCLoadValveOpen,
            ReagentRobotPositionSet,
            ReagentRobotPositionActual,
            ReagentRobotPositionSetX,
            ReagentRobotPositionSetY,
            ReagentRobotPositionActualX,
            ReagentRobotPositionActualY,
            ReagentRobotStatusX,
            ReagentRobotStatusY,
            ReagentRobotErrorX,
            ReagentRobotErrorY,
            ReagentRobotControlX,
            ReagentRobotControlY,
            ReagentRobotCheckX,
            ReagentRobotCheckY,
            GripperSetDown,
            GripperSetUp,
            GripperSetOpen,
            GripperSetClose,
            GasTransferSetUp,
            GasTransferSetDown,
            Reactor1SetPosition,
            Reactor1ActualPosition,
            Reactor1SetY,
            Reactor1ActualY,
            Reactor1RobotStatus,
            Reactor1RobotError,
            Reactor1RobotControl,
            Reactor1RobotCheck,
            Reactor1SetUp,
            Reactor1SetDown,
            Reactor1Up,
            Reactor1Down,
            Reactor1Stopcock1Position,
            Reactor1Stopcock2Position,
            Reactor1Stopcock3Position,
            Reactor1Collet1On,
            Reactor1ColletSetTemperature,
            Reactor1ColletActualTemperature,
            Reactor1Collet2On,
            Reactor1Collet2SetTemperature,
            Reactor1Collet2ActualTemperature,
            Reactor1Collet3On,
            Reactor1Collet3SetTemperature,
            Reactor1Collet3ActualTemperature,
            Reactor1StirMotor,
            Reactor1RadiationDetector,
            Reactor2SetPosition,
            Reactor2ActualPosition,
            Reactor2SetY,
            Reactor2ActualY,
            Reactor2RobotStatus,
            Reactor2RobotError,
            Reactor2RobotControl,
            Reactor2RobotCheck,
            Reactor2SetUp,
            Reactor2SetDown,
            Reactor2Up,
            Reactor2Down,
            Reactor2Stopcock1Position,
            Reactor2Stopcock2Position,
            Reactor2Stopcock3Position,
            Reactor2Collet1On,
            Reactor2ColletSetTemperature,
            Reactor2ColletActualTemperature,
            Reactor2Collet2On,
            Reactor2Collet2SetTemperature,
            Reactor2Collet2ActualTemperature,
            Reactor2Collet3On,
            Reactor2Collet3SetTemperature,
            Reactor2Collet3ActualTemperature,
            Reactor2StirMotor,
            Reactor2RadiationDetector,
            Reactor3SetPosition,
            Reactor3ActualPosition,
            Reactor3SetY,
            Reactor3ActualY,
            Reactor3RobotStatus,
            Reactor3RobotError,
            Reactor3RobotControl,
            Reactor3RobotCheck,
            Reactor3SetUp,
            Reactor3SetDown,
            Reactor3Up,
            Reactor3Down,
            Reactor3Stopcock1Position,
            Reactor3Stopcock2Position,
            Reactor3Stopcock3Position,
            Reactor3Collet1On,
            Reactor3ColletSetTemperature,
            Reactor3ColletActualTemperature,
            Reactor3Collet2On,
            Reactor3Collet2SetTemperature,
            Reactor3Collet2ActualTemperature,
            Reactor3Collet3On,
            Reactor3Collet3SetTemperature,
            Reactor3Collet3ActualTemperature,
            Reactor3StirMotor,
            Reactor3RadiationDetector):
        """ Stupidest constructor in the whole f**king worls """
        self.LogID = LogID
        self.Timestamp = Timestamp
        self.VacuumSystemOn = VacuumSystemOn
        self.VacuumSystemPressure = VacuumSystemPressure
        self.CoolingSystemOn = CoolingSystemOn
        self.PressureRegulator1SetPressure = PressureRegulator1SetPressure
        self.PressureRegulator1ActualPressure = PressureRegulator1ActualPressure
        self.PressureRegulator2SetPressure = PressureRegulator2SetPressure
        self.PressureRegulator2ActualPressure = PressureRegulator2ActualPressure
        self.GasTransferValveOpen = GasTransferValveOpen
        self.F18LoadValveOpen = F18LoadValveOpen
        self.HPLCLoadValveOpen = HPLCLoadValveOpen
        self.ReagentRobotPositionSet = ReagentRobotPositionSet
        self.ReagentRobotPositionActual = ReagentRobotPositionActual
        self.ReagentRobotPositionSetX = ReagentRobotPositionSetX
        self.ReagentRobotPositionSetY = ReagentRobotPositionSetY
        self.ReagentRobotPositionActualX = ReagentRobotPositionActualX
        self.ReagentRobotPositionActualY = ReagentRobotPositionActualY
        self.ReagentRobotStatusX = ReagentRobotStatusX
        self.ReagentRobotStatusY = ReagentRobotStatusY
        self.ReagentRobotErrorX = ReagentRobotErrorX
        self.ReagentRobotErrorY = ReagentRobotErrorY
        self.ReagentRobotControlX = ReagentRobotControlX
        self.ReagentRobotControlY = ReagentRobotControlY
        self.ReagentRobotCheckX = ReagentRobotCheckX
        self.ReagentRobotCheckY = ReagentRobotCheckY
        self.GripperSetDown = GripperSetDown
        self.GripperSetUp = GripperSetUp
        self.GripperSetOpen = GripperSetOpen
        self.GripperSetClose = GripperSetClose
        self.GasTransferSetUp = GasTransferSetUp
        self.GasTransferSetDown = GasTransferSetDown
        self.Reactor1SetPosition = Reactor1SetPosition
        self.Reactor1ActualPosition = Reactor1ActualPosition
        self.Reactor1SetY = Reactor1SetY
        self.Reactor1ActualY = Reactor1ActualY
        self.Reactor1RobotStatus = Reactor1RobotStatus
        self.Reactor1RobotError = Reactor1RobotError
        self.Reactor1RobotControl = Reactor1RobotControl
        self.Reactor1RobotCheck = Reactor1RobotCheck
        self.Reactor1SetUp = Reactor1SetUp
        self.Reactor1SetDown = Reactor1SetDown
        self.Reactor1Up = Reactor1Up
        self.Reactor1Down = Reactor1Down
        self.Reactor1Stopcock1Position = Reactor1Stopcock1Position
        self.Reactor1Stopcock2Position = Reactor1Stopcock2Position
        self.Reactor1Stopcock3Position = Reactor1Stopcock3Position
        self.Reactor1Collet1On = Reactor1Collet1On
        self.Reactor1ColletSetTemperature = Reactor1ColletSetTemperature
        self.Reactor1ColletActualTemperature = Reactor1ColletActualTemperature
        self.Reactor1Collet2On = Reactor1Collet2On
        self.Reactor1Collet2SetTemperature = Reactor1Collet2SetTemperature
        self.Reactor1Collet2ActualTemperature = Reactor1Collet2ActualTemperature
        self.Reactor1Collet3On = Reactor1Collet3On
        self.Reactor1Collet3SetTemperature = Reactor1Collet3SetTemperature
        self.Reactor1Collet3ActualTemperature = Reactor1Collet3ActualTemperature
        self.Reactor1StirMotor = Reactor1StirMotor
        self.Reactor1RadiationDetector = Reactor1RadiationDetector
        self.Reactor2SetPosition = Reactor2SetPosition
        self.Reactor2ActualPosition = Reactor2ActualPosition
        self.Reactor2SetY = Reactor2SetY
        self.Reactor2ActualY = Reactor2ActualY
        self.Reactor2RobotStatus = Reactor2RobotStatus
        self.Reactor2RobotError = Reactor2RobotError
        self.Reactor2RobotControl = Reactor2RobotControl
        self.Reactor2RobotCheck = Reactor2RobotCheck
        self.Reactor2SetUp = Reactor2SetUp
        self.Reactor2SetDown = Reactor2SetDown
        self.Reactor2Up = Reactor2Up
        self.Reactor2Down = Reactor2Down
        self.Reactor2Stopcock1Position = Reactor2Stopcock1Position
        self.Reactor2Stopcock2Position = Reactor2Stopcock2Position
        self.Reactor2Stopcock3Position = Reactor2Stopcock3Position
        self.Reactor2Collet1On = Reactor2Collet1On
        self.Reactor2ColletSetTemperature = Reactor2ColletSetTemperature
        self.Reactor2ColletActualTemperature = Reactor2ColletActualTemperature
        self.Reactor2Collet2On = Reactor2Collet2On
        self.Reactor2Collet2SetTemperature = Reactor2Collet2SetTemperature
        self.Reactor2Collet2ActualTemperature = Reactor2Collet2ActualTemperature
        self.Reactor2Collet3On = Reactor2Collet3On
        self.Reactor2Collet3SetTemperature = Reactor2Collet3SetTemperature
        self.Reactor2Collet3ActualTemperature = Reactor2Collet3ActualTemperature
        self.Reactor2StirMotor = Reactor2StirMotor
        self.Reactor2RadiationDetector = Reactor2RadiationDetector
        self.Reactor3SetPosition = Reactor3SetPosition
        self.Reactor3ActualPosition = Reactor3ActualPosition
        self.Reactor3SetY = Reactor3SetY
        self.Reactor3ActualY = Reactor3ActualY
        self.Reactor3RobotStatus = Reactor3RobotStatus
        self.Reactor3RobotError = Reactor3RobotError
        self.Reactor3RobotControl = Reactor3RobotControl
        self.Reactor3RobotCheck = Reactor3RobotCheck
        self.Reactor3SetUp = Reactor3SetUp
        self.Reactor3SetDown = Reactor3SetDown
        self.Reactor3Up = Reactor3Up
        self.Reactor3Down = Reactor3Down
        self.Reactor3Stopcock1Position = Reactor3Stopcock1Position
        self.Reactor3Stopcock2Position = Reactor3Stopcock2Position
        self.Reactor3Stopcock3Position = Reactor3Stopcock3Position
        self.Reactor3Collet1On = Reactor3Collet1On
        self.Reactor3ColletSetTemperature = Reactor3ColletSetTemperature
        self.Reactor3ColletActualTemperature = Reactor3ColletActualTemperature
        self.Reactor3Collet2On = Reactor3Collet2On
        self.Reactor3Collet2SetTemperature = Reactor3Collet2SetTemperature
        self.Reactor3Collet2ActualTemperature = Reactor3Collet2ActualTemperature
        self.Reactor3Collet3On = Reactor3Collet3On
        self.Reactor3Collet3SetTemperature = Reactor3Collet3SetTemperature
        self.Reactor3Collet3ActualTemperature = Reactor3Collet3ActualTemperature
        self.Reactor3StirMotor = Reactor3StirMotor
        self.Reactor3RadiationDetector = Reactor3RadiationDetector


class RunLog(Base):
    """
    RunLog Object
    """
    __tablename__ = 'RunLog'
    LogID = Column(Integer, primary_key=True)
    Timestamp = Column(DateTime, default=datetime.now)
    Level = Column(Integer)
    UserID = Column(Integer, ForeignKey('Users.UserID'))
    SequenceID = Column(Integer, ForeignKey('Sequences.SequenceID'))
    ComponentID = Column(Integer, ForeignKey('Components.ComponentID'))
    Message = Column(String(length=1024))

    def __init__(self,
            timestamp=0,
            level=0,
            userID=None,
            seqID=None,
            compID=None,
            message="",
            logID = None):
        if logID is not None:
            self.LogID = logID
        self.Level = level
        self.UserID = userID
        self.SequenceID = seqID
        self.ComponentID = compID
        self.Message = message

    def __repr__(self):
        return '<RunLog(%s, %s)>' % (self.LogID, self.Timestamp)


class Sequence(Base):
    """
    Sequence Object
    """
    __tablename__ = 'Sequences'
    SequenceID = Column(Integer, primary_key=True)
    Name = Column(String(length=64))
    Comment = Column(String(length=255))
    Type = Column(String(length=20))
    CreationDate = Column(DateTime, default=datetime.now)
    UserID = Column(Integer, ForeignKey('Users.UserID'))
    FirstComponentID = Column(Integer)
    ComponentCount = Column(Integer)
    Valid = Column(Boolean, default=False)
    Dirty = Column(Boolean, default=False)
    first_component = relationship('Component',
            primaryjoin="Component.ComponentID=="
            "Sequence.FirstComponentID",
            foreign_keys=[FirstComponentID],
            uselist=False)
    component = relationship('Component',
            primaryjoin="Component.SequenceID=="
            "Sequence.SequenceID")

    def __init__(self,
            name="",
            comment="",
            seq_type="",
            creationData="",
            userID=0,
            firstComponentID=0,
            componentCount=0,
            valid=False,
            dirty=False):
        self.Name = name
        self.Comment = comment
        self.Type = seq_type
        self.CreationData = creationData
        self.UserID = userID
        self.FirstComponentID = firstComponentID
        self.ComponentCount = componentCount
        self.Valid = valid
        self.Dirty = dirty

    def __repr__(self):
        return '<Sequence(%s,%s)>' % (self.SequenceID, self.Name)

    def as_dict(self):
        """
        Function shall return the
        Sequences class attributes as a
        Python dictionary object.
        Funciton expects no parameters
        Function returns a Sequence as a
        dictionary object.
        """
        comp_dict = {}
        comp_dict['id'] = int(self.SequenceID)
        comp_dict['name'] = str(self.Name)
        comp_dict['comment'] = str(self.Comment)
        comp_dict['date'] = self.CreationDate.strftime('%m/%d/%Y')
        comp_dict['time'] = self.CreationDate.strftime('%H:%M.%S')
        comp_dict['components'] = int(self.ComponentCount)
        comp_dict['valid'] = bool(self.Valid)
        comp_dict['dirty'] = bool(self.Dirty)
        return comp_dict

    def update_from_dict(self, seq_dict):
        '''
        Updates the attributes of the sequence
        with the values of the passed in dict.
        Function expects a dictionary object
        with keys that map to the Sequence's
        attributes/fields.
        Function returns no output.
        '''
        # First validate the entries
        comp_vtor.check('check_sequence', seq_dict)
        # Valid, let's update the entries of the sequence
        # Grab the session object so we can modify via ORM
        sequence = session.query(Sequence).filter_by(\
                SequenceID = self.SequenceID).first()

        for key, value in seq_dict.iteritems():
            if key == "name":
                sequence.Username = value
            elif key == "comment":
                sequence.Comment = value
            elif key == "type":
                sequence.Type = value
            elif key == "userid":
                sequence.UserID = value
            elif key == "firstcomponentid":
                sequence.FirstComponentID = value
            elif key == "componentcount":
                sequence.ComponentCount = value
            elif key == "valid":
                sequence.Valid = value
            elif key == "dirty":
                sequence.Dirty = value
            elif key == "creationdate":
                sequence.CreationDate =\
                        datetime.strptime(value,\
                        '%Y-%m-%d %H:%M:%S')
            else:
                # Else we have an unknown key, flag it
                print "uhoh2"
                print "%s%s" % (key, value)
        session.commit()

class User(Base):
    """
    User Object
    """
    __tablename__ = 'Users'
    UserID = Column(Integer, primary_key=True)
    Username = Column(String(length=30), unique=True)
    Password = Column(String(length=30))
    FirstName = Column(String(length=20))
    LastName = Column(String(length=20))
    RoleID = Column(Integer, ForeignKey('Roles.RoleID'))
    Email = Column(String(30))
    Phone = Column(String(20))
    MessageLevel = Column(Integer)
    ClientState = Column(String(2048))
    sequences = relationship('Sequence', backref='user')
    runlogs = relationship('RunLog', backref='user')

    def __init__(self,
            username="",
            passwd="",
            firstname="",
            lastname="",
            roleID=0,
            email="",
            phone="",
            messageLevel=0,
            clientState=""):
        """ User constructor """
        self.Username = username
        self.Password = passwd
        self.FirstName = firstname
        self.LastName = lastname
        self.RoleID = roleID
        self.Email = email
        self.Phone = phone
        self.MessageLevel = messageLevel
        self.ClientState = clientState

    def __repr__(self):
        return '<User(%d,%s,%s,%s)>' % (self.UserID,
         self.Username,
         self.FirstName,
         self.LastName)

    def as_dict(self):
        """
        Function shall return the
        Users class attributes as a
        Python dictionary object.
        Funciton expects no parameters
        Function returns a User as a
        dictionary object.
        """
        user_dict = {'type': 'user'}
        user_dict['username'] = str(self.Username)
        user_dict['firstname'] = str(self.FirstName)
        user_dict['lastname'] = str(self.LastName)
        user_dict['accesslevel'] = int(self.RoleID)
        user_dict['email'] = str(self.Email)
        user_dict['phone'] = str(self.Phone)
        user_dict['messagelevel'] = int(self.MessageLevel)
        return user_dict

    def update_from_dict(self, user_dict):
        '''
        Updates the attributes of the user
        with the values of the passed in dict.
        Function expects a dictionary object
        with keys that map to the User's
        attributes/fields.
        Function returns no output.
        '''
        # First validate the entries
        comp_vtor.check('check_user', user_dict)
        # Valid, let's update the entries of the users
        # Grab the session object so we can modify via ORM
        user = session.query(User).filter_by(\
                UserID = self.UserID).first()
        for key, value in user_dict.iteritems():
            if key == "username":
                user.Username = value
            elif key == "password":
                # Encrypt password
                encrypt_pw = md5(value)
                user.Password = encrypt_pw.hexdigest()
            elif key == "firstname":
                user.FirstName = value
            elif key == "lastname":
                user.LastName = value
            elif key == "email":
                user.Email = value
            elif key == "phone":
                user.Phone = value
            elif key == "message_level":
                user.MessageLevel = value
            elif key == "role_id":
                user.RoleID = value
            elif key == "clientstate":
                user.ClientState = json.dumps(value)
            else:
                # Else we have an unknown key, flag it
                print "%s,%s" % (key, value)
        # Update to DB
        session.commit()

metadata = Base.metadata
Session = sessionmaker(bind=engine)
session = Session()
def loadSession():
    return session

if __name__ == '__main__':
    """ If the database and tables don't exist create them! """
    metadata.create_all(checkfirst=True)
    from IPython import embed
    embed()
