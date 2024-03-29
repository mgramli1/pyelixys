#/usr/bin/env python
""" This script acts like the elixys hw
it connects as a client to the websocket server
and streams packets properly formed.
It knows how to "act" like the hardware and has
callbacks that cause changes to the system state,
and consequently to the packets just as would
on the real hardaware.
"""
import sys
import time
import signal
import thread
import threading
import struct
import Queue

import websocket
from websocket import ABNF

from multiprocessing import Event

from pyelixys.logs import hwsimlog as log
from pyelixys.hal.status import Status
from pyelixys.hal.elixysobject import ElixysObject
from threading import Timer
import time

import collections


###Added 5/5/2014 by: joshua.thompson@sofiebio.com
stop_event = Event() #ws client will stop when stop_event is set (see on_close function)
###

class AxisStatus(object):

    INEMERGBIT = (1 << 15)
    INCRDYBIT = (1 << 14)
    INZONE1BIT = (1 << 13)
    INZONE2BIT = (1 << 12)
    INPZONEBIT = (1 << 11)
    INMODESBIT = (1 << 10)
    INWENDBIT = (1 << 9)
    INSVONBIT = (1 << 4)
    INALMBIT = (1 << 3)
    INMOVEBIT = (1 << 2)
    INHOMENDBIT = (1 << 1)
    INPOSENDBIT = (1 << 0)


    def __init__(self, status_value=0):
        self.status = status_value
        #debug
        #print "__init__ self.status = status_value: " + str(self.status)

    def isMoving(self):
        if self.status & self.INMOVEBIT:
            return True
        return False

    def setMoving(self):
        
        self.status |= self.INMOVEBIT
        #debug
        #print "setMoving: self.status |= self.INMOVEBIT: " + str(self.status)

    def clearMoving(self):
        self.status &= ~self.INMOVEBIT
        #debug
        #print "clearMoving: self.status &= ~self.INMOVEBIT: " + str(self.status)

    def isAlarm(self):
        if self.status & self.INALMBIT:
            return True
        return False

    def setAlarm(self):
        self.status |= self.INALMBIT
        #debug
        #print "setAlarm: self.status |= self.INALMBIT: " + str(self.status)

    def clearAlarm(self):
        self.status &= ~self.INALMBIT
        #debug
        #print "clearAlarm: self.status &= ~self.INALMBIT: " + str(self.status)

    def isHome(self):
        if self.status & self.INHOMENDBIT:
            return True
        return False

    def setHome(self):
        self.status |= self.INHOMENDBIT
        #debug
        #print "setHome: self.status |= self.INHOMENBIT: " + str(self.status)

    def clearHome(self):
        self.status &= ~self.INHOMENDBIT
        #debug
        #print "clearHome: self.status &= ~self.INHOMENBIT: " + str(self.status)

    def isInPosition(self):
        if self.status & self.INPOSENDBIT:
            return True
        return False

    def setInPosition(self):
        self.status |= self.INPOSENDBIT
        #debug
        #print "setInPosition: self.status |= self.INPOSENBIT: " + str(self.status)

    def clearInPosition(self):
        self.status &= ~self.INPOSENDBIT
        #debug
        #print "clearInPosition: self.status &= ~self.INPOSENBIT: " + str(self.status)

    def isServoOn(self):
        if self.status & self.INSVONBIT:
            return True
        return False

    def setServoOn(self):
        self.status |= self.INSVONBIT
        #debug
        #print "setServoOn: self.status |= self.INSVONBIT: " + str(self.status)

    def clearServoOn(self):
        self.status &= ~self.INSVONBIT
        #debug
        #print "clearServoOn: self.status &= ~self.INSVONBIT: " + str(self.status)

    def isPosLoad(self):
        if self.status & self.INWENDBIT:
            return True
        return False

    def setPosLoad(self):
        self.status |= self.INWENDBIT
        #debug
        #print "setPosLoad: self.status |= self.INWENDBIT: " + str(self.status)

    def clearPosLoad(self):
        self.status &= ~self.INWENDBIT
        #debug
        #print "clearPosLoad: self.status &= ~self.INWENDBIT: " + str(self.status)

    def isPosZone(self):
        if self.status & self.INPZONEBIT:
            return True
        return False

    def setPosZone(self):
        self.status |= self.INPZONEBIT
        #debug
        #print "setPosZone: self.status |= self.INPZONEBIT: " + str(self.status)

    def clearPosZone(self):
        self.status &= ~self.INPZONEBIT
        #debug
        #print "clearPosZone: self.status &= ~self.INPZONEBIT: " + str(self.status)

    def isZone1(self):
        if self.status & self.INZONE1BIT:
            return True
        return False

    def setZone1(self):
        self.status |= self.INZONE1BIT
        #debug
        #print "setZone1: self.status |= self.INZONE1BIT: " + str(self.status)

    def clearZone1(self):
        self.status &= ~self.INZONE1BIT
        #debug
        #print "clearZone1: self.status &= ~self.INZONE1BIT: " + str(self.status)

    def isZone2(self):
        if self.status & self.INZONE2BIT:
            return True
        return False

    def setZone2(self):
        self.status |= self.INZONE2BIT
        #debug
        #print "setZone2: self.status |= self.INZONE2BIT: " + str(self.status)

    def clearZone2(self):
        self.status &= ~self.INZONE2BIT
        #debug
        #print "setZone2: self.status &= ~self.INZONE2BIT: " + str(self.status)

    def isCtrlReady(self):
        if self.status & self.INCRDYBIT:
            return True
        return False

    def setCtrlReady(self):
        self.status |= self.INCRDYBIT
        #debug
        #print "setCtrlReady: self.status |= self.INCRDYBIT: " + str(self.status)

    def clear(self):
        self.status = 0
        self.setHome()
        self.setZone1()
        self.setZone2()
        self.setCtrlReady()
        self.setInPosition()
        self.setServoOn()

    def __repr__(self):
        return "AxisStatus(0x%X)" % self.status

    def __str__(self):
        return "0x%X" % self.status


