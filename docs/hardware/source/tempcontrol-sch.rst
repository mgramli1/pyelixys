================================
Temperature Controller Subsystem
================================
The synthesizer unit has 9 independent heating elements each with an individual thermocouple.
The synthesizer will need to maintain temperature on all three individual heaters.
Temperature control will be done in firmware on the LPC1768 microcontroller.
Each thermocouple temperature will be sampled by a Maxim MAX31855_ Cold-Junction compensated thermocouple to digital converter.
The MAX31855_ has a SPI interface and can be treated a standard device on the peripheral bus. 

For controlling the heater we will need to drive 9 solid state relays.
The heating elements each use 1 Amp at 120VAC, so each relay must be capable of supplying 1 Amp of current.  
The CX_ Series relay from Crydom_ can deliver 5 Amps at 480V.  This meets the specifications for a system intended for Europe.
The relay must be a zero crossing type since the heater are resistive loads.

An addition AC relay is required to drive the vacuum pump. This is an inductive load and so should be a random turn on type.
The motor on the vacuum uses less than 2 Amps.

The control signals from the relays comes from BSS84_ P-FET transistors, this is because the solid state relays accepts a control voltage of 4V - 15V outside the range of our microcontroller (3V3).
A MCP23S18_ IO expander is used to control the individual heater relay signals.

-------
Signals
-------

* SCK - SPI Clock signal
* MOSI - SPI Master Output Slave Input
* MISO - SPI Master Input Slave Output
* CS - Chip select
* INT - Interrupt, signals a change on inputs
* RESET - Reset device

----------
Connectors
----------
TBD

---
ICs
---
* MAX31855_

	* Accurate Thermocouple-to-Digital Converter IC Simplifies Designs and Lowers System Cost

* MCP23S18_

	* 16-bit I/O expander for high speed SPI™ Compatible interface

* CX_ Series SSR

	* SIP SSR - Ratings to 5A @ 280 VAC - SCR output for heavy industrial loads - AC or DC control - Zero-crossing (resistive loads) or random-fire (inductive loads) output
	
* BSS84_ P-FET

	* P-channel enhancement mode vertical DMOS transistor
	
--------
Actuator
--------

* Chromalox_ cartridge heaters
	
	* CIR-1021-279304_ cartridge heater, 100W

------
Sensor
------

* K Type thermocouple, Omega_ Engineering

	* HTTC72-K-116U-1.25-UNGR

---------
Schematic
---------
(SynthesizerTemperatureController.SchDoc)

.. _BSS84: http://www.nxp.com/documents/data_sheet/BSS84.pdf
.. _MAX31855: http://www.maximintegrated.com/datasheet/index.mvp/id/7273
.. _MCP23S18: http://www.microchip.com/wwwproducts/Devices.aspx?dDocName=en537376
.. _CX: http://www.crydom.com/en/Products/Catalog/AdvancedWebPage.aspx?CategoryText1=PCB%20Mount&CategoryText2=AC%20Output&CategoryText3=CX%20Series%20SIP%20SSR%20-%20Ratings%20to%205A%20@%20280%20VAC%20-%20AC%20or%20DC%20control
.. _Crydom: http://www.crydom.com/
.. _Chromalox: http://www.chromalox.com/
.. _CIR-1021-279304: http://www.valinonline.com/images/support_docs/cir250.pdf
.. _Omega: http://www.omega.com/