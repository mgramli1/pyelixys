=========================
Video Pass-thru Subsystem
=========================
The video capture system for the synthesizer uses the PC213_ series camera.
The connector on the camera is removes and a 3 wires cable is directly soldered to the camera.
The camera uses 100mA at 12Volts.  

A locking screw on connector is used to connect the camera to the synthesizer board.
12V power and ground are provides by the synthesizer board.
The video signal is passed through the synthesizer board to a 15 pin high density DBSub connector.

The DSUB connector matches the connector on the back of the host PC capture card. 
We are using a PV-981_ 4 port video capture card from Bluecherry_ .

----------
Connectors
----------
* TRAPC3MX_
	* 3 pin screw-on thru hole connector for audio video applications.
	
* 156-3315-E_
	* 15 Pin DSUB or similar
 
---------
Schematic
---------
(SynthesizerVideo.SchDoc)


.. _156-3315-E: http://www.mouser.com/ProductDetail/Kobiconn/156-3315-E/?qs=RC2ne4458IJMP%252bd8Z1f5lQ==
.. _TRAPC3MX: http://www.switchcraft.com/ProductSummary.aspx?Parent=620
.. _PC213: http://www.supercircuits.com/media/docs/633580318620312500_PC212_PC213.pdf
.. _PV-981: http://store.bluecherry.net/pv-981-4-port-video-capture-card-120fps-realtime-recording-pci-e-version.html
.. _Bluecherry: http://store.bluecherry.net/