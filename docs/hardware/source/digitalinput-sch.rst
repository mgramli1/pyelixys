=======================
Digital Input Subsystem
=======================
The synthesizer unit has 6 pneumatic axis.  Each axis has a up and down sensor for a total of 12 position sensors.
There are two type of sensors.

* D-A96V_ is a mechanical reed type sensor
* D-M9N_ is a solid state hall effect type sensor

The reed sensor is used on all but 1 of the axis.
The gripper actuator requires the solid state sensor since this sensor is less sensitive a close range,
and the travel range of the gripper is very small.

Fortunately regardless of sensor type the same conditioning circuit can be used.
Each 6 pin connector can power and monitor 2 position sensors, either up or down.
Pins 1 & 2 on the connector provide power to sensors if required.
The solid state sensor requires power.
Pins 3 & 4 on the connector are the output from the sensors, they are pulled high using resistors.
The MCP23S18_ IO Expander is used to provide 16 input pins, all accessible on the SPI peripheral bus. 

-------
Signals
-------
The *digital input subsystem* exposes 6 signals.

* SCK - SPI Clock signal
* MOSI - SPI Master Output Slave Input
* MISO - SPI Master Input Slave Output
* CS - Chip select signal
* RESET - Reset signal
* INT - Interrupt signal if configured as inputs, not used in the valve driver design

----------
Connectors
----------
Two position sensors are connected to a connector. We are using the TE_ Connectivity Micro Mate-n-lok connectors.
The surface mount connectors are 3-794636-6_.

---
ICs
---  
* MCP23S18_

	* Microchip_ SPI IO Expander

-------
Sensors
-------	
* D-A96V_

	* Reed switches
	
* D-M9N_
	
	* Solid state auto switch

---------
Schematic
---------
(SynthesizerDigitalInputs.SchDoc)	
	
.. _MCP23S18: http://www.microchip.com/wwwproducts/Devices.aspx?dDocName=en537376
.. _D-A96V: http://www.coastpneumatics.com/americansmc/my1_w/2_my1_w_series_cylinders_switches.pdf
.. _D-M9N: http://www.smc.eu/portal/WebContent/local/DK/download_kataloger/pdf/D-M9_solid-state_aftaster(UK).pdf
.. _Microchip: http://www.microchip.com/
.. _3-794636-6: http://www.te.com/catalog/pn/en/3-794636-6
.. _TE: http://www.te.com/en/home.html