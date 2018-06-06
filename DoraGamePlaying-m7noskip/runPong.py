# run Pong sim. 

import experiment
from Eviroment import Enviroment
from DoraModelTime import DoraAgent as Agent
import numpy as np
import matplotlib as mat
mat.use("AGG")
from matplotlib import pyplot as plt
import pdb

# create the agent and load the saved data.
agent = Agent(double=False)
#actionTable = json.load(open("./" + folder + '/' + filename + '/' + filename + "act.table",'r'))
#dimensionTable = json.load(open("./" + folder + '/' + filename + '/' + filename + "dim.table",'r'))
#agent.actionTable = actionTable
#agent.dimensionTable = dimensionTable
agent = agent.load('Breakout_1_800')
agent.flipWeights("X","Y")

# 
enviroment = Enviroment(Breakout=False,gameMode="vector",rewardMode="follow",autoFire=True)
NrGames = 200
writeOn = 10
savePath = 'Pong1'
experiment.testAgent(enviroment, agent,NrGames,writeOn,savePath, show=True)





