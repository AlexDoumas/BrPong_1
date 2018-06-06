import numpy as np
from matplotlib import pyplot as plt

def loadFile(filename):
  f = open(filename,'r')
  text = f.read()
  f.close()
  
  rewards = []
  steps = []
  for line in text.split('\n'):
    pieces = line.split(',')
    if(len(pieces) == 2):
      rewards.append(float(pieces[0]))
      steps.append(int(pieces[1]))
  return rewards,steps

def loadFiles(files):
  rewards = []
  steps = []
  for f in files:
    r,s = loadFile(f)
    rewards.extend(r)
    steps.extend(s)
    
  return rewards,steps,

def plotResults(rewards,steps,outputFile):
  plt.subplot(2,1,1)
  plt.plot(rewards)
  plt.xlabel('number of games played')
  plt.ylabel('reward received per game')
  
  plt.subplot(2,1,2)
  plt.plot(steps)
  plt.xlabel('number of games played')
  plt.ylabel('number of actions taken per game')
  
  plt.savefig(outputFile)

def Average(rewards,n):
  return [np.mean(rewards[i:i+n]) for i in range(len(rewards)-n)]

if(__name__ == "__main__"):
  LargeAgent = ['LargeAgent/2018-01-15 11:50:29.380284']
  SmallAgent = ['SmallAgent/2018-01-15 13:12:18.774147']
  rewards,steps = loadFiles(['./SmallAgent/29-01-2018'])
  rewards = Average(rewards,10)
  steps = Average(steps,10)
  plotResults(rewards,steps,"./test.png")