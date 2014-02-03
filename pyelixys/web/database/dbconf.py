# Import config object to be used for
# system configurations
from configobj import ConfigObj
import os

configfile = "pyelixys/web/database/dbconf.ini"

# Open the system configuration
config = ConfigObj(configfile)

if __name__ == "__main__":
    from IPython import embed
    embed()
