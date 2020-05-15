# resimulation of Smith. 

# imports. 
import random, json
import dataTypes
import buildNetwork
import basicRunDORA
import pdb

parameters = {'asDORA': True, 'gamma': 0.3, 'delta': 0.1, 'eta': 0.9, 'HebbBias': 0.5,'bias_retrieval_analogs': True, 'use_relative_act': True, 'run_order': ['cdr', 'selectTokens', 'r', 'wp', 'm', 'p', 'f', 's', 'c'], 'run_cyles': 5000, 'write_on_iteration': 100, 'firingOrderRule': 'random', 'strategic_mapping': False, 'ignore_object_semantics': False, 'ignore_memory_semantics': True, 'mag_decimal_precision': 0, 'dim_list': ['height', 'width', 'depth', 'size'], 'exemplar_memory': False, 'recent_analog_bias': True, 'lateral_input_level': 1, 'screen_width': 1200, 'screen_height': 700, 'doGUI': False, 'GUI_update_rate': 50, 'starting_iteration': 0}

###############################################################################
# FUNCTIONS.
###############################################################################

# function to make an analog with some objects. 
# this function takes as input a list of object semantics for each object to make. It returns the updated memory and the new analog with the new objects. 
def add_objects(memory, trial_type): 
    # make a sym file version of the analog that includes all the objects for both experimenters and child. 
    # select the dimensional values for the objects based on trial_type. 
    objs_sym = []
    if trial_type == 'whole':
        # all objects are identical, so you only need one set of dimensional values. 
        width = random.sample([0,1,2,3,4,5,6,7],2)
        height = random.sample([0,1,2,3,4,5,6,7],2)
        colour = random.sample([0,1,2,3,4,5,6,7],2)
        shape = random.sample(['circle', 'square', 'rectangle', 'triangle', 'diamond', 'oval', 'star', 'cloud'],2)
        # make exp1 object. 
        objs_sym.append({'name': 'non_exist', 'RBs': [{'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj1', 'object_sem': [['x_ext', 1, 'x_ext', 'nil', 'state'], ['x_ext'+str(width[0]), 1, 'x_ext', width[0], 'value'], ['y_ext', 1, 'y_ext', 'nil', 'state'], ['y_ext'+str(height[0]), 1, 'y_ext', height[0], 'value'], ['total_ext', 1, 'total_ext', 'nil', 'state'], ['total_ext'+str(width[0]*height[0]), 1, 'total_ext', width[0]*height[0], 'value'], ['colour', 1, 'colour', 'nil', 'state'], ['colour'+str(colour[0]), 1, 'colour', colour[0], 'value'], [str(shape[0]), 1, 'shape', 'nil', 'state']], 'P': 'non_exist'}], 'set': 'memory', 'analog': 0})
        # make exp2 object. 
        objs_sym.append({'name': 'non_exist', 'RBs': [{'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj1', 'object_sem': [['x_ext', 1, 'x_ext', 'nil', 'state'], ['x_ext'+str(width[0]), 1, 'x_ext', width[0], 'value'], ['y_ext', 1, 'y_ext', 'nil', 'state'], ['y_ext'+str(height[0]), 1, 'y_ext', height[0], 'value'], ['total_ext', 1, 'total_ext', 'nil', 'state'], ['total_ext'+str(width[0]*height[0]), 1, 'total_ext', width[0]*height[0], 'value'], ['colour', 1, 'colour', 'nil', 'state'], ['colour'+str(colour[0]), 1, 'colour', colour[0], 'value'], [str(shape[0]), 1, 'shape', 'nil', 'state']], 'P': 'non_exist'}], 'set': 'memory', 'analog': 0})
        # make child match object. 
        objs_sym.append({'name': 'non_exist', 'RBs': [{'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj1', 'object_sem': [['x_ext', 1, 'x_ext', 'nil', 'state'], ['x_ext'+str(width[0]), 1, 'x_ext', width[0], 'value'], ['y_ext', 1, 'y_ext', 'nil', 'state'], ['y_ext'+str(height[0]), 1, 'y_ext', height[0], 'value'], ['total_ext', 1, 'total_ext', 'nil', 'state'], ['total_ext'+str(width[0]*height[0]), 1, 'total_ext', width[0]*height[0], 'value'], ['colour', 1, 'colour', 'nil', 'state'], ['colour'+str(colour[0]), 1, 'colour', colour[0], 'value'], [str(shape[0]), 1, 'shape', 'nil', 'state']], 'P': 'non_exist'}], 'set': 'memory', 'analog': 0})
        # make child unmatch object. 
        objs_sym[2]['RBs'].append({'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj2', 'object_sem': [['x_ext', 1, 'x_ext', 'nil', 'state'], ['x_ext'+str(width[1]), 1, 'x_ext', width[1], 'value'], ['y_ext', 1, 'y_ext', 'nil', 'state'], ['y_ext'+str(height[1]), 1, 'y_ext', height[1], 'value'], ['total_ext', 1, 'total_ext', 'nil', 'state'], ['total_ext'+str(width[1]*height[1]), 1, 'total_ext', width[1]*height[1], 'value'], ['colour', 1, 'colour', 'nil', 'state'], ['colour'+str(colour[1]), 1, 'colour', colour[1], 'value'], [str(shape[1]), 1, 'shape', 'nil', 'state']]})
    elif trial_type == 'feature':
        # select one feature that is identical for everyone, all other features are shuffled. 
        width = random.sample([0,1,2,3,4,5,6,7],6)
        height = random.sample([0,1,2,3,4,5,6,7],6)
        colour = random.sample([0,1,2,3,4,5,6,7],6)
        shape = random.sample(['circle', 'square', 'rectangle', 'triangle', 'diamond', 'oval', 'star', 'cloud'],6)
        dims = [width, height, colour]
        dim = random.choice(range(3))
        for i in range(len(dims[dim])):
            dims[dim][i] = dims[dim][0]
        width.append(random.choice([0,1,2,3,4,5,6,7]))
        height.append(random.choice([0,1,2,3,4,5,6,7]))
        colour.append(random.choice([0,1,2,3,4,5,6,7]))
        shape.append(random.choice(['circle', 'square', 'rectangle', 'triangle', 'diamond', 'oval', 'star', 'cloud']))
        go_on = False
        while not go_on:
            if dims[dim][6] == dims[dim][5]:
                dims[dim][6] = random.choice([0,1,2,3,4,5,6,7])
            else:
                go_on = True
        # make exp1 objects. 
        objs_sym.append({'name': 'non_exist', 'RBs': [{'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj1', 'object_sem': [['x_ext', 1, 'x_ext', 'nil', 'state'], ['x_ext'+str(width[0]), 1, 'x_ext', width[0], 'value'], ['y_ext', 1, 'y_ext', 'nil', 'state'], ['y_ext'+str(height[0]), 1, 'y_ext', height[0], 'value'], ['total_ext', 1, 'total_ext', 'nil', 'state'], ['total_ext'+str(width[0]*height[0]), 1, 'total_ext', width[0]*height[0], 'value'], ['colour', 1, 'colour', 'nil', 'state'], ['colour'+str(colour[0]), 1, 'colour', colour[0], 'value'], [str(shape[0]), 1, 'shape', 'nil', 'state']], 'P': 'non_exist'}], 'set': 'memory', 'analog': 0})
        objs_sym[0]['RBs'].append({'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj2', 'object_sem': [['x_ext', 1, 'x_ext', 'nil', 'state'], ['x_ext'+str(width[1]), 1, 'x_ext', width[1], 'value'], ['y_ext', 1, 'y_ext', 'nil', 'state'], ['y_ext'+str(height[1]), 1, 'y_ext', height[1], 'value'], ['total_ext', 1, 'total_ext', 'nil', 'state'], ['total_ext'+str(width[1]*height[1]), 1, 'total_ext', width[1]*height[1], 'value'], ['colour', 1, 'colour', 'nil', 'state'], ['colour'+str(colour[1]), 1, 'colour', colour[1], 'value'], [str(shape[1]), 1, 'shape', 'nil', 'state']]})
        # make exp2 objects. 
        objs_sym.append({'name': 'non_exist', 'RBs': [{'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj1', 'object_sem': [['x_ext', 1, 'x_ext', 'nil', 'state'], ['x_ext'+str(width[3]), 1, 'x_ext', width[3], 'value'], ['y_ext', 1, 'y_ext', 'nil', 'state'], ['y_ext'+str(height[3]), 1, 'y_ext', height[3], 'value'], ['total_ext', 1, 'total_ext', 'nil', 'state'], ['total_ext'+str(width[3]*height[3]), 1, 'total_ext', width[3]*height[3], 'value'], ['colour', 1, 'colour', 'nil', 'state'], ['colour'+str(colour[3]), 1, 'colour', colour[3], 'value'], [str(shape[3]), 1, 'shape', 'nil', 'state']], 'P': 'non_exist'}], 'set': 'memory', 'analog': 0})
        objs_sym[1]['RBs'].append({'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj2', 'object_sem': [['x_ext', 1, 'x_ext', 'nil', 'state'], ['x_ext'+str(width[4]), 1, 'x_ext', width[4], 'value'], ['y_ext', 1, 'y_ext', 'nil', 'state'], ['y_ext'+str(height[4]), 1, 'y_ext', height[4], 'value'], ['total_ext', 1, 'total_ext', 'nil', 'state'], ['total_ext'+str(width[4]*height[4]), 1, 'total_ext', width[4]*height[4], 'value'], ['colour', 1, 'colour', 'nil', 'state'], ['colour'+str(colour[4]), 1, 'colour', colour[4], 'value'], [str(shape[4]), 1, 'shape', 'nil', 'state']]})
        # make child match objects. 
        objs_sym.append({'name': 'non_exist', 'RBs': [{'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj1', 'object_sem': [['x_ext', 1, 'x_ext', 'nil', 'state'], ['x_ext'+str(width[5]), 1, 'x_ext', width[5], 'value'], ['y_ext', 1, 'y_ext', 'nil', 'state'], ['y_ext'+str(height[5]), 1, 'y_ext', height[5], 'value'], ['total_ext', 1, 'total_ext', 'nil', 'state'], ['total_ext'+str(width[5]*height[5]), 1, 'total_ext', width[5]*height[5], 'value'], ['colour', 1, 'colour', 'nil', 'state'], ['colour'+str(colour[5]), 1, 'colour', colour[5], 'value'], [str(shape[5]), 1, 'shape', 'nil', 'state']], 'P': 'non_exist'}], 'set': 'memory', 'analog': 0})
        objs_sym[2]['RBs'].append({'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj2', 'object_sem': [['x_ext', 1, 'x_ext', 'nil', 'state'], ['x_ext'+str(width[6]), 1, 'x_ext', width[6], 'value'], ['y_ext', 1, 'y_ext', 'nil', 'state'], ['y_ext'+str(height[6]), 1, 'y_ext', height[6], 'value'], ['total_ext', 1, 'total_ext', 'nil', 'state'], ['total_ext'+str(width[6]*height[6]), 1, 'total_ext', width[6]*height[6], 'value'], ['colour', 1, 'colour', 'nil', 'state'], ['colour'+str(colour[6]), 1, 'colour', colour[6], 'value'], [str(shape[6]), 1, 'shape', 'nil', 'state']]})
        # make child unmatched object. 
        objs_sym[2]['RBs'].append({'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj3', 'object_sem': [['x_ext', 1, 'x_ext', 'nil', 'state'], ['x_ext'+str(width[6]), 1, 'x_ext', width[6], 'value'], ['y_ext', 1, 'y_ext', 'nil', 'state'], ['y_ext'+str(height[6]), 1, 'y_ext', height[6], 'value'], ['total_ext', 1, 'total_ext', 'nil', 'state'], ['total_ext'+str(width[6]*height[6]), 1, 'total_ext', width[6]*height[6], 'value'], ['colour', 1, 'colour', 'nil', 'state'], ['colour'+str(colour[6]), 1, 'colour', colour[6], 'value'], [str(shape[6]), 1, 'shape', 'nil', 'state']]})
    else:
        # one relation is identical for everyone. Others are shuffled so no identical relations. 
        width = random.sample([0,1,2,3,4,5,6,7],6)
        height = random.sample([0,1,2,3,4,5,6,7],6)
        colour = random.sample([0,1,2,3,4,5,6,7],6)
        shape = random.sample(['circle', 'square', 'rectangle', 'triangle', 'diamond', 'oval', 'star', 'cloud'],6)
        dims = [width, height, colour]
        dim = random.choice(range(3))
        dims[dim][0] = dims[dim][1]
        dims[dim][2] = dims[dim][3]
        dims[dim][4] = dims[dim][5]
        width.append(random.choice([0,1,2,3,4,5,6,7]))
        height.append(random.choice([0,1,2,3,4,5,6,7]))
        colour.append(random.choice([0,1,2,3,4,5,6,7]))
        shape.append(random.choice(['circle', 'square', 'rectangle', 'triangle', 'diamond', 'oval', 'star', 'cloud']))
        go_on = False
        while not go_on:
            if dims[dim][6] == dims[dim][5]:
                dims[dim][6] = random.choice([0,1,2,3,4,5,6,7])
            else:
                go_on = True
        # make exp1 objects. 
        objs_sym.append({'name': 'non_exist', 'RBs': [{'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj1', 'object_sem': [['x_ext', 1, 'x_ext', 'nil', 'state'], ['x_ext'+str(width[0]), 1, 'x_ext', width[0], 'value'], ['y_ext', 1, 'y_ext', 'nil', 'state'], ['y_ext'+str(height[0]), 1, 'y_ext', height[0], 'value'], ['total_ext', 1, 'total_ext', 'nil', 'state'], ['total_ext'+str(width[0]*height[0]), 1, 'total_ext', width[0]*height[0], 'value'], ['colour', 1, 'colour', 'nil', 'state'], ['colour'+str(colour[0]), 1, 'colour', colour[0], 'value'], [str(shape[0]), 1, 'shape', 'nil', 'state']], 'P': 'non_exist'}], 'set': 'memory', 'analog': 0})
        objs_sym[0]['RBs'].append({'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj2', 'object_sem': [['x_ext', 1, 'x_ext', 'nil', 'state'], ['x_ext'+str(width[1]), 1, 'x_ext', width[1], 'value'], ['y_ext', 1, 'y_ext', 'nil', 'state'], ['y_ext'+str(height[1]), 1, 'y_ext', height[1], 'value'], ['total_ext', 1, 'total_ext', 'nil', 'state'], ['total_ext'+str(width[1]*height[1]), 1, 'total_ext', width[1]*height[1], 'value'], ['colour', 1, 'colour', 'nil', 'state'], ['colour'+str(colour[1]), 1, 'colour', colour[1], 'value'], [str(shape[1]), 1, 'shape', 'nil', 'state']]})
        # make exp2 objects. 
        objs_sym.append({'name': 'non_exist', 'RBs': [{'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj1', 'object_sem': [['x_ext', 1, 'x_ext', 'nil', 'state'], ['x_ext'+str(width[3]), 1, 'x_ext', width[3], 'value'], ['y_ext', 1, 'y_ext', 'nil', 'state'], ['y_ext'+str(height[3]), 1, 'y_ext', height[3], 'value'], ['total_ext', 1, 'total_ext', 'nil', 'state'], ['total_ext'+str(width[3]*height[3]), 1, 'total_ext', width[3]*height[3], 'value'], ['colour', 1, 'colour', 'nil', 'state'], ['colour'+str(colour[3]), 1, 'colour', colour[3], 'value'], [str(shape[3]), 1, 'shape', 'nil', 'state']], 'P': 'non_exist'}], 'set': 'memory', 'analog': 0})
        objs_sym[1]['RBs'].append({'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj2', 'object_sem': [['x_ext', 1, 'x_ext', 'nil', 'state'], ['x_ext'+str(width[4]), 1, 'x_ext', width[4], 'value'], ['y_ext', 1, 'y_ext', 'nil', 'state'], ['y_ext'+str(height[4]), 1, 'y_ext', height[4], 'value'], ['total_ext', 1, 'total_ext', 'nil', 'state'], ['total_ext'+str(width[4]*height[4]), 1, 'total_ext', width[4]*height[4], 'value'], ['colour', 1, 'colour', 'nil', 'state'], ['colour'+str(colour[4]), 1, 'colour', colour[4], 'value'], [str(shape[4]), 1, 'shape', 'nil', 'state']]})
        # make child match objects. 
        objs_sym.append({'name': 'non_exist', 'RBs': [{'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj1', 'object_sem': [['x_ext', 1, 'x_ext', 'nil', 'state'], ['x_ext'+str(width[5]), 1, 'x_ext', width[5], 'value'], ['y_ext', 1, 'y_ext', 'nil', 'state'], ['y_ext'+str(height[5]), 1, 'y_ext', height[5], 'value'], ['total_ext', 1, 'total_ext', 'nil', 'state'], ['total_ext'+str(width[5]*height[5]), 1, 'total_ext', width[5]*height[5], 'value'], ['colour', 1, 'colour', 'nil', 'state'], ['colour'+str(colour[5]), 1, 'colour', colour[5], 'value'], [str(shape[5]), 1, 'shape', 'nil', 'state']], 'P': 'non_exist'}], 'set': 'memory', 'analog': 0})
        objs_sym[2]['RBs'].append({'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj2', 'object_sem': [['x_ext', 1, 'x_ext', 'nil', 'state'], ['x_ext'+str(width[6]), 1, 'x_ext', width[6], 'value'], ['y_ext', 1, 'y_ext', 'nil', 'state'], ['y_ext'+str(height[6]), 1, 'y_ext', height[6], 'value'], ['total_ext', 1, 'total_ext', 'nil', 'state'], ['total_ext'+str(width[6]*height[6]), 1, 'total_ext', width[6]*height[6], 'value'], ['colour', 1, 'colour', 'nil', 'state'], ['colour'+str(colour[6]), 1, 'colour', colour[6], 'value'], [str(shape[6]), 1, 'shape', 'nil', 'state']]})
        # make child unmatched object. 
        objs_sym[2]['RBs'].append({'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj3', 'object_sem': [['x_ext', 1, 'x_ext', 'nil', 'state'], ['x_ext'+str(width[6]), 1, 'x_ext', width[6], 'value'], ['y_ext', 1, 'y_ext', 'nil', 'state'], ['y_ext'+str(height[6]), 1, 'y_ext', height[6], 'value'], ['total_ext', 1, 'total_ext', 'nil', 'state'], ['total_ext'+str(width[6]*height[6]), 1, 'total_ext', width[6]*height[6], 'value'], ['colour', 1, 'colour', 'nil', 'state'], ['colour'+str(colour[6]), 1, 'colour', colour[6], 'value'], [str(shape[6]), 1, 'shape', 'nil', 'state']]})
    # make the new analogs. 
    for analog in objs_sym:
        memory = buildNetwork.makeAnalog([analog], memory)
    # obj_analog is the last three analogs in memory.analogs.
    obj_analog = [memory.analogs[-3], memory.analogs[-2], memory.analogs[-1]]
    # returns. 
    return obj_analog, memory

