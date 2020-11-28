## About
This project is an implementation of the board game Clue with an AI player. The agent was created using TensorFlow using Reinforcement Learning techniques. The game board was implemented with PyGame.

There are three main components.
1. Scripts for training a Weapon/Character guessing agent
2. Scripts for training a Room guessing agent
3. A fully playable game of Clue with the trained AI

## Requirements
Review the `clue_env.yml` Anaconda environment export

The tensorflow-gpu package was used during development and training. I assume it will work with the Tensorflow CPU version, but I haven't tested that.

## Running the Game
Need to specify the policies to run for the two agents in `main.py`

To run the game...
`python main.py`

## Training 
The checkpoints are saved every 250 episodes and the policy it saved at the end of training. They are saved in folders in the working directory.

Weapon/Character Guess Agent
`python clue_tf.py`

Room Guess Agent
`python clue_tf_cat_dqn.py`

## Evaluation
Evaluating a single agent. You'll need to set the path to the policy in the script..
`python clue_tf_eval.py`

Evaluating a both agents at the same time. You'll need to set the path to both policies in the script..
`python clue_tf_eval_both.py`
