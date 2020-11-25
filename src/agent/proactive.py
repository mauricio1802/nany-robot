from enum import Enum
from itertools import repeat
from .utils import find_move_to, distances_to_childs, get_child
from .actions import PerceptAttr, CleanDirty, MoveToChild, MoveToDirty, MoveToPen, PickUpChild, ReleaseChild
from ..env.agent import Agent
from ..env.child import Child
from ..env.questions import Questions
from ..utils.directions import Directions, move


class PlanAction(Enum):
    PICKUP_CHILD, CLEAN_DIRTY = range(2)


class ProactiveAgent(Agent):
    def __init__(self, env, pos, plan_freq):
        self.env = env
        self.pos = pos
        self.plan_freq = plan_freq
        self.actions_remaining = 0

        self.carry = None
        self.plan_action = None
        self.children_order = []    

    def __goals_changed(self):
        remaining_childs = len(self.children_order)
        if self.plan_action is PlanAction.PICKUP_CHILD and remaining_childs == 0:
            return True
        return False
    
    def __make_plan(self):
        all_cells = [ (i, j) for i in range(self.env.rows) for j in range(self.env.cols) ]
        pen_cells = list(filter(lambda c : self.env.check(Questions.IS_PEN, c), all_cells))
        pen_cells = sorted(pen_cells)
        middle_pen = pen_cells[len(pen_cells) // 2 - 1]

        distances_from_me = distances_to_childs(self.env, self.pos)
        if not len(distances_from_me):
            self.plan_action = PlanAction.CLEAN_DIRTY
            return
        
        distances_from_pen = distances_to_childs(self.env, middle_pen)
        maxi = 0
        first_target = None
        children = []

        self.plan_action = PlanAction.PICKUP_CHILD

        for child, distance in distances_from_me.items():
            children.append(child)
            advance = distances_from_pen.get(child, distance) - distance
            if advance > maxi:
                maxi = advance
                first_target = child
        
        if first_target is not None:
            children.remove(first_target)
            children.insert(0, first_target)
            self.children_order = children
        else:
            ordered_childs = sorted(distances_from_me.items(), key = lambda x : x[1])
            self.children_order = [ x[0] for x in ordered_childs ]
        
    def __act(self, percept):
        actions = []

        if self.plan_action is PlanAction.PICKUP_CHILD:
            actions  = [ CleanDirty, ReleaseChild, PickUpChild, MoveToPen, MoveToChild ]

        if self.plan_action is PlanAction.CLEAN_DIRTY:
            actions = [ CleanDirty, MoveToDirty ]

        for action in actions:
            if action.check(percept):
                if action is ReleaseChild:
                    self.children_order.pop(0)
                action.act(percept, self.env) 
                return

    def move(self, pos):
        self.pos = pos
    
    def see(self):
        percept = {}

        check_func = lambda x : self.env.check(Questions.HAVE_CHILD, x) and get_child(self.env, x) == self.children_order[0]
        move_next_child = find_move_to(self.env, self.pos, check_func) if self.children_order else None

        percept[PerceptAttr.AGENT] = self
        percept[PerceptAttr.CARRYING] = True if self.carry else False
        percept[PerceptAttr.IN_PEN] = self.env.check(Questions.IS_PEN, self.pos)
        percept[PerceptAttr.IN_DIRTY] = self.env.check(Questions.IS_DIRTY, self.pos)
        percept[PerceptAttr.NEXT_CHILD] = move_next_child
        percept[PerceptAttr.NEXT_DIRTY] = find_move_to(self.env, self.pos, lambda x : self.env.check(Questions.IS_DIRTY, x))
        percept[PerceptAttr.NEXT_PEN] = find_move_to(self.env, self.pos, lambda x : self.env.check(Questions.IS_PEN, x))
        
        if percept[PerceptAttr.NEXT_CHILD] is None:
            percept[PerceptAttr.CHILD_IN_NEXT] = False
        else:
            percept[PerceptAttr.CHILD_IN_NEXT] = self.env.check(Questions.HAVE_CHILD, move(self.pos, percept[PerceptAttr.NEXT_CHILD])) 
        
        if percept[PerceptAttr.NEXT_PEN] is None:
            percept[PerceptAttr.PEN_IN_NEXT] = False
        else:
            percept[PerceptAttr.PEN_IN_NEXT] = self.env.check(Questions.IS_PEN, move(self.pos, percept[PerceptAttr.NEXT_PEN])) 

        return percept

    def action(self):
        if not self.actions_remaining or self.__goals_changed():
            self.__make_plan() 
            self.actions_remaining = self.plan_freq
        percept = self.see()
        

        self.__act(percept)

        self.actions_remaining -= 1
    


            


    



    
