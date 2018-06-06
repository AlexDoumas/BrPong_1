import sys
sys.path.append('/home/dylopd/Documents/Dora/currentVers/')

import numpy as np
import tensorflow as tf

import os
import json

import entropy_ops as entropy

class DoraTimeAgent:
  
  def __init__(self,double=False):
    #self.symfile = symfile
    
    self.possibleDimentions = ["X","Y","Xvel","Yvel"]
    if(double):
      self.possiblePredicates = ["SameMore","MoreMore","LessMore","SameSame","MoreSame","LessSame","SameLess","MoreLess","LessLess"]
    else:
      self.possiblePredicates = ["Same","More","Less"]
    self.possibleObjects = ["Ball","Paddle"]
    self.NrActions = 3
    
    self.previousGameState = None
    
    self.time = 0
    
    self.setupTables()
    
    self.lr = 0.01
    self.y = 0.01
    
    self.e = 1.0
    self.deltaE = -0.1
    
    #skipframes
    self.skipFrame = 1
    self.currentFrame = -1


  def setupTables(self):
    #lookup tables to pick an object given a gamestate
    self.objectTable = {}
    
    # the lookup table to pick a dimention given a gameState
    self.dimention_space_Table = {}
    self.dimention_time_Table = {}
    for dim in self.possibleDimentions:
      self.dimention_space_Table[dim] = {}
      self.dimention_time_Table[dim] = {}
    
    # a lookup table to pick an action given a space and time predicate
    self.actionTable = {}
    for dim1 in self.possibleDimentions:
      self.actionTable[dim1] = {}
      for dim2 in self.possibleDimentions:
	self.actionTable[dim1][dim2] = {}
	for spacePred in self.possiblePredicates:
	  self.actionTable[dim1][dim2][spacePred] = {}
	  for obj in self.possibleObjects:
	    self.actionTable[dim1][dim2][spacePred][obj] = {}
	    for timePred in self.possiblePredicates:
	      self.actionTable[dim1][dim2][spacePred][obj][timePred] = {}
	      for action in range(self.NrActions):
		self.actionTable[dim1][dim2][spacePred][obj][timePred][action] = self.getInitialNumber()

  def getInitialNumber(self):
    return np.random.random()

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
  def getSpacePredicate(self,gameStateDict,dimention):
    
    if("X" in gameStateDict["Paddle"].keys()):
      Largest,Smallest,same,iterations = entropy.ent_magnitudeMoreLessSame(gameStateDict["Paddle"][dimention],gameStateDict["Ball"][dimention])
      if(same):
	return "Same"
      elif(Largest == gameStateDict["Paddle"][dimention]):
	return "More"
      else:
	return "Less"
    elif("X1" in gameStateDict["Paddle"].keys()):
      #check the first cordinate on the dimension
      Largest,Smallest,same,iterations = entropy.ent_magnitudeMoreLessSame(gameStateDict["Paddle"][dimention + "1"],gameStateDict["Ball"][dimention + "1"])
      if(same):
	part1 = "Same"
      elif(Largest == gameStateDict["Paddle"][dimention + "1"]):
	part1 = "More"
      else:
	part1 = "Less"
	
      #check the first cordinate on the dimension
      Largest,Smallest,same,iterations = entropy.ent_magnitudeMoreLessSame(gameStateDict["Paddle"][dimention + "2"],gameStateDict["Ball"][dimention + "2"])
      if(same):
	part2 = "Same"
      elif(Largest == gameStateDict["Paddle"][dimention + "2"]):
	part2 = "More"
      else:
	part2 = "Less"
      return part1 + part2
    return "Error Something whent wrong"
    
  #get the predicate applicable to the current gamestate on the given dimention
  def getTimePredicate(self,gameStateDict,previousGameState,dimention,obj):
    
    if("X" in gameStateDict["Paddle"].keys()):
      dim = dimention
    elif("X1" in gameStateDict["Paddle"].keys()):
      dim = dimention + "1"
    
    Largest,Smallest,same,iterations = entropy.ent_magnitudeMoreLessSame(gameStateDict[obj][dim]+1,previousGameState[obj][dim]+1)
    pred = ""
    if(same):
      pred = "Same"
    elif(Largest == gameStateDict[obj][dim]):
      pred = "More"
    else:
      pred = "Less"
    
    if("X" in gameStateDict["Paddle"].keys()):
      return pred
    elif("X1" in gameStateDict["Paddle"].keys()):
      return pred+pred
    return "Error Something whent wrong"

  """
  make a numpy array into a dictionary key
  """
  def toKey(self,array):
    ar = (array/0.1).astype(np.int32)
    return str(ar).strip('[]').replace('\n','')
    
  def pickObject(self,gameStateKey):
    if( not gameStateKey in self.objectTable.keys()):
      self.objectTable[gameStateKey] = {}
      for obj in self.possibleObjects:
	self.objectTable[gameStateKey][obj] = self.getInitialNumber()
	
    objIdx = np.argmax([self.objectTable[gameStateKey][obj] for obj in self.possibleObjects])
    
    return self.possibleObjects[objIdx], objIdx
    
  def initDimentionTable(self,gameStateKey,dimentionTable):
    # if there is no information about the gameState make some
    if( not gameStateKey in dimentionTable.keys()):
      dimentionTable[gameStateKey] = {}
      for dim in self.possibleDimentions:
	dimentionTable[gameStateKey][dim] = self.getInitialNumber()

  #pick one of the possible dimentions given an gameState
  def pickDimention(self,gameStateKey,dimentionTable):
    #make sure that the keys exsist
    self.initDimentionTable(gameStateKey,dimentionTable)

    # search wich dimentions has the highest qvalue
    dimIndex = np.argmax([dimentionTable[gameStateKey][dim] for dim in self.possibleDimentions])
    
    return self.possibleDimentions[dimIndex], dimIndex

  #select an action given a predicate
  def selectAction(self,dimention,predicate):    
	  
    pass
    
    return 0

  def getAction(self, gameState):
    self.currentFrame += 1
    gameStateKey = self.toKey(gameState)
    gameStateDict = self.gameStateToDict(gameState)
    
    self.SpaceDim,spaceIdx = self.pickDimention(gameStateKey,self.dimention_space_Table)
    self.SpacePred = self.getSpacePredicate(gameStateDict,self.SpaceDim)
    
    self.timeDim, dimIdx = self.pickDimention(gameStateKey,self.dimention_time_Table)
    self.sampledObj, objIdx = self.pickObject(gameStateKey)
    
    if(self.previousGameState is None):
      self.previousGameState = gameStateDict
      
    self.timePred = self.getTimePredicate(gameStateDict,self.previousGameState,self.timeDim,self.sampledObj)
    
    values = [self.actionTable[self.SpaceDim][self.timeDim][self.SpacePred][self.sampledObj][self.timePred][action] for action in range(self.NrActions)]
    action = np.argmax(values)  
    
    self.previousGameState = gameStateDict
    return action  

  def update(self,oldState,action,newState,reward,terminal):
    
    gameStateKeyOld = self.toKey(oldState)
    gameStateDictOld = self.gameStateToDict(oldState)
    
    gameStateKeyNew = self.toKey(newState)
    gameStateDictNew = self.gameStateToDict(newState)
    
    """
    Update space dimention table
    """
    self.initDimentionTable(gameStateKeyOld,self.dimention_space_Table)
    currentValue = self.dimention_space_Table[gameStateKeyOld][self.SpaceDim]
    newSpaceDim,spaceIdx = self.pickDimention(gameStateKeyNew,self.dimention_space_Table)
    #make sure that the keys exsist
    self.initDimentionTable(gameStateKeyNew,self.dimention_space_Table)    
    expedReward = self.dimention_space_Table[gameStateKeyNew][newSpaceDim]
    self.dimention_space_Table[gameStateKeyOld][self.SpaceDim] = currentValue + self.lr*(reward + self.y * expedReward)
    
    """
    Update time dimention table
    """
    currentValue = self.dimention_time_Table[gameStateKeyOld][self.timeDim]
    newTimeDim,timeIdx = self.pickDimention(gameStateKeyNew,self.dimention_time_Table)
    #make sure that the keys exsist
    self.initDimentionTable(gameStateKeyNew,self.dimention_time_Table)    
    expedReward = self.dimention_time_Table[gameStateKeyNew][newTimeDim]
    self.dimention_time_Table[gameStateKeyOld][self.timeDim] = currentValue + self.lr*(reward + self.y * expedReward)
    
    """
    Update action table
    """
    newObj, objIdx = self.pickObject(gameStateKeyNew)
    newSpacePred = self.getSpacePredicate(gameStateDictNew,newSpaceDim)
    newTimePred = self.getTimePredicate(gameStateDictNew,gameStateDictOld,newTimeDim,newObj)
    
    currentValue = self.actionTable[self.SpaceDim][self.timeDim][self.SpacePred][self.sampledObj][self.timePred][action]
    expedReward = np.max(self.actionTable[newSpaceDim][newTimeDim][newSpacePred][newObj][newTimePred].values())
    self.actionTable[self.SpaceDim][self.timeDim][self.SpacePred][self.sampledObj][self.timePred][action] = currentValue + self.lr*(reward + self.y * expedReward)
    
  """
  flip the weights
  """
  def flipWeights(self,dim1,dim2):
    #flip space dimention table
    temp = self.dimention_space_Table[dim1]
    self.dimention_space_Table[dim1] = self.dimention_space_Table[dim2]
    self.dimention_space_Table[dim2] = temp
    
    #flip time dimention table
    temp = self.dimention_time_Table[dim1]
    self.dimention_time_Table[dim1] = self.dimention_time_Table[dim2]
    self.dimention_time_Table[dim2] = temp
    
    #flip the action table
    for dim in self.possibleDimentions:
      temp = self.actionTable[dim][dim1]
      self.actionTable[dim][dim1] = self.actionTable[dim][dim2]
      self.actionTable[dim][dim2] = temp
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
      dimention_space_Table = json.load(open("./" + folder + '/' + filename + '/' + filename + "dim_space.table",'r'))
      dimention_time_Table = json.load(open("./" + folder + '/' + filename + '/' + filename + "dim_time.table",'r'))
      
      agent.actionTable = actionTable
      agent.dimention_space_Table = dimention_space_Table
      agent.dimention_time_Table = dimention_time_Table
      
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
    
    json.dump(self.dimention_space_Table,open("./" + folder + '/' + filename + '/' + filename + "dim_space.table",'w'))
    json.dump(self.dimention_time_Table,open("./" + folder + '/' + filename + '/' + filename + "dim_time.table",'w'))
    json.dump(self.actionTable,open("./" + folder + '/' + filename + '/' + filename + "act.table",'w'))
    # "./" + folder + '/' + filename + '/' + filename)
    

if(__name__ == "__main__"):
  from Eviroment import Enviroment
  env = Enviroment(gameMode="vector",rewardMode="follow",autoFire=True)
  agent = DoraTimeAgent()
  
  for i in range(10):
    S = env.reset()
    done = False
    while not done:
      action = agent.getAction(S)
      S1,r,done,info = env.step(action)
      
      agent.update(S,action,S1,r,done)
      env.render()
    print env.reward
      
  
