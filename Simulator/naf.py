import numpy as np
import gym
from carom import Carom

from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Flatten, Input, Concatenate
from keras.optimizers import Adam

from rl.agents import NAFAgent
from rl.memory import SequentialMemory
from rl.random import OrnsteinUhlenbeckProcess
from rl.core import Processor

class CaromProcessor(Processor):
    def process_reward(self, reward):
        return reward


ENV_NAME = 'Carom-v0'
gym.undo_logger_setup()


# Get the environment and extract the number of actions.
env = Carom(render = False)
np.random.seed(321)
env.seed(321)
assert len(env.action_space.shape) == 1
nb_actions = env.action_space.shape[0]

# Build all necessary models: V, mu, and L networks.
V_model = Sequential()
V_model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
V_model.add(Dense(16))
V_model.add(Activation('relu'))
V_model.add(Dense(16))
V_model.add(Activation('relu'))
V_model.add(Dense(16))
V_model.add(Activation('relu'))
V_model.add(Dense(1))
V_model.add(Activation('linear'))
print(V_model.summary())

mu_model = Sequential()
mu_model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
mu_model.add(Dense(16))
mu_model.add(Activation('relu'))
mu_model.add(Dense(16))
mu_model.add(Activation('relu'))
mu_model.add(Dense(16))
mu_model.add(Activation('relu'))
mu_model.add(Dense(nb_actions))
mu_model.add(Activation('linear'))
print(mu_model.summary())

action_input = Input(shape=(nb_actions,), name='action_input')
observation_input = Input(shape=(1,) + env.observation_space.shape, name='observation_input')
x = Concatenate()([action_input, Flatten()(observation_input)])
x = Dense(32)(x)
x = Activation('relu')(x)
x = Dense(32)(x)
x = Activation('relu')(x)
x = Dense(32)(x)
x = Activation('relu')(x)
x = Dense(((nb_actions * nb_actions + nb_actions) // 2))(x)
x = Activation('linear')(x)
L_model = Model(inputs=[action_input, observation_input], outputs=x)
print(L_model.summary())

# Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
# even the metrics!
processor = CaromProcessor()
memory = SequentialMemory(limit=50000, window_length=1)
random_process = OrnsteinUhlenbeckProcess(theta=.15, mu=0., sigma=.3, size=nb_actions)
agent = NAFAgent(nb_actions=nb_actions, V_model=V_model, L_model=L_model, mu_model=mu_model,
                 memory=memory, nb_steps_warmup=100, random_process=random_process,
                 gamma=.99, target_model_update=1e-3, processor = processor)
agent.compile(Adam(lr=.001, clipnorm=1.), metrics=['mae'])
agent.load_weights('cdqn_{}_weights.h5f'.format(ENV_NAME))

# Okay, now it's time to learn something! We visualize the training here for show, but this
# slows down training quite a lot. You can always safely abort the training prematurely using
# Ctrl + C.
agent.fit(env, nb_steps=50000, visualize=False, verbose=1, nb_max_episode_steps=200)

# After training is done, we save the final weights.
agent.save_weights('cdqn_{}_weights.h5f'.format(ENV_NAME), overwrite=True)
# Finally, evaluate our algorithm for 5 episodes.
env.render = True

agent.test(env, nb_episodes=10, visualize=False, nb_max_episode_steps=200)