class StatusSimulator(Status):
    """
    The StatusSimulator object is intended to
    act like a status object but can also generate
    the proper binary "packet" format that the HW
    generates.  The ElxiysSimulator uses it to keep
    track of its simulate HW state, and then
    generate properly formatted packets to ship
    to the host
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the status with values we would expect when
        the HW first turns on
        """
        super(StatusSimulator, self).__init__(self, *args, **kwargs)

        log.debug("Initialize The StatusSimulator")
        self.is_valid = True

        log.debug("Set the initial state of the system")
        # Initialize Header
        self.store['Header'] = {}
        self.store['Header']['packet_id'] = 0
        self.store['Header']['packet_type'] = 63
        self.store['Header']['system_error_code'] = 0

        # Initialize Mixers
        mixers = []
        self.store['Mixers'] = {}
        for i in range(self.sysconf['Mixers']['count']):
            mixer = {'duty_cycle':0.0, 'period': 0}
            self.store['Mixers'][i] = mixer
            mixers.append(mixer)

        self.store['Mixers']['Subs'] = mixers
        self.store['Mixers']['count'] = \
                self.sysconf['Mixers']['count']
        self.store['Mixers']['error_code'] = '\x00'
        self.store


        # Initialize Valves
        self.store['Valves'] = {}
        self.store['Valves']['error_code'] = '\x00'
        self.store['Valves']['state0'] = 0
        self.store['Valves']['state1'] = 0
        self.store['Valves']['state2'] = 0

        # Initialize Thermocouples
        thermocouples = []
        self.store['Thermocouples'] = {}
        for i in range(self.sysconf['Thermocouples']['count']):
            thermocouple = {'error_code': '\x00',
                            'temperature':25.0}
            self.store['Thermocouples'][i] = thermocouple
            thermocouples.append(thermocouple)

        self.store['Thermocouples']['Subs'] = thermocouples
        self.store['Thermocouples']['count'] = \
                self.sysconf['Thermocouples']['count']

        # Initialize AUX Thermocouples
        auxthermocouples = []
        self.store['AuxThermocouples'] = {}
        for i in range(self.sysconf['AuxThermocouples']['count']):
            auxthermocouple = {'error_code': '\x00',
                            'temperature':25.0}
            self.store['AuxThermocouples'][i] = auxthermocouple
            auxthermocouples.append(auxthermocouple)

        self.store['AuxThermocouples']['Subs'] = auxthermocouples
        self.store['AuxThermocouples']['count'] = \
                self.sysconf['AuxThermocouples']['count']

        # Initialize heaters
        self['Heaters'] = {'state':0}

        # Initialize Temperature Controllers
        tempctrls = []
        self.store['TemperatureControllers'] = {}
        for i in range(self.sysconf['TemperatureControllers']['count']):
            tempctrl = {'error_code':'\x00', 'setpoint':0.0}
            self.store['TemperatureControllers'][i] = tempctrl
            tempctrls.append(tempctrl)


        self.store['TemperatureControllers']['error_code'] = 0
        self.store['TemperatureControllers']['Subs'] = tempctrls
        self.store['TemperatureControllers']['count'] = \
                self.sysconf['TemperatureControllers']['count']

        # Initialize SMC Interfaces
        smcinterfaces = []
        self.store['SMCInterfaces'] = {}
        for i in range(self.sysconf['SMCInterfaces']['count']):
            smcinterface = {'analog_in':0.0,
                            'analog_out':0.0}
            self.store['SMCInterfaces'][i] = smcinterface
            smcinterfaces.append(smcinterface)

        self.store['SMCInterfaces']['Subs'] = smcinterfaces
        self.store['SMCInterfaces']['count'] = \
                self.sysconf['SMCInterfaces']['count']
        self.store['SMCInterfaces']['error_code'] = '\x00'

        # Initialize Fans
        self.store['Fans'] = {}
        self.store['Fans']['state'] = '\x01'

        # Initialize Linear Actuators
        linacts = []
        self['LinearActuators'] = dict()

        self.linact_stats = []

        for i in range(self.sysconf['LinearActuators']['count']):
            stat = AxisStatus()
            stat.clear()
            self.linact_stats.append(stat)
            self.linact_stats
            linact = {'error_code': 0,
                      'position': 0,
                      'requested_position':0}


            self.store['LinearActuators'][i] = linact
            linacts.append(linact)

        self['LinearActuators']['error_code'] = 0
        self['LinearActuators']['Subs'] = linacts
        self['LinearActuators']['count'] = \
                self.sysconf['LinearActuators']['count']



        # Initialize Digital Inputs
        self.store['DigitalInputs'] = {}
        self.store['DigitalInputs']['error_code'] = '\x00'
        self.store['DigitalInputs']['state'] = 4095

        # Initialize Liquid Sensors
        liqsensors = []
        self.store['LiquidSensors'] = {}
        for i in range(self.sysconf['LiquidSensors']['count']):
            liqsensor = {'analog_in':0.0}
            self.store['LiquidSensors'][i] = liqsensor
            liqsensors.append(liqsensor)

        self.store['LiquidSensors']['Subs'] = liqsensors
        self.store['LiquidSensors']['count'] = \
                self.sysconf['LiquidSensors']['count']
        self.store['LiquidSensors']['error_code'] = '\x00'

        radsensors = []
        self['RadiationSensors'] = dict()
        self['RadiationSensors']['error_code']= '\x00'

        for i in range(self.sysconf['RadiationSensors']['count']):
            radsens = {'error_code': 0,
                      'analog_in':0}

            self.store['RadiationSensors'][i] = radsens

        self['RadiationSensors']['Subs'] = radsensors

        self['RadiationSensors']['count']= \
                self.sysconf['RadiationSensors']['count']

        for key,value in self.store.items():
            setattr(self,key,value)

    def update_linact_state(self):

        for i in range(self.sysconf['LinearActuators']['count']):
            self.store['LinearActuators'][i]['error_code'] = self.linact_stats[i].status


    def generate_packet_data(self):
        """ This function reads the current state
        and then formats it properly to send to the host
        via the websocket protocol.  This format is 'binary'
        and so it is essential to get right!! Or the
        host will get invalid data.  To do this we read the proper
        format from the config file (see sysconf on the ElixysObject)
        """

        self.update_linact_state()

        subs = self.fmt.subsystems
        vals = []
        for subname, subcount, subvals in subs:
            # Top Level params
            ## print "BEGIN:", subname
            topparams = subvals.keys()
            ## print "TOPPARAMS", topparams
            repeat = False
            if "Repeat" in topparams:
                ## print subname,"REPEAT"
                repeat = True
                topparams.remove('Repeat')

            ## print "TOPPARAMS", topparams
            if not topparams is None:
                for topparam in topparams:
                    
                    #print subname,":",topparam
                    vals.append(self.store[subname][topparam])

            if "Repeat" in subvals:
                for i in range(subcount):
                    for subparam in subvals['Repeat'].keys():
                        vals.append(self.store[subname][i][subparam])
                      
                        #print subname,i,":", subcount, subvals['Repeat'].keys()



        return vals


    def generate_packet(self):
        """ Take the data from which we properly arranged
        and pack it properly to produce our "binary" packet.
        Ship it to the host for to convert back to python types!
        """
        data = self.generate_packet_data()
        fmtstruct = self.fmt.get_struct()
        try:
            return fmtstruct.pack(*data)

        except Exception as e:
            log.error(str(data))
            raise e
        #self.store[sub[0]]



