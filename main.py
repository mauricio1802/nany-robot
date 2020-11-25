import numpy as np
from pprint import pprint
from random import randint
from src.env.env import Environment, EnvStatus
from src.agent.reactive import BrooksA
from src.agent.proactive import ProactiveAgent
if __name__ == '__main__':
    n_envs = 0
    results = []
    while n_envs < 1:

        rows = randint(5, 10)
        cols = randint(5, 10)
        t = randint(rows*cols // 10, rows*cols *2)
        dirty_percent = randint(0, 50)
        blocks_percent = randint(0, 50)
        childs = randint(2, 4)

        fired_times = [0, 0]
        cleaned_times = [0, 0]
        dirty_level = [[], []] 
        invalid_env = False

        for i in range(30):
            try:
                en1 = Environment(rows, cols, lambda env, pos : BrooksA(env, pos), t, blocks_percent, dirty_percent, childs)
                en2 = Environment(rows, cols, lambda env, pos : ProactiveAgent(env, pos, 100), t, blocks_percent, dirty_percent, childs)
            except AssertionError:
                invalid_env = True
                break
            envs = [en1, en2]
            for i, env in enumerate(envs):
                env.run()
                if env.result == EnvStatus.ROBOT_FIRED:
                    fired_times[i] += 1
                if env.result == EnvStatus.HOUSE_CLEANED:
                    cleaned_times[i] += 1
                dirty_level[i].append(np.mean(env.dirty_history))
            
        if invalid_env:
            continue

        agents_result =  [(fired_times[i], cleaned_times[i], np.mean(dirty_level[i])) for i in range(2)]
        result = ((rows, cols, t, dirty_percent, blocks_percent, childs), agents_result) 
        results.append(result)

        n_envs += 1

    pprint(results)
