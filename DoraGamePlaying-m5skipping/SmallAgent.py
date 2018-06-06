import numpy as np
import tensorflow as tf

import os

class SmallAgent:
  
  """
  make sure the neural network is build
  """
  def __init__(self,inputSize=8):
    self.actionsTaken = 0
    
    self.skipFrame = 1 # repeat the action for this number of frames
    self.currentFrame = -1 # a counter to see at which frame we are now
    
    # variable to save a batch of transitions for later training
    self.states = None 	#the game state of the transition
    self.actionLabel = None #the Label of what action should have been taken in the given states
    
    # the number of transition needed to be collected before updating the network
    self.updateSize = 64
    
    #build the tensor graph
    self.buildNetwork(inputSize)
  
  def buildNetwork(self,inputSize):
    #make the sesion
    self.sess = tf.Session()
    
    #an initializer object so that the weights don't start at zero
    initializer = tf.contrib.layers.xavier_initializer()
    
    #define the nerual netwotk
    
    #game state input
    self.gameState = tf.placeholder(tf.float32,shape=[None,inputSize],name="gameState")
    #A fully connected layer
    D1 = tf.layers.dense(self.gameState,512,activity_regularizer=tf.nn.relu,kernel_initializer=initializer,bias_initializer=initializer,name="D1")
    #and the output layer
    self.output = tf.layers.dense(D1,3,kernel_initializer=initializer,bias_initializer=initializer,name="output")
    
    #define tensors for the loss and update functions
    #a placeholder for what the Q-values should be
    self.disiredOutput = tf.placeholder(shape=[None,3],dtype=tf.float32,name="label")
    # the loss function (Y - modelOutput)^2
    self.loss = tf.reduce_sum(tf.square(self.disiredOutput - self.output),name="loss")
    # the optimizer tensors to minimize the loss function
    trainer = tf.train.AdamOptimizer(learning_rate=0.001)
    self.updateModel = trainer.minimize(self.loss)    
    
    #a saver object needed to save the tensorgraph
    self.saver = tf.train.Saver()
    
    #initialise all the tensors
    init = tf.global_variables_initializer()
    self.sess.run(init)
  
  """
  get a aproperiate action given the gameState
  """
  def getAction(self, gameState):
    self.currentFrame += 1
    
    #once every skipframes calculate a new actions otherwise return the last one
    if(self.currentFrame%self.skipFrame == 0):
      #add the batch dimention to the gamestate so the neural network will except it
      neuralInput = np.expand_dims(gameState,axis=0)

      #calculate the expected future rewards
      expectedReward = self.sess.run(self.output, feed_dict={self.gameState:neuralInput})

      #return the action with the highest expected reward
      self.lastAction = np.argmax(expectedReward[0])
      
    # return the last computed action
    return self.lastAction 
  
  """
  given the past experiense undate the neural network to generate more usefull actions
  in this case this is done with Q-learning
  """
  def update(self,oldState,action,newState,reward,terminal):
    loss = 0
    #if there are no tranistion stored
    if(self.states is None):
      #store the current transition
      self.states = np.expand_dims(oldState,axis=0)
      self.actionLabel = reward
    else:
      #add the current transition to the memory
      self.states = np.concatenate((self.states,np.expand_dims(oldState,axis=0)),axis=0)
      self.actionLabel = np.concatenate((self.actionLabel,reward),axis=0)
    
    # when enough transistion have been stored
    if(self.states.shape[0] == self.updateSize):
      #see what the agent expected as reward
      
      #update the weights of the model by calling the optimizer tensor
      loss,_ = self.sess.run([self.loss,self.updateModel],feed_dict={self.gameState:self.states,self.disiredOutput:self.actionLabel})
      
      #remove the stored batch
      self.states = None
      self.actionLabel = None
    return loss
  
  """
  load a previous saved network into this one
  """
  @staticmethod
  def load(filename):
    folder = os.path.dirname(filename)
    filename = filename.replace(folder + '/','')
    if(os.path.isfile(folder + '/' + filename + '/' + filename + '.meta')):
      #create an agent object
      agent = SmallAgent()
      
      #load the weights from disk
      saver = tf.train.import_meta_graph(folder + '/' + filename + '/' + filename + '.meta')
      saver.restore(agent.sess,tf.train.latest_checkpoint('./' + folder + '/' + filename))
      
      #attach the loaded weights to the agent object
      graph = agent.sess.graph
      
      print [n.name for n in graph.as_graph_def().node]
      
      agent.output = graph.get_tensor_by_name("output:0")
      agent.gameState = graph.get_tensor_by_name("gameState:0")
      agent.disiredOutput = graph.get_tensor_by_name("label:0")
      agent.loss = graph.get_tensor_by_name("loss:0")
    else:
      return SmallAgent()
  
  """
  save the tensor graph in its own folder
  """
  def save(self,filename):
    folder = os.path.dirname(filename)
    filename = filename.replace(folder + '/','')
    if(not os.path.isdir("./" + folder)):
      os.mkdir(folder);
    if(not os.path.isdir("./" + folder + '/' + filename)):
      os.mkdir("./" + folder + '/' + filename);
      
    self.saver.save(self.sess, "./" + folder + '/' + filename + '/' + filename)