# fucntion to sample reps from LTM with particular semantics. 
# function takes as input the memory and a list of semantics to sample based on. It finds preds in LTM with those semantics, and samples some. It returns the sampled preds. 
def sample_LTM_rep(memory, semantics, start, threshold=0.95):
    # initialise preds to empty. 
    props = []
    # find POs that connect to the approprite semantics above threshold. Use the POs learned since last simulation, given by the start variable. 
    for myPO in memory.POs[start:]:
        props = add_current_prop(props, myPO, semantics, threshold)
    # sample one element from preds. 
    if len(props) > 0:
        sampled_prop = random.sample(props, 1)
    else:
        sampled_prop = []
    # returns. 
    return sampled_prop

# function to check if the current prop should be added to sample array. 
def add_current_prop(props, myPO, semantics, threshold):
    top_unit = find_top_unit(myPO)
    if top_unit.my_type == 'PO':
        # sample with a small probability. 
        rand_num = random.random()
        if rand_num > .97:
            props.append(top_unit)
    elif myPO.predOrObj == 1:
        # get names of all my semantics with weights above threshold. 
        my_semantics = []
        for link in myPO.mySemantics:
            if link.weight >= threshold:
                my_semantics.append(link.mySemantic.name)
        # check intersection of my_semantics list and semantics list. 
        int_sem = list(set(my_semantics).intersection(semantics))
        if len(int_sem) == len(semantics):
            top_unit = find_top_unit(myPO)
            props.append(top_unit)
    # returns. 
    return props

