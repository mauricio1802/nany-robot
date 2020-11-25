from enum import Enum
from random import choice, shuffle, randint
from itertools import accumulate
from .tile import Tile
from .pen import Pen
from .dirty import Dirty
from .child import Child
from .obstacle import Obstacle
from .questions import Questions
from .agent import Agent
from ..utils.directions import Directions, move, sum_tuple


class EnvStatus(Enum):
    HOUSE_CLEANED, ROBOT_FIRED, TIME_END = range(3)


class Environment:
    def __init__(self, N, M, agent_factory, t, blocks_percent, dirty_percent, n_childs):
        self.rows = N
        self.cols = M
        self.field = [ [ Tile() for _ in range(M) ] for _ in range(N) ]
        self.agent = agent_factory(self, (0, 0)) 
        self.t = t 
        self.turn = 1
        self.children = []
        self.dirty_history = []
        self.result = None

        n_blocks = blocks_percent * N * M // 100 
        n_dirty = dirty_percent * N * M // 100
        
        assert n_blocks + n_dirty + n_childs * 2 + 1 <= N * M
        assert n_childs <= N or n_childs <= M

        self.__place_random(n_blocks, n_dirty, n_childs, self.agent)
        
    def __repr__(self):
        ch = {Dirty : "D", Obstacle : "O", Child : "C",  Pen : "P"}
        rows = []
        for row in self.field:
            actu = []
            for c in row:
                if c.check(Questions.IS_EMPTY):
                    actu.append(" ")
                else:
                    try:
                        actu.append(ch[type(c._Tile__elements[0])])
                    except:
                        actu.append("A")
            rows.append(" ".join(actu))
        return "\n".join(rows)
    
    def __place_random(self, n_blocks, n_dirty, n_childs, agent):
        N, M = self.rows, self.cols
        all_pos = [ (i, j) for i in range(N) for j in range(M) ]
        
        in_col, in_row = _n_in_a_col(N, M, n_childs),  _n_in_a_row(N, M, n_childs)
        pens = list(choice(list(filter(lambda l : len(l) != 0, [in_col, in_row]))))

        for p in pens:
            self.add(Pen(), p)
        
        empty_cells = list(filter(lambda x : self.check(Questions.IS_EMPTY, x), all_pos))
        shuffle(empty_cells)
        block_cells = empty_cells[:n_blocks]
        for bc in block_cells:
            self.add(Obstacle(self, bc), bc)
            
        empty_cells = list(filter(lambda x : self.check(Questions.IS_EMPTY, x), all_pos))
        shuffle(empty_cells)
        child_cells = empty_cells[:n_childs]
        
        self.children = []
        for cc in child_cells:
            child = Child(self, cc, 0.5)
            self.children.append(child)
            self.add(child, cc)
        
        empty_cells = list(filter(lambda x : self.check(Questions.IS_EMPTY, x), all_pos))
        agent_pos = choice(empty_cells)
        self.add(agent, agent_pos)
        agent.move(agent_pos)        
        
        empty_cells = list(filter(lambda x : self.check(Questions.IS_EMPTY, x), all_pos))
        shuffle(empty_cells)
        dirty_cells = empty_cells[:min(n_dirty, len(empty_cells))]
        for dc in dirty_cells:
            self.add(Dirty(), dc)
    
    def __end_condition(self):
        if self.turn == self.t * 100:
            self.result = EnvStatus.TIME_END
            return True

        dirty_percent = self.__compute_dirty_percent()
        if dirty_percent >= 60:
            self.result = EnvStatus.ROBOT_FIRED
            return True

        n_child_out = 0
        for child in self.children:
            if not self.check(Questions.IS_PEN, child.pos):
                n_child_out += 1
        
        if n_child_out == 0 and dirty_percent == 0:
            self.result = EnvStatus.HOUSE_CLEANED
            return True
        
        return False

    def __clean(self):
        for row in self.field:
            for cell in row:
                cell.clean()

    def __randomize(self):
        all_pos = [ (i, j) for i in range(self.rows) for j in range(self.cols) ]
        n_blocks = len(list(filter(lambda c : self.check(Questions.HAVE_OBSTACLE, c), all_pos)))
        n_dirty = len(list(filter(lambda c : self.check(Questions.IS_DIRTY, c), all_pos)))
        n_childs = len(list(filter(lambda c : self.check(Questions.IS_PEN, c), all_pos)))

        self.__clean()
        self.__place_random(n_blocks, n_dirty, n_childs, self.agent)

    def __compute_dirty_percent(self):            
        all_pos = [ (i, j) for i in range(self.rows) for j in range(self.cols) ]
        n_dirty = 0
        for pos in all_pos:
            if self.check(Questions.IS_DIRTY, pos):
                n_dirty += 1
        return (n_dirty * 100) / (self.rows * self.cols)


    def __compute_new_dirty(self, pos):
        cells = [ pos ] + [ move(pos, dest) for dest in Directions if self.valid_position(move(pos, dest)) ]
        extra_directions = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
        cells += [ sum_tuple(pos, direct) for direct in extra_directions if self.valid_position(sum_tuple(pos, direct))]

        n_childs = len(list(filter(lambda c : self.check(Questions.HAVE_CHILD, c), cells)))
        n_dirty = 0
        if n_childs == 1:
            n_dirty = randint(0, 1) 
        if n_childs == 2:
            n_dirty = randint(0, 3)
        if n_childs >= 3:
            n_dirty = randint(0, 6)

        shuffle(cells) 
        return (n_dirty, cells) 

    def run(self):
        while not self.__end_condition():
            # print("ENVIRONMET")
            # print(self)
            self.agent.action()
            if self.__end_condition():
                break
            for child in self.children:
                n_new_dirty, cells_new_dirty = self.__compute_new_dirty(child.pos)
                if child.move():
                    while n_new_dirty and cells_new_dirty:
                        cell = cells_new_dirty.pop()
                        if self.check(Questions.IS_EMPTY, cell):
                            self.add(Dirty(), cell)
                            n_new_dirty -= 1
            
            if self.turn % self.t == 0:
                self.__randomize()

            self.dirty_history.append(self.__compute_dirty_percent())
            self.turn += 1

    def valid_position(self, pos):
        row, col = pos
        return row >= 0 and row < self.rows and col >= 0 and col < self.cols
    
    def remove(self, element, pos):
        row, col = pos
        self.field[row][col].remove_element(element)
    
    def add(self, element, pos):
        row, col = pos
        self.field[row][col].add_element(element)
    
    def check(self, question, pos):
        row, col = pos
        return self.field[row][col].check(question) 
    
    def get_element(self, pos, index = 0):
        row, col = pos
        return self.field[row][col].get_element(index)
    


def _n_in_a_row(rows, cols, n):
    if cols < n:
        return []

    row = randint(0, rows-1)
    direction = choice([Directions.E, Directions.W])

    col = randint(0, cols-1)

    if direction is Directions.E:
        while cols - col < n:
            col -= 1
        cells = [(row, col)] + [ Directions.E for _ in range(n - 1) ]
        return list(accumulate(cells, move))

    if direction is Directions.W:
        while col + 1 < n:
            col += 1
        cells = [(row, col)] + [ Directions.W for _ in range(n - 1)]
        return list(accumulate(cells, move))

def _n_in_a_col(rows, cols, n):
    if rows < n:
        return []

    col = randint(0, cols-1)
    direction = choice([Directions.S, Directions.N])

    row = randint(0, rows-1)

    if direction is Directions.S:
        while rows - row < n:
            row -= 1
        cells = [(row, col)] + [ Directions.S for _ in range(n - 1) ]
        return list(accumulate(cells, move))

    if direction is Directions.N:
        while row + 1 < n:
            row += 1
        cells = [(row, col)] + [ Directions.N for _ in range(n - 1)]
        return list(accumulate(cells, move))
    




    
