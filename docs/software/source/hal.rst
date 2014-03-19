# Full Documentation for the ElixysHAL

pyelixys.hal documentation
==========================

.. automodule:: pyelixys.hal

The ElixysObject
----------------
.. autoclass:: pyelixys.hal.elixysobject.ElixysObject
    :members:

The Hardware Config (hwconf)
----------------------------
.. automodule:: pyelixys.hal.hwconf

The Command Formatter
---------------------
.. automodule:: pyelixys.hal.cmdfmt

.. autoclass:: pyelixys.hal.cmdfmt.CommandFormatFactory
    :members:

The Hardware Commands
---------------------
.. automodule:: pyelixys.hal.cmds

.. autoclass:: pyelixys.hal.cmds.Command
    :members:

.. autoclass:: pyelixys.hal.cmds.CommandLookup
    :members:

The Hardware Status
-------------------
.. automodule:: pyelixys.hal.statusfmt

.. autoclass:: pyelixys.hal.statusfmt.StatusMessageFormatFactory
    :members:

.. automodule:: pyelixys.hal.status

.. autoclass:: pyelixys.hal.status.StatusThread
    :members:

.. autoclass:: pyelixys.hal.status.Status
    :members:

.. autoclass:: pyelixys.hal.status.ElixysReadOnlyError

The Websocket Server
--------------------
.. automodule:: pyelixys.hal.wsserver

.. autoclass:: pyelixys.hal.wsserver.WSHandler
    :members:

.. autoclass:: pyelixys.hal.wsserver.WSServerProcess
    :members:

.. autofunction:: pyelixys.hal.wsserver.start_server

.. autofunction:: pyelixys.hal.wsserver.stop_server

.. autofunction:: pyelixys.hal.wsserver.exit_gracefully


The Control Board Abstraction
-----------------------------
.. automodule:: pyelixys.hal.controlbox

.. autoclass:: pyelixys.hal.controlbox.ControlBoxSystem
    :members:

The Synthesizer Board Abstraction
---------------------------------

.. automodule:: pyelixys.hal.hal

.. autoclass:: pyelixys.hal.hal.SynthesizerObject
    :members:

.. autoclass:: pyelixys.hal.hal.SynthesizerSubObject
    :members:

.. autoclass:: pyelixys.hal.hal.StateMessageParser
    :members:

.. autoclass:: pyelixys.hal.hal.State
    :members:

.. autoclass:: pyelixys.hal.hal.Mixer
    :members:

.. autoclass:: pyelixys.hal.hal.Valve
    :members:

.. autoclass:: pyelixys.hal.hal.Thermocouple
    :members:

.. autoclass:: pyelixys.hal.hal.AuxThermocouple
    :members:

.. autoclass:: pyelixys.hal.hal.Heater
    :members:

.. autoclass:: pyelixys.hal.hal.TemperatureController
    :members:

.. autoclass:: pyelixys.hal.hal.SMCInterface
    :members:

.. autoclass:: pyelixys.hal.hal.Fan
    :members:

.. autoclass:: pyelixys.hal.hal.LinearActuator
    :members:

.. autoclass:: pyelixys.hal.hal.DigitalInput
    :members:

.. autoclass:: pyelixys.hal.hal.LiquidSensor
    :members:

.. autoclass:: pyelixys.hal.hal.SynthesizerHAL
    :members:

Notes On Working with the HAL
-----------------------------
It is possible to load the HAL directly and use
it to communicate with the board via a IPython
terminal.  The IPython terminal is like *extremely*
high powered CLI that you can explore the HAL
and the subsystems of the HAL.

From the root of the pyelixys repository
run the following command in your bash shell.

.. code-block:: bash

    python -m pyelixys.hal.hal

This command will create an instance of the
`pyelixys.hal.hal.SynthesizerHAL` and store it in
the variable `s`, start the websocket communication
server and finally start up and IPython terminal.

To see the status of the LinearActuators one could then type:

.. code-block:: python

    s.status.LinearActuators

This would return a dictionary with all the current linear
actuator parameters and status variable.

s.status itself is a dictionary like object and could also be
explored as in:

.. code-block:: python

    s.status['LinearActuators'][0]

Which would return the status of the first linear actuator.

Similarily one could send commands to the SynthesizerHAL
instance as shown here:

.. code-block:: python

    s.valves[0].on = True

Which would turn on the first of the 48 valves
on the elixys synthesizer board.

The Elixys System Level Abstraction
-----------------------------------

To make it even easier for the developer
a further level of abstraction was applied
the system in the `pyelixys.hal.system.System`
class.  It provides high level routines
so a developer can work with the
`reagent_robot` or the `reactor[0]` without directly
talking to the hardware via the SynthesizerHAL instance.

Each high-level abstraction of a subsystem is itself a class,
for example `pyelixys.hal.reactor.Reactor` making the developers
life that much easier.


The SystemObject
----------------
All subsystems, reactors, reagent robots, etc.
inherit from the SystemObject.

.. automodule:: pyelixys.hal.systemobject

.. autoclass:: pyelixys.hal.systemobject.SystemObject
    :members:


The Coolant Pump
----------------
The coolant pump can be turned on or off.
Yup thats it!

.. automodule:: pyelixys.hal.coolantpump

.. autoclass:: pyelixys.hal.coolantpump.CoolantPump
    :members:
    :inherited-members:

