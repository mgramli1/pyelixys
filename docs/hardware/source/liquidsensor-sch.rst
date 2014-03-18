=======================
Liquid Sensor Subsystem
=======================
The liquid sensor subsystem is intended for use with the OPB350_ series tube liquid sensor.
Internally it consists of a photodiode and a photo transistor.  
The photo diode anode is the red wire, while the cathode is the black wire.
A current limiting resistor is provided on the board and power (3V3) is supplied by this subsystem.

Generally, phototransistors_ can be used as either a common-emitter or common-collector amplifier.
The emitter of the sensor is  connected to the green wire, while the collector is connected to the grey.
Our design will use it as the common-collector, as this is the design in the reference datasheet for the OPB350_ .
A adjustable 10kOhm trimpot allows the circuit to be *tuned* to the expected liquid.
A 2.5kOhm series resistor sets the default value.
Additionally we are using a MCP3204_ 8 channel ADC to sample the resulting signal.
This allows us to use software to set the liquid present threshold.

The schematic for the system is *SynthesizerLiquidSensor.SchDoc*

-------
Signals
-------

* SCK - SPI Clock signal
* MOSI - SPI Master Output Slave Input
* MISO - SPI Master Input Slave Output
* CS - Chip select signal

----------
Connectors
----------

4 pin Micro Mate-n-lok connector 3-794636-4_

---
ICs
---

* MCP3204_
	
	* The MCP3204 12-bit Analog-to-Digital Converter (ADC) combines high performance and low power consumption in a small package

---------
Schematic
---------
(SynthesizerLiquidSensors.SchDoc)

.. _OPB350: http://technology.ttelectronics.com/images/uploads/productdatasheets/OPB350.pdf
.. _phototransistors: http://www.fairchildsemi.com/an/AN/AN-3005.pdf
.. _MCP3204: http://www.microchip.com/wwwproducts/Devices.aspx?dDocName=en010533
.. _3-794636-4: http://www.te.com/catalog/pn/en/3-794636-4?RQPN=3-794636-4