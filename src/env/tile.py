from .dirty import Dirty
from .pen import Pen
from .child import Child
from .obstacle import Obstacle
from .agent import Agent
from .questions import Questions



class Tile:
    def __init__(self):
        self.__elements = []
    
    def add_element(self, element):
        self.__elements.append(element)

    def remove_element(self, element):
        self.__elements.remove(element)
    
    def get_element(self, index):
        return self.__elements[index]
    
    def clean(self):
        self.__elements = []

    def check(self, question):
        if question is Questions.IS_EMPTY:
            return len(self.__elements) == 0

        def has_one(tp):
            return any(map(lambda x : isinstance(x, tp), self.__elements))        

        if question is Questions.IS_DIRTY:
            return has_one(Dirty)

        if question is Questions.IS_PEN:
            return has_one(Pen)
        
        if question is Questions.HAVE_OBSTACLE:
            return has_one(Obstacle)
        
        if question is Questions.HAVE_CHILD:
            return has_one(Child)
        
        if question is Questions.HAVE_ROBOT:
            return any(map(lambda x : issubclass(type(x), Agent), self.__elements))

        return False
    