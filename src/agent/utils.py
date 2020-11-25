from itertools import repeat
from ..env.questions import Questions
from ..env.child import Child
from ..utils.directions import Directions, move


def can_move_to(env, x):
    if not env.valid_position(x):
        return False
    is_block = env.check(Questions.HAVE_OBSTACLE, x)
    has_child = env.check(Questions.HAVE_CHILD, x)
    is_pen = env.check(Questions.IS_PEN, x)
    return not (is_block or (is_pen and has_child))
    

def get_child(env, pos):
    index = 0
    while True:
        element = env.get_element(pos, index)
        if isinstance(element, Child):
            return element
        index += 1


def find_move_to(env, pos, condition):

    first_moves = [ (direc, move(pos, direc)) for direc in Directions if can_move_to(env, move(pos, direc)) ]
    visited = [pos] + [ x[1] for x in first_moves]
    queue = first_moves


    while queue:
        direction, actual = queue.pop(0)
        if condition(actual):
            return direction
        nexts = [ move(actual, direc) for direc in Directions ]
        nexts = filter(lambda x: can_move_to(env, x), nexts)
        nexts = list(filter(lambda x : not x in visited, nexts))
        queue.extend(list(zip(repeat(direction, len(nexts)), nexts)))
        visited.extend(nexts)

    return None


def distances_to_childs(env, pos):

    distances_to_childs = {}

    visited = [ pos ]
    queue = [ (0, pos) ]

    while queue:
        steps, actual = queue.pop(0)
        if env.check(Questions.HAVE_CHILD, actual) and not env.check(Questions.IS_PEN, actual):
            distances_to_childs[get_child(env, actual)] = steps 
        
        nexts = [ move(actual, direc) for direc in Directions ]
        nexts = filter(lambda x : can_move_to(env, x), nexts)
        nexts = list(filter(lambda x : not x in visited, nexts))
        queue.extend(zip(repeat(steps + 1, len(nexts)), nexts))
        visited.extend(nexts)
    
    return distances_to_childs