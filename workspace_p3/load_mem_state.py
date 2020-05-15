# load a simulation state. 

# imports. 
import random, json
import dataTypes
import buildNetwork
import basicRunDORA
import pdb

parameters = {'asDORA': True, 'gamma': 0.3, 'delta': 0.1, 'eta': 0.9, 'HebbBias': 0.5,'bias_retrieval_analogs': True, 'use_relative_act': True, 'run_order': ['cdr', 'selectTokens', 'r', 'wp', 'm', 'p', 'f', 's', 'c'], 'run_cyles': 5000, 'write_on_iteration': 100, 'firingOrderRule': 'random', 'strategic_mapping': False, 'ignore_object_semantics': False, 'ignore_memory_semantics': True, 'mag_decimal_precision': 0, 'dim_list': ['height', 'width', 'depth', 'size'], 'exemplar_memory': False, 'recent_analog_bias': True, 'lateral_input_level': 1, 'screen_width': 1200, 'screen_height': 700, 'doGUI': False, 'GUI_update_rate': 50, 'starting_iteration': 0}

# function to load a sym file.
def load_sym(file_name):
    f = open(file_name, 'r')
    simType = ''
    di = {'simType': simType} # porting from Python2 to Python3
    f.seek(0)
    exec (f.readline(), di) # porting from Python2 to Python3
    # check if sym file or json dump. 
    if di['simType'] == 'sym_file':
        symstring = ''
        for line in f:
            symstring += line
        symProps = [] # porting from Python2 to Python3
        di = {'symProps': symProps} # porting from Python2 to Python3
        exec (symstring, di) # porting from Python2 to Python3
        symProps = di['symProps']
    elif di['simType'] == 'json_sym':
         symProps = json.loads(f.readline())
    return symProps

# memorty state to load. 
memory_state = 'batch_run1000'

# initialise memory. 
memory = buildNetwork.initializeMemorySet()
# load a sym file.
symProps = load_sym(memory_state)
# interpret the sym file. 
mysym = buildNetwork.interpretSymfile(symProps)
# build the network object with memory. 
memory = basicRunDORA.dataTypes.memorySet()
memory = buildNetwork.buildTheNetwork(mysym[0], memory)
network = basicRunDORA.runDORA(memory, parameters)

pdb.set_trace()




