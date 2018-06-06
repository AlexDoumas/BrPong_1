import numpy as np
from sklearn.neural_network import MLPClassifier
import sklearn

"""
agent that returns a random action indepandant of the game gameState
this agent is unable to learn but has a update function for interface reasons
"""
class debugAgent:
  def __init__(self):
    self.gameStates = None
    self.labels = None
    
    self.classifier = MLPClassifier(max_iter=20000,verbose=False)
  
  """
  generate a random action 
  """
  def getAction(self,gameState):
    try:
      y = self.classifier.predict(np.expand_dims(gameState,axis=0))
      return np.argmax(y,axis=1)[0]
    except sklearn.exceptions.NotFittedError as e:
      return np.random.randint(0,3)
  
  """
  do nothing
  """
  def update(self,old_state,action,new_state,reward,terminal, batch):
    if(self.gameStates is None):
      self.gameStates = np.expand_dims(new_state,axis=0)
      self.labels = reward
    else:
      self.gameStates = np.concatenate((self.gameStates,np.expand_dims(new_state,axis=0)),axis=0)
      self.labels = np.concatenate((self.labels,reward),axis=0)
      
    if(terminal):
      
      self.classifier.fit(self.gameStates,self.labels)
      if(batch%5==0):
	self.gameStates = None
	self.labels = None
	print("I threw my data away")
      

  """
  nothing to load so do nothing
  """
  @staticmethod
  def load(filename):
    return debugAgent()
  
  """
  nothing to save so do nothing
  """
  def save(self,filename):
    print self.gameStates
    np.savetxt(filename +"/X.csv",np.asarray(self.gameStates),delimiter=",")
    np.savetxt(filename +"/Y.csv",self.labels,delimiter=",")
    
  
if(__name__ == "__main__"):
  from Eviroment import Enviroment
  import time
  
  env = Enviroment(Breakout=True,gameMode="vector",rewardMode="label",autoFire=True)
  
  agent = debugAgent()
  batch=0
  done = False
  for game in range(100):
    S = env.reset()
    done = False
  
    while not done:
      action = agent.getAction(S)
      S1,r,done,info = env.step(action)
      agent.update(S,action,S1,r,done, batch)
      S = S1
      
    batch+=1
      
      #env.render()
    print (env.reward/float(env.steps))
    #agent.save("debugAgent")