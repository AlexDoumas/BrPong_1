import sys
from Eviroment import Enviroment

import numpy as np
from matplotlib import pyplot as plt
import os

"""
let the agent play a game in the given enviroment
if learn is true the update function of the agent is called
if show is true the game state is rendered

returns the reward gained in the game and the number of action taken in the game
"""
def playGame(env,agent,learn=False,show=True):
  State = env.reset()
  done = False
  while not done:
    #ask the agent for an action and perfom that action in the eviroment
    action = agent.getAction(State)
    newState,reward,done,info = env.step(action)
    
    if(learn):
      agent.update(State,action,newState,reward,done)
    
    if(show):
      env.render()
      
    State = newState
  
  return env.reward,env.steps

"""
play a given number of games with an given agent in a given enviroment and let the agent learn
if show is true the game is rendered

returns a list containing the reward gained in each game and a list containing the number of steps taken for each game
"""
def trainAgent(enviroment, agent,NrGames, show=True):
  #pre allocate memory for the resulting lists
  rewards = [0 for _ in range(NrGames)]
  nrSteps = [0 for _ in range(NrGames)]
  
  # play the given numbers of games
  for i in range(NrGames):
    reward,steps = playGame(enviroment,agent,learn=True,show=show)
    rewards[i] = reward
    nrSteps[i] = steps
    
  return rewards,nrSteps

"""
Train the neural network as specified in atari2600
(The neural network complete with vison)
"""
def TrainLargeAgent(NrGames,writeOn,savePath,show=False):
  from LargeAgent import LargeAgent as Agent
  
  #make the enviroment
  env = Enviroment(enhancedReward=True,autoFire=True)
  #because of the influence of tensorflow draw the enviroment once before making any call to tensorflow of don't draw at all
  if(show):
    env.reset()
    env.render()
  
  #make the agent
  agent = Agent()
  
  #see how many times to save the agent
  NrBatches = int(NrGames / float(writeOn)) + 1
  
  
  totalNrFrames = 0
  #Train some games then save the results keep repeating until all number of games have been played
  for i in range(NrBatches):
    print "batch",i,"of",NrBatches
    #train the agent
    reward,steps = trainAgent(env,agent,writeOn,show=show)
    
    totalNrFrames += np.sum(steps)
    #save the itermediate agent
    agent.save(savePath + "_" + str(i*writeOn))
    
    #save the stats
    f = open(savePath,'a')
    for r,s in zip(reward,steps):
      f.write(str(r) + "," + str(s) + '\n')
    f.close()

    env.makeVideo(savePath + "_" + str(i*writeOn) + ".gif")

def TrainSmallAgent(NrGames,writeOn,savePath,show=False):
  from SmallAgent import SmallAgent as Agent
  
  #make the enviroment
  env = Enviroment(fullImage=False,enhancedReward=True,autoFire=True)
  if(show):
    env.reset()
    env.render()
    
  agent = Agent()
  
  #see how many times to save the agent
  NrBatches = int(NrGames / float(writeOn)) + 1
  
  #Train some games then save the results keep repeating until all number of games have been played
  for i in range(NrBatches):
    print "batch",i,"of",NrBatches
    #train the agent
    reward,steps = trainAgent(env,agent,writeOn,show=show)
    
    #save the itermediate agent
    agent.save(savePath + "_" + str(i*writeOn))
    
    #save the stats
    f = open(savePath,'a')
    for r,s in zip(reward,steps):
      f.write(str(r) + "," + str(s) + '\n')
    f.close()

    env.makeVideo(savePath + "_" + str(i*writeOn) + ".gif")
  
def TrainDoraAgent(NrGames,writeOn,savePath,show=False):
  from DoraModel import DoraAgent as Agent
  
  #make the enviroment
  env = Enviroment(fullImage=False,enhancedReward=True,autoFire=True)
  if(show):
    env.reset()
    env.render()
    
  agent = Agent("symfile")
  
  #see how many times to save the agent
  NrBatches = int(NrGames / float(writeOn)) + 1
  
  #Train some games then save the results keep repeating until all number of games have been played
  for i in range(NrBatches):
    print "batch",i,"of",NrBatches
    #train the agent
    reward,steps = trainAgent(env,agent,writeOn,show=show)
    
    #save the itermediate agent
    agent.save(savePath + "_" + str(i*writeOn))
    
    #save the stats
    f = open(savePath,'a')
    for r,s in zip(reward,steps):
      f.write(str(r) + "," + str(s) + '\n')
    f.close()
    
    env.makeVideo(savePath + "_" + str(i*writeOn) + ".gif")

if(__name__ == "__main__"):
  from datetime import datetime as date
  
  mode = sys.argv[1]
  
  if(mode == "small"):
    TrainSmallAgent(100000,1000,"SmallAgentTest/" + str(date.now().strftime("%d-%m-%Y")),show=False)
  elif(mode == "large"):
    TrainLargeAgent(100000,1000,"LargeAgent/" + str(date.now().strftime("%d-%m-%Y")),show=False)
  elif(mode == "dora"):
    TrainDoraAgent(100000,1000,"Dora/" + str(date.now().strftime("%d-%m-%Y")),show=False)
  else:
    pass


