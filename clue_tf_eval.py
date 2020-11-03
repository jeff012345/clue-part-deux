import tensorflow as tf

import os

from clue_tf_env import ClueGameEnv

from tf_agents.policies import policy_saver
from tf_agents.environments import tf_py_environment

tf.compat.v1.enable_v2_behavior()

eval_py_env = ClueGameEnv(eval = True)
eval_tf_env = tf_py_environment.TFPyEnvironment(eval_py_env)


policy_dir = os.path.join("models", "c51-5", "policy")
saved_policy = tf.compat.v2.saved_model.load(policy_dir)


num_episodes = 1000
wins = 0

for cnt in range(num_episodes):
    time_step = eval_tf_env.reset()

    while not time_step.is_last():
        action_step = saved_policy.action(time_step)
        time_step = eval_tf_env.step(action_step.action)

    if eval_py_env._clue.winner == eval_py_env._ai_player:
        wins += 1

    if cnt % 50 == 0:
        print("Game " + str(cnt) + " of " + str(num_episodes))

print("Win ratio = " + str((wins / num_episodes) * 100) + "%")