# funciton to find and return the top unit token unit of a input PO. 
def find_top_unit(myPO):
    top_unit = [myPO]
    # find myPOs RBs. 
    RBs = myPO.myRBs
    # if there are RBs, check if any connect to a P unit. 
    if len(RBs) > 0:
        Ps = []
        for myRB in RBs:
            # check if that RB connects to a P. 
            if len(myRB.myParentPs) > 0:
                for myP in myRB.myParentPs:
                    Ps.append(myP)
        # if there are Ps, select one at random to be the top unit, otherwise randomly sample one of the RBs to be top unit. 
        if len(Ps) > 0:
            top_unit = random.sample(Ps, 1)
        else:
            top_unit = random.sample(RBs, 1)
    # returns. 
    return top_unit[0] # return only the first element as top_unit is a list (because random.sample() returns a list). 

# function to pick to objects from obj_analog. 
def select_objs(obj_analog): 
    # get all the objs in obj_analog. 
    objs = []
    for myPO in obj_analog.myPOs:
        if myPO.predOrObj == 0:
            objs.append(myPO)
    # select 2. 
    objs = random.sample(objs, 2)
    # returns. 
    return objs

# # function to pick objects from a set that are similar on a given dimension.
# def find_objs(obj_analog, dimension):
#     # get all the objs in obj_analog, and find their value on the dimension.
#     objs = []
#     objs_value = []
#     for myPO in obj_analog.myPOs:
#         if myPO.predOrObj == 0:
#             objs.append(myPO)
#             # find myPO value on dimension.
#
#
#
#     # returns.
#     return objs

