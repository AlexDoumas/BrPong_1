import numpy as np
import tensorflow as tf

import os

class LargeAgent:
  
  """
  make sure the neural network is build
  """
  def __init__(self, trajectory=False):
    self.actionsTaken = 0
        
    self.skipFrame = 1 # repeat the action for this number of frames
    self.currentFrame = -1 # a counter to see at which frame we are now
    
    # variable to save a batch of transitions for later training
    self.states = None 	#the game state of the transition
    self.actionLabels = None #the reward gotten for that action
    
    # the number of transition needed to be collected before updating the network
    self.updateSize = 128
    
    #build the tensor graph
    self.buildNetwork()
  
  #make the tensorgraph
  def buildNetwork(self):
    #make the sesion
    self.sess = tf.Session()
    
    #an initializer object so that the weights don't start at zero
    initializer = tf.contrib.layers.xavier_initializer()
    
    #define the nerual netwotk
    
    #game state input
    self.gameState = tf.placeholder(tf.float32,shape=[None,84,84,4],name="gameState")
    
    #the first three convolutional layers
    C1 = tf.layers.conv2d(self.gameState,32,8,strides=4,activity_regularizer=tf.nn.relu,kernel_initializer=initializer,bias_initializer=initializer,name="C1")
    C2 = tf.layers.conv2d(C1,64,4,strides=2,activity_regularizer=tf.nn.relu,kernel_initializer=initializer,bias_initializer=initializer,name="C2")
    C3 = tf.layers.conv2d(C2,64,3,strides=1,activity_regularizer=tf.nn.relu,kernel_initializer=initializer,bias_initializer=initializer,name="C3")
    #flaten the covolutional output
    F1 = tf.contrib.layers.flatten(C3)
    #A fully connected layer
    D1 = tf.layers.dense(F1,512,activity_regularizer=tf.nn.relu,kernel_initializer=initializer,bias_initializer=initializer,name="D1")
    #and the output layer
    self.output = tf.layers.dense(D1,3,kernel_initializer=initializer,bias_initializer=initializer,name="output")
    
    #define tensors for the loss and update functions
    #a placeholder for what the Q-values should be
    self.disiredOutput = tf.placeholder(shape=[None,3],dtype=tf.float32,name="label")
    # the loss function (Y - modelOutput)^2
    self.loss = tf.reduce_sum(tf.square(self.disiredOutput - self.output),name="loss")
    # the optimizer tensors to minimize the loss function
    trainer = tf.train.GradientDescentOptimizer(learning_rate=0.001)
    updateModel = trainer.minimize(self.loss)
    
    #make a dummy constance that needs the update tensor otherwise we can;t use partial run
    with tf.control_dependencies([updateModel]):
      self.dummy = tf.constant(0)
    
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
      neuralInput = np.expand_dims(newState,axis=0)
      self.states = neuralInput
      self.actionLabel = reward
    else:
      #add the current transition to the memory
      neuralInput = np.expand_dims(newState,axis=0)
      self.states = np.concatenate((self.states,neuralInput),axis=0)
      self.actionLabel = np.concatenate((self.actionLabel,reward),axis=0)
    
    # when enough transistion have been stored
    if(self.states.shape[0] == self.updateSize):
      #see what the agent expected as reward
      
      #update the weights of the model by calling the optimizer tensor
      loss,_ = self.sess.run([self.loss,self.dummy],feed_dict={self.gameState:self.states,self.disiredOutput:self.actionLabel})
      
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
      agent = LargeAgent()
      
      #load the weights from disk
      saver = tf.train.import_meta_graph(folder + '/' + filename + '/' + filename + '.meta')
      saver.restore(agent.sess,tf.train.latest_checkpoint('./' + folder + '/' + filename))
      
      #attach the loaded weights to the agent object
      graph = agent.sess.graph
      
      agent.output = graph.get_tensor_by_name("output:0")
      agent.gameState = graph.get_tensor_by_name("gameState:0")
      agent.disiredOutput = graph.get_tensor_by_name("label:0")
      agent.loss = graph.get_tensor_by_name("loss:0")
    else:
      return LargeAgent()
  
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