import numpy as np

"""
agent that returns a random action indepandant of the game gameState
this agent is unable to learn but has a update function for interface reasons
"""
class randomAgent:
  """
  generate a random action 
  """
  def getAction(self,gameState):
    return np.random.randint(0,100)
  
  """
  do nothing
  """
  def update(self,old_state,action,new_state,reward):
    pass

  """
  nothing to load so do nothing
  """
  @staticmethod
  def load(filename):
    return randomAgent()
  
  """
  nothing to save so do nothing
  """
  def save(self,filename):
    pass
  
class designedAgent:
  
  def getBallAfterGettingPoint(self,Ball):
    if(Ball["XVel"] > 0):
      return Ball
    
    #in how many steps does the ball reach the bottom
    collitionTime = (0.3 - Ball["X"])/Ball["XVel"]
    #when it reaches the bottom what is its Y cordinate
    Ybounce = Ball["YVel"]*collitionTime + Ball["Y"]
    YVel = Ball["YVel"]
    
    #if the Y cordinate is negative it means that the ball bounced on the left side
    #asuming the outcomming corner is the same as the incoming corner 
    if(Ybounce <= 0):
      Ybounce = -1*Ybounce
      YVel = YVel*-1
    elif(Ybounce >= 1.0):
      #if the ycordinate is larger than 1.0 it bounced on the right side
      Ybounce = 1.0 - (Ybounce - 1.0)
      YVel = YVel*-1
    
    ball = {"X":0.3,"Y":Ybounce,"XVel":-1*Ball["XVel"],"YVel":YVel}
    return ball
  
  #calculare where the ball would meet the paddle
  def getCollisionPointBreakout(self,Ball):
    if(Ball["XVel"] > 0):
      #in how many steps does the ball reach the bottom
      collitionTime = (0.79047619 - Ball["X"])/Ball["XVel"]
      #when it reaches the bottom what is its Y cordinate
      Ycollision = Ball["YVel"]*collitionTime + Ball["Y"]
      
      #if the Y cordinate is negative it means that the ball bounced on the left side
      #asuming the outcomming corner is the same as the incoming corner 
      if(Ycollision <= 0):
	Ycollision = -1*Ycollision
      elif(Ycollision >= 1.0):
	#if the ycordinate is larger than 1.0 it bounced on the right side
	Ycollision = 1.0 - (Ycollision - 1.0)
      
      return Ycollision
      
    return 0
  
  def getActionBreakout(self, gameState):
    action = 0
    
    paddle = {"X":gameState[0],"Y":gameState[1],"XVel":gameState[2],"YVel":gameState[3]}
    ball = {"X":gameState[4],"Y":gameState[5],"XVel":gameState[6],"YVel":gameState[7]}
    
    #Ball = self.getBallAfterGettingPoint(ball)
    Ycollision = self.getCollisionPointBreakout(ball)
    #print Ycollision
    
    if(Ycollision == 0):
      action = 0
    elif(paddle["Y"] - 0.05 > Ycollision):
      action = 2
    elif(paddle["Y"] + 0.05 < Ycollision):
      action = 1

    return action
  
  #calculare where the ball would meet the paddle
  def getCollisionPointPong(self,Ball):
    if(Ball["YVel"] > 0):
      #in how many steps does the ball reach the bottom
      collitionTime = (0.8875 - Ball["Y"])/Ball["YVel"]
      #when it reaches the bottom what is its Y cordinate
      Xcollision = Ball["XVel"]*collitionTime + Ball["X"]
      
      #if the Y cordinate is negative it means that the ball bounced on the left side
      #asuming the outcomming corner is the same as the incoming corner 
      if(Xcollision <= 0):
	Xcollision = -1*Xcollision
      elif(Xcollision >= 0.9):
	#if the ycordinate is larger than 1.0 it bounced on the right side
	Xcollision = 0.9 - (Xcollision - 0.9)
      
      return Xcollision
      
    return 0
  
  def getActionPong(self, gameState):
    action = 0
    
    paddle = {"X":gameState[0],"Y":gameState[1],"XVel":gameState[2],"YVel":gameState[3]}
    ball = {"X":gameState[4],"Y":gameState[5],"XVel":gameState[6],"YVel":gameState[7]}
    
    #Ball = self.getBallAfterGettingPoint(ball)
    Xcollision = self.getCollisionPointPong(ball)
    print ball["X"]
    
    if(Xcollision == 0):
      action = 0
    elif(paddle["X"] - 0.034 > Xcollision ):
      action = 2
    elif(paddle["X"] + 0.035 < Xcollision ):
      action = 1

    return action
  
  def getAction(self,gameState):
    return self.getActionBreakout(gameState)
  
  """
  do nothing
  """
  def update(self,old_state,action,new_state,reward):
    pass

  """
  nothing to load so do nothing
  """
  @staticmethod
  def load(filename):
    return randomAgent()
  
  """
  nothing to save so do nothing
  """
  def save(self,filename):
    pass
  
if(__name__ == "__main__"):
  from Eviroment import Enviroment
  
  env = Enviroment(Breakout=True,enhancedReward=True,fullImage=False,autoFire=True)
  
  agent = designedAgent()
  
  done = False
  S = env.reset()
  while not done:
    action = agent.getAction(S)
    S,r,done,info = env.step(action)
    
    env.render()
    
  env.makeVideo('designedAgent.gif')