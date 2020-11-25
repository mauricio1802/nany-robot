from enum import Enum

DIRECTIONS_LABELS = ["N", "E", "S", "W"]

class Directions(Enum):
    N, E, S, W = [(-1, 0), (0, 1), (1, 0), (0, -1)]

def sum_tuple(t1, t2):
    return (t1[0] + t2[0], t1[1] + t2[1])

def sub_tuple(t1, t2):
    return (t1[0] - t2[0], t1[1] - t2[1])

def direction(pos1, pos2):
    direc = sub_tuple(pos1, pos2) 
    assert direc in Directions 
    return direc

def move(pos1, direc):
    assert direc in Directions 
    return sum_tuple(pos1, direc.value)