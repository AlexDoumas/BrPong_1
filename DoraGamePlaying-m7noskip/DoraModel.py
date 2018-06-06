import sys
sys.path.append('/home/dylopd/Documents/Dora/currentVers/')

import numpy as np
import tensorflow as tf

import os
import json
import pdb

import entropy_ops as entropy

class DoraAgent:
  
  def __init__(self,double=False):
    #self.symfile = symfile
    
    self.possibleDimentions = ["X","Y","Xvel","Yvel"]
    if(double):
        self.possiblePredicates = ["SameMore","MoreMore","LessMore","SameSame","MoreSame","LessSame","SameLess","MoreLess","LessLess"]
    else:
        self.possiblePredicates = ["Same","More","Less"]
    self.possiblePreds2 = ["Same","More","Less"] # for use with trajectories. 
    self.possiblePreds3 = ['Same', 'Diff'] # for iuse with relation of trajectories. 
    self.useTime = False
    self.lastChosenDim = None
    self.lastChosenPred = None
    self.lastTrajItem = None
    self.lastChosenTrajectory = None
    self.NrActions = 3
    self.predHistory = [] # initialise an empty array to store a dictionary of representational history. 
    self.lastGameStates = None # where previous gamestates are stored. 
    
    self.time = 0
    
    self.setupTables()
    
    self.lr = 0.01
    self.y = 0.01
    
    self.e = 0.9
    self.deltaE = -0.0001
    
    #skipframes
    self.skipFrame = 1
    self.currentFrame = -1
    
    #collect transitions and perform larger updates in one go
    self.States = None
    self.actionLabels = None
    
    self.updateSize = 128

  def setupTables(self):
    # the lookup table to pick a dimention given a gameState
    self.dimentionTable = {}
    self.actionTable = {}
    # and now make the lookup tables for dimention and action. 
    for dim in self.possibleDimentions:
        self.dimentionTable[str(dim)] = 0
        self.actionTable[dim] = {}
        if self.useTime == True:
            for pred in self.possiblePredicates:
                for trajB in self.possiblePreds2:
                    for trajP in self.possiblePreds2:
                        action = pred + trajB + trajP
                        self.actionTable[dim][action] = [0.0]*self.NrActions
        else:
            for pred in self.possiblePredicates:
                action = pred
                self.actionTable[dim][action] = [0.0]*self.NrActions
    
  def gameStateToDict(self,gameState):
    #put the game state in a dictionary for reablility sake
    gm = (gameState*100).astype(np.int32)
    gm[gm==0] = 1
    
    gameState = {}
    if(gm.shape[0] == 8):
      gameState["Paddle"] = {"X":gm[0],"Y":gm[1],"Xvel":gm[2]+50,"Yvel":gm[3]+50}
      gameState["Ball"] = {"X":gm[4],"Y":gm[5],"Xvel":gm[6]+50,"Yvel":gm[7]+50}
    elif(gm.shape[0] == 12):
      gameState["Paddle"] = {"X1":gm[0],"Y1":gm[1],"X2":gm[2],"Y2":gm[3],"Xvel1":gm[4]+50,"Yvel1":gm[5]+50,"Xvel2":gm[4]+50,"Yvel2":gm[5]+50}
      gameState["Ball"] = {"X1":gm[6],"Y1":gm[7],"X2":gm[8],"Y2":gm[9],"Xvel1":gm[10]+50,"Yvel1":gm[11]+50,"Xvel2":gm[10]+50,"Yvel2":gm[11]+50}
    return gameState

  #get the predicate applicable to the current gamestate on the given dimention
  def getPredicate(self,gameState,dimention):
    gameStateDict = self.gameStateToDict(gameState)
    
    if(gameState.shape[0] == 8):
      Largest,Smallest,same,iterations = entropy.ent_magnitudeMoreLessSame(gameStateDict["Paddle"][dimention],gameStateDict["Ball"][dimention])
      if(same):
          return "Same"
      elif (gameStateDict["Paddle"][dimention]-4 < gameStateDict["Ball"][dimention]) and (gameStateDict["Paddle"][dimention]+4 > gameStateDict["Ball"][dimention]):
          return "Same"
      elif(Largest == gameStateDict["Paddle"][dimention]):
          return "More"
      else:
          return "Less"
    elif(gameState.shape[0] == 12):
      #check the first cordinate on the dimention
      Largest,Smallest,same,iterations = entropy.ent_magnitudeMoreLessSame(gameStateDict["Paddle"][dimention + "1"],gameStateDict["Ball"][dimention + "1"])
      if(same):
	part1 = "Same"
      elif(Largest == gameStateDict["Paddle"][dimention + "1"]):
	part1 = "More"
      else:
	part1 = "Less"
	
      #check the first cordinate on the dimention
      Largest,Smallest,same,iterations = entropy.ent_magnitudeMoreLessSame(gameStateDict["Paddle"][dimention + "2"],gameStateDict["Ball"][dimention + "2"])
      if(same):
	part2 = "Same"
      elif(Largest == gameStateDict["Paddle"][dimention + "2"]):
	part2 = "More"
      else:
	part2 = "Less"
      return part1 + part2
    return "Error Something whent wrong"

  """
  make a discrete vector from the continiuos game vector
  """
  def makeGird(self,gamestate):
    pass
    return (gamestate/0.1).astype(np.int32)

  """
  make a numpy array into a dictionary key
  """
  def toKey(self,array):
    ar = (array/0.1).astype(np.int32)
    return str(ar).strip('[]').replace('\n','')
    
  #pick one of the possible dimentions given an gameState
  def pickDimention(self,gameStateKey):
    # pick the dim with the highest weight plus some noise. 
    dim = max(self.dimentionTable, key=self.dimentionTable.get)
    dimIndex = self.possibleDimentions.index(dim)
    #a small chance of picking a random dimention
    if(np.random.rand() < self.e):
        dimIndex = np.random.randint(0,len(self.possibleDimentions))
        dim = self.possibleDimentions[dimIndex]
    return dim, dimIndex

  #select an action given a predicate
  def selectAction(self,dimention,predicate):
      action = np.argmax(self.actionTable[dimention][predicate])
      if(np.random.rand() < self.e):
          action = np.random.randint(0,3)
      return action

  def getAction(self, gameState):
    self.currentFrame += 1
    self.toKey(gameState)
    gameStateKey = self.toKey(gameState)
    
    # get an dimention given the gamestate
    self.lastChosenDim,dimNr = self.pickDimention(gameStateKey)
    self.lastChosenDim = "Y"
    #get the predicate for a given dimention
    self.lastChosenPred = self.getPredicate(gameState,self.lastChosenDim)
    #select an action
    action = self.selectAction(self.lastChosenDim,self.lastChosenPred)
    
    self.e = np.max([0.0,self.e + self.deltaE])
    
    self.time += 1
    return action  

  def update(self,oldState,action,newState,reward,terminal):
    #update the dimention table
    NewgameStateKey = self.toKey(newState)
    # get the expected reward in the new state
    expedReward = np.max([self.dimentionTable[dim] for dim in self.possibleDimentions])
    OldgameStateKey = self.toKey(oldState)
    self.dimentionTable[self.lastChosenDim] = self.dimentionTable[self.lastChosenDim] + self.lr*(reward + self.y * expedReward)
    
    # the dimention that the agent would pick in this new state. 
    newDim,newDimNr = self.pickDimention(NewgameStateKey)
    # the predicate that the agent would make in the newState. 
    newPred = self.getPredicate(newState,newDim)
    # the trajectory of the items, if there is a lastGameState.
    if self.lastGameStates is not None:
        lastTrajBall, lastTrajPaddle, lastTrajRel = self.getTrajs(newState)
    else:
        lastTrajBall, lastTrajPaddle, lastTrajRel = None, None, None
    if self.useTime:
        if lastTrajRel is not None and self.lastTrajRel is not None:
            action_name = newPred + lastTrajBall + lastTrajPaddle
            # NOTE: Making a second action_name called action_name2 out of the self.lastChosenPred + self.lastTrajPaddle + self.lastTRajRel. The reason is that Dylan's original code updated expected reward using newPred and actionTable using self.lastChosenPred. I don't actually think there's a difference between these two for the purposes of the current function, but I'm honoring the original separation for legacy purposes. 
            action_name2 = self.lastChosenPred + self.lastTrajBall + self.lastTrajPaddle 
            expedReward = np.max(self.actionTable[newDim][action_name])
            #update the action table
            self.actionTable[self.lastChosenDim][action_name2][action] = self.actionTable[self.lastChosenDim][action_name2][action] + self.lr*(reward + self.y * expedReward)
    else:
        action_name = newPred
        # NOTE: Making a second action_name called action_name2 out of the self.lastChosenPred + self.lastTrajPaddle + self.lastTRajRel. The reason is that Dylan's original code updated expected reward using newPred and actionTable using self.lastChosenPred. I don't actually think there's a difference between these two for the purposes of the current function, but I'm honoring the original separation for legacy purposes. 
        action_name2 = self.lastChosenPred
        expedReward = np.max(self.actionTable[newDim][action_name])
        #update the action table
        self.actionTable[self.lastChosenDim][action_name2][action] = self.actionTable[self.lastChosenDim][action_name2][action] + self.lr*(reward + self.y * expedReward)
  
  """
  flip the weights
  """
  def flipWeights(self,dim1,dim2):
    #flip the dimention table
    for key in self.dimentionTable:
      temp = self.dimentionTable[key][dim1]
      self.dimentionTable[key][dim1] = self.dimentionTable[key][dim2]
      self.dimentionTable[key][dim2] = temp
      
    #flip the action table
    temp = self.actionTable[dim1]
    self.actionTable[dim1] = self.actionTable[dim2]
    self.actionTable[dim2] = temp

  @staticmethod
  def load(filename):
    folder = os.path.dirname(filename)
    filename = filename.replace(folder + '/','')
    if(os.path.isfile(folder + '/' + filename + '/' + filename + "dim.table")):
      agent = DoraAgent()
      
      actionTable = json.load(open("./" + folder + '/' + filename + '/' + filename + "act.table",'r'))
      dimentionTable = json.load(open("./" + folder + '/' + filename + '/' + filename + "dim.table",'r'))
      
      agent.actionTable = actionTable
      agent.dimentionTable = dimentionTable
      
      return agent
    else:
      return DoraAgent()

  def save(self,filename):
    folder = os.path.dirname(filename)
    filename = filename.replace(folder + '/','')
    if(not os.path.isdir("./" + folder)):
      os.mkdir(folder);
    if(not os.path.isdir("./" + folder + '/' + filename)):
      os.mkdir("./" + folder + '/' + filename);
    
    json.dump(self.dimentionTable,open("./" + folder + '/' + filename + '/' + filename + "dim.table",'w'))
    json.dump(self.actionTable,open("./" + folder + '/' + filename + '/' + filename + "act.table",'w'))
    # "./" + folder + '/' + filename + '/' + filename)
    
if(__name__ == "__main__"):
  import time
  from Eviroment import Enviroment
  
  env = Enviroment(gameMode="vector2",rewardMode="follow",autoFire=True)
  
  agent = DoraAgent(double=True)
  
  action = 0
  
  frame = -1
  skipFrame = 1
  
  done = False
  S = env.reset()
  while not done:
    frame += 1
    if(frame%skipFrame==0):
      action = agent.getAction(S)
    S,r,done,info = env.step(action)
    time.sleep(0.5)
    env.render()
  print "game evaluation: ", env.reward