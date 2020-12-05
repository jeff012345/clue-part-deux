from __future__ import absolute_import, division, print_function

import base64
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import IPython
import os

import tensorflow as tf

from tf_agents.agents.dqn import dqn_agent
from tf_agents.agents.reinforce import reinforce_agent
from tf_agents.agents.categorical_dqn import categorical_dqn_agent
from tf_agents.drivers import dynamic_step_driver
from tf_agents.environments import suite_gym
from tf_agents.environments import tf_py_environment
from tf_agents.eval import metric_utils
from tf_agents.metrics import tf_metrics
from tf_agents.networks import q_network
from tf_agents.networks import categorical_q_network
from tf_agents.networks import actor_distribution_network
from tf_agents.policies import random_tf_policy
from tf_agents.policies import policy_saver
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.trajectories import trajectory
from tf_agents.utils import common

from clue_tf_env import ClueGameEnv
from clue_room_tf_env import ClueGameRoomEnv
from ai_players import RLPlayer
from paths import Board

tf.compat.v1.enable_v2_behavior()

## cache this data
Board.calculate_room_distances()

## utility functions
def compute_avg_return(environment, policy, num_episodes=10):
    total_return = 0.0

    wins = 0

    for _ in range(num_episodes):
        time_step = environment.reset()
        episode_return = 0.0

        while not time_step.is_last():
            action_step = policy.action(time_step)
            time_step = environment.step(action_step.action)
            episode_return += time_step.reward

        total_return += episode_return
        
        if isinstance(eval_py_env._clue.winner, RLPlayer):
            wins += 1

    print("Win Ratio = " + str(wins / num_episodes))

    avg_return = total_return / num_episodes
    return avg_return.numpy()[0]

def collect_step(environment, policy, buffer):
  time_step = environment.current_time_step()
  action_step = policy.action(time_step)
  next_time_step = environment.step(action_step.action)
  traj = trajectory.from_transition(time_step, action_step, next_time_step)

  # Add trajectory to the replay buffer
  buffer.add_batch(traj)
 
def collect_episode(environment, policy, num_episodes):

  episode_counter = 0
  environment.reset()

  while episode_counter < num_episodes:
    time_step = environment.current_time_step()
    action_step = policy.action(time_step)
    next_time_step = environment.step(action_step.action)
    traj = trajectory.from_transition(time_step, action_step, next_time_step)

    # Add trajectory to the replay buffer
    replay_buffer.add_batch(traj)

    if traj.is_boundary():
        episode_counter += 1

##
## Hyperparameters
##
num_iterations = 10000 # @param {type:"integer"}
collect_episodes_per_iteration = 20 # @param {type:"integer"}
replay_buffer_capacity = 100000 # @param {type:"integer"}

batch_size = 64  # @param {type:"integer"}
#learning_rate = 1e-3  # @param {type:"number"}
learning_rate = 1e-3  # @param {type:"number"}
gamma = 0.99
log_interval = 25  # @param {type:"integer"}

#num_atoms = 51  # @param {type:"integer"}
num_atoms = 51  # @param {type:"integer"}
min_q_value = -100  # @param {type:"integer"}
max_q_value = 0  # @param {type:"integer"}
n_step_update = 3  # @param {type:"integer"}

num_eval_episodes = 25 # @param {type:"integer"}
eval_interval = 250 # @param {type:"integer"}

fc_layer_params = (1000,1500,1000)

##
## environment setup
##

train_py_env = ClueGameEnv() #ClueGameRoomEnv()
eval_py_env = ClueGameEnv() #ClueGameRoomEnv()

train_env = tf_py_environment.TFPyEnvironment(train_py_env)
eval_env = tf_py_environment.TFPyEnvironment(eval_py_env)

##
## Setup Network
##
categorical_q_net = categorical_q_network.CategoricalQNetwork(
    train_env.observation_spec(),
    train_env.action_spec(),
    num_atoms=num_atoms,
    fc_layer_params=fc_layer_params)

##
## Setup Agent
##

optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate=learning_rate)

train_step_counter = tf.compat.v2.Variable(0)

agent = categorical_dqn_agent.CategoricalDqnAgent(
    train_env.time_step_spec(),
    train_env.action_spec(),
    categorical_q_network=categorical_q_net,
    optimizer=optimizer,
    min_q_value=min_q_value,
    max_q_value=max_q_value,
    n_step_update=n_step_update,
    td_errors_loss_fn=common.element_wise_squared_loss,
    gamma=gamma,
    train_step_counter=train_step_counter)
agent.initialize()

##
## Policies
##

eval_policy = agent.policy
collect_policy = agent.collect_policy

##
## replay buffer
##
replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
    data_spec=agent.collect_data_spec,
    batch_size=train_env.batch_size,
    max_length=replay_buffer_capacity)

## create the checkpointer
checkpoint_dir = os.path.join(".", 'checkpoint')
train_checkpointer = common.Checkpointer(
    ckpt_dir=checkpoint_dir,
    max_to_keep=1,
    agent=agent,
    policy=agent.policy,
    replay_buffer=replay_buffer,
    global_step=train_step_counter
)

if os.path.isdir(checkpoint_dir) and len(os.listdir(checkpoint_dir)) != 0:
    train_checkpointer.initialize_or_restore()
    train_step_counter = tf.compat.v1.train.get_global_step()
    print("loading from checkpoint")

# Dataset generates trajectories with shape [BxTx...] where
# T = n_step_update + 1.
dataset = replay_buffer.as_dataset(
    num_parallel_calls=3, sample_batch_size=batch_size,
    num_steps=n_step_update + 1).prefetch(3)

iterator = iter(dataset)

# (Optional) Optimize by wrapping some of the code in a graph using TF function.
agent.train = common.function(agent.train)

# Reset the train step
agent.train_step_counter.assign(0)

# Evaluate the agent's policy once before training.
avg_return = compute_avg_return(eval_env, agent.policy, num_eval_episodes)
returns = [avg_return]

print("Train")
for _ in range(num_iterations):
    # Collect a few episodes using collect_policy and save to the replay buffer.
    collect_episode(train_env, agent.collect_policy, collect_episodes_per_iteration)

    # Use data from the buffer and update the agent's network.
    experience, unused_info = next(iterator)
    train_loss = agent.train(experience)
    replay_buffer.clear()

    step = agent.train_step_counter.numpy()

    if step % log_interval == 0:
        print('step = {0}: loss = {1}'.format(step, train_loss.loss))

    if step % eval_interval == 0:
        avg_return = compute_avg_return(eval_env, agent.policy, num_eval_episodes)
        print('step = {0}: Average Return = {1}'.format(step, avg_return))
        returns.append(avg_return)

        # checkpoint saved
        train_checkpointer.save(train_step_counter)



iterations = range(0, num_iterations + 1, eval_interval)
plt.plot(iterations, returns)
plt.ylabel('Average Return')
plt.xlabel('Iterations')
plt.ylim(top=0)
plt.show()

policy_dir = os.path.join(".", 'policy')
tf_policy_saver = policy_saver.PolicySaver(agent.policy)
tf_policy_saver.save(policy_dir)

print(str(returns))