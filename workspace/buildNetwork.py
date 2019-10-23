# buildNetwork.py
# code to make the network structure for DORA.
# Structure:
# A large object simulation, with fields:
# Memory.Ps (all Ps); Main.RBs (all RBs); Main.POs (all POs)
# Semantics
# driver.Ps; driver.RBs; driver.POs
# recipient.Ps; recipient.RBs; recipient.POs
# newSet.Ps; newSet.RBs; newSet.POs (all tokens in the emerging schema)

# imports.
import random
import dataTypes
import pdb

# create the currentsym class. It will have fields, driver (containing driver sym props to be made), recipent(containing recipient sym props to be made), and memory (containing memory sym props to be made).
# noinspection PyPep8Naming
class currentsym(object):
    def __init__(self, driver, recipient, memory):
        self.driver = driver
        self.recipient = recipient
        self.memory = memory

# interpret the sym file and build the currentsym data structure. Return the currentsym structure and the number of analogs in driver, recipient, and memory.
# noinspection PyPep8Naming
def interpretSymfile(symfile):
    # a symfile is a list of Propositions.
    # iterate through each proposition and put it in either the driver, the recipient, or memory.
    # First initialize driver, recipient, and memory sets:
    driver = []
    recipient = []
    memory = []
    # now sort and find the number of analogs in driver, recipient, and memory.
    driver_num = 0
    recipient_num = 0
    memory_num = 0
    for prop in symfile:
        # check the set.
        if prop['set'] == 'driver':
            driver.append(prop)
            # now check if the analog of the current prop is greater than the driver_num (the current highest listed analog for the driver). If so, replace driver_num.
            if prop['analog'] > driver_num:
                driver_num = prop['analog']
        elif prop['set'] == 'recipient':
            recipient.append(prop)
             # now check if the analog of the current prop is greater than the recipient_num (the current highest listed analog for the recipient). If so, replace recipient_num.
            if prop['analog'] > recipient_num:
                recipient_num = prop['analog']
        elif prop['set'] == 'memory':
            memory.append(prop)
            # now check if the analog of the current prop is greater than the memory_num (the current highest listed analog for the memory). If so, replace memory_num.
            if prop['analog'] > memory_num:
                memory_num = prop['analog']
    # now, arrange all the elements in driver according to their analog. That is, put all Ps from analog-1 in together on a list, all Ps from analog-2 together in a list, and so forth.
    driver_sorted = []
    recipient_sorted = []
    memory_sorted = []
    for i in range(driver_num+1):
        driver_set = []
        for prop in driver:
            if prop['analog'] == i:
                driver_set.append(prop)
        driver_sorted.append(driver_set)
    driver = driver_sorted
    for i in range(recipient_num+1):
        recipient_set = []
        for prop in recipient:
            if prop['analog'] == i:
                recipient_set.append(prop)
        recipient_sorted.append(recipient_set)
    recipient = recipient_sorted
    for i in range(memory_num+1):
        memory_set = []
        for prop in memory:
            if prop['analog'] == i:
                memory_set.append(prop)
        memory_sorted.append(memory_set)
    memory = memory_sorted
    # now make the currentsym object:
    mycurrentsym = currentsym(driver, recipient, memory)
    # and return mycurrentsym.
    return [mycurrentsym, driver_num, recipient_num, memory_num]

# initialize memory set for use when you are loading up a completely new simulation.
def initializeMemorySet():
    memory = dataTypes.memorySet()
    return memory

# Main build function (takes in a currentsym data structure, a memory structure (should be empty if you're making a new network), and builds the network):
def buildTheNetwork(currentsym, memory):
    # iterate through each element of currentsym:
    for analog in currentsym.driver:
        memory = makeAnalog(analog, memory)
    for analog in currentsym.recipient:
        memory = makeAnalog(analog, memory)
    for analog in currentsym.memory:
        memory = makeAnalog(analog, memory)
    # done.
    return memory

