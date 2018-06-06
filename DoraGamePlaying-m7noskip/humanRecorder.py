import sys
import os
from pymouse import PyMouseEvent
from threading import Thread

from Eviroment import Enviroment

class DetectMouseClick(PyMouseEvent):
    def __init__(self):
        PyMouseEvent.__init__(self)
        self.buttons = {0:False,1:False,2:False}

    def click(self, x, y, button, press):
      self.buttons[button] = press
    
    def start(self):
	self.thread = Thread(target = self.run)
        self.thread.start()
        
    def stop(self):
      self.thread.stop()

class human:
  
  def __init__(self):
    self.screen = (0,1919)
    self.env = None
    self.mouse = DetectMouseClick()
    self.mouse.start()
    self.playerReady = False
  
  def getAction(self,gameState):
    self.env.render()
    
    while(not self.playerReady):
      self.playerReady = sum(self.mouse.buttons.values()) > 0
      
    
    if(self.mouse.buttons[1]):
      return 2
    elif(self.mouse.buttons[2]):
      return 1
    else:
      return 0
    
  def update(self,oldState,action,newState,reward,terminal):
    self.playerReady = not terminal
  
  def save(self,filename):
    folder = os.path.dirname(filename)
    filename = filename.replace(folder + '/','')
    if(not os.path.isdir("./" + folder)):
      os.mkdir(folder)
  
  @staticmethod
  def load(filename):
    return human()
  
