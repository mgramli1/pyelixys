.. Synthesizer Board documentation master file, created by
   sphinx-quickstart on Tue Aug 06 12:03:18 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Synthesizer Board's documentation!
=============================================
The **synthesizer board** is the *in-cell* electronic control system for the
Elixys Automated Radiochemistry system.   It provides driver and control over
all features of the *Elixys* system.  It contains subsystems for:

* Pneumatic valve drivers
* Temperature control
* Vacuum driver
* Pressure regulator control
* Mixer motor drivers
* Liquid sensors
* Video pass-thru

The entire system is controlled by an ARM Cortex-M3 microcontroller.

Contents:

.. toctree::	
   :maxdepth: 2
   
   overview-sch
   controller-sch
   chipselect-sch
   valvedrive-sch
   liquidsensor-sch
   smcreg-sch
   tempcontrol-sch
   videopassthru-sch
   digitalinput-sch
   power-sch
   raddetect-schsf



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