# function to apply props to objects. 
def apply_preds(obj_analog, objs, props, dimension, memory):
    # run the two objects in objs through the comparitor. 
    val_obj1 = [link.mySemantic.amount for link in objs[0].mySemantics if (link.mySemantic.dimension == dimension) and link.mySemantic.ont_status == 'value']
    val_obj2 = [link.mySemantic.amount for link in objs[1].mySemantics if (link.mySemantic.dimension == dimension) and link.mySemantic.ont_status == 'value']
    if val_obj1 > val_obj2:
        status = 'more'
    elif val_obj1 < val_obj2:
        status = 'less'
    else:
        status = 'same'
    # if props defines a relation, then apply it to the objs, if it defines a single-place pred, then apply only to one object. 
    # find the preds. 
    preds = []
    if props[0].my_type == 'P':
        # find the preds. 
        for myRB in props[0].myRBs:
            preds.append(myRB.myPred[0])
    elif props[0].my_type == 'RB':
        # find the preds. 
        preds.append(props[0].myPred[0])
    else:
        # no preds. 
        preds = []
    # order the preds to match the objects: if status is 'more', but the more pred first, and so on. 
    if len(preds) > 1:
        max_weight = max([x.weight for x in preds[0].mySemantics])
        sem_names = [x.mySemantic.name for x in preds[0].mySemantics if x.weight == max_weight]
        if 'less' in sem_names:
            # reorder the preds. 
            preds.reverse()
    # apply the preds. 
    obj_analogy, memory = make_new_prop(obj_analog, objs, preds, memory)
    # returns. 
    return obj_analog, memory

