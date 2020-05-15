# sims R&G. 

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
def add_objects(memory, objects): 
    # make a sym file version of the analog that includes all the objects from the objects list. 
    objs_sym = [{'name': 'non_exist', 'RBs': [], 'set': 'memory', 'analog': 0}]
    # get and order three widths and hights. 
    width1 = round(random.random()*100)
    width2 = round(random.random()*100)
    width3 = round(random.random()*100)
    width = [width1, width2, width3]
    width.sort()
    hight1 = round(random.random()*100)
    hight2 = round(random.random()*100)
    hight3 = round(random.random()*100)
    hight = [hight1, hight2, hight3]
    hight.sort()
    for item in range(len(objects)):
        objs_sym[0]['RBs'].append({'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': objects[item], 'object_sem': [['x_ext', 1, 'x_ext', 'nil', 'state'], ['x_ext'+str(width[item]), 1, 'x_ext', width[item], 'value'], ['y_ext', 1, 'y_ext', 'nil', 'state'], ['y_ext'+str(hight[item]), 1, 'y_ext', hight[item], 'value'], ['total_ext', 1, 'total_ext', 'nil', 'state'], ['total_ext'+str(width[item]*hight[item]), 1, 'total_ext', width[item]*hight[item], 'value']], 'P': 'non_exist'})
    # make the new analog. 
    memory = buildNetwork.makeAnalog(objs_sym, memory)
    # obj_analog is the last analog in memory.analogs.
    obj_analog = memory.analogs[-1]
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
    # if top_unit.my_type == 'PO':
#         # sample with a small probability.
#         rand_num = random.random()
#         if rand_num > .97:
#             props.append(top_unit)
    if myPO.predOrObj == 1:
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

# function to run a simple RB trial. 
def run_RGtrial(network, start, tally, correct):
    # make some objects for child. 
    obj_analog1, network.memory = add_objects(network.memory, ['obj1', 'obj2', 'obj3'])
    # make some objects for experimenter. 
    obj_analog2, network.memory = add_objects(network.memory, ['obj1', 'obj2', 'obj3'])
    # select a dimension.
    dimension = random.sample(['x_ext', 'y_ext', 'total_ext'], 1)
    dimension.append(random.sample(['more', 'less'], 1)[0])
    # get two props. 
    prop1 = sample_LTM_rep(network.memory, dimension, start, threshold=0.95)
    prop2 = sample_LTM_rep(network.memory, dimension, start, threshold=0.95)
    prop3 = sample_LTM_rep(network.memory, dimension, start, threshold=0.95)
    prop4 = sample_LTM_rep(network.memory, dimension, start, threshold=0.95)
    # apply prop to objects. 
    obj_analog1, network.memory = apply_preds(obj_analog1, [obj_analog1.myPOs[0], obj_analog1.myPOs[1]], prop1, dimension[0], network.memory)
    obj_analog1, network.memory = apply_preds(obj_analog1, [obj_analog1.myPOs[1], obj_analog1.myPOs[2]], prop2, dimension[0], network.memory)
    obj_analog2, network.memory = apply_preds(obj_analog2, [obj_analog2.myPOs[0], obj_analog2.myPOs[1]], prop3, dimension[0], network.memory)
    obj_analog2, network.memory = apply_preds(obj_analog2, [obj_analog2.myPOs[1], obj_analog2.myPOs[2]], prop4, dimension[0], network.memory)
    # put obj_analog1 in the driver and obj_analog2 in the recipient. 
    network.memory = basicRunDORA.add_tokens_to_set(network.memory, network.memory.analogs.index(obj_analog1), 'analog', 'driver')
    network.memory = basicRunDORA.add_tokens_to_set(network.memory, network.memory.analogs.index(obj_analog2), 'analog', 'recipient')
    # clear and update the contents of driver and recipient. 
    network.memory = basicRunDORA.clearDriverSet(network.memory)
    network.memory = basicRunDORA.clearRecipientSet(network.memory)
    network.memory = basicRunDORA.findDriverRecipient(network.memory)
    # do mapping and print results.
    network.do_map()
    basicRunDORA.DORA_GUI.term_map_display(network.memory) # show mappings. 
    # order the recipient and driver objects. 
    driver_objs = []
    for myPO in network.memory.driver.POs:
        if myPO.predOrObj == 0:
            driver_objs.append(myPO)
    recipient_objs = []
    for myPO in network.memory.recipient.POs:
        if myPO.predOrObj == 0:
            recipient_objs.append(myPO)
    # select an item from recipient as the sticker. 
    sticker_index = random.sample([0,1,2], 1)
    sticker_index = sticker_index[0]
    # find recipient sticker max map unit. 
    max_map = 0.0
    max_map_unit = None
    for mapping in recipient_objs[sticker_index].mappingConnections:
        if mapping.weight > max_map:
            max_map = mapping.weight
            max_map_unit = mapping.driverToken
    # check if maps to appropriate driver object and update correct variable. 
    if max_map_unit is driver_objs[sticker_index]:
        correct = 1
    elif max_map_unit == None:
        rand_num = random.random()
        if rand_num < .34:
            correct = 1
        else:
            correct = 0
    else:
        correct = 0
    # clear mapping result. 
    network.memory = basicRunDORA.reset_inferences(network.memory)
    network.memory = basicRunDORA.reset_maker_made_units(network.memory)
    network.memory = basicRunDORA.reset_mappings(network.memory)
    network.memory = basicRunDORA.update_Names_nil(network.memory)
    network.memory = basicRunDORA.indexMemory(network.memory)
    network.memory = basicRunDORA.initialize_memorySet(network.memory)
    #returns.
    return correct

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
def run_RGsim(trials, memory_states):
    last_POs = 0
    last_RBs = 0
    last_Ps = 0
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
        # find which reps were learned since the last simulation. 
        new_POs = len(network.memory.POs) - last_POs
        new_RBs = len(network.memory.RBs) - last_RBs
        new_Ps = len(network.memory.Ps) - last_Ps
        last_POs = len(network.memory.POs)
        last_RBs = len(network.memory.RBs)
        last_Ps = len(network.memory.Ps)
        start_POs = len(network.memory.POs) - new_POs
        start_RBs = len(network.memory.RBs) - new_RBs
        start_Ps = len(network.memory.Ps) - new_Ps
        new_objs, new_preds, new_rels = count_reps(memory, start_POs, start_RBs, start_Ps)
        print(new_POs, new_RBs, new_Ps)
        print(len(new_objs), len(new_preds), len(new_rels))
        # run 1000 trials. 
        tally = {'P': 0, 'RB': 0, 'PO': 0}
        correct = 0
        for i in range(trials):
            was_correct = run_RGtrial(network, start_POs, tally, correct)
            correct += was_correct
        print(tally, '\n', correct, '\n\n\n')
        

############################################################################
# run sim. 
############################################################################
memory_states = ['batch_run1000', 'batch_run2000', 'batch_run3000']
run_RGsim(100, memory_states)
pdb.set_trace()






 