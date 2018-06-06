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
    # if the cordinates are double
    if(len(gameState) == 12):
      paddle = {"X1":gameState[0],"Y1":gameState[1],"X2":gameState[2],"Y2":gameState[3],"XVel":gameState[4],"YVel":gameState[5]}
      ball = {"X1":gameState[6],"Y1":gameState[7],"X2":gameState[8],"Y2":gameState[9],"XVel":gameState[10],"YVel":gameState[11]}
      
      # when the ball is above the paddle
      if(paddle["Y1"] < ball["Y1"] and paddle["Y2"] > ball["Y2"]):
	# do nothing
	action = 0
      elif(paddle["Y1"] > ball["Y1"]):
	# move left
	action = 2
      elif(paddle["Y2"] < ball["Y2"]):
	# move right
	action = 1

    # if the cordinates are single
    elif(len(gameState) == 8):
      paddle = {"X":gameState[0],"Y":gameState[1],"XVel":gameState[2],"YVel":gameState[3]}
      ball = {"X":gameState[4],"Y":gameState[5],"XVel":gameState[6],"YVel":gameState[7]}
      
      Ycollision = ball["Y"]#self.getCollisionPointBreakout(ball)
      
      #Do nothing is ball Y coordinate is 0 meaning there is no ball
      if(Ycollision == 0):
	action = 0
      #If the (middle of the) Y coordinate of the paddle is larger than the Y coordinate of the ball, go right
      elif(paddle["Y"] - 0.05 > Ycollision):
	action = 2
      #If the (middle of the) Y coordinate of the paddle is smaller than the Y coordinate of the ball, go left
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
    
    # if the cordinates are double
    if(len(gameState) == 12):
      paddle = {"X1":gameState[0],"Y1":gameState[1],"X2":gameState[2],"Y2":gameState[3],"XVel":gameState[4],"YVel":gameState[5]}
      ball = {"X1":gameState[6],"Y1":gameState[7],"X2":gameState[8],"Y2":gameState[9],"XVel":gameState[10],"YVel":gameState[11]}
      
      # when the ball is above the paddle
      if(paddle["X1"] < ball["X1"] and paddle["X2"] > ball["X2"]):
	# do nothing
	action = 0
      elif(paddle["X1"] > ball["X1"]):
	# move left
	action = 2
      elif(paddle["X2"] < ball["X2"]):
	# move right
	action = 1
    
    # if the cordinates are single
    elif(len(gameState) == 8):
      paddle = {"X":gameState[0],"Y":gameState[1],"XVel":gameState[2],"YVel":gameState[3]}
      ball = {"X":gameState[4],"Y":gameState[5],"XVel":gameState[6],"YVel":gameState[7]}
      
      Xcollision = ball["X"]#self.getCollisionPointPong(ball)
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
  import time
  
  env = Enviroment(Breakout=True,gameMode="vector2",rewardMode="follow",autoFire=True)
  
  agent = designedAgent()
  
  done = False
  S = env.reset()
  while not done:
    action = agent.getAction(S)
    S,r,done,info = env.step(action)
    
    env.render()
    
  env.makeVideo('designedAgent.gif')