# function to apply a given set of preds from LTM to objects from an analog.  
def make_new_prop(obj_analog, objs, preds, memory):
    # make copies of the pred tokens. 
    new_preds = []
    for pred in preds:
        # make a new PO. 
        name = 'po_'+str(random.random())
        new_pred = dataTypes.POUnit(name, 'memory', obj_analog, False, obj_analog, 1)
        # make new links for all semantics and add links to memory. 
        for link in pred.mySemantics:
            # make a new link. 
            new_link = dataTypes.Link(new_pred, None, link.mySemantic, link.weight)
            # add the link to the PO. 
            new_pred.mySemantics.append(new_link)
            # add the link to the semantic. 
            link.mySemantic.myPOs.append(new_link)
            # add new_link to memory. 
            memory.Links.append(new_link)
        # add pred to memory.  
        memory.POs.append(new_pred)
        # add pred to new_preds. 
        new_preds.append(new_pred)
    # apply preds to objects. 
    # check if you need a P unit (preds share a P), and if so make one and add to memory and obj_analog. 
    need_P = check_need_P(preds)
    # check if you need an RB unit (pred) has an RB. 
    need_RB = check_need_RB(preds)
    if need_P == True:
        new_P = dataTypes.PUnit('new_P', 'memory', obj_analog, False, obj_analog)
        memory.Ps.append(new_P)
        obj_analog.myPs.append(new_P)
        # do predicate appliction. 
        for i in range(len(new_preds)):
            # make the RB. 
            name = 'RB_'+str(random.random())
            new_RB = dataTypes.RBUnit(name, 'memory', obj_analog, False, obj_analog)
            # add pred and obj to RB. 
            new_RB.myPred.append(new_preds[i])
            new_RB.myObj.append(objs[i])
            # add RB to pred and obj.
            new_preds[i].myRBs.append(new_RB)
            objs[i].myRBs.append(new_RB)
            # add RB to memory and analog.
            memory.RBs.append(new_RB)
            obj_analog.myRBs.append(new_RB)
            # add new_RB to P unit. 
            new_P.myRBs.append(new_RB)
            new_RB.myParentPs.append(new_P)
    elif need_RB:
        for i in range(len(new_preds)):
            # make the RB. 
            name = 'RB_'+str(random.random())
            new_RB = dataTypes.RBUnit(name, 'memory', obj_analog, False, obj_analog)
            # add pred and obj to RB. 
            new_RB.myPred.append(new_preds[i])
            new_RB.myObj.append(objs[i])
            # add RB to pred and obj.
            new_preds[i].myRBs.append(new_RB)
            objs[i].myRBs.append(new_RB)
            # add RB to memory and analog.
            memory.RBs.append(new_RB)
            obj_analog.myRBs.append(new_RB)
    # add all new_preds to obj_analog.
    for pred in new_preds:
        obj_analog.myPOs.append(pred)
    # returns.
    return obj_analog, memory

