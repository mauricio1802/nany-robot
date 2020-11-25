from enum import Enum
from ..utils.directions import move
from ..env.dirty import Dirty


class PerceptAttr(Enum):
    PEN_IN_NEXT, CHILD_IN_NEXT, AGENT,\
    NEXT_CHILD, NEXT_PEN, NEXT_DIRTY,\
    CARRYING, IN_PEN, IN_DIRTY = range(9)


class MoveToDirty:
    @staticmethod
    def check(percept):
        if percept[PerceptAttr.NEXT_DIRTY] is None:
            return False
        return True

    @staticmethod
    def act(percept, env):
        agent = percept[PerceptAttr.AGENT]
        destination = move(agent.pos, percept[PerceptAttr.NEXT_DIRTY])
        env.remove(agent, agent.pos)
        agent.pos = destination
        env.add(agent, destination)


class MoveToChild:
    @staticmethod
    def check(percept):
        if percept[PerceptAttr.NEXT_CHILD] is None:
            return False
        return True

    @staticmethod
    def act(percept, env):
        agent = percept[PerceptAttr.AGENT]
        destination = move(agent.pos, percept[PerceptAttr.NEXT_CHILD])
        env.remove(agent, agent.pos)
        agent.pos = destination
        env.add(agent, destination)


class MoveToPen:
    @staticmethod
    def check(percept):
        return percept[PerceptAttr.CARRYING] and percept[PerceptAttr.NEXT_PEN]

    @staticmethod
    def act(percept, env):
        agent = percept[PerceptAttr.AGENT]
        destination = move(agent.pos, percept[PerceptAttr.NEXT_PEN])
        env.remove(agent, agent.pos)
        agent.pos = destination
        env.add(agent, agent.pos)


class PickUpChild:
    @staticmethod
    def check(percept):
        return percept[PerceptAttr.CHILD_IN_NEXT] and not percept[PerceptAttr.CARRYING]

    @staticmethod
    def act(percept, env):
        agent = percept[PerceptAttr.AGENT]
        destination = move(agent.pos, percept[PerceptAttr.NEXT_CHILD])
        child = env.get_element(destination)
        env.remove(agent, agent.pos)
        agent.pos = destination
        env.remove(child, destination)
        env.add(agent, destination)
        agent.carry = child
        child.carry()


class ReleaseChild:
    @staticmethod
    def check(percept):
        return percept[PerceptAttr.CARRYING] and percept[PerceptAttr.PEN_IN_NEXT]

    @staticmethod
    def act(percept, env):
        agent = percept[PerceptAttr.AGENT]
        destination = move(agent.pos, percept[PerceptAttr.NEXT_PEN])
        env.remove(agent, agent.pos)
        agent.pos = destination
        env.add(agent, agent.pos)
        env.add(agent.carry, agent.pos)
        agent.carry.release()
        agent.carry.pos = agent.pos
        agent.carry = None


class CleanDirty:
    @staticmethod
    def check(percept):
        return percept[PerceptAttr.IN_DIRTY] and not percept[PerceptAttr.CARRYING]

    @staticmethod
    def act(percept, env):
        agent = percept[PerceptAttr.AGENT]
        index = 0
        while True:
            ele = env.get_element(agent.pos, index)
            if isinstance(ele, Dirty):
                env.remove(ele, agent.pos)
                return
            index += 1