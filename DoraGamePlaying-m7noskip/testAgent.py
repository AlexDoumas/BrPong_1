from Eviroment import Enviroment
import numpy as np

if(__name__ == "__main__"):
  from SmallAgent import SmallAgent as Agent
  show = False
  
  #make the enviroment
  env = Enviroment(fullImage=False,enhancedReward=True,autoFire=True)
  if(show):
    env.reset()
    env.render()
  
  agent = Agent.load('')
  
  write = 0
  
  rweards = []
  for i in range(500):
    S = env.reset()
    done = False
    while not done:
      action = agent.getAction(S)
      Snew,reward,done,info = env.step(action)
      agent.update(S,action,Snew,reward,done)
      S = Snew
      if(show):
	env.render()
    if(write == 0):
      write = 1
      env.makeVideo('./randomMovement.gif')
    if(i == 250 and write == 1):
      write = 2
      env.makeVideo('./halfRandomMovement.gif')
    rweards.append(env.reward)
    print "End Game",env.reward
  
  env.makeVideo('./minimalRandomMovement.gif')
  
  first = np.mean(rweards)
  second = np.std(rweards)
  
  rweards = []
  for _ in range(30):
    S = env.reset()
    done = False
    while not done:
      action = agent.getAction(S)
      Snew,reward,done,info = env.step(action)
      agent.update(S,action,Snew,reward,done)
      S = Snew
      if(show):
	env.render()
    rweards.append(env.reward)
    print "End Game",env.reward
  
  first2 = np.mean(rweards)
  second2 = np.std(rweards)
  
  print first,second
  print first2,second2
  
  agent.e = 0.0
  S = env.reset()
  done = False
  while not done:
    action = agent.getAction(S)
    Snew,reward,done,info = env.step(action)
    agent.update(S,action,Snew,reward,done)
    S = Snew
    if(show):
      env.render()
      
  env.makeVideo('./endMovement.gif')