#!/usr/bin/env python
# enums.py - define Koordinator task status values

"""
This module defines enum types to represent the possibles statuses and error
levels of tasks.
"""

# Standard imports
import re
from enum import Enum, auto, unique

#-------------------------------------------------------------------------------
# EStatus
#-------------------------------------------------------------------------------


@unique
class EStatus(Enum):
    """Represent the possible task status values."""
    IN_PROGRESS = auto()
    ERROR = auto()
    COMPLETED = auto() # only in schemas

    def __str__(self):
        """Print out 'InProgress' instead of 'EStatus.IN_PROGRESS'."""
        # Turn 'underscore-separated' into camel case
        return re.sub('_([a-z])', r'\1', self.name.capitalize())

#-------------------------------------------------------------------------------
#  EErrorLevel
#-------------------------------------------------------------------------------

# Possible parameter and schema type values
@unique
class EErrorLevel(Enum):
    NONE = auto()
    MINOR = auto()
    CRITICAL = auto()
    FATAL = auto()

    def __str__(self):
        """Print out 'Critical' instead of 'EErrorLevel.CRITICAL'."""
        # Turn 'underscore-separated' into camel case
        return re.sub('_([a-z])', '\1', self.name.capitalize())