class ElixysSimulator(ElixysObject):
    """ The ElixysSimulator object reads the incoming packets
    from the host/user and updates its state appropriately
    This object has the proper methods on it to simulate
    the HW.  These methods are registered to react to
    the proper commands coming in from the host/user
    """

    def __init__(self):
        """ The ElixysSimulator initializes its
        status and then registers the callbacks to be executed
        when the commands come in from the host/user
        """
        self.status = StatusSimulator()
        self.cb_map = {}
        log.debug("Initialize the ElixysSimulator, register callbacks")

        # Setup Callbacks for Mixer commands
        self.register_callback('Mixers',
                               'set_period',
                               self.mixers_set_period)

        self.register_callback('Mixers',
                               'set_duty_cycle',
                               self.mixers_set_duty_cycle)

        # Setup Callbacks for Valve commands
        self.register_callback('Valves',
                               'set_state0',
                               self.valves_set_state0)

        self.register_callback('Valves',
                               'set_state1',
                               self.valves_set_state1)

        self.register_callback('Valves',
                               'set_state2',
                               self.valves_set_state2)

        # Setup Callbacks for Temperature controllers
        self.register_callback('TemperatureControllers',
                               'set_setpoint',
                               self.tempctrl_set_setpoint)

        self.register_callback('TemperatureControllers',
                               'turn_on',
                               self.tempctrl_turn_on)

        self.register_callback('TemperatureControllers',
                               'turn_off',
                               self.tempctrl_turn_off)

        # Setup Callbacks for SMC Intrefaces
        self.register_callback('SMCInterfaces',
                               'set_analog_out',
                               self.smcinterfaces_set_analog_out)

        # Setup Callbacks for Fans
        self.register_callback('Fans',
                               'turn_on',
                               self.fans_turn_on)

        self.register_callback('Fans',
                               'turn_off',
                               self.fans_turn_off)

        # Setup Callback for Linear Actuators
        self.register_callback('LinearActuators',
                               'set_requested_position',
                               self.linacts_set_requested_position)

        self.register_callback('LinearActuators',
                               'home_axis',
                               self.linacts_home_axis)

        self.register_callback('LinearActuators',
                               'gateway_start',
                               self.linacts_gateway_start)

        self.register_callback('LinearActuators',
                               'turn_on',
                               self.linacts_turn_on)

        self.register_callback('LinearActuators',
                               'pause',
                               self.linacts_pause)

        self.register_callback('LinearActuators',
                               'start',
                               self.linacts_start)

        self.register_callback('LinearActuators',
                               'brake_release',
                               self.linacts_brake_release)

        self.register_callback('LinearActuators',
                               'reset',
                               self.linacts_reset)

        self.tempctrl_thread = thread.start_new_thread(self.run_tempctrls,())


    def parse_cmd(self, cmd_pkt):
        """
        Parse the cmd sent from the host
        Expect little endian
        -first integer is the cmd_id
        -second integer is the device_id
            You can think of this as a 2 integer
            long register we are writing too
        - the parameter type is variable,
            so we look it up and get the callback fxn that will change
            the proper state variable (or start a thread that will simulate
            some HW change)
        """
        log.debug("Testelixyshw client parse_cmd")
        # Create struct for unpacking the cmd_id and dev_id
        cmd_id_struct = struct.Struct("<ii")

        # Length of the packet
        len_cmd_id = cmd_id_struct.size

        # Extract cmd_id and dev_id
        cmd_id, dev_id = cmd_id_struct.unpack(cmd_pkt[:len_cmd_id])
        log.debug("CMDID:#%d|DEVID:#%d", cmd_id, dev_id)

        # Look up callback and parameter type
        cb, param_fmt_str = self.cb_map[cmd_id]

        # Create struct to unpack the parameter
        param_struct = struct.Struct(param_fmt_str)

        # Unpack paramter depending on expected type
        param = param_struct.unpack(cmd_pkt[len_cmd_id:])
        log.debug("PARAM:%s", param)

        # Return the cb fxn, the dev_id and the param
        # Something else can pass the dev_id and param in to callback
        # This simulates some HW action as a result of a user/host command
        return (cb, dev_id, param)


    def register_callback(self,sub_sys,cmd_name, fxn):
        """ This method is a shortcut for regestering
        a callback with some subsystem and cmd name
        """
        cmd_id, param_fmt = self.lookup_cmd(sub_sys,cmd_name)
        self.cb_map[cmd_id] = (fxn, param_fmt)

    def lookup_cmd(self, sub_sys, cmd_name):
        """
        Just a shortcut for getting the commands infor
        associated with a sub_system (think "Mixers")
        and a cmd name (this will return some integer and
        parameter expected format!
        """
        return self.sysconf[sub_sys]['Commands'][cmd_name]

    def run_callback(self, cmdpkt):
        """
        When a command comes in from the user/host
        this fxn is used to properly parse
        the packet and execute the proper callback
        """

        log.debug("Execute PKT: %s",repr(cmdpkt))

        # Determine callback to exectue
        cmdfxn, dev_id, param = self.parse_cmd(cmdpkt)
        # Execute the callback
        cmdfxn(dev_id, *param)
    
    

    def mixers_set_period(self, devid, period):
        """ Mixer set period callback """
        log.debug("Set mixer %d period = %d", devid, period)
        self.status.Mixers[devid]['period'] = period

    def mixers_set_duty_cycle(self, devid, duty):
        """ Mixer set the duty cycle """
        log.debug("Set mixer %d duty cycle = %f", devid, duty)
        self.status.Mixers[devid]['duty_cycle'] = duty

    def valves_set_state0(self, devid, state):
        """ Set valve state0 """
        log.debug("Set valve state0 = %s", bin(state))
        self.status.Valves['state0'] = state
        self.update_digital_inputs()

    def valves_set_state1(self, devid, state):
        """ Set valve state1 """
        log.debug("Set valve state1 = %s", bin(state))
        self.status.Valves['state1'] = state
        self.update_digital_inputs()

    def valves_set_state2(self, devid, state):
        """ Set valve state2 """
        log.debug("Set valve state2 = %s", bin(state))
        self.status.Valves['state2'] = state

    def tempctrl_set_setpoint(self, devid, value):
        """ Set temperature controller setpoint """
        log.debug("Set temperature controller %d setpoint = %f",
                    devid, value)
        self.status.TemperatureControllers[devid]['setpoint'] = value

    def tempctrl_turn_on(self, devid, value=None):
        """ Turn temperature controller on """
        log.debug("Turn on temperture controller %d", devid)
        self.status.TemperatureControllers[devid]['error_code'] = '\x01'

    def tempctrl_turn_off(self, devid, value=None):
        """ Turn off temperature controllers """
        log.debug("Turn off temperature controller %d", devid)
        self.status.TemperatureControllers[devid]['error_code'] = '\x00'

    def smcinterfaces_set_analog_out(self, devid, value):
        """ SMC Interface set analog out """
        log.debug(" SMC Interface %d set analog out = %f", devid, value)

    def fans_turn_on(self, devid, value=None):
        """ Fans turn on """
        log.debug("Turn on Fan %d", devid)
        state = self.status.Fans['state']
        state |= 1 << devid
        self.status.Fans['state'] = state

    def fans_turn_off(self, devid, value=None):
        """ Fans turn off """
        log.debug("Turn off Fan %d", devid)
        state = self.status.Fans['state']
        state &= ~(1 << devid)
        self.status.Fans['state'] = state

    ''' this function is already define (see below) -- take out once confirmed with Henry
    def linacts_set_requested_position(self, devid, position):
        """ Linear Actuator set requested position """
        log.debug("Set the linear actuator %d requested position = %d",
                    devid, position)
    '''
        
    def linacts_home_axis(self, devid, value=None):
        """ Linear Actuator home axis """
        log.debug("Home the linear actuator %d", devid)
        self.status.LinearActuators[devid]['requested_position'] = 0 #Added 5/7/2014 by joshua.thompson@sofiebio.com

        def fxn():
            self.status.linact_stats[devid].clearHome()
            self.status.linact_stats[devid].setMoving()
            time.sleep(1.0)
            while not self.status.LinearActuators[devid]['position'] <= 0:
                self.status.LinearActuators[devid]['position'] -= 10
                if self.status.LinearActuators[devid]['position'] < 0:
                    self.status.LinearActuators[devid]['position'] = 0
                time.sleep(0.1)

            self.status.linact_stats[devid].clear()

        #Timer(0.5, fxn).start() #taken out 5/8/2014 by joshua.thompson@sofiebio.com
        time.sleep(0.5) #added
        fxn()#added
        

    def linacts_gateway_start(self, devid, value=None):
        log.debug("Set the gateway start bit")

    def linacts_set_requested_position(self, devid, value=0):
        log.debug("Set requested position of actuator %d to %f mm" \
                % (devid, value/100.0))
        self.status.LinearActuators[devid]['requested_position'] = value

    def linacts_turn_on(self, devid, value=None):
        log.debug("Axis %d turn on" % devid)

        self.status.linact_stats[devid].setServoOn()
        if (self.status.LinearActuators[devid]['position'] == self.status.LinearActuators[devid]['requested_position']):
            self.status.linact_stats[devid].setInPosition()



    def linacts_pause(self, devid, value=None):
        log.debug("Axis %d pause" % devid)
        self.status.linact_stats[devid].clearMoving()


    def linacts_start(self, devid, value=None):
        log.debug("Axis %d start" % devid)

        def fxn():
            self.status.linact_stats[devid].clearInPosition()
            self.status.linact_stats[devid].setMoving()

            while not (self.status.LinearActuators[devid]['position'] == self.status.LinearActuators[devid]['requested_position']):
                print 'linacts_start() running: pos = ' + str(self.status.LinearActuators[devid]['position']) #debug

                # If our error less than 5mm set them equal
                if abs(self.status.LinearActuators[devid]['position'] - self.status.LinearActuators[devid]['requested_position']) < 500 :
                    self.status.LinearActuators[devid]['position'] = self.status.LinearActuators[devid]['requested_position']
                    break;

                # If position is greater than req position deincrement
                if (self.status.LinearActuators[devid]['position']  > self.status.LinearActuators[devid]['requested_position']):
                    step = -100

                # Else increment
                else:
                    step = 100

                self.status.LinearActuators[devid]['position'] += step
                time.sleep(0.01)

            self.status.linact_stats[devid].clearMoving()
            self.status.linact_stats[devid].setInPosition()

        #Timer(0.5, fxn).start()
        time.sleep(0.5) #added
        fxn()#added

    def linacts_brake_release(self, devid, value=None):
        log.debug("Axis %d brake release" % devid)

    def linacts_reset(self, devid, value=None):
        log.debug("Axis %d reset" % devid)
        self.status.linact_stats[devid].clear()
        self.status.linact_stats[devid].clearHome()


    def update_digital_inputs(self):
        """ Evaluate the valve states and determine
        expected digital input status
        """

        # Check for Reactor 0 down (DI 0)
        if ((self.status['Valves']['state0'] & (1 << 6)) and
                not(self.status['Valves']['state1'] & (1 << 6))):
            log.debug("Reactor 0 will go down. DI0=True")
            def fxn():
                self.status['DigitalInputs']['state'] &= ~(1 << 0)
            #Timer(2.0, fxn).start()
            time.sleep(0.5) #added
            fxn()#added
            self.status['DigitalInputs']['state'] |= (1 << 1)



        # Check for Reactor 0 up (DI 1)
        if ((self.status['Valves']['state1'] & (1 << 6)) and
                not(self.status['Valves']['state0'] & (1 << 6))):
            log.debug("Reactor 0 will go up. DI1=True")
            def fxn():
                self.status['DigitalInputs']['state'] &= ~(1 << 1)
            #Timer(2.0,fxn).start()
            time.sleep(2.0) #added
            fxn()#added
            self.status['DigitalInputs']['state'] |= (1 << 0)


        # Check for Reactor 1 down (DI 3)
        if ((self.status['Valves']['state0'] & (1 << 5)) and
                not(self.status['Valves']['state1'] & (1 << 5))):
            log.debug("Reactor 1 will go down. DI3=True")
            def fxn():
                self.status['DigitalInputs']['state'] &= ~(1 << 3)
            #Timer(2.0, fxn).start()
            time.sleep(2.0) #added
            fxn()#added
            self.status['DigitalInputs']['state'] |= (1 << 2)



        # Check for Reactor 1 up (DI 2)
        if ((self.status['Valves']['state1'] & (1 << 5)) and
                not(self.status['Valves']['state0'] & (1 << 5))):
            log.debug("Reactor 1 will go up. DI2=True")
            def fxn():
                self.status['DigitalInputs']['state'] &= ~(1 << 2)
            #Timer(2.0,fxn).start()
            time.sleep(2.0) #added
            fxn()#added
            self.status['DigitalInputs']['state'] |= (1 << 3)


        # Check for Reactor 2 down (DI 5)
        if ((self.status['Valves']['state0'] & (1 << 4)) and
                not(self.status['Valves']['state1'] & (1 << 4))):
            log.debug("Reactor 1 will go down. DI3=True")
            def fxn():
                self.status['DigitalInputs']['state'] &= ~(1 << 5)
            #Timer(2.0, fxn).start()
            time.sleep(2.0) #added
            fxn()#added
            self.status['DigitalInputs']['state'] |= (1 << 4)



        # Check for Reactor 2 up (DI 4)
        if ((self.status['Valves']['state1'] & (1 << 4)) and
                not(self.status['Valves']['state0'] & (1 << 4))):
            log.debug("Reactor 1 will go up. DI2=True")
            def fxn():
                self.status['DigitalInputs']['state'] &= ~(1 << 4)
            #Timer(2.0,fxn).start()
            time.sleep(2.0) #added
            fxn()#added
            self.status['DigitalInputs']['state'] |= (1 << 5)

        # Check for Gripper up (DI 6)
        if ((self.status['Valves']['state0'] & (1 << 10)) and
                not(self.status['Valves']['state1'] & (1 << 10))):
            log.debug("Gripper will go up. DI6=True")
            def fxn():
                self.status['DigitalInputs']['state'] &= ~(1 << 6)
            #Timer(1.0,fxn).start()
            time.sleep(1.0) #added
            fxn()#added
            self.status['DigitalInputs']['state'] |= (1 << 7)

        # Check for Gripper lower (DI 7)
        if ((self.status['Valves']['state1'] & (1 << 10)) and
                not(self.status['Valves']['state0'] & (1 << 10))):
            log.debug("Gripper will go down. DI7=True")
            def fxn():
                self.status['DigitalInputs']['state'] &= ~(1 << 7)
            #Timer(1.0,fxn).start()
            time.sleep(1.0) #added
            fxn()#added
            self.status['DigitalInputs']['state'] |= (1 << 6)

        # Check for GasTransfer up (DI 9)
        if ((self.status['Valves']['state1'] & (1 << 9)) and
                not(self.status['Valves']['state0'] & (1 << 9))):
            log.debug("GasTransfer will go up. DI9=True")
            def fxn():
                self.status['DigitalInputs']['state'] &= ~(1 << 9)
            #Timer(1.0,fxn).start()
            time.sleep(1.0) #added
            fxn()#added
            self.status['DigitalInputs']['state'] |= (1 << 8)

        # Check for GasTransfer lower (DI 8)
        if ((self.status['Valves']['state0'] & (1 << 9)) and
                not(self.status['Valves']['state1'] & (1 << 9))):
            log.debug("GasTransfer will go down. DI9=True")
            def fxn():
                self.status['DigitalInputs']['state'] &= ~(1 << 8)
            #Timer(1.0,fxn).start()
            time.sleep(1.0) #added
            fxn()#added
            self.status['DigitalInputs']['state'] |= (1 << 9)

        # Check for Gripper Open  (DI 10)
        if ((self.status['Valves']['state1'] & (1 << 8)) and
                not(self.status['Valves']['state0'] & (1 << 8))):
            log.debug("Gripper will open. DI10=True")
            def fxn():
                self.status['DigitalInputs']['state'] &= ~(1 << 10)
            #Timer(0.2, fxn).start()
            time.sleep(0.2) #added
            fxn()#added
            self.status['DigitalInputs']['state'] |= (1 << 11)

        # Check for Gripper Close (DI 11)
        if ((self.status['Valves']['state0'] & (1 << 8)) and
                not(self.status['Valves']['state1'] & (1 << 8))):
            log.debug("Gripper will close. DI11=True")
            def fxn():
                self.status['DigitalInputs']['state'] &= ~(1 << 11)
            #Timer(0.2, fxn).start()
            time.sleep(0.2) #added
            fxn()#added
            self.status['DigitalInputs']['state'] |= (1 << 10)

    def run_tempctrls(self):
        while True:
            self.manage_tempctrls()
            time.sleep(0.5)

    def manage_tempctrls(self):
        for devid in range(9):
            tempctrl = self.status['TemperatureControllers'][devid]
            thermo = self.status['Thermocouples'][devid]
            if tempctrl['error_code'] == '\x01':
                # TempCtrl is on
                if thermo['temperature'] < tempctrl['setpoint']:
                    thermo['temperature'] += 0.5
                else:
                    # We are at temperature
                    #  do nothing
                    pass
            else:
                # If tempctrl is off slowly cool
                if thermo['temperature'] > 25.0:
                    thermo['temperature'] -= 0.05

