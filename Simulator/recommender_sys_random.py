import gym
import numpy as np
from tensorflow.keras.layers import Activation, Concatenate, Dense, Flatten, Input
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.optimizers import Adam
from rl.agents import DDPGAgent
from rl.memory import *
from carom import Carom

ENV_NAME = 'Carom-v0'
# gym.undo_logger_setup()


# Get the environment and extract the number of actions.
env = Carom(render = False)
np.random.seed(323)
env.seed(323)
assert len(env.action_space.shape) == 1
nb_actions = env.action_space.shape[0]

# Next, we build a very simple model.
actor = Sequential()
actor.add(Flatten(input_shape=(1,) + env.observation_space.shape))
actor.add(Dense(16))
actor.add(Activation('relu'))
actor.add(Dense(16))
actor.add(Activation('relu'))
actor.add(Dense(16))
actor.add(Activation('relu'))
actor.add(Dense(nb_actions))
actor.add(Activation('linear'))

action_input = Input(shape=(nb_actions,), name='action_input')
observation_input = Input(shape=(1,) + env.observation_space.shape, name='observation_input')
flattened_observation = Flatten()(observation_input)
x = Concatenate()([action_input, flattened_observation])
x = Dense(32)(x)
x = Activation('relu')(x)
x = Dense(32)(x)
x = Activation('relu')(x)
x = Dense(32)(x)
x = Activation('relu')(x)
x = Dense(1)(x)
x = Activation('linear')(x)
critic = Model(inputs=[action_input, observation_input], outputs=x)

memory = SequentialMemory(limit=50000, window_length=1)
agent = DDPGAgent(nb_actions=nb_actions, actor=actor, critic=critic, critic_action_input=action_input,
                  memory=memory, nb_steps_warmup_critic=100, nb_steps_warmup_actor=100, gamma=.99, target_model_update=1e3)
agent.compile(Adam(lr=.001, clipnorm=1.), metrics=['mae'])
agent.load_weights('ddpg_{}_2balls_final_weights_v4.h5f'.format(ENV_NAME))

# def B(b):
#     env.render = False
#     state = env.reset()
#     pos = env.arraystate2pos(state)
#     print(pos)
#     optimal_action = np.zeros(2)
#     action, optimal_action, a, b, theta = agent.test(env, nb_episodes=500000, visualize=False, nb_max_episode_steps=200, modif = True, pos = pos)
#     env.non_random_reset(pos[0], pos[1], pos[2])
#     env.render = True
#     env.step(action, rand = optimal_action, a = a, b = b, theta = theta)


# state = env.reset()
# pos = env.arraystate2pos(state)
# optimal_action = np.zeros(2)
# optimal_action[0], optimal_action[1], a, b, theta = agent.test(env, nb_episodes=500000, visualize=False, nb_max_episode_steps=200, modif = True, pos = pos)

# env.non_random_reset(pos[0], pos[1], pos[2])
# env.render = True
# env.step(optimal_action, a = a, b = b, theta = theta)
nb_test = 50
for i in range(nb_test):
    env.render = False
    state = env.reset()
    pos = env.arraystate2pos(state)
    optimal_action = np.zeros(2)
    action, optimal_action, a, b, theta = agent.test(env, nb_episodes=500000, visualize=False, nb_max_episode_steps=200, modif = True, pos = pos)
    env.non_random_reset(pos[0], pos[1], pos[2])
    env.render = True
    env.step(action, rand = optimal_action, a = a, b = b, theta = theta)