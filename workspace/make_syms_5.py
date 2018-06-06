# code to build sym file for a simple batch run using prototyped sym structures.

# imports.
import random, copy, pdb

# create the prototype sym object (e.g., objects in isolation, RBs, whole props, etc.).
#####################################################################################################
# SOME EXAMPLES:
# prototype for simple objects: {'name': 'non_exist', 'RBs': [{'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj', 'object_sem': None, 'P': 'non_exist'}, {'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj', 'object_sem': None, 'P': 'non_exist'}], 'set': 'memory', 'analog': None} # you need to replace the object_name, and fill in the object_sem and analog. 
# prototype for just RBs: {'name': 'non_exist', 'RBs': [{'pred_name': 'pred', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj', 'object_sem': [], 'P': 'non_exist'}, {'pred_name': 'pred', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj', 'object_sem': [], 'P': 'non_exist'}], 'set': 'driver', 'analog': None} # you need to replace the pred_name and object_name, and fill in the pred_sem, object_sem, , and analog. 
# prototype for full propositions: {'name': 'p', 'RBs': [{'pred_name': 'pred', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj', 'object_sem': [], 'P': 'non_exist'}, {'pred_name': 'pred', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj', 'object_sem': [], 'P': 'non_exist'}], 'set': 'memory', 'analog': None} # you need to replace the pred_names, the obj_names, and the 'name' (i.e., the prop name), and fill in the pred_sem, object_sem, and analog. 
# prototype for higher-order propositions: {'name': 'p_lower', 'RBs': [{'pred_name': 'pred', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj', 'object_sem': [], 'P': 'non_exist'}, {'pred_name': 'pred', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj', 'object_sem': [], 'P': 'non_exist'}], 'set': 'driver', 'analog': None}, {'name': 'p_higher', 'RBs': [{'pred_name': 'knower', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj', 'object_sem': [], 'P': 'non_exist'}, {'pred_name': 'pred', 'pred_sem': [], 'higher_order': True, 'object_name': 'non_exist', 'object_sem': [], 'P': 'p_lower'}], 'set': 'driver', 'analog': None} # you need to replace the pred_names, obj_names, and the 'names' (i.e., the prop names), and fill in the pred_sem, object_sem, and analog.
#####################################################################################################
prototypes=[{'name': 'non_exist', 'RBs': [{'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj', 'object_sem': None, 'P': 'non_exist'}, {'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj', 'object_sem': None, 'P': 'non_exist'}], 'set': 'memory', 'analog': None}]

# create a dict with parameters for each prototype you've specified directly above.
# prototype_variety = what kind of prototype structure above are the given parameters applicable to? 'so'=simple_object; 'jRB'=just_RBs; 'fp'=full_propositions; 'hop'=higher_order_propositions.
# kinds = how many varieties of propositions (each built from the prototype).
# number = how many of each type.
# total_sem = the total number of semantics.
# semantics_per_PO = the number of semantics per PO.
# specific_semantics_per_PO = the number of specific semantics for each PO.
# place_relation = how many places are the real world relations that the system should learn.
parameters = [{'prototype_variety': 'so', 'kinds': 1, 'number': 100, 'semantics_per_PO': [16], 'place_relation': [2]}]
# finally, set the number of total sematnics.
total_sem = 10000

# create the range of semantics.
sem_list = []
for semantic in range(total_sem):
    sem_name = 'semantic'+str(semantic)
    sem_list.append(sem_name)

# create list of pairs of values from 1-10. 
# create 20 different, and 10 same.
pair_list = []
for i in range(20):
    # pick 2 different values between 1 and 10. 
    first = round(random.random()*9)+1
    second = round(random.random()*9)+1
    while second == first:
        second = round(random.random()*9)+1
    new_pair = [first,second]
    pair_list.append(new_pair)
for i in range(10):
    # pick 2 different values between 1 and 10. 
    first = round(random.random()*9)+1
    new_pair = [first,first]
    pair_list.append(new_pair)
dimensions = ['size','height', 'width', 'depth']

# now make the sym_dicts. Use the prototypes in the sym prototypes from the prototypes array to make sym structures.
sym_props = []
analog_counter = 0
prototype_counter = 0
for prop_type in parameters:
    for kind in range(prop_type['kinds']):
        for element in range(prop_type['number']):
            # check what kind of prototype you're using to make the current sym structure.
            if prop_type['prototype_variety'] == 'so':
                # you're making simple objects, so you need to replace the object_name, and fill in the object_sem and analog.
                # for each RB in new_sym_dict, fill in the appropriate name and semantic information.
                # make a sym dictionary based on the prototype dictionary (specified above).
                new_sym_dict = copy.deepcopy(prototypes[prototype_counter])
                # set a counter to count each argument of the to be learned relatons.
                counter = 0
                # select 1 same and 1 different dimension. 
                dims = random.sample(dimensions, 2)
                # select one to be different and the other to be same. 
                random.shuffle(dims)
                # select a value for same. 
                same_val = round(random.random()*9)+1
                # select two values for different. 
                dif_val1 = round(random.random()*9)+1
                dif_val2 = dif_val1
                while dif_val2 == dif_val1:
                    dif_val2 = round(random.random()*9)+1
                # make the RBs. 
                counter = 1
                for RB in new_sym_dict['RBs']:
                    # name the object.
                    RB['object_name'] += (str(analog_counter)+str(counter)+str(random.random()))
                    # add all the dimensions. 
                    vital_sem = []
                    # add the vital semantics. 
                    vital_sem.append([dims[0], 1, dims[0], 'nil', 'state'])
                    vital_sem.append([dims[0]+str(same_val), 1, dims[0], same_val, 'value'])
                    vital_sem.append([dims[1], 1, dims[1], 'nil', 'state'])
                    if counter%2 != 0:
                        vital_sem.append([dims[1]+str(dif_val1), 1, dims[1], dif_val1, 'value'])
                    else:
                        vital_sem.append([dims[1]+str(dif_val2), 1, dims[1], dif_val2, 'value'])
                    RB['object_sem'] = vital_sem
                    # add the remaining sem.
                    remaining_sem = random.sample(sem_list,(prop_type['semantics_per_PO'][0]-4))
                    for sem in remaining_sem:
                        RB['object_sem'].append(sem)
                    counter += 1
                # update the analog information for the new_sym_dict.
                new_sym_dict['analog'] = analog_counter
                # add the new sym_dict to the sym_props.
                sym_props.append(new_sym_dict)
                # update the analog_counter
                analog_counter += 1
            elif prop_type['prototype_variety'] ==  'jRB':
                # you're making RB structures, so you need to replace the pred_name and object_name, and fill in the pred_sem, object_sem, , and analog.
                pass
            elif prop_type['prototype_variety'] ==  'fp':
                # you're making full P structures, so you need to replace the pred_names, the obj_names, and the 'name' (i.e., the prop name), and fill in the pred_sem, object_sem, and analog.
                pass
            elif prop_type['prototype_variety'] ==  'hop':
                # you're making higher-order propositions, so you need to replace the pred_names, obj_names, and the 'names' (i.e., the prop names), and fill in the pred_sem, object_sem, and analog.
                pass
    # update the prototype_counter.
    prototype_counter += 1

# now write all the sym_props to a file.
write_file = open('new_sym_file.py', 'w')
write_file.write('simType=\'sim_file\' \nsymProps = ' + str(sym_props))



