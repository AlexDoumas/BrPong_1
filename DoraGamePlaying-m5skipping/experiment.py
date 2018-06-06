import sys
from Eviroment import Enviroment

import numpy as np
import matplotlib as mat
mat.use("AGG")

from matplotlib import pyplot as plt
import os
import pdb
  

"""
let the agent play a game in the given enviroment
if learn is true the update function of the agent is called
if show is true the game state is rendered

returns the reward gained in the game and the number of action taken in the game
"""
def playGame(env,agent,learn=False,show=True):
  State = env.reset()
  #pdb.set_trace()
  done = False
  lastaction = 0
  while not done:
    #ask the agent for an action and perfom that action in the eviroment
    action = agent.getAction(State)
    newState,reward,done,info = env.step(action, State) # you'll want to add an argument for lastaction in future. 
    if(learn):
      agent.update(State,action,newState,reward,done)
    
    if(show):
      env.render()
    
    State = newState
    lastaction = action
    #pdb.set_trace()
  return env.reward,env.rawReward,env.steps

def saveResults(savePath,enviroment,agent,rewards,rawRewards,nrSteps,iteration):
    #save the itermediate agent
    agent.save(savePath + "_" + str(iteration))
  
    #save the stats
    f = open(savePath,'a')
    for r,raw,s in zip(rewards,rawRewards,nrSteps):
      f.write(str(r) + "," + str(raw) + "," + str(s) + '\n')
    f.close()

    enviroment.makeVideo(savePath + "_" + str(iteration) + ".gif")

"""
play a given number of games with an given agent in a given enviroment and let the agent learn
if show is true the game is rendered

returns a list containing the reward gained in each game and a list containing the number of steps taken for each game
"""
def trainAgent(enviroment, agent,NrGames,writeOn,savePath, show=True):  
  #see how many times to save the agent
  NrBatches = int(NrGames / float(writeOn)) + 1
  #Train some games then save the results keep repeating until all number of games have been played
  for b in range(1,NrBatches+1):
    
    #pre allocate memory for the resulting lists
    rewards = [0 for _ in range(writeOn)]
    rawRewards = [0 for _ in range(writeOn)]
    nrSteps = [0 for _ in range(writeOn)]
  
    # play the given numbers of games
    for i in range(writeOn):
      reward,rawReward,steps = playGame(enviroment,agent,learn=True,show=show)
      rewards[i] = reward
      rawRewards[i] = rawReward
      nrSteps[i] = steps
      
      #if it is the first game save the results
      if(b==1 and i==0):
	saveResults(savePath,enviroment,agent,rewards,rawRewards,nrSteps,0)
    
    saveResults(savePath,enviroment,agent,rewards,rawRewards,nrSteps,b*writeOn)
    """
    #save the itermediate agent
    agent.save(savePath + "_" + str(b*writeOn))
  
    #save the stats
    f = open(savePath,'a')
    for r,raw,s in zip(rewards,rawRewards,nrSteps):
      f.write(str(r) + "," + str(raw) + "," + str(s) + '\n')
    f.close()

    enviroment.makeVideo(savePath + "_" + str(b*writeOn) + ".gif")
    """
  return rewards,rawRewards,nrSteps

def testAgent(enviroment, agent,NrGames,writeOn,savePath, show=True):
    #see how many times to save the agent
    NrBatches = int(NrGames / float(writeOn)) + 1
    
    #Train some games then save the results keep repeating until all number of games have been played
    for b in range(1,NrBatches+1):
        #pre-allocate memory for the resulting lists
        rewards = [0 for _ in range(writeOn)]
        rawRewards = [0 for _ in range(writeOn)]
        nrSteps = [0 for _ in range(writeOn)]
        # play the given numbers of games
        for i in range(writeOn):
            reward,rawReward,steps = playGame(enviroment,agent,learn=False,show=show)
            rewards[i] = reward
            rawRewards[i] = rawReward
            nrSteps[i] = steps
            #if it is the first game, save the results
            if(b==1 and i==0):
	            agent.save(savePath + "_" + str(0))
	if(MakeVideo):
	    enviroment.makeVideo(savePath + "_" + str(0) + ".gif")
        saveResults(savePath,enviroment,agent,rewards,rawRewards,nrSteps,b*writeOn)
        """
        #save the itermediate agent
        agent.save(savePath + "_" + str(b*writeOn))
        #save the stats
        f = open(savePath,'a')
        for r,raw,s in zip(rewards,rawRewards,nrSteps):
            f.write(str(r) + "," + str(raw) + "," + str(s) + '\n')
        f.close()
        enviroment.makeVideo(savePath + "_" + str(b*writeOn) + ".gif")
        """
    return rewards,rawRewards,nrSteps

