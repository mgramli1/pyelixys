Elixys Hardware Software API
==============================================
pyelixys is a library for communicating with the [Sofie Biosciences][sofiebiolink]
[Elixys hardware][elixyslink].  The the hardware is a design based upon the [mbed
development board][mbedlink].  It communicates with the hardware using the
[websocket protocol][websocketlink].  This library abstracts the hardware to python objects.

Developing with pyelixys
------------------------
First, install pip.
```bash
sudo apt-get install python-setuptools
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
Install the python dependencies by executing the
install dependencies script in the root of pyelixys
```bash
./install_dependencies.sh
```

If installing on linux, you will need numpy.
(This should be installed by running the install
dependencies script).
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

If the database does not exist, it will now!
The filename of the database is located in
the dbconf.ini and can be fount in database
directory.
This will execute the setup of the database and return
the user in an Ipython terminal upon completion. At this
point, a user may run additional scripts or commands.
To exit Ipython, type `exit`.

The database is accessed through the wonderful
[sqlalchemy][sqlalchemylink] library, and the models can be found
in model.py


Initializing Data in the Database
---------------------------------
Developers might like to start with some default data.
This can be done by populating the database with data.
In order to populate the database with data, simply run:


```bash
python -m pyelixys.web.database.populatedb
```

This shall store a user with default settings onto the database.
If the database did not already exist it will now!
The user shall be returned to an an Ipython terminal upon completion.
At this point, a user may run additional scripts or commands.
To exit Ipython, type `exit`.

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
