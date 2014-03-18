=======================================
Pressure Sensor and Regulator Subsystem
=======================================

While there is only a single SMC pressure sensor used inside of the Synthesizer unit to monitor the vacuum pressure,
we could imagine plenty of future use cases that would require driving SMC regulators and pressure sensors.
The SMC Misc Interfaces is intended to be used with either a digital regulator or a digital pressure gauge.

A MCP4822_ dual DAC from microchip provides a way of setting the set point on regulators.  
This signal is amplified by and Analog Devices OP777 single supply capable operational amplifier with a gain of 3.
This allows us near fullscale on the standard 10V analog input of the digital pressure regulators.
The MCP4822_ has a SPI interface an can be treated as an ordinary peripheral.

The digital pressure gauges and pressure regulator output a monitor signal that can be sampled by an ADC.
The monitor signal is passed through a simple voltage divider to bring it in the range of our 3V3 ADC.
The MCP3202_ is a dual SPI based ADC that can be treated as a standard peripheral on our SPI bus.
 
-------
Signals
-------

* SCK - SPI Clock signal
* MOSI - SPI Master Output Slave Input
* MISO - SPI Master Input Slave Output
* DAC_CS - DAC Chip select signal
* ADC_CS - ADC Chip select signal
 
----------
Connectors
----------

4 pin Micro Mate-n-lok connector 3-794636-4_

---
ICs
---
* MCP4822_
	
	* Dual channel 12-bit DAC with internal voltage reference

* MCP3202_

	* 12-bit Analog-to-Digital Converter (ADC) combines high performance and low power consumption in a small package
	
---------
Schematic
---------
(SynthesizerSMCMiscInterface.SchDoc)
	
.. _MCP4822: http://www.microchip.com/wwwproducts/Devices.aspx?dDocName=en024016
.. _MCP3202: http://www.microchip.com/wwwproducts/Devices.aspx?dDocName=en010532
.. _3-794636-4: http://www.te.com/catalog/pn/en/3-794636-4?RQPN=3-794636-4