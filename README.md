Elixys Hardware Software API
==============================================
pyelixys is a library for communicating with the [Sofie Biosciences][sofiebiolink]
[Elixys hardware][elixyslink].  The the hardware is a design based upon the [mbed 
development board][mbedlink].  It communicates with the hardware using the 
[websocket protocol][websocketlink].  This library abstracts the hardware to python objects.

Developing with pyelixys
------------------------
First you should install python and virtualenv.
```bash
pip install virtualenv
```
Now setup the pyelixys sandbox environment
```bash
virtualenv pyelixys
cd pyelixys
```
Active the sandbox environment
```bash
source bin/activate
```
Clone the repository
```bash
git clone git@github.com:henryeherman/pyelixys.git
cd pyelixys
```
Install the python dependencies using pip
```bash
pip install -r requirements.txt
```

If installing on linux, you will need numpy.
To install numpy in a virtualenv 
requires the python dev
package. Before installing the requirements with pip
run the following command.
```bash
sudo apt-get install python2.7-dev
```

Working with the HAL & the Hardware Simulator
---------------------------------------------
To run the Elixys host server and gain access
to system object, which gives access to all
features the Elixys Robot, run the following
command from the root of the virtual environment.
The system object will be loaded as the variable
`s`.

```bash
python -m pyelixys.hal.system
```

To run the Elixys hardware simulator, run this
command from the root of the Elixys virtual
environment.
```bash
python -m pyelixys.hal.tests.testelixyshw
```

The hardware simulator object and all corresponding
status information is accessible from the variable
`e`.

[mbedlink]: http://mbed.org/
[sofiebiolink]: http://sofiebio.com/
[elixyslink]: http://sofiebio.com/products/chemistry/
[websocketlink]: http://en.wikipedia.org/wiki/WebSocket
