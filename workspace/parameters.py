parameters = {
    'firingOrderRule': 'random', 
    'asDORA': True, 
    'gamma': 0.3, 
    'delta': 0.1, 
    'eta': 0.9, 
    'HebbBias': 0.5, 
    'lateral_input_level': 1, 
    'strategic_mapping': False,
    'ignore_object_semantics': False, 
    'ignore_memory_semantics': False, 
    'exemplar_memory': False, # should use exemplar rule for memories and form a new exemplar anytime I learn (i.e., modify a token or learn new tokens) in WM. 
    'recent_analog_bias': True, # should I be biased towards selecting recently learned analogs during learning? 
    'bias_retrieval_analogs': True, 
    'use_relative_act': True, 
    'run_order': ['cdr', 'selectTokens', 'r', 'm', 'b', 'w', 'wp', 'p', 'f', 's', 'c'], # why did I put 'b' after 'm'? 
    'run_cyles': 15, 
    'doGUI': True, 
    'screen_width': 1200, 
    'screen_height': 700, 
    'GUI_update_rate': 10, 
    'starting_iteration': 0, 
    'write_on_iteration': 10}


