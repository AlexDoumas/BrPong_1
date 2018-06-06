import numpy as np
from matplotlib import pyplot as plt
import sys

def loadFile(filename):
  return np.genfromtxt(filename, delimiter=',')

def loadFiles(files):
  result = None
  for f in files:
    data = loadFile(f)
    if(result is None):
      result = data
    else:
      result = np.concatenate((result,data),axis=0)
    
  return result

def plotResults(data,names,outputFile):
  
  plt.figure()
  for i, title in enumerate(names):
    ax = plt.subplot(3,1,i+1)
    plt.plot(data[i])
    #ax.ylabel('reward gained')
    #ax.xlabel('games played')
    ax.set_title(title)
  plt.savefig(outputFile)

def compairHumanData(X,data,humanAverage,outputFile,Title):
  plt.figure()
  plt.plot(X,data)
  plt.plot(X,humanAverage, "r--")
  plt.title(Title)
  plt.xlabel("Number of games played")
  plt.ylabel("Average Points scored")
  plt.legend(["network performance","human average score"])
  plt.savefig(outputFile)

def Average(rewards,n):
  return [np.mean(rewards[i:i+n]) for i in range(len(rewards)-n)]

if(__name__ == "__main__"):
  dataFolder = sys.argv[1]
  outputFile = sys.argv[-1]
  
  data = loadFiles([dataFolder + "/" + "Breakout_1"])
  data = Average(data[:,1],20)
  X = range(len(data))
  
  humanAverage = loadFiles(["Dylan/Dylan_scores","Zina_Breakout/Zina_scores"])[:,1]
  humanAverage = np.mean(humanAverage)
  humanAverage = [humanAverage]*len(X)
  
  print len(X),len(data)
  
  compairHumanData(X,data,humanAverage,outputFile,"Centroid neural network")