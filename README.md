Elixys Hardware Software API
==============================================
pyelixys is a library for communicating with the [Sofie Biosciences][sofiebiolink]
[Elixys hardware][elixyslink].  The the hardware is a design based upon the [mbed
development board][mbedlink].  It communicates with the hardware using the
[websocket protocol][websocketlink].  This library abstracts the hardware to python objects.

Developing with pyelixys
------------------------
First, install pip, python-dev, and mysqlclient.
```bash
sudo apt-get install python-setuptools
sudo apt-get install python-dev
sudo apt-get install libmysqlclient-dev
```
Next, install the virtual environment - virtualenv.
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

The simulator is automatically started if
configured the controlbox and/or synthesizer
options are set to `True`

The hardware simulator object and all corresponding
status information is accessible from the variable
`s.simulator`.


Working with the Database
-------------------------
By default pyelixys is configured to use a sqlite file based
database.  It will appear in the root of your virtual environment
as soon as you initialized it. To initialize it run:


```bash
sudo python -m pyelixys.web.database.model
```

If the database does not exist it will now!
The filename of the database is located in
the dbconf.ini and can be fount in database
directory.

The database is accessed through the wonderful
[sqlalchemy][sqlalchemylink] library, and the models can be found
in model.py


Initializing Data in the Database
---------------------------------
TBD


Starting the Webserver
------------------------------------------
To run the Elixys web server, perform the following
command in the root of the virtual environment. The
runserver shall run on port 80 and requires sudo
permissions to execute.

```bash
sudo python runserver.py
```

The webserver shall handle all web requests to and
from the Elixys server. To access the webserver, open
a browser and visit the URL: `localhost`. You will be
required to enter your creditionals.
Examples of URLs to visit include:
`localhost/state`
`localhost/config`
`localhost/runstate`

[mbedlink]: http://mbed.org/
[sofiebiolink]: http://sofiebio.com/
[elixyslink]: http://sofiebio.com/products/chemistry/
[websocketlink]: http://en.wikipedia.org/wiki/WebSocket
[sqlalchemylink]: http://www.sqlalchemy.org/
