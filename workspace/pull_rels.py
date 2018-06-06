# extract some relations from a batch set that meet a set of specific criteria. 

# imports. 
import json
import pdb

# selection dimensions. 
dimensions = ['X', 'Y', 'time']
invs = ['more', 'less', 'same']

# list of files to read memory data from.
#state_list = ['batch_run100', 'batch_run200', 'batch_run300', 'batch_run400', 'batch_run500', 'batch_run600', 'batch_run700', 'batch_run800', 'batch_run900', 'batch_run1000', 'batch_run1100', 'batch_run1200', 'batch_run1300', 'batch_run1400', 'batch_run1500', 'batch_run1600', 'batch_run1700', 'batch_run1800', 'batch_run1900', 'batch_run2000', 'batch_run2100', 'batch_run2200', 'batch_run2300', 'batch_run2400', 'batch_run2500', 'batch_run2600', 'batch_run2700', 'batch_run2800', 'batch_run2900', 'batch_run3000', 'batch_run3100', 'batch_run3200', 'batch_run3300', 'batch_run3400', 'batch_run3500', 'batch_run3600', 'batch_run3700', 'batch_run3800', 'batch_run3900', 'batch_run4000', 'batch_run4100', 'batch_run4200', 'batch_run4300', 'batch_run4400', 'batch_run4500', 'batch_run4600', 'batch_run4700', 'batch_run4800', 'batch_run4900', 'batch_run5000']
state_list = ['batch_run2000']

# for each memory state in state_list find the relations on the specified dimensions.
memory_list = []
for state in state_list:
    # load in the json file.
    myfile = open(state, 'r')
    myfile.seek(0)
    myfile.readline()
    props_master = json.loads(myfile.readline())
    # make a list of all the relations that code a relation for the specified dimensions.
    selected_rels = []
    for prop in props_master:
        # check that it is a relation.
        if prop['name'] != 'non_exist':
            # check that dimension semantics and 'more'/'less'/'same' are in the pred semantics of both RBs. 
            dims1 = [semantic for semantic in prop['RBs'][0]['pred_sem'] if (semantic[0] in dimensions) and (semantic[1]>.9)]
            invs1 = [semantic for semantic in prop['RBs'][0]['pred_sem'] if (semantic[0] in invs) and (semantic[1]>.9)]
            dims2 = [semantic for semantic in prop['RBs'][1]['pred_sem'] if (semantic[0] in dimensions) and (semantic[1]>.9)]
            invs2 = [semantic for semantic in prop['RBs'][1]['pred_sem'] if (semantic[0] in invs) and (semantic[1]>.9)]
            if min(len(dims1), len(dims2), len(invs1), len(invs2)) > 0:
                # add the prop to selected rels.
                selected_rels.append(prop)

# write slected_rels to a new file.
myfile2 = open('rels_for_gen', 'w')
for rel in selected_rels:
    myfile2.write(str(rel)+'\n')



