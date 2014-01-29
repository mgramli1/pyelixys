"""
This file shall create a dictionary
object to be reference from the 
sequence manager class.

Import each component from the components/
directory. Then map each component class
to a dictionary to be used by the sequence
manager class.
"""
from pyelixys.sequence.components.add import Add
from pyelixys.sequence.components.cassette import Cassette
from pyelixys.sequence.components.comment import Comment
from pyelixys.sequence.components.evaporate import Evaporate
from pyelixys.sequence.components.transfer import Transfer
from pyelixys.sequence.components.react import React
from pyelixys.sequence.components.prompt import Prompt
from pyelixys.sequence.components.install import Install
from pyelixys.sequence.components.trapf18 import TrapF18
from pyelixys.sequence.components.elutef18 import EluteF18
from pyelixys.sequence.components.initialize import Initialize
from pyelixys.sequence.components.mix import Mix
from pyelixys.sequence.components.move import Move
from pyelixys.sequence.components.externaladd import ExternalAdd

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
