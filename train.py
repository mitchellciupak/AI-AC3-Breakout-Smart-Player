# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 11:32:21 2020

@author: mjcre
"""

# Import
import torch
import torch.nn.functional as F
from envs import create_atari_env
from model import ActorCritic
from torch.autograd import Variable

# Init ensurance the models share the same gradient
def ensure_shared_grads(model, shared_model):
    for param, shared_param in zip(model.parameters(), shared_model.parameters()):
        if shared_param.grad is not None:
            return
        shared_param._grad = param.grad
        
        
def train(rank, params, shared_model, optimizer):
    torch.manual_seed(params.seed + rank) # shifting the seed with rank to asynchronize each training agent
    env = create_atari_env(params.env_name) # creating an optimized environment thanks to the create_atari_env function
    env.seed(params.seed + rank) # aligning the seed of the environment on the seed of the agent
    model = ActorCritic(env.observation_space.shape[0], env.action_space) # creating the model from the ActorCritic class
    state = env.reset() # state is a numpy array of size 1*42*42, in black & white
    state = torch.from_numpy(state) # converting the numpy array into a torch tensor
    done = True # when the game is done
    episode_length = 0 # initializing the length of an episode to 0
    
    while True: # repeat
        episode_length += 1 # incrementing the episode length by one
        model.load_state_dict(shared_model.state_dict()) # synchronizing with the shared model - the agent gets the shared model to do an exploration on num_steps
        if done: # if it is the first iteration of the while loop or if the game was just done, then:
            cx = Variable(torch.zeros(1, 256)) # the cell states of the LSTM are reinitialized to zero
            hx = Variable(torch.zeros(1, 256)) # the hidden states of the LSTM are reinitialized to zero
        else: # else:
            cx = Variable(cx.data) # we keep the old cell states, making sure they are in a torch variable
            hx = Variable(hx.data) # we keep the old hidden states, making sure they are in a torch variable
        values = [] # initializing the list of values (V(S))
        log_probs = [] # initializing the list of log probabilities
        rewards = [] # initializing the list of rewards
        entropies = [] # initializing the list of entropies
        for step in range(params.num_steps): # going through the num_steps exploration steps
            value, action_values, (hx, cx) = model((Variable(state.unsqueeze(0)), (hx, cx))) # getting from the model the output V(S) of the critic, the output Q(S,A) of the actor, and the new hidden & cell states
            prob = F.softmax(action_values) # generating a distribution of probabilities of the Q-values according to the softmax: prob(a) = exp(prob(a))/sum_b(exp(prob(b)))
            log_prob = F.log_softmax(action_values) # generating a distribution of log probabilities of the Q-values according to the log softmax: log_prob(a) = log(prob(a))
            entropy = -(log_prob * prob).sum(1) # H(p) = - sum_x p(x).log(p(x))
            entropies.append(entropy) # storing the computed entropy
            if done: # if the episode is done:
                episode_length = 0 # we restart the environment
                state = env.reset() # we restart the environment
            state = torch.from_numpy(state) # tensorizing the new state
            rewards.append(reward) # storing the new observed reward
            if done: # if we are done
                break # we stop the exploration and we directly move on to the next step: the update of the shared model
            
            
            
            
            
            
            
            