e = ElixysSimulator()
simstatus = e.status

cmds = Queue.Queue()

def on_message(ws, message):
    """ When test client receives a command print it to console """
   
    print "FROM SERVER (sim talking): %s" % repr(message)
    #cmds.put(message)
    
    e.run_callback(message)
    #increment packet id after callback returns
    e.status['Header']['packet_id'] = e.status['Header']['packet_id'] + 1 #increment packet_id so host knows command completed
    print 'Incrementing packet id! from run_callback (client)'


def on_error(ws, error):
    """ If we have a communication error print it to console """
    print error


def on_close(ws):
    """ If websocket hardware server closes the connection print to console """
    stop_event.set() #set stop_event so that while loop in on_open() stops
    print 'simulator websocket closed'


def on_open(ws):
    """ On opening a new connection to the websocket server take the
    test_data increment the packet_id and send it to the server as
    a status packet.  This is done in a thread so the main thread
    can still receive the incoming command packets and print them to
    the console """
    # i = 0 -- josh took this out
    def run(*args):
        i = 0
        while (stop_event.is_set() == False): #Added 5/5/2014 by joshua.thompson@sofiebio.com previously while (True)
            #log.debug("Sent packet id: #%d", i)
            
            pkt = e.status.generate_packet()
            ws.send(pkt, ABNF.OPCODE_BINARY)
            time.sleep(.2)
            i+=1
        #ws.close()
        #print "thread terminating..."
    thread.start_new_thread(run, ())


