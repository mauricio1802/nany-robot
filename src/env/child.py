from random import random, choice
from .questions import Questions
from ..utils.directions import DIRECTIONS_LABELS, Directions, move

class Child:
    def __init__(self, env, pos, move_prob):
        self.pos = pos
        self.env = env
        self.__move_prob = move_prob
        self.__is_carried = False

    def carry(self):
        self.__is_carried = True
    
    def release(self):
        self.__is_carried = False
    
    def is_captured(self):
        return self.env.check(Questions.IS_PEN, self.pos) or self.__is_carried

    def move(self):
        if self.is_captured():
            return False

        if random() > self.__move_prob:
            return False
        
        direction = Directions[choice(DIRECTIONS_LABELS)]
        destination = move(self.pos, direction)

        if not self.env.valid_position(destination):
            return False

        if self.env.check(Questions.IS_EMPTY, destination):
            self.env.remove(self, self.pos) 
            self.env.add(self, destination) 
            self.pos = destination
            return True
        
        if self.env.check(Questions.HAVE_OBSTACLE, destination):
            can_move = self.env.get_element(destination).move(direction) 
            if can_move:
                self.env.remove(self, self.pos)
                self.env.add(self, destination) 
                self.pos = destination
            return can_move

        return False 

        


    
    