The F18 Delivery
----------------
The F18 delivery valve can be turned on or off

.. automodule:: pyelixys.hal.f18

.. autoclass:: pyelixys.hal.f18.F18
    :members:
    :inherited-members:

Multiple Pneumatic Actuators
----------------------------
The Elixys system has a total of
5 pneumatic linear actuators each
actuator has the same interface and
inherits from the PnuematicActuator class

.. automodule:: pyelixys.hal.pneumaticactuator

.. autoclass:: pyelixys.hal.pneumaticactuator.PneumaticActuator
    :members:
    :inherited-members:

The Gas Transfer Tool
---------------------
The GasTransfer is itself a instance of a PneumaticActuator
but can also control the gas transfer valve as well

.. automodule:: pyelixys.hal.gastransfer

.. autoclass:: pyelixys.hal.gastransfer.GasTransfer
    :members:
    :inherited-members:

The Gripper Tool
----------------
The Gripper is itself an instance of the PneumaticActuator
but can also open and close around a vial.

.. automodule:: pyelixys.hal.gripper

.. autoclass:: pyelixys.hal.gripper.Gripper
    :members:
    :inherited-members:

The Linear Axis
---------------
The Elixys system has a total of 5 linear actuators.
3 actuators on the reactors, and 2 actuators dedicated
to the reagent robot.  The LinearAxis class allows
the developer to initialize, home and move these actuators.

.. automodule:: pyelixys.hal.linearaxis

.. autoclass:: pyelixys.hal.linearaxis.LinearAxis
    :members:
    :inherited-members:

The Mixers
----------
The mixers can have their duty cycle and period set.
The duty cycle *should* be driectly proportional to
the RPM of the mixer motor on the Elixys Robot.
The Elixys Synthesizer has 3 mixer motors, one per reactor.

.. automodule:: pyelixys.hal.mixer

.. autoclass:: pyelixys.hal.mixer.Mixer
    :members:
    :inherited-members:

The Pressure Regulators
-----------------------
The Pressure Regulators can be used to set and/or
retrieve the current pressure setpoint.
The also provide methods to ramp the pressure
over an allotted time period.  The current pressure
can also be retrieved.

.. automodule:: pyelixys.hal.pressureregulator

.. autoclass:: pyelixys.hal.pressureregulator.PressureRegulator
    :members:
    :inherited-members:

The Stopcocks
-------------
The Stopcocks can be turned clockwise or counter-clockwise.
Each reactor has three associate stockcocks.

.. automodule:: pyelixys.hal.stopcock

.. autoclass:: pyelixys.hal.stopcock.Stopcock
    :members:
    :inherited-members:


The Temperature Controllers
---------------------------
The Temperature Controllers allow the user to set each
the temperature controller setpoints and the read the temperatures
from the thermocouples.

Each controller is an combination of the three individual
temperature controllers on each reactor.  Each reactor
has a three piece collet and each collet has an associated
temperature controller in firmware.

.. automodule:: pyelixys.hal.tempctrl

.. autoclass:: pyelixys.hal.tempctrl.TempCtrl
    :members:
    :inherited-members:

The Reactors
------------
The Reactor class is the primary access point to control
each of the three Reactors on the Elixys Radiochemistry
system.  Each reactor is itself an instance of the `PneumaticActuator`
class, and contains an associate `LinearAxis`.  Additionally,
it has a `TemperatureController`, a `Mixer`, a `F18` dispenser,
and three associated stopcocks.

.. automodule:: pyelixys.hal.reactor

.. autoclass:: pyelixys.hal.reactor.Reactor
    :members:
    :inherited-members:

The Reagent Robot
-----------------
The ReagentRobot is composed of 2 `LinearAxis`
the `GasTransfer` and `Gripper`, and the 3 `PressureRegulators`.

It has several **high-level** routines that can be used to move the
x,y robot to known locations in the hwconf.

.. automodule:: pyelixys.hal.reagentrobot

.. autoclass:: pyelixys.hal.reagentrobot.ReagentRobot
    :members:
    :inherited-members:

The Elixys System Abstraction Class
-----------------------------------
The `System` is composed of three `Reactor` objects,
a `ReagentRobot` object, 3 `PressureRegulator` objects,
a `F18` dispenser object, and a `CoolantPump`.
Creating an instance of the `System` will start the
websocket server.

.. automodule:: pyelixys.hal.system

.. autoclass:: pyelixys.hal.system.System
    :members:
    :inherited-members:

Working with the Elixys System Abstraction
-----------------------------------------
Developers will likely want to *play* with the elixys
robot.  This is fairly straightforward.
Load the system module on the hal to create an
instance of the `System` class and store it in the variable `s`.
The following command, when executed from the root of
the pyelixys repository will do this and start and IPython
shell so a developer can work interactively with the robot.
It should be noted that it is also possible to work without
the actual robot by starting the simulators, this can be done by modifiying
the `controlbox` and `synthesizer` parameters in the hwconf.ini
under the `Simulator` heading.

.. code-block:: bash

    python -m pyelixys.hal.system

For example to home the reagent robot from the IPython terminal
run the following:

.. code-block:: python

    s.reagent_robot.home()

Or to lift the first reactor:

.. code-block:: python

    s.reactors[0].lift()

* :ref:`search`
