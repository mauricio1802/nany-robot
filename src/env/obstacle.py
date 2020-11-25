from .questions import Questions
from ..utils.directions import move

class Obstacle:
    def __init__(self, env, pos):
        self.env = env
        self.pos = pos 

    def move(self, direction):
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