# function to see if predicates in preds list share a P unit. 
def check_need_P(preds):
    need_P = False
    # preds can't share a P if there is only one pred. 
    if len(preds) > 1:
        # get list of all Ps for first pred. 
        pred1_Ps = []
        for myRB in preds[0].myRBs:
            for myP in myRB.myParentPs:
                pred1_Ps.append(myP)
        # get list of all Ps for second pred. 
        pred2_Ps = []
        for myRB in preds[1].myRBs:
            for myP in myRB.myParentPs:
                pred2_Ps.append(myP)
        # are any of the Ps in the two lists shared? If yes, then set need_P to true. 
        need_P = not set(pred1_Ps).isdisjoint(pred2_Ps)
        # NOTE: you only need to look at the first two preds because if they share a P it means any other preds in preds list will also share a P as all the preds in the preds list are from a single multi-place relation.
    # returns. 
    return need_P

# function to see if the POs in preds list are preds and connected to a RB unit. 
def check_need_RB(preds):
    need_RB = False 
    # are any of the preds in preds connected to RBs? 
    for pred in preds:
        if len(pred.myRBs) > 0:
            need_RB = True
            pass
    # returns. 
    return need_RB

# function to run a simple trial. 
def run_trial(network, start, tally, correct, trial_type):
    # create reps; the kind of trial will determine what kind of objects to make (types are 'whole', 'feature', 'relation'). 
    obj_analogs, network.memory = add_objects(network.memory, trial_type)
    # child_analog is the last analog of obj_analogs. 
    child_analog = obj_analogs[2]
    # if the trial type is whole, put child analog in driver and one of experimenter analogs in recipient, and try to map. 
    if trial_type == 'whole':
        # place child objects in driver, and one experimenter object in recipient, and map. 
        exp_analog = random.choice(obj_analogs[:2])
        network.memory = basicRunDORA.add_tokens_to_set(network.memory, network.memory.analogs.index(child_analog), 'analog', 'driver')
        network.memory = basicRunDORA.add_tokens_to_set(network.memory, network.memory.analogs.index(exp_analog), 'analog', 'recipient')
        # clear and update the contents of driver and recipient. 
        network.memory = basicRunDORA.clearDriverSet(network.memory)
        network.memory = basicRunDORA.clearRecipientSet(network.memory)
        network.memory = basicRunDORA.findDriverRecipient(network.memory)
        # do mapping and print results.
        network.do_map()
        basicRunDORA.DORA_GUI.term_map_display(network.memory) # show mappings.
        # clear mapping result. 
        network.memory = basicRunDORA.reset_inferences(network.memory)
        network.memory = basicRunDORA.reset_maker_made_units(network.memory)
        network.memory = basicRunDORA.reset_mappings(network.memory)
        network.memory = basicRunDORA.update_Names_nil(network.memory)
        network.memory = basicRunDORA.indexMemory(network.memory)
        network.memory = basicRunDORA.initialize_memorySet(network.memory)
    else: # for 'feature' and 'relation' trials. 
        # find the dimension experimenter objects match on by comparing experimenter sets.  
        dimension = None
        Exp1 = obj_analogs[0]
        Exp2 = obj_analogs[1]
        for link in Exp1.myPOs[0].mySemantics:
            found_flag = False
            if link.mySemantic.ont_status == 'value':
                dim = link.mySemantic.dimension
                val = link.mySemantic.amount
                for link2 in Exp1.myPOs[1].mySemantics:
                    if link2.mySemantic.ont_status == 'value' and link2.mySemantic.dimension == dim and link2.mySemantic.amount == val:
                        found_flag = True
                        dimension = dim
                        break
            if found_flag:
                break
        # sample experimenter objects to use for mapping. 
        exp_analog = random.choice(obj_analogs[:2])
        # sample two props from LTM that match dimension. 
        propExp = sample_LTM_rep(network.memory, dimension, start, threshold=0.95)
        propChild = sample_LTM_rep(network.memory, dimension, start, threshold=0.95)
        # apply propExp to experimenter objects. 
        objsExp = select_objs(exp_analog)
        exp_analog, network.memory = apply_preds(exp_analog, objsExp, propExp, dimension, network.memory)
        # apply propChild to child objects. 
        # first, find any child objects that match on the dimension and put them in objsChild. 
        val0 = [x.mySemantic.amount for x in child_analog.myPOs[0].mySemantics if x.mySemantic.dimension == dimension and x.mySemantic.ont_status == 'value']
        val1 = [x.mySemantic.amount for x in child_analog.myPOs[1].mySemantics if x.mySemantic.dimension == dimension and x.mySemantic.ont_status == 'value']
        val2 = [x.mySemantic.amount for x in child_analog.myPOs[2].mySemantics if x.mySemantic.dimension == dimension and x.mySemantic.ont_status == 'value']
        if val0 == val1:
            objsChild = [child_analog.myPOs[0], child_analog.myPOs[1]]
        elif val1 == val2:
            objsChild = [child_analog.myPOs[1], child_analog.myPOs[2]]
        elif val0 == val2:
            objsChild = [child_analog.myPOs[0], child_analog.myPOs[2]]
        # apply propChild to child objects. 
        child_analog, network.memory = apply_preds(child_analog, objsChild, propChild, dimension, network.memory)
        # child objects in driver, experimenter in recipient, and map. 
        network.memory = basicRunDORA.add_tokens_to_set(network.memory, network.memory.analogs.index(child_analog), 'analog', 'driver')
        network.memory = basicRunDORA.add_tokens_to_set(network.memory, network.memory.analogs.index(exp_analog), 'analog', 'recipient')
        # clear and update the contents of driver and recipient. 
        network.memory = basicRunDORA.clearDriverSet(network.memory)
        network.memory = basicRunDORA.clearRecipientSet(network.memory)
        network.memory = basicRunDORA.findDriverRecipient(network.memory)
        # do mapping and print results.
        network.do_map()
        basicRunDORA.DORA_GUI.term_map_display(network.memory) # show mappings.
        # clear mapping result. 
        network.memory = basicRunDORA.reset_inferences(network.memory)
        network.memory = basicRunDORA.reset_maker_made_units(network.memory)
        network.memory = basicRunDORA.reset_mappings(network.memory)
        network.memory = basicRunDORA.update_Names_nil(network.memory)
        network.memory = basicRunDORA.indexMemory(network.memory)
        network.memory = basicRunDORA.initialize_memorySet(network.memory)
    #returns.
    return tally, correct

