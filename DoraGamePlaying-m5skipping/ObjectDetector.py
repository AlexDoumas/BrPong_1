import numpy as np
from scipy.ndimage.measurements import find_objects
from scipy.ndimage import label

# get the area in pixels for a given slice obj
def getArea(obj):
  return (obj[0].stop - obj[0].start) * (obj[1].stop - obj[1].start)

def getDimentions(obj):
  return ((obj[0].stop - obj[0].start) , (obj[1].stop - obj[1].start))

#get the centre cordinates for a given slice obj
def getCenter(obj):
  return [(s.start + s.stop)/2.0 for s in obj]

#cordinates of the last seen ball and bar
lastBall = np.asarray([0.0,0.0])
lastBar = np.asarray([0.0,0.0])

def detectObjectBreakout(state,double=False):
  global lastBall
  global lastBar
  
  #cut of some of the unimportant stuff (like the score and the borders) and remove the background color
  im = (np.sum(state[25:,:,:],2) == 344)[40:,:150]
  
  #find color blobs in this image (should only have two)
  labeled_array, num_features = label(im)  
  slices = find_objects(labeled_array)
  
  if(not double):
    ball = np.asarray([0.0,0.0])
    bar = np.asarray([0.0,0.0])
  else:
    ball = np.asarray([0.0,0.0,0.0,0.0])
    bar = np.asarray([0.0,0.0,0.0,0.0])
  
  #for every blob that is found
  for obj in slices:
    area = getArea(obj)
    center = getCenter(obj)
    #if the area of the blob is larger than 10 pixels the blob is the bar
    if(area > 10):
      if(not double):
	bar = np.asarray([(center[0] + 40)/float(state.shape[0]),(center[1])/float(state.shape[1])])
      else:
	#vector x1,y1,x2,y2
	bar = np.asarray([(obj[0].start + 40)/float(state.shape[0]),(obj[1].start)/float(state.shape[1]),(obj[0].stop + 40)/float(state.shape[0]),(obj[1].stop)/float(state.shape[1])])
    #if the area of the blob is less than 10 pixels the blob is the ball
    elif(area < 10):
      if(not double):
	ball = np.asarray([(center[0] + 40)/float(state.shape[0]),(center[1])/float(state.shape[1])])
      else:
	ball = np.asarray([(obj[0].start + 40)/float(state.shape[0]),(obj[1].start)/float(state.shape[1]),(obj[0].stop + 40)/float(state.shape[0]),(obj[1].stop)/float(state.shape[1])])
  
  #if a ball was found calulate the velocity of the ball 
  if(np.all(ball > 0)):
    ballVelocity = ball[0:2] - lastBall[0:2]
    lastBall = ball
  else:
    ballVelocity = np.asarray([0.0,0.0])
  
  #if a bar was found calulate the bar velocity
  if(np.all(bar > 0)):
    barVelocity = bar[0:2] - lastBar[0:2]
    lastBar = bar
  else:
    barVelocity = np.asarray([0.0,0.0])
    
  return bar,barVelocity,ball,ballVelocity


def detectObjectPong(state,double=False): 
  global lastBall
  global lastBar
  
  #cut of some of the unimportant stuff (like the score and the borders) and remove the background color
  im = (np.sum(state,2,dtype=np.float) - 233)[35:194,:]
  
  #find color blobs in this image (should only have two)
  labeled_array, num_features = label(im)
  slices = find_objects(labeled_array)
  
  ball = np.asarray([0.0,0.0,0.0,0.0])
  bar = []
  
  #for every blob that is found
  for obj in slices:
    area = getArea(obj)
    center = getCenter(obj)
    #if the area of the blob is larger than 10 pixels the blob is the bar
    if(area > 10):
      if(not double):
	bar.append(np.asarray([(center[0] + 35)/float(state.shape[0]),center[1]/float(state.shape[1])]))
      else:
	bar.append(np.asarray([(obj[0].start + 35)/float(state.shape[0]),(obj[1].start)/float(state.shape[1]),(obj[0].stop + 35)/float(state.shape[0]),(obj[1].stop)/float(state.shape[1])]))
    #if the area of the blob is less than 10 pixels the blob is the ball
    elif(area < 10):
      if(not double):
	ball = np.asarray([(center[0] + 35)/float(state.shape[0]),center[1]/float(state.shape[1])])
      else:
	ball = np.asarray([(obj[0].start + 35)/float(state.shape[0]),(obj[1].start)/float(state.shape[1]),(obj[0].stop + 35)/float(state.shape[0]),(obj[1].stop)/float(state.shape[1])])
  
  if(len(bar) == 1):
    bar = bar[0]
  elif(len(bar) == 0):
    bar = np.asarray([0.0]*2*double)
  elif(bar[0][1] > bar[1][1]):
    bar = bar[0]
  else:
    bar = bar[1]
  
  #if a ball was found calulate the velocity of the ball 
  if(np.all(ball > 0)):
    ballVelocity = ball[0:2] - lastBall[0:2]
    lastBall = ball
  else:
    ballVelocity = np.asarray([0.0,0.0])
  
  #if a bar was found calulate the bar velocity
  if(np.all(bar > 0)):
    barVelocity = bar[0:2] - lastBar[0:2]
    lastBar = bar
  else:
    barVelocity = np.asarray([0.0,0.0])
  
  return bar,barVelocity,ball,ballVelocity


if(__name__ == "__main__"):
  import sys 
  sys.path.append('/home/dylopd/Documents/OpenAIGym/env/lib/python2.7/site-packages/')
  from matplotlib import pyplot as plt
  
  import gym
  import time
  
  env = gym.make('Breakout-v0')
  s = env.reset()
  s, r, done_n, info = env.step(1)
  
  done_n = False
  while not done_n:
    bar,barVelocity,ball,ballVelocity = detectObjectBreakout(s,double=False)
    if(ball[0] < bar[0]):
      s, r, done_n, info = env.step(2)
    elif(ball[0] > bar[0]):
      s, r, done_n, info = env.step(3)
    else:
      s, r, done_n, info = env.step(0)
    s, r, done_n, info = env.step(1)
      
    print ball
    env.render()
    #time.sleep(0.4)