from enum import Enum
from itertools import repeat
from .utils import find_move_to
from .actions import PerceptAttr, CleanDirty, ReleaseChild, PickUpChild, MoveToPen, MoveToChild, MoveToDirty
from ..env.agent import Agent
from ..env.questions import Questions
from ..utils.directions import Directions, move
from ..env.child import Child
from ..env.dirty import Dirty
from ..env.pen import Pen



class BrooksA(Agent):
    def __init__(self, env, pos):
        self.env = env
        self.pos = pos
        self.carry = None

        self.actions = [ CleanDirty, ReleaseChild, PickUpChild, MoveToPen, MoveToChild, MoveToDirty ]


    def see(self):
        percept = {}

        percept[PerceptAttr.AGENT] = self
        percept[PerceptAttr.CARRYING] = True if self.carry else False
        percept[PerceptAttr.IN_PEN] = self.env.check(Questions.IS_PEN, self.pos)
        percept[PerceptAttr.IN_DIRTY] = self.env.check(Questions.IS_DIRTY, self.pos)
        percept[PerceptAttr.NEXT_CHILD] = find_move_to(self.env, self.pos, lambda x : self.env.check(Questions.HAVE_CHILD, x))
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

    def move(self, pos):
        self.pos = pos

    def action(self):
        percept = self.see()
        for act in self.actions:
            if act.check(percept):
                act.act(percept, self.env)
                return




            


