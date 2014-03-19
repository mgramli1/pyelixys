#!/usr/bin/env python
""" The Status object is maintained by
the websocket server.  The hardware connects
to the websocket server and continously updates
the state to match the state of the hardware.
The Status object has a dictionary like interface,
and all of the datatypes from the client are properly
converted to their respective python datatypes,
and attached to the Status object according to the
the hwconf
"""
import sys
import time
import threading
import copy
import collections
from Queue import Empty
from pyelixys.hal.statusfmt import StatusMessageFormatFactory
from pyelixys.elixysexceptions import ElixysValueError, \
                                        ElixysCommError

from pyelixys.hal.elixysobject import ElixysObject
from pyelixys.utils.elixysthread import ElixysStoppableThread
from pyelixys.logs import statlog as log


class ElixysReadOnlyError(ElixysValueError):
    """ Exception raised if a user trys to write
    to a value of the dictionary, the status dictionary
    is read-only!
    """
    pass


class StatusThread(ElixysStoppableThread):
    """ The status thread is a consumer of packets from
    the websocket server.  It continuously reads from the
    queue and properly parse the packets into the Status object"""
    def __init__(self, status, status_queue):
        super(StatusThread, self).__init__()
        self.queue = status_queue
        self.status = status

    def loop(self):
        """ Main loop, parse packet then wait some time """
        try:
            # todo timeout from hwconf
            statpkt = self.queue.get(block=False, timeout=0.1)
            self.status.parse_packet(statpkt)
        except Empty:
            # todo sleep time from hwconf
            time.sleep(0.1)

class Status(ElixysObject, collections.MutableMapping):
    """ The Status object has a dictionary interface,
    it is capable of properly parsing the binary packets from
    the client hardware an converting them into python data types """
    def __init__(self, *args, **kwargs):
        self.fmt = StatusMessageFormatFactory()
        self.struct = self.fmt.get_struct()
        self.store = dict()
        self.update(dict(*args, **kwargs))
        self.lock = threading.Lock()
        self.is_valid = False

    def __getitem__(self, key):
        if self.is_valid is False:
            return None
        self.lock.acquire()
        val = self.store[self.__keytransform__(key)]
        self.lock.release()
        return val

    def __setitem__(self, key, value):
        #raise ElixysReadOnlyError("Status Packet only updated"
        #                          "by new packet from hardware")
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        self.lock.acquire()
        del self.store[self.__keytransform__(key)]
        self.lock.release()

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key

    def __getattr__(self, name):
        if self.is_valid:
            super(Status, self).__getattr__(self, name)
        else:
            raise ElixysCommError("The status packet is invalid, is a client connected?")

    def parse_packet(self, pkt):
        """ Maybe the most complicates function, read the config and
        properly parses the binary packet from the hardware accordingly """
        #TODO rework this, too complicated!
        subsystems = self.fmt.subsystems
        data = self.struct.unpack(pkt)
        data_dict = dict()
        data_idx = 0
        for subsystem, count, messagefmt in subsystems:
            #print subsystem
            sub_dict = dict()

            for key, value in messagefmt.items():
                if isinstance(value, str):
                    #print key, data_idx
                    sub_dict[key] = data[data_idx]
                    data_idx += 1

                elif key == "Repeat":
                    rptmessagefmt = messagefmt['Repeat']
                    units = []
                    for i in range(count):
                        unit_dict = dict()
                        for rkey, rval in rptmessagefmt.items():
                            unit_dict[rkey] = data[data_idx]
                            #print rkey, data_idx
                            data_idx += 1
                        units.append(unit_dict)
                        sub_dict[i] = unit_dict
                    sub_dict['Subs'] = units
                    sub_dict['count'] = count
            data_dict[subsystem] = sub_dict
        self.lock.acquire()
        self.store = data_dict
        for key, value in data_dict.items():
            setattr(self,key,value)
        self.lock.release()
        self.is_valid = True
        return data_dict

    def update_from_queue(self, queue):
        """ Start a thread to pop messages of the queue
        and parse them at a frequent interval, updating all
        dictionary values to reflect the state of the hardware
        """
        self.thread = StatusThread(self, queue)
        self.thread.start()

    def stop_update(self):
        """ Disable the update thread
        """
        log.debug("Starting update thread")
        self.thread.stop()

    def as_json(self):
        """ Return the status of the hardware
        as a json object, useful for displaying
        the results in a web app """
        return json.dumps(self.store, indent=2)

    def as_dict(self):
        """ Copy all the data from the status object
        and return a dictionary, this "freezes" the state
        of the synthesizer hardware
        """
        return copy.deepcopy(self.store)

status = Status()

if __name__ == '__main__':
    from IPython import embed
    import json