"""
given an list of game enviroments and names this function will create a small neural agent
and train it on the games sequentially
"""
def experimentOnSmall(experimentName,games,gameNames,double=False):
  from SmallAgent import SmallAgent as Agent
  
  if(double):
    inputSize = 12
  else:
    inputSize = 8
    
  agent = Agent(inputSize=inputSize)
  
  for game,name in zip(games,gameNames):
    if(double):
      game.setGameMode("vector2")
    else:
      game.setGameMode("vector")
    trainAgent(game,agent,NrOfTrainingGames,writeOn,experimentName + "/" + name,show=False)

"""
given an list of game enviroments and names this function will create a large neural agent
and train it on the games sequentially
"""   
def experimentOnLarge(experimentName,games,gameNames):
  from LargeAgent import LargeAgent as Agent
  
  agent = Agent()
  
  for game,name in zip(games,gameNames):
    trainAgent(game,agent,NrOfTrainingGames,writeOn,experimentName + "/" + name,show=False)

"""
given an list of game enviroments and names this function will create a dora agent
and train it on the games sequentially
"""   
def experimentOnDora(experimentName,games,gameNames,double):
  from DoraModelTime import DoraAgent as Agent
  # initialise the agent. 
  agent = Agent(double)
  # here games are the videogames to play (e.g., Breakout) instiantiated as environment objects, and named by the corresponding element in gameNames (e.g., if the first element in games is an environment set to play Breakout, the first elemennt of gameNames is 'breakout'). 
  for game,name in zip(games,gameNames):
    #pdb.set_trace()
    if(double):
      game.setGameMode("vector2")
    else:
      game.setGameMode("vector")
    # 
    trainAgent(game,agent,NrOfTrainingGames,writeOn,experimentName + "/" + name,show=False)
    if(double):
      agent.flipWeights("X1","Y1")
      agent.flipWeights("X2","Y2")
    else:
      agent.flipWeights("X","Y")
    
"""
given an list of game enviroments and names this function will create a doratime agent
and train it on the games sequentially
"""   
def experimentOnDoraTime(experimentName,games,gameNames,double):
  from DoraTime import DoraTimeAgent as Agent
  
  agent = Agent(double=double)
  
  for game,name in zip(games,gameNames):
    if(double):
      game.setGameMode("vector2")
    else:
      game.setGameMode("vector")

    trainAgent(game,agent,NrOfTrainingGames,writeOn,experimentName + "/" + name,show=False)
    if(double):
      agent.flipWeights("X1","Y1")
      agent.flipWeights("X2","Y2")
    else:
      agent.flipWeights("X","Y")
    
def continueOnDora(experimentName,games,gameNames):
  from DoraModel import DoraAgent as Agent
  
  agent = Agent.load("Dora_BPB/Breakout_1_1000")
  agent.flipWeights("X","Y")
  
  for game,name in zip(games,gameNames):
    trainAgent(game,agent,NrOfTrainingGames,writeOn,experimentName + "/" + name,show=False)
    agent.flipWeights("X","Y")
    
if(__name__ == "__main__"):
  
  #The number game to train the agent on
  NrOfTrainingGames = 1000
  #save the result after every number game
  writeOn = 10
  mode = sys.argv[1]
  saveFile = sys.argv[2]
  if(mode == "small"):
    double = sys.argv[3] == "true"
    games = [Enviroment(gameMode="vector",rewardMode="label",autoFire=True),Enviroment(Breakout=False,gameMode="vector",rewardMode="label",autoFire=True),Enviroment(gameMode="vector",rewardMode="label",autoFire=True)]
    gameNames = ["Breakout_1","Pong","Breakout_2"]
    experimentOnSmall(saveFile,games,gameNames,double)
  elif(mode == "large"):
    games = [Enviroment(gameMode="neural",rewardMode="label",autoFire=True),Enviroment(Breakout=False,gameMode="neural",rewardMode="label",autoFire=True),Enviroment(gameMode="neural",rewardMode="label",autoFire=True)]
    gameNames = ["Breakoutg_1","Pong","Breakout_2"]
    experimentOnSmall(saveFile,games,gameNames)
  elif(mode == "dora"):
    double = sys.argv[3] == "true"
    games = [Enviroment(gameMode="vector",rewardMode="follow",autoFire=True),Enviroment(Breakout=False,gameMode="vector",rewardMode="follow",autoFire=True),Enviroment(gameMode="vector",rewardMode="follow",autoFire=True)]
    gameNames = ["Breakout_1","Pong","Breakout_2"]
    experimentOnDora(saveFile,games,gameNames,double)
  elif(mode == "doraTime"):
    double = sys.argv[3] == "true"
    games = [Enviroment(gameMode="vector",rewardMode="follow",autoFire=True),Enviroment(Breakout=False,gameMode="vector",rewardMode="follow",autoFire=True),Enviroment(gameMode="vector",rewardMode="follow",autoFire=True)]
    gameNames = ["Breakout_1","Pong","Breakout_2"]
    experimentOnDoraTime(saveFile,games,gameNames,double)