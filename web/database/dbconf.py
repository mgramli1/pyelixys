# Import config object to be used for
# system configurations
from configobj import ConfigObj
import os

# Open the system configuration
# Check if an .ini file exists
if os.path.isfile('database/dbconf.ini'):
    # Running as a webserver
    configfile = 'database/dbconf.ini'
    config = ConfigObj(configfile)

elif os.path.isfile('dbconf.ini'):
    # Running as a DBComm script
    configfile = 'dbconf.ini'
    config = ConfigObj(configfile)

elif os.path.isfile('/opt/elixys/config/SystemConfiguration.ini'):
    configfile = '/opt/elixys/config/SystemConfiguration.ini'
    config = ConfigObj(configfile)
