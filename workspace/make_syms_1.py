# code to build sym file for a simple batch run using prototyped sym structures.

# imports.
import random, copy, pdb

# create the prototype sym object (e.g., objects in isolation, RBs, whole props, etc.).
#prototype={'name': 'non_exist', 'RBs': [{'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj', 'object_sem': None, 'P': 'non_exist'}], 'set': 'driver', 'analog': None}
prototype={'name': 'non_exist', 'RBs': [{'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj', 'object_sem': None, 'P': 'non_exist'}, {'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj', 'object_sem': None, 'P': 'non_exist'}], 'set': 'memory', 'analog': None}

kinds = 4 # how many varieties of propositions (each built from the prototype).
number = 10 # how many of each type.
total_sem = 1000 # the total number of semantics.
semantics_per_PO = 10 # the number of semantics per PO.
specific_semantics_per_PO = 3 # the number of specific semantics for each PO.
place_relation = 2 # how many places are the real world relations that the system should learn.

# create the range of semantics
sem_list = []
for semantic in range(total_sem):
    sem_name = 'semantic'+str(semantic)
    sem_list.append(sem_name)

# for each kind, select defining semantics for each of its roles.
#vital_sem =[]
#for kind in range(kinds):
#    kind_vital_sem = []
#    for i in range(place_relation):
#        # select the defining semantics.
#        chosen_sem = random.sample(sem_list, 3)
#        kind_vital_sem.append(chosen_sem)
#    vital_sem.append(kind_vital_sem)
#pdb.set_trace()

# for each kind, select defining semantics for each of its roles.
vital_sem =[]
num_taken = 0
for kind in range(kinds):
    kind_vital_sem = []
    for i in range(place_relation):
        # select the defining semantics from the head of the semantics list.
        # create a variable called current_num as a proxy to num_taken for use in the loop so that the value of num_taken can be adjusted in the body of the loop itself.
        current_num = num_taken
        role_vital_sem = []
        for j in range(current_num, current_num+specific_semantics_per_PO):
            role_vital_sem.append(sem_list[j])
            num_taken += 1
        kind_vital_sem.append(role_vital_sem)
    vital_sem.append(kind_vital_sem)

# now make the sym_dicts.
sym_props = []
analog_counter = 0
for kind in range(kinds):
    for element in range(number):
        # make a sym dictionary based on the prototype dictionary (specified above).
        new_sym_dict = copy.deepcopy(prototype)
        # set a counter to count each argument of the to be learned relatons.
        counter = 0
        # for each RB in new_sym_dict, fill in the appropriate name and semantic information.
        for RB in new_sym_dict['RBs']:
            # name the object.
            RB['object_name'] += (str(analog_counter)+str(counter)+str(random.random()))
            # add the vital_sem.
            RB['object_sem'] = copy.deepcopy(vital_sem[kind][counter])
            # add the remaining sem.
            remaining_sem = random.sample(sem_list,(semantics_per_PO-specific_semantics_per_PO))
            for sem in remaining_sem:
                RB['object_sem'].append(sem)
            # update the counter, so that it accesses the correct group of semantics from vital_sem.
            counter += 1
        # update the analog information for the new_sym_dict.
        new_sym_dict['analog'] = analog_counter
        # add the new sym_dict to the sym_props.
        sym_props.append(new_sym_dict)
        # update the analog_counter
        analog_counter += 1

# now write all the sym_props to a file.
write_file = open('new_sym_file.py', 'w')
write_file.write('simType=\'sym_file\' \nsymProps = ' + str(sym_props))


