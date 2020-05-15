# code to create formated sym files organised by proposition for insertion of new objects. 
# you need to return a text file wherein each prop is demarcated with each field on a new line, and semantics organised by weight.

# imports.
import random, json

#######################################################################
# FUNCTIONS
#######################################################################
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

# function to write memory state in a formated form to a file. 
def write_formatted_mem_state(state, only_Ps, only_RBsPs):
    # open the state_list as a dictionary.
    mem_state_list = load_states([state])
    # create a string that includes each item in the memory state. 
    memory_list = ''
    for prop in mem_state_list[0]:
        skip = False
        if only_Ps:
            if prop['name'] == 'non_exist':
                skip = True
        elif only_RBsPs:
            for myRB in prop['RBs']:
                if myRB['pred_name'] == 'non_exist':
                    skip = True
        # start the dictionary item.
        if not skip:
            memory_list += '{'
            # write the name, set, and analog.
            memory_list = memory_list + '\'name\': ' + '\'' + prop['name'] + '\'' +',\n'
            memory_list = memory_list + ' ' + '\'set\': ' + '\'' + prop['set'] + '\'' + ',\n'
            memory_list = memory_list + ' ' + '\'analog\': ' + str(prop['analog']) +',\n'
            # write the RBs.
            memory_list = memory_list + ' ' + '\'RBs\': ['
            for myRB in prop['RBs']:
                # print the pred_name and pred_sem and higher_order. 
                memory_list = memory_list + '\n     {\'pred_name\': ' + '\'' + myRB['pred_name'] + '\',\n'
                memory_list = memory_list + '      \'pred_sem\': ' + '['
                for semantic in myRB['pred_sem']:
                    memory_list = memory_list + '\n          ' + str(semantic) + ','
                memory_list = memory_list + '],\n'
                memory_list = memory_list + '      \'higher_order\': ' + str(myRB['higher_order']) + ',\n'
                # print the object_name and object_sem. 
                memory_list = memory_list + '      \'object_name\': ' + '\'' + myRB['object_name'] + '\',\n'
                memory_list = memory_list + '      \'object_sem\': ' + '['
                for semantic in myRB['object_sem']:
                    memory_list = memory_list + '\n          ' + str(semantic) + ','
                memory_list = memory_list + '],\n'
                # print the P field.
                memory_list = memory_list + '     \'P\': ' + '\'' + myRB['P'] + '\'},'
            # and finish the proposition.
            memory_list = memory_list[:-1]
            memory_list = memory_list + ']},\n\n'
    # write memory_list to a file. 
    file_name = 'formatted_' + state
    with open(file_name, 'w') as f:
        f.write(memory_list)

#######################################################################
# MAIN BODY. 
#######################################################################

# set the state list. 
state_list = ['sampled_sizebatch_run500', 'sampled_sizebatch_run1000', 'sampled_sizebatch_run1500']

# for each memort state, create a text file with each proposition (or element in the mem_state_list) numbered and separated by a blank line, and each dictionary element of the proposition listed on it's own line. 
for state in state_list:
    # write the state to a formatted form.
    write_formatted_mem_state(state, False, False)






