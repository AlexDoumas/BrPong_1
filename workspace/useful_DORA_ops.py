# useful code for running DORA straight from the network object without invoking the terminal GUI. 

# imports. 
import random, json
import buildNetwork
import basicRunDORA
import pdb

# set the parameters. 
parameters = {
    'asDORA': False, 
    'gamma': 0.3, 
    'delta': 0.1, 
    'eta': 0.9, 
    'HebbBias': 0.5, 
    'bias_retrieval_analogs': True, 
    'use_relative_act': True, 
    'run_order': ['cdr', 'selectTokens', 'r', 'wp', 'm', 'p', 'f', 's', 'c'], 
    'run_cyles': 5000, 
    'write_on_iteration': 100, 
    'firingOrderRule': 'random', 
    'strategic_mapping': False,
    'ignore_object_semantics': False, 
    'ignore_memory_semantics': True, 
    'dim_list': [], 
    'exemplar_memory': False, 
    'recent_analog_bias': True, 
    'lateral_input_level': 1, 
    'screen_width': 1200, 'screen_height': 700, 'doGUI': True, 'GUI_update_rate': 10, 'starting_iteration': 0}

# to load a sym file. 
#f = open('file_name', 'r')
#f.seek(0)
#exec (f.readline())
#symProps = json.loads(f.readline())
# OR, just set symProps equal to a dict. 
#symProps = []

# initialise memory. 
memory = buildNetwork.initializeMemorySet()
# interpret the sym file. 
mysym = buildNetwork.interpretSymfile(symProps)
# build the network object with memory. 
memory = basicRunDORA.dataTypes.memorySet()
memory = buildNetwork.buildTheNetwork(mysym[0], memory)
#memory = buildNetwork.buildTheNetwork(symProps, memory)
network = basicRunDORA.runDORA(memory, parameters)
# make sure the driver and recipient are all set up.
network.memory = basicRunDORA.clearDriverSet(network.memory)
network.memory = basicRunDORA.clearRecipientSet(network.memory)
network.memory = basicRunDORA.findDriverRecipient(network.memory)

# DORA operations run operatons. 
network.do_retrieval()
network.do_map()
network.do_entropy_ops_between()
network.do_entropy_ops_within(pred_only=True)
pred_ok = basicRunDORA.predication_requirements(network.memory)
if pred_ok:
    network.do_predication()
form_ok = basicRunDORA.rel_form_requirements(network.memory)
if form_ok:
    network.do_rel_form()
gen_ok = basicRunDORA.rel_gen_requirements(network.memory)
if gen_ok:
    network.do_rel_gen()
schema_ok = basicRunDORA.schema_requirements(network.memory)
if schema_ok:
    network.do_schematization()

# put an analog in the driver.
analog_num = network.memory.analogs.index(analog)
network.memory = basicRunDORA.add_tokens_to_set(network.memory, analog_num, 'analog', 'driver')
# clear the contents of driver and recipient. 
network.memory = basicRunDORA.clearDriverSet(network.memory)
network.memory = basicRunDORA.clearRecipientSet(network.memory)
network.memory = basicRunDORA.findDriverRecipient(network.memory)

# DORA extra operations. 
# enter the view mode in terminal to see network state and mappings. 
basicRunDORA.DORA_GUI.term_network_display(network.memory, 'driver') # show driver. 
basicRunDORA.DORA_GUI.term_network_display(network.memory, 'recipient') # show recipient. 
basicRunDORA.DORA_GUI.term_network_display(network.memory, 'memory') # show memory. 
basicRunDORA.DORA_GUI.term_map_display(network.memory) # show mappings. 
# clear mappings, madeUnits, inferences, and newSet.
network.memory = basicRunDORA.reset_inferences(network.memory)
network.memory = basicRunDORA.reset_maker_made_units(network.memory)
network.memory = basicRunDORA.reset_mappings(network.memory)
network.memory = basicRunDORA.update_Names_nil(network.memory)
network.memory = basicRunDORA.indexMemory(network.memory)
network.memory = basicRunDORA.initialize_memorySet(network.memory)
network.memory.newSet.Ps, network.memory.newSet.RBs, network.memory.newSet.POs = [], [], []
# update the names of items in memory.
network.memory = basicRunDORA.update_Names_nil(network.memory)
# save the network state. 
basicRunDORA.write_memory_to_symfile(network.memory, 'new_name')




