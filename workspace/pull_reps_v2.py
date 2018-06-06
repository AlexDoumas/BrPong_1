# code to extract representations of predicates and relations from state files to create new state files. Primarily useful for pulling representations from big learning runs for use in task specific simulations. 

import json, random
import pdb

# list of files to read memory data from.
state_list = ['batch_run100', 'batch_run200', 'batch_run300', 'batch_run400', 'batch_run500', 'batch_run600', 'batch_run700', 'batch_run800', 'batch_run900', 'batch_run1000', 'batch_run1100', 'batch_run1200', 'batch_run1300', 'batch_run1400', 'batch_run1500', 'batch_run1600', 'batch_run1700', 'batch_run1800', 'batch_run1900', 'batch_run2000', 'batch_run2100', 'batch_run2200', 'batch_run2300', 'batch_run2400', 'batch_run2500', 'batch_run2600', 'batch_run2700', 'batch_run2800', 'batch_run2900', 'batch_run3000', 'batch_run3100', 'batch_run3200', 'batch_run3300', 'batch_run3400', 'batch_run3500', 'batch_run3600', 'batch_run3700', 'batch_run3800', 'batch_run3900', 'batch_run4000', 'batch_run4100', 'batch_run4200', 'batch_run4300', 'batch_run4400', 'batch_run4500', 'batch_run4600', 'batch_run4700', 'batch_run4800', 'batch_run4900', 'batch_run5000']

###############################################################################
# FUNCTIONS. 
###############################################################################

# function to load the state file(s). 
def load_states(state_list):
    mem_state_list = []
    for state in state_list:
        # load in the json file.
        myfile = open(state, 'r')
        myfile.seek(0)
        myfile.readline()
        mem_state = json.loads(myfile.readline())
        mem_state_list.append(mem_state)
    # return mem_state_list. 
    return mem_state_list

# function to break down a mem_state in to relations, RBs, and objects. 
def break_up_reps(mem_state):
    # collect all the Ps, RBs, and objs in separate arrays. 
    Ps = [prop for prop in mem_state if prop['name'] != 'non_exist']
    RBs = [prop for prop in mem_state if (prop['name'] == 'non_exist') and (prop['RBs'][0]['pred_name'] != 'non_exist')]
    objs = [prop for prop in mem_state if (prop['name'] == 'non_exist') and (prop['RBs'][0]['pred_name'] == 'non_exist')]
    # make an array of arrays of Ps, RBs, and objs.
    separated_arrays = [Ps, RBs, objs]
    # return separated_arrays. 
    return separated_arrays

# function to find all the reps in a list that are strongly connected to a critical semantic. 
def find_critical_reps(reps, criterion):
    dim_reps = []
    # for each proposition, check if the critical semantic exists with a high weight. 
    for prop in reps:
        for currentRB in prop['RBs']:
            # if you have an RB or relation, then look for the critical semantic amoung the pred_semantics. 
            if len(currentRB['pred_sem']) > 0:
                for semantic in currentRB['pred_sem']:
                    if (semantic[0] == criterion) and (semantic[1]>.9):
                        dim_reps.append(prop)
                        break
            else:
                # otherwise, look for the critical semantic amoung the obj_semantics. 
                for semantic in currentRB['object_sem']:
                    if (semantic[0] == criterion) and (semantic[1]>.9):
                        dim_reps.append(prop)
                        break
            # check if the current prop has been added to dim_reps, and if so, break out of the for loop as you don't need to iterate through more RBs. 
            if prop in dim_reps:
                break
    # return dim_reps. 
    return dim_reps 

# function to sample from an array of representations for a representation attached to the criterion semantic. 
def sample_item_from_state(state_array, criterion):
    # randomly sample a proposition from the state_array, and check if it contains the criterion semantic. 
    go_on = True
    while go_on:
        prop = random.sample(state_array,1)
        for currentRB in prop[0]['RBs']:
            # if you have an RB or relation, then look for the critical semantic amoung the pred_semantics. 
            if len(currentRB['pred_sem']) > 0:
                for semantic in currentRB['pred_sem']:
                    if (semantic[0] == criterion) and (semantic[1]>.9):
                        go_on = False
                        break
            else:
                # otherwise, look for the critical semantic amoung the obj_semantics. 
                for semantic in currentRB['object_sem']:
                    if (semantic[0] == criterion) and (semantic[1]>.9):
                        go_on = False
                        break
            if go_on == False:
                break
    # return the sampled item.
    return prop

