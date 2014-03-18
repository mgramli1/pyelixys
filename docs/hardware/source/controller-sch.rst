=======================
Controller Architecture
=======================

The Elixys Synthesizer Controller board uses an ARM Cortex-M3 microcontroller.
This main IC is an LPC1768 96MHz.  It is the same microcontroller used on the mbed_ development board.
This microcontroller was selected because of the rapid prototyping environment available for it allowing the
firmware developer to quickly test and develop working code extremely quickly.
Additionally, it contains all of the necessary peripherals.

The host will communicate with the remote system via an Ethernet interface.
This is a nearly ideal interface for our application as it is simple to use and has become nearly ubiquitous.
The LPC1768_ has a built in ethernet MAC but requires an external ethernet PHY. We considered using the LAN9303_ , a 10/100 
3 port ethernet switch with built in PHY.  This would be ideal since we would be able to use the remote synthesizer unit 
like an ethernet switch and connect additional devices to it in the cell.  This will likely be implemented on a future revision.
We elect to use the DP83848J_ instead from the mbed reference design. This PHY was originally a National Semiconductor product but is now
a Texas Instrument IC.  It is connected as in the mbed reference design_ .

Programming the microcontroller will be done using either its JTAG interface or the UART bootloader.  
Both modes have been tested and shown to work.  
The JTAG programmer and UART to USB virtual serial port will be placed on the board to make in field testing and development easier.
A single FTDI chip will allow both modes of programming as well as providing a UART debug port during development.
The FT2232H_ IC is chosen as it is compatible with OpenOCD and open source JTAG debugging suite.
For additional flexibility a USB Hub is added to the device to expose both the FTDI chip and the LPC1768 native USB port.
The USB Hub capabilities are provided by a SMC USB2514_ IC. SMC was acquired by Microchip, so this is a Microchip part.
Two USB peripheral ports go unused.

-------
Signals
-------
The controller exposes the following signals that are available to the peripheral subsystems:

	* SCK - SPI Clock signal (P0.7)		
	* MOSI - SPI Master Output Slave Input (P0.9)
	* MISO - SPI Master Input Slave Output (P0.8)
	* CSDAT - Chip select data (P1.24)
	* CSSCK - Chip select clock (P1.20)
	* CSCLR - Chip select clear (P1.22)
	* CSOE -  Chip select output enable (P1.25)
	* POSDIGINT - Position sensor digital interrupt (P2.11)
	* POSRST - Position sensor reset (P2.12)
	* MOTOR[0-3] - 4x PWM signals (P2.0, P2.1, P2.2, P2.3)
	* MTRRST - Motor driver reset (P2.6)
	* MTRFLT - Motor driver fault detection (P2.13)
	* VALVRST - Valve reset (P2.7)
	* RAD[0-5] - 6x Radiation detector analog input (P0.23, P0.24, P0.25, P0.26, P1.30, P1.31)
 
------------------------
Communication Interfaces
------------------------
The controller has the following communication interfaces:

	* Ethernet
		
		* Provided by DP83848J_ and the LPC1768_
		
	* USB UART debug port
	
		* Provided by the LPC1768_ and FT2232H_ and USB2514_
	
	* Native USB peripheral
		
		* Provided by the LPC1768_ and USB2514_
		
	* USB JTAG interface

		* Provided by the LPC1768_ and FT2232H_ and USB2514_

---
ICs
---

* LPC1768_

	* NXP_ ARM Cortex-M3 processor, running at frequencies of up to 100 MHz

* DP83848J_

	* Texas Instruments Ethernet PHY

* FT2232H_

	* FTDI_ USB 2.0 Hi-Speed (480Mb/s) to UART/FIFO IC

* USB2514_
	
	* SMC_ High performance, low-power, small footprint hub controller IC
		
.. note::
	Add LEDs for debugging

---------
Schematic
---------
(SynthesizerController.SchDoc)	
	
.. _LPC1768: http://www.nxp.com/documents/data_sheet/LPC1769_68_67_66_65_64_63.pdf	
.. _mbed: http://www.mbed.org/
.. _LAN9303: http://www.smsc.com/Products/Ethernet_and_Embedded_Networking/Ethernet_Switches/LAN9303_LAN9303M
.. _DP83848J:  http://www.ti.com/product/dp83848j
.. _design: http://mbed.org/media/uploads/chris/lpc1768-refdesign-schematic.pdf
.. _USB2514: http://www.smsc.com/main/catalog/usb251x.html
.. _FT2232H: http://www.ftdichip.com/Products/ICs/FT2232H.htm
.. _SMC: http://www.smsc.com/
.. _FTDI: http://www.ftdichip.com/
.. _NXP: http://www.nxp.com/