# code to make the datatypes in a specific analog.
def makeAnalog(analog, memory):
    # you want to keep track of all the Ps, RBs, and POs you've made in this analog so that you can reuse POs among the propositions in the analog (e.g., use the same John in loves(John, Mary) and loves(Mary, John)).
    # make a new analog object and add it to memory.analogs (but make sure the analog isn't empty).
    if len(analog) > 0:
        new_analog = dataTypes.Analog()
        memory.analogs.append(new_analog)
    # find the current analog.
    # iterate through each element of the analog, which is a proposition:
    for prop in analog:
        # create a group unit if you should.
        ######################## HERE ########################

        # create the P unit if you should (i.e., if prop['name'] != 'non_exist').
        if prop['name'] != 'non_exist':
            newP = dataTypes.PUnit(prop['name'], prop['set'], prop['analog'], False, new_analog)
            # if the newP does exist in the current analog, set newP = to the P already in currentPs to which newP should correspond (e.g., if the newP is LJM, and LJM is the 3rd P in currentPs, set newP = currentP[2]). Otherwise, put the newP in the currentPs list.
            add_new_P = True
            for myP in memory.Ps:
                if (newP.set == myP.set)  and (newP.myanalog == myP.myanalog):
                    if newP.name == myP.name: # if the P already exists, then set newP to P, and set add_new_P to False.
                        newP = myP
                        add_new_P = False
                        break
            if add_new_P:
                # add the P to the memory and the new_analog object.
                memory.Ps.append(newP)
                new_analog.myPs.append(newP)
        else:
            newP = 'non_exist'
        # now make the new RBs.
        # for each RB in prop, create the RB, hook it up to it's parent P, make it's pred (and pred semantics) and object (and object semantics), hook it up to it's pred and object (and if it is higher order, it's child P).
        for myRB in prop['RBs']:
            # make the myRB. First check if you should make the RB (i.e., if RB['pred_name] != 'non_exist').
            if myRB['pred_name'] != 'non_exist':
                # get the RB's name.
                if myRB['higher_order']:
                    RB_name = myRB['pred_name']+myRB['P']
                else:
                    RB_name = myRB['pred_name']+myRB['object_name']
                # make the myRB.
                newRB = dataTypes.RBUnit(RB_name, prop['set'], prop['analog'], False, new_analog)
                # put the new RB in memory and in the new_analog.
                memory.RBs.append(newRB)
                new_analog.myRBs.append(newRB)
                # hook up the RB to the newP and vise versa if there is a newP.
                if newP !='non_exist':
                    newRB.myParentPs.append(newP)
                    newP.myRBs.append(newRB)
            else:
                newRB = 'non_exist'
            # make the RB's pred and object.
            # if newRB != 'non_exist', then make the pred.
            if newRB != 'non_exist':
                # make the pred.
                newPred = dataTypes.POUnit(myRB['pred_name'], prop['set'], prop['analog'], False, new_analog, 1)
                # check to make sure the pred doesn't already exist in the currentPreds.
                add_new_pred = True
                for pred in memory.POs:
                    if (newPred.set == pred.set) and (newPred.myanalog == pred.myanalog):
                        if (newPred.name == pred.name) and (pred.predOrObj == 1): # if that pred already exists and is a pred (i.e., pred.predOrObj == 1), then set newPred = pred, and set add_new_pred to False.
                            newPred = pred
                            add_new_pred = False
                            break
                if add_new_pred and newPred != 'non_exist':
                    # else, if the newPred is actually new and has been made (i.e., the newPred != 'non_exist'), add it to currentPreds and make its semantics.
                    # add the new Pred to memory and to the new_analog.
                    memory.POs.append(newPred)
                    new_analog.myPOs.append(newPred)
                    # make the newPred's semantics.
                    # make sure that no semantics are repeated in the list of pred_sem (i.e., the same semantic should not be listed twice).
                    # NOTE: you could also accomplisth the loop below with list(set(RB['pred_sem'])), but that would not maintain order. While order of the items does not functionally matter here, I've chosen to use a method that maintains order here.
                    pred_sem_list = []
                    for item in myRB['pred_sem']:
                        if item not in pred_sem_list:
                            pred_sem_list.append(item)
                    for semantic in pred_sem_list:
                        # check if the semantic should be made (i.e., it doesn't already exist).
                        makeNewSem = True
                        # is the semantic in a list or not?
                        if type(semantic) is list:
                            for oldsemantic in memory.semantics:
                                if oldsemantic.name == semantic[0]:
                                    makeNewSem = False
                                    newSem = oldsemantic
                                    break
                        else:
                            for oldsemantic in memory.semantics:
                                if oldsemantic.name == semantic:
                                    makeNewSem = False
                                    newSem = oldsemantic
                                    break
                        # if makeNewSem is True, then make the new semantic unit and add it to memory.semantics, otherwise, connect the newSem (which has already been set directly above to the value of the semantic in memory.semantics that the newPred should be connected to) to newPred.
                        if makeNewSem:
                            # create the new semantic and the newLink.
                            # check wheter semantic codes a dimension or not.
                            if (type(semantic) is list) and (len(semantic) > 4):
                                newSem = dataTypes.Semantic(semantic[0], semantic[2], semantic[3], semantic[4])
                                newLink = dataTypes.Link(newPred, [], newSem, semantic[1])
                            elif (type(semantic) is list) and (len(semantic) > 2):
                                newSem = dataTypes.Semantic(semantic[0], semantic[2], semantic[3])
                                newLink = dataTypes.Link(newPred, [], newSem, semantic[1])
                            elif type(semantic) is list:
                                newSem = dataTypes.Semantic(semantic[0])
                                newLink = dataTypes.Link(newPred, [], newSem, semantic[1])
                            else:
                                # default to a semantic with a weight of 1. 
                                newSem = dataTypes.Semantic(semantic)
                                newLink = dataTypes.Link(newPred, [], newSem, 1)
                            # add newLink to newSem and newPred, and add newLink to currentLinks, and newSem to memory.semantics.
                            newSem.myPOs.append(newLink)
                            newPred.mySemantics.append(newLink)
                            memory.Links.append(newLink)
                            memory.semantics.append(newSem)
                        else:
                            # create the newLink. 
                            # if semantic is a list, then use semantic[1] for the weight, else default to a weight of 1. 
                            if type(semantic) is list:
                                newLink = dataTypes.Link(newPred, [], newSem, semantic[1])
                            else:
                                newLink = dataTypes.Link(newPred, [], newSem, 1)
                            # add newLink to newSem and newPred, and add newLink to currentLinks, (don't need to add newSem to memory.semantics because it is already there (remember that makeNewSem == False)).
                            newSem.myPOs.append(newLink)
                            newPred.mySemantics.append(newLink)
                            memory.Links.append(newLink)
                # hook the newPred to the newRB and viseversa.
                newPred.myRBs.append(newRB)
                newRB.myPred.append(newPred)
            # if the RB is not higher-order, make the newobject.
            if not myRB['higher_order']:
                newObject = dataTypes.POUnit(myRB['object_name'], prop['set'], prop['analog'], False, new_analog, 0)
                # check to make sure the newObject doesn't already exist in the currentObjects.
                make_new_obj = True
                for obj in memory.POs:
                    if (newObject.set == obj.set) and (newObject.myanalog == obj.myanalog):
                        if (newObject.name == obj.name) and (obj.predOrObj == 0): # if the object already exists and is an object (i.e., newObject.predOrObj == 0), then set newObject to obj, and make_new_obj to False
                            newObject = obj
                            make_new_obj = False
                            break
                if make_new_obj:
                    # else, the newObject is actually new, add it to memory and the new_analog and make its semantics.
                    new_analog.myPOs.append(newObject)
                    memory.POs.append(newObject)
                    # make the newobject's semantics.
                    # make sure that no semantics are repeated in the list of object_sem (i.e., the same semantic should not be listed twice).
                    # NOTE: you could also accomplisth the loop below with list(set(RB['object_sem'])), but that would not maintain order. While order of the items does not functionally matter here, I've chosen to use a method that maintains order here.
                    obj_sem_list = []
                    for item in myRB['object_sem']:
                        if item not in obj_sem_list:
                            obj_sem_list.append(item)
                    for semantic in obj_sem_list:
                        # check if the semantic should be made (i.e., it doesn't already exist).
                        makeNewSem = True
                        # is the semantic in a list or not?
                        if type(semantic) is list:
                            for oldsemantic in memory.semantics:
                                if oldsemantic.name == semantic[0]:
                                    makeNewSem = False
                                    newSem = oldsemantic
                                    break
                        else:
                            for oldsemantic in memory.semantics:
                                if oldsemantic.name == semantic:
                                    makeNewSem = False
                                    newSem = oldsemantic
                                    break
                        # if makeNewSem is True, then make the new semantic unit and add it to memory.semantics, otherwise, connect the newSem (which has already been set directly above to the value of the semantic in memory.semantics that the newPred should be connected to) to newObject.
                        if makeNewSem:
                            # create the new semantic and the newLink.
                            # check wheter semantic codes a dimension or not.
                            if (type(semantic) is list) and (len(semantic) > 4):
                                newSem = dataTypes.Semantic(semantic[0], semantic[2], semantic[3], semantic[4])
                                newLink = dataTypes.Link(newObject, [], newSem, semantic[1])
                            elif (type(semantic) is list) and (len(semantic) > 2):
                                newSem = dataTypes.Semantic(semantic[0], semantic[2], semantic[3])
                                newLink = dataTypes.Link(newObject, [], newSem, semantic[1])
                            elif type(semantic) is list:
                                newSem = dataTypes.Semantic(semantic[0])
                                newLink = dataTypes.Link(newObject, [], newSem, semantic[1])
                            else:
                                # default to a semantic with a weight of 1. 
                                newSem = dataTypes.Semantic(semantic)
                                newLink = dataTypes.Link(newObject, [], newSem, 1)
                            # add newLink to newSem and newPred, and add newLink to currentLinks, and newSem to memory.semantics.
                            newSem.myPOs.append(newLink)
                            newObject.mySemantics.append(newLink)
                            memory.Links.append(newLink)
                            memory.semantics.append(newSem)
                        else:
                            # create the newLink. 
                            # if semantic is a list, then use semantic[1] for the weight, else default to a weight of 1. 
                            if type(semantic) is list:
                                newLink = dataTypes.Link(newObject, [], newSem, semantic[1])
                            else:
                                newLink = dataTypes.Link(newObject, [], newSem, 1)
                            # add newLink to newSem and newObject, and add newLink to currentLinks, (don't need to add newSem to memory.semantics because it is already there (remember that makeNewSem == False)).
                            newSem.myPOs.append(newLink)
                            newObject.mySemantics.append(newLink)
                            memory.Links.append(newLink)
                # hook the newObject up to the new RB and viseversa (if you have actually made a newRB; i.e., newRB != 'non_exist').
                if newRB != 'non_exist':
                    newObject.myRBs.append(newRB)
                    newRB.myObj.append(newObject)
                # hook up the pred and object in the same_RB_POs field of both pred and obj if there is a newPred also.
                if newRB != 'non_exist': # if newRB != 'non_exist' it means that a new pred has been made.
                    newPred.same_RB_POs.append(newObject)
                    newObject.same_RB_POs.append(newPred)
            elif myRB['higher_order']:
                # connect the RB to it's child P and viseversa.
                # child P should already have been made. It should be the P in the myRB.Pth place .
                # if the RB takes a child P unit, then you must find the P unit that connects to the current myRB. It will be the last P unit you made with the name RB['P'].
                foundChildP = False
                for myP in reversed(memory.Ps):
                    if myP.name == myRB['P']:
                        # connect the current RB to that P and vise versa.
                        newRB.myChildP.append(myP)
                        myP.myParentRBs.append(newRB)
                        foundChildP = True
                        break
                if not foundChildP:
                    print('You are trying to create a higher-order proposition with a child P that does not exist. Please check your sym file.')
    # now make sure all the weights in all the links are represented as floats. 
    for Link in memory.Links:
        Link.weight = float(Link.weight)
    # done.
    return memory