# funciton to count the reps of each type in memory from a start point in POs. 
def count_reps(memory, start_POs, start_RBs, start_Ps):
    new_objs = []
    new_preds = []
    new_rels = []
    for myPO in memory.POs[start_POs:]:
        if len(myPO.myRBs) == 0:
            new_objs.append(myPO)
        else:
            for myRB in myPO.myRBs:
                if len(myRB.myParentPs) == 0:
                    if myRB not in new_preds:
                        new_preds.append(myRB)
                else:
                    for myP in myRB.myParentPs:
                        if myP not in new_rels:
                            new_rels.append(myP)
    for myRB in memory.RBs[start_RBs:]:
        if len(myRB.myParentPs) == 0:
            if myRB not in new_preds:
                new_preds.append(myRB)
        else:
            for myP in myRB.myParentPs:
                if myP not in new_rels:
                    new_rels.append(myP)
    for myP in memory.Ps[start_Ps:]:
        if myP not in new_rels:
            new_rels.append(myP)
    # returns. 
    return new_objs, new_preds, new_rels

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

# run a sim. 
def run_sim(trials, memory_states):
    for memory_state in memory_states:
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
        # run trials of each kind ('whole', 'feature', 'relation'). 
        correct_w = 0
        correct_f = 0
        correct_r = 0
        start_POs = 0
        tally = 0
        for i in range(trials):
            # run a 'whole' trial. 
            tally, was_correct = run_trial(network, start_POs, tally, correct_w, 'whole')
            correct_w += was_correct
            # run a 'feature' trial. 
            tally, was_correct = run_trial(network, start_POs, tally, correct_w, 'feature')
            correct_f += was_correct
            # run a 'relation' trial. 
            tally, was_correct = run_trial(network, start_POs, tally, correct_w, 'relation')
            correct_r += was_correct
        print(tally, '\n', correct_w, '\n', correct_f, '\n', correct_r, '\n', '\n\n\n')
        

############################################################################
# run sim. 
############################################################################
memory_states = ['batch_run1000', 'batch_run2000', 'batch_run3000']
run_sim(100, memory_states)






