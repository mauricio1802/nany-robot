from enum import Enum

class Questions(Enum):
    IS_EMPTY, IS_DIRTY, IS_PEN, HAVE_OBSTACLE, HAVE_ROBOT, HAVE_CHILD = range(6)