# function to write a set of specified critical representations (i.e., props that have some critical semantic) to a named json dump.
def write_crit_reps(crit_array, file_name):
    json.dump(crit_array, open(file_name, 'w'))
    # now prepend 'simType='sym_file' symProps = '. NOTE: This process is clunky, because you have to write all the json information to a textfile first as the json.dump() function requires a second argument (the open() component), and thus writes over the content of the text file, and consequently does not allow prepended text information. Prepending information to a text file requires rewriting the text file.
    with open(file_name, 'r+') as f:
        old_text = f.read() # read all the contents of f into a new variable. 
        f.seek(0) # go back to the start of f. 
        f.write('simType=\'json_sym\' \n' + old_text)
   
##########################################################################################
# MAIN BODY.
##########################################################################################
# set the criterion semantics. 
criteria = ['size', 'height', 'depth', 'width']
# load all the memory states. 
mem_state_list = load_states(state_list)
# find critical reps from each loaded state. 
state_crit = []
for state in mem_state_list:
    # break up the state into Ps, RBs, and objs.
    sep_arrays = break_up_reps(state)
    # find the reps that include the critical semantics.
    crit_arrays = []
    for criterion in criteria:
        crit_Ps = find_critical_reps(sep_arrays[0], criterion)
        crit_RBs = find_critical_reps(sep_arrays[1], criterion)
        crit_objs = find_critical_reps(sep_arrays[2], criterion)
        all_crit = find_critical_reps(state, criterion)
        # put them in an array. 
        crit_array = [criterion, crit_Ps, crit_RBs, crit_objs, all_crit]
        crit_arrays.append(crit_array)
    state_crit.append(crit_arrays)
# write all the crit_arrays to file. 
# for state_array in state_crit:
#     for crit_array in state_array:
#         write_array = crit_array[1]+crit_array[2]+crit_array[3]
#         batch = state_list[state_crit.index(state_array)]
#         file_name = crit_array[0]+batch
#         write_crit_reps(write_array, file_name)
# now, sample items from each of the states that meet each criterion and write those to file.
states_sampled = []
for state_array in mem_state_list:
    # for each criterion in criteria, sample 4 items from the state array 10 times. 
    sampled_this_state = []
    for criterion in criteria:
        sampled_reps = []
        for sample in range(10):
            trial_reps = []
            for iteration in range(4):
                # with probability .9, sample from the 100 most recently learned items, otherwise, sample from the entire array of items (i.e., all of crit_array[4]). 
                rand_num = random.random()
                if rand_num <= .9:
                    start_point = 200
                    sampled_item = sample_item_from_state(state_array[start_point:], criterion)
                else:
                    sampled_item = sample_item_from_state(state_array, criterion)
                trial_reps.append(sampled_item[0]) # NOTE: You are appending sample[0] because random.sample() returns a list, so the sample is a one item list containing the sampled dict. 
            sampled_reps.append(trial_reps)
        #batch = state_list[mem_state_list.index(state_array)]
        #file_name = 'sampled_'+criterion+batch
        #write_crit_reps(sampled_reps, file_name)
        sampled_this_state.append(sampled_reps)
    states_sampled.append(sampled_this_state)
#pdb.set_trace()
# next, count the number of sampled relations, RBs, and objects in each state.
# for state in state_crit:
#     print 'STATE: '+str(state_crit.index(state)+1)
#     for sample in state:
#         print 'objects='+str(len(sample[3]))
#         print 'single-place preds='+str(len(sample[2]))
#         print 'relations='+str(len(sample[1]))
#     print '\n\n'
# next, count the number of sampled relations, RBs, and objects in each sampled state.
for state in states_sampled:
    print 'STATE: '+str(states_sampled.index(state)+1)
    num_successes = 0
    for dimension in state:
        successes = 0
        for trial in dimension:
            Ps = [prop for prop in trial if prop['name'] != 'non_exist']
            if len(Ps) >= 3:
                successes+=1
        print str(successes/10.0) + ' successes for dimension' + str(state.index(dimension))
        num_successes += successes
        # Ps = [prop for prop in sample if prop['name'] != 'non_exist']
        # RBs = [prop for prop in sample if (prop['name'] == 'non_exist') and (prop['RBs'][0]['pred_name'] != 'non_exist')]
        # objs = [prop for prop in sample if (prop['name'] == 'non_exist') and (prop['RBs'][0]['pred_name'] == 'non_exist')]
        # print 'objects='+str(len(objs))
        # print 'single-place preds='+str(len(RBs))
        # print 'relations='+str(len(Ps))
    print 'Total correct: ' + str(num_successes/40.0)
    print '\n\n'

# pdb.set_trace()



