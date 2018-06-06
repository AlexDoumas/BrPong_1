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
parameters = [{'prototype_variety': 'so', 'kinds': 1, 'number': 10, 'semantics_per_PO': [10], 'specific_semantics_per_PO': [3], 'place_relation': [2]}]
# finally, set the number of total sematnics.
total_sem = 1000

# create the range of semantics.
sem_list = []
for semantic in range(total_sem):
    sem_name = 'semantic'+str(semantic)
    sem_list.append(sem_name)

# for each type of proposition (i.e., each kind of prototype) you are making, for each kind, select defining semantics for each of its roles.
# initialise the empty array of vital semantics, vital_sem, and the num_taken counter.
vital_sem =[]
num_taken = 0
for prop_type in parameters:
    for kind in range(prop_type['kinds']):
        kind_vital_sem = []
        for i in range(prop_type['place_relation'][0]):
            # select the defining semantics from the head of the semantics list.
            # create a variable called current_num as a proxy to num_taken for use in the loop so that the value of num_taken can be adjusted in the body of the loop itself.
            current_num = num_taken
            role_vital_sem = []
            for j in range(current_num, current_num+prop_type['specific_semantics_per_PO'][0]):
                role_vital_sem.append(sem_list[j])
                num_taken += 1
            kind_vital_sem.append(role_vital_sem)
        vital_sem.append(kind_vital_sem)

# now make the sym_dicts. Use the prototypes in the sym prototypes from the prototypes array to make sym structures.
sym_props = []
analog_counter = 0
prototype_counter = 0
for prop_type in parameters:
    for kind in range(prop_type['kinds']):
        for element in range(prop_type['number']):
            # make a sym dictionary based on the prototype dictionary (specified above).
            new_sym_dict = copy.deepcopy(prototypes[prototype_counter])
            # check what kind of prototype you're using to make the current sym structure.
            if prop_type['prototype_variety'] ==  'so':
                # you're making simple objects, so you need to replace the object_name, and fill in the object_sem and analog.
                # set a counter to count each argument of the to be learned relatons.
                counter = 0
                # for each RB in new_sym_dict, fill in the appropriate name and semantic information.
                for RB in new_sym_dict['RBs']:
                    # name the object.
                    RB['object_name'] += (str(analog_counter)+str(counter)+str(random.random()))
                    # add the vital_sem.
                    RB['object_sem'] = copy.deepcopy(vital_sem[kind][counter])
                    # add the remaining sem.
                    remaining_sem = random.sample(sem_list,(prop_type['semantics_per_PO'][0]-prop_type['specific_semantics_per_PO'][0]))
                    for sem in remaining_sem:
                        RB['object_sem'].append(sem)
                    # update the counter, so that it accesses the correct group of semantics from vital_sem.
                    counter += 1
            elif prop_type['prototype_variety'] ==  'jRB':
                # you're making RB structures, so you need to replace the pred_name and object_name, and fill in the pred_sem, object_sem, , and analog.
                pass
            elif prop_type['prototype_variety'] ==  'fp':
                # you're making full P structures, so you need to replace the pred_names, the obj_names, and the 'name' (i.e., the prop name), and fill in the pred_sem, object_sem, and analog.
                pass
            elif prop_type['prototype_variety'] ==  'hop':
                # you're making higher-order propositions, so you need to replace the pred_names, obj_names, and the 'names' (i.e., the prop names), and fill in the pred_sem, object_sem, and analog.
                pass
            # update the analog information for the new_sym_dict.
            new_sym_dict['analog'] = analog_counter
            # add the new sym_dict to the sym_props.
            sym_props.append(new_sym_dict)
            # update the analog_counter
            analog_counter += 1
    # update the prototype_counter.
    prototype_counter += 1

# now write all the sym_props to a file.
write_file = open('new_sym_file.py', 'w')
write_file.write('simType=\'sym_file\' \nsymProps = ' + str(sym_props))



