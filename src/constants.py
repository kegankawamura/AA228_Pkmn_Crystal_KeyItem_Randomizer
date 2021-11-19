from typing import NamedTuple
from enum import Enum

# Number of key items/checks
NUMKEYS = 32

# Number of locations/nodes in graph
NUMLOCS = 36

# Node Names

# List of (Node, TrainerLevel) tuples for trainers

# List of (Node, (lower, upper)) tuples for wild pokemon

# All check structs

'''
'struct'-like class that represents checks and
their associated name and rewards.
'''
class Check(NamedTuple):
	name: Enum
	reward: float = 0.0
