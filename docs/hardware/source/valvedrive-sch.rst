================================
Pneumatic Valve Driver Subsystem
================================

The Remote Synthesizer system must be able to drive at least 32 24Volt air valves.  
For future expansion we will design the Synthesizer board to be able to drive a total of 48 pneumatic valves.

The valves are manufactured by SMC_.  The specific part number is SYJ3240-5MOZ.
The SYJ3000_ Series Valves require 0.55 watts starting power and 0.22 Watts holding power.
This is approximately 30mA peak current.  
To drive each valve we will use the Darlington transistor array ULN2803A_.
Each transistor is 50V capable and can deliver 500mA.  
Additionally an 2.7kOhm input resistor allows it to interface directly with CMOS devices. 
Each package comes with 8 transistors so we require at least 6 ULN2803A_ ICs for our 48 valves.


The valve driver subsystem is designed around the MCP23S18_ IO Expander.
This IC developed by Microchips allows our microcontroller to drive 16 IO pins using only the four signals
from the SPI bus (this includes the CS line).  

Each signal of the 16 expanded signals can then drive an individual signal on each Darlington transistor.
The schematic *SynthesizerValveDriver.SchDoc* shows a single MCP23S18_ controlling a pair of ULN2803A_ Darlington arrays for a total of 16 channels.
3 of these subsystems are required on the final design to allow us to drive a total of 48 channels.

-------
Signals
-------
The Valve Driver circuits exposes 6 signals.

* SCK - SPI Clock signal
* MOSI - SPI Master Output Slave Input
* MISO - SPI Master Input Slave Output
* CS - Chip select signal
* RESET - Reset signal
* INT - Interrupt signal if configured as inputs, not used in the valve driver design

----------
Connectors
----------
The 16 channels of each valve driver subsystem are connected using the TE_ Connectivity Micro Mate-n-lok connectors.
The surface mount connectors are 4-794627-6_ .

---
ICs
---  
* MCP23S18_
	
	* Microchip_ SPI IO Expander from Microchip

* ULN2803A_

	* TI_ 8 Darlington transistor array
	
---------
Actuators
---------

* SYJ3000_ series valves
	
	* Specific model SYJ3240-5MOZ 

---------
Schematic
---------
(SynthesizerValveDriver.SchDoc)
	
.. _SMC: http://www.smcpneumatics.com/ 
.. _SYJ3000: http://www.coastpneumatics.com/americansmc/SYJ3000/SYJ3000_Series_Valves.pdf
.. _ULN2803A: http://www.ti.com/lit/ds/symlink/uln2803a.pdf
.. _MCP23S18: http://www.microchip.com/wwwproducts/Devices.aspx?dDocName=en537376
.. _4-794627-6: http://www.te.com/catalog/pn/en/4-794627-6
.. _TE: http://www.te.com/en/home.html
.. _Microchip: http://www.microchip.com/
.. _TI: http://www.ti.com/