def exit_gracefully(signum, frame):
    """ If requested by signal, exit gracefully """
    print "Exit Gracefully, Ctrl+C pressed"
    sys.exit(0)


class Simulator(threading.Thread):
    """ Runs the websocket client simulator """

    def __init__(self):
        """ (Constructor) """
        #websocket.enableTrace(True) # Enable for websocket trace!
        super(Simulator, self).__init__()
       
      
        self.ws = websocket.WebSocketApp("ws://localhost:8888/ws",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
        
        self.ws.on_open = on_open
        
            
    def run(self):
        self.ws.run_forever()


def start_simulator_thread():
    """ Start the simulator in a thread
    create a websocket client and run it in
    thread.  Also grab the elixys simulator.
    """
    #websocket.enableTrace(True) # Enable for websocket trace!
    #ws = websocket.WebSocketApp("ws://localhost:8888/ws",
    #                            on_message=on_message,
    #                            on_error=on_error,
    #                            on_close=on_close)
    #ws.on_open = on_open
    #hwthread = thread.start_new_thread(ws.run_forever,())
    sim = Simulator()
    sim.start()
    
    return e, sim



if __name__ == "__main__":

    # Setup signal callback
    signal.signal(signal.SIGINT, exit_gracefully)
    ws, hwthread = start_simulator_thread()

    from IPython import embed
    embed()
