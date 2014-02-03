#!/usr/bin/env python
""" The Hardware config can be imported from this module
file.  Any object that inherits from the ElixysObject
should have access to the configuration through the
self.sysconf variable.  The config itself is
contained in the hwconf.ini.  It should be modified
VERY carefully.  The hwconfspec.ini is used to
validate the config. It should only be
modified by developers who are willing to accept
the consequences!
"""
from configobj import ConfigObj
from validate import Validator
from validate import ValidateError


def command_check(vals):
    """ Validates the commands in the config file """
    #print "Running command check"
    #print vals
    try:
        cmdint = int(vals[0])
    except IndexError:
        raise ValidateError("Command should be list separated "
                "by comma first value should be integer")

    except ValueError:
        raise ValidateError("Command should be integer")

    try:
        fmtchropts = "xcbB?hHiIlLqQfdspP"
        if not str(vals[1]) in fmtchropts:
            raise ValidateError("Expected format character "
                    "value: %s" % fmtchropts)
        fmtchr = str(vals[1])
    except IndexError:
        raise ValidateError("Command should be list separated "
                "by comma, second value should be character")
    #print vals

    return cmdint, fmtchr
    #raise ValidateError('A list was passed when an email address was expected')

def list3ints_check(vals):
    """ Validates that we recieve a list of 3 ints """
    # print "Running list of 3 ints validation"
    if len(vals) != 3:
        raise ValidateError("Expecting a list of 3 integers. "
                "Did not receive 3 integers.")

    try:
        idxs = [int(val) for val in vals]
    except ValueError:
        raise ValidateError("List should be of integers!")

    return idxs


configspec = "pyelixys/hal/hwconfspec.ini"
configfile = "pyelixys/hal/hwconf.ini"
config = ConfigObj(configfile, configspec=configspec)
validator = Validator({'command': command_check,
                       'list3ints': list3ints_check})
results = config.validate(validator, preserve_errors=True)


if __name__ == '__main__':
    from IPython import embed
    print """ The system configuration can be explored
        using the config variable.  It has a dictionary like
        interface.  See the ConfigObj documentation for more details.
        The contents of the hwconf.ini are parsed and made available to
        all elixys system objects.  To make changes to the
        elixys hwconfig please edit the hwconf.ini file.
        This file is validated according to the hwsonfspec.ini.
        This file SHOULD NOT BE MODIFIED as it will likely stop
        the system from running correctly or even AT ALL.
        """
    embed()
