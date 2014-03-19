"""
The sequence submodule contains
the unit operations of the Elixys Synthesizer
These operations include:

    * Add
    * Cassette
    * Comment
    * Evaporate
    * Transfer
    * React
    * Prompt
    * Install
    * TrapF18
    * EluteF18
    * Initialize
    * Mix
    * Move
    * ExternalAdd

"""

from components.add import Add
from components.cassette import Cassette
from components.comment import Comment
from components.evaporate import Evaporate
from components.transfer import Transfer
from components.react import React
from components.prompt import Prompt
from components.install import Install
from components.trapf18 import TrapF18
from components.elutef18 import EluteF18
from components.initialize import Initialize
from components.mix import Mix
from components.move import Move
from components.externaladd import ExternalAdd

comp_lookup = dict()
comp_lookup['ADD'] = Add
comp_lookup['CASSETTE'] = Cassette
comp_lookup['EVAPORATE'] = Evaporate
comp_lookup['TRANSFER'] = Transfer
comp_lookup['REACT'] = React
comp_lookup['PROMPT'] = Prompt
comp_lookup['INSTALL'] = Install
comp_lookup['COMMENT'] = Comment
comp_lookup['TRAPF18'] = TrapF18
comp_lookup['ELUTEF18'] = EluteF18
comp_lookup['INITIALIZE'] = Initialize
comp_lookup['MIX'] = Mix
comp_lookup['MOVE'] = Move
comp_lookup['EXTERNALADD'] = ExternalAdd
