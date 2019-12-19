# entropy same/diff/more/less.
# operations for DORA's same/different/more/less detection using simple entropy. Find instances of same/different and more/less using entropy.
# Basic idea (same/diff): For same/different, compare or over-lay the two representations. Create a DORAese sematnic signal (i.e., shared units have greater activation than unshared units). Calculate the error of the DORAese semantic pattern to a pattern with no entropy (i.e., all the active semantics have activation of 1.0). The extent of the error is a measure of difference, with low (or zero) error corresponding to 'same', and higher error corresponding to 'different'.
# Basic idea (more/less): For more/less the idea is very similar to same/diff. If you have two instances coded with magnitude, and the magnitude corresponds to a level of neural firing (more firing for more magnitude), identifying more and less is simply comparing or over-laying the two representations of magnitude, and computing an error signal. The higher the error signal the greater the difference, and the item that is over-activated by the error signal (i.e., the error signal shows too much activation) is the 'more' item, and the under-activated item (i.e., the error signal shows too little activation) is the 'less' item.

# imports.
import dataTypes
import operator, random, pdb

# function to calculate over-all same/diff from entropy.
def ent_overall_same_diff(semantic_array):
    # check semantic array and calculate a similarity score as ratio of unshared to total features. 
    error_array = []
    act_array = []
    for semantic in semantic_array:
        # if activation is greater than 0.1, add activation to act_array and add 1.0 to error_array. 
        if semantic.act > 0.1:
            act_array.append(semantic.act)
            error_array.append(1.0)
    # calcuate the error by subtracting act_array from error_array.
    # NOTE: You can do this operation either with numpy (turning the lists into arrays) or with map and operator.
    #a_error_array = numpy.array(error_array)
    #a_act_array = numpy.array(act_array)
    #diff_array = a_error_array - a_act_array
    diff_array = list(map(operator.sub, error_array, act_array))
    sum_diff = sum(diff_array)
    sum_act = sum(act_array)
    similarity_ratio = float(sum_diff)/float(sum_act)
    # return the similarity_ratio.
    return similarity_ratio

# function to learn tunings to the similarity_ratio output above. Takes as input a list of similarity_ratios to learn tunings for, an argument, num_nodes, indicating the number of nodes the network should have, and an argument, tune_precision, indicating how precise the tunings should become.
def learn_similarity_tunings(similarity_ratios, num_nodes, tune_precision):
    # make a network of num_nodes.
    simNet = dataTypes.similarityNet()
    winning_nodes = []
    for i in range(num_nodes):
        simNet.nodes.append(dataTypes.basicSimNode())
    # run the similarity network.
    # set gamma and delta.
    gamma, delta = 0.3, 0.1
    for similarity_ratio in similarity_ratios:
        go_on = True
        while go_on:
            # update the inputs of all nodes.
            simNet.update_inputs(similarity_ratio)
            # for DEBUGGING.
            #for node in simNet.nodes:
            #    print str(node.input)
            # update the activations of all nodes.
            simNet.update_acts(gamma, delta)
            # tune the winning node.
            simNet.tune_network(similarity_ratio)
            # if the tuning on the winning node (i.e., the range of that node's threshold) is less than tune_precision, set go_on flag to False, and move to the next similarity_ratio to train.
            # find the winning_node.
            high_act = 0.0
            winning_node = None
            for node in simNet.nodes:
                if node.act > high_act:
                    high_act = node.act
                    winning_node = node
            # check the precision of the tuning for that node.
            if winning_node:
                # for DEBUGGING.
                print 'sim_ratio=',str(similarity_ratio)
                print 'high_act=',str(high_act)
                print 'winning_node=',str(simNet.nodes.index(winning_node))
                print ''
                if (winning_node.threshold[1]-winning_node.threshold[0]) <= tune_precision:
                    go_on = False
                    winning_nodes.append(winning_node)
    # return the similarityNetwork.
    return simNet, winning_nodes

# function that calculates specific same/diff semantics from entropy.
def ent_specific_semantics_same_diff(semantics):
    # take in a semantic array, check it, and return a list of all shared features (semantics with activations near 1; the same stuff), and a list of all unshared features (semantics with activations near .5; the different stuff).
    # initialise empty arrays for shared and unshared semantics.
    shared = []
    unshared = []
    # iterate semantics, and put any semantics with act >= 0.9 in shared, and any sematnics with act between 0.4 and 0.6 in unshared.
    for semantic in semantics:
        if semantic.act >= 0.9:
            shared.append(semantic)
        elif 0.4 <= semantic.act <= 0.6:
            unshared.append(semantic)
    # return the shared and unshared arrays.
    return shared, unshared

# function that specifies to which PO each unshared semantic is most strongly connected.
def which_semantic_unshared(myPO1, myPO2, unshared):
    # take in the 2 POs, PO1 and PO2, and the list of unshared semantics. return two lists of unshared semantics, the first specifying the unshared semantics that are most strongly connected to PO1, and the second specifying the unshared semantics that are most strongly connected to PO2.
    # initialise empty arrays, one for the unshared semantics belonging to PO1 and the other for the unshared semantics belonging to PO2.
    unsharedPO1 = []
    unsharedPO2 = []
    # iterate through the unshared semantics and sort them into the arrays for PO1 and PO2.
    for semantic in unshared:
        for link in semantic.myPOs:
            if myPO1 is link.myPO:
                if link.weight >= 0.4 and semantic.act <= 0.6:
                    unsharedPO1.append(semantic)
            elif myPO2 is link.myPO:
                if link.weight >= 0.4 and semantic.act <= 0.6:
                    unsharedPO2.append(semantic)
    # return the arrays of sorted unshared semantics.
    return unsharedPO1, unsharedPO2

# function calculates more/less/same from two codes of extent based on entropy and competion.
def ent_magnitudeMoreLessSame(extent1, extent2):
    # take two representations of extent, and have them compete.
    # first build a simple entropyNet with the extents as lower-level nodes.
    entropyNet = dataTypes.entropyNet()
    for i in range(max(extent1,extent2)):
        new_sem = dataTypes.basicEntNode(False, True, [])
        entropyNet.inputs.append(new_sem)
    # and now make an object attached to each extent as a higher-level (output) node.
    # first make the nodes.
    extent_node1 = dataTypes.basicEntNode(True, False, [])
    extent_node2 = dataTypes.basicEntNode(True, False, [])
    entropyNet.outputs = [extent_node1, extent_node2]
    # connect each node to the correct extent semantics.
    for i in range(extent1):
        # create a link between the ith input unit and extent_node1.
        new_connection = dataTypes.basicLink(extent_node1, entropyNet.inputs[i], 1.0)
        entropyNet.connections.append(new_connection) 
        # add the connection to the higher and lower nodes it links.
        extent_node1.connections.append(new_connection)
        entropyNet.inputs[i].connections.append(new_connection)
    for i in range(extent2):
        # create a link between the ith input unit and extent_node2.
        new_connection = dataTypes.basicLink(extent_node2, entropyNet.inputs[i], 1.0)
        entropyNet.connections.append(new_connection)
        # add the connection to the higher and lower nodes it links.
        extent_node2.connections.append(new_connection)
        entropyNet.inputs[i].connections.append(new_connection)
    # set activations of all extent nodes to 1.0.
    for node in entropyNet.inputs:
        node.act = 1.0
    # until the network settles (i.e., only one output node is active for 3 iterations), keep running.
    unsettled = 0
    iterations = 0
    # set gamma and delta.
    gamma, delta = 0.3, 0.1
    delta_outputs_previous = 0.0
    settled = 0
    while settled < 3:
        # update the inputs to the output units.
        for node in entropyNet.outputs:
            node.clear_input()
            node.update_input(entropyNet)
        # update the activations of the output units.
        for node in entropyNet.outputs:
            node.update_act(gamma, delta)
        # FOR DEBUGGING: print inputs and outputs of all nodes.
        #pdb.set_trace()
        print 'iteration = ', iterations
        print 'INPUTS'
        for node in entropyNet.inputs:
            print node.input, ', ', node.act
        print 'OUTPUTS'
        for node in entropyNet.outputs:
            print node.input, ', ', node.act
        # check for settling. if the delta_outputs has not changed, add 1 to settled, otherwise, clear unsettled.
        delta_outputs = entropyNet.outputs[0].act-entropyNet.outputs[1].act
        print delta_outputs == delta_outputs_previous
        print settled
        print ''
        if delta_outputs == delta_outputs_previous:
            settled += 1
        else:
            settled = 0
        delta_outputs_previous = delta_outputs
        iterations += 1
    # the active output node is 'more', and the inactive output node is 'less', or the two extents are equal.
    if entropyNet.outputs[0].act > entropyNet.outputs[1].act:
        more = extent1
        less = extent2
        same_flag = False
    elif entropyNet.outputs[0].act < entropyNet.outputs[1].act:
        more = extent2
        less = extent1
        same_flag = False
    else: # the two extents are equal.
        more = 'NONE'
        less = 'NONE'
        same_flag = True
    # return more, less, a flag indicating whether the values are the same (called same_flag), and the number of iterations to settling.
    return more, less, same_flag, iterations

# function to learn basic magnitude comparison circuit that will support the output of the ent_magnitudeMoreLessSame() function. It takes as input the number of learning trials you want to give it. 
def learn_mag_circuit(learning_trials):
    # build the initial network. This network consists of a unit marking PO units settling, three time-in-comparison-cycle units (two connected to the unit makring PO settling, the other a gating unit connected to the PO units and active when both POs are active), and three MLS semantics (just semantic units randomly connected to the time-in-comparison-cycle units that will come to code invariant "more", "less", and "same" after learning). 
    settling_unit = dataTypes.basicTimingNode('settling', [], [], [])
    time_unit1, time_unit2 = dataTypes.basicTimingNode('A', [], [], []), dataTypes.basicTimingNode('B', [], [], [])
    time_unit3 = dataTypes.basicGateNode('gate', [], [])
    Local_inhib = dataTypes.localInhibitor()
    semantic1, semantic2, semantic3 = dataTypes.MLS_sem('semantic1', [], []), dataTypes.MLS_sem('semantic2', [], []), dataTypes.MLS_sem('semantic3', [], [])
    # set a POs flag indicating whether both POs are active after settling (to be used in learning magnitude vs. sameness; 1.0==both POs active after settling, 0.0==only one PO is active after settling). 
    POs = 0.0
    # create links between settling unit and timing units. Weights are random values between .5 and 1. 
    link1 = dataTypes.basicLink(settling_unit, time_unit1, 0.8)
    settling_unit.lower_connections.append(link1)
    time_unit1.higher_connections.append(link1)
    link2 = dataTypes.basicLink(settling_unit, time_unit2, 0.5)
    settling_unit.lower_connections.append(link2)
    time_unit2.higher_connections.append(link2)
    time_unit3.input_nodes.append(POs)
    # create links between timing units and semantics. 
    link3, link4, link5 = dataTypes.basicLink(time_unit1, semantic1, .5), dataTypes.basicLink(time_unit1, semantic2, .2), dataTypes.basicLink(time_unit1, semantic3, .2)
    time_unit1.lower_connections.append(link3)
    time_unit1.lower_connections.append(link4)
    time_unit1.lower_connections.append(link5)
    semantic1.higher_connections.append(link3)
    semantic2.higher_connections.append(link4)
    semantic3.higher_connections.append(link5)
    link6, link7, link8 = dataTypes.basicLink(time_unit2, semantic1, .2), dataTypes.basicLink(time_unit2, semantic2, .5), dataTypes.basicLink(time_unit2, semantic3, .2)
    time_unit2.lower_connections.append(link6)
    time_unit2.lower_connections.append(link7)
    time_unit2.lower_connections.append(link8)
    semantic1.higher_connections.append(link6)
    semantic2.higher_connections.append(link7)
    semantic3.higher_connections.append(link8)
    link9, link10, link11 = dataTypes.basicLink(time_unit3, semantic1, .2), dataTypes.basicLink(time_unit3, semantic2, .2), dataTypes.basicLink(time_unit3, semantic3, .5)
    time_unit3.output_nodes.append(link9)
    time_unit3.output_nodes.append(link10)
    time_unit3.output_nodes.append(link11)
    semantic1.higher_connections.append(link9)
    semantic2.higher_connections.append(link10)
    semantic3.higher_connections.append(link11)
    # finally, set up lateral connections. These are not established by links, but rather any nodes in the same layer are placed in one-another's .lateral_connections field. Timing units and MLS semantics are all laterally inhibitory. 
    time_unit1.lateral_connections.append(time_unit2)
    time_unit1.lateral_connections.append(time_unit3)
    time_unit2.lateral_connections.append(time_unit1)
    time_unit2.lateral_connections.append(time_unit3)
    semantic1.lateral_connections.append(semantic2)
    semantic1.lateral_connections.append(semantic3)
    semantic2.lateral_connections.append(semantic1)
    semantic2.lateral_connections.append(semantic3)
    semantic3.lateral_connections.append(semantic1)
    semantic3.lateral_connections.append(semantic2)
    # put the units in arrays. 
    time_units = [time_unit1, time_unit2]
    gate_units = [time_unit3]
    MLS_semantics = [semantic1, semantic2, semantic3]
    # set gamma and delta for leaky integrator activation function. 
    gamma, delta = 0.3, 0.1
    # start the training process. 
    for train_instance in range(learning_trials):
        # is this a trial when both POs are active or not? 
        rand_num = random.random()
        if rand_num > .5:
            same_flag = False
            gate_units[0].input_nodes[0] = 0.0
        else:
            same_flag = True
            gate_units[0].input_nodes[0] = 1.0
        # activate unit indicating settling. 
        settling_unit.act = 1.0
        # for n iterations, until the LI fires, run the network. 
        for iteration in range(110):
            # three units (marking time-in-comparison-cycle) compete to become active. 
            # update the input of time-in-cycle and semantic units. 
            for unit in time_units:
                unit.update_input()
            for unit in gate_units:
                unit.update_input()
            for unit in MLS_semantics:
                unit.update_input()
            # get max_sem_input. 
            max_sem_input = 0.0
            for semantic in MLS_semantics:
                if semantic.input > max_sem_input:
                    max_sem_input = semantic.input
            # subtractive normalisation. 
            for semantic in MLS_semantics:
                if semantic.input < max_sem_input:
                    semantic.input -= max_sem_input
            # then updat max_sem_input for divisive normalisation. 
            for semantic in MLS_semantics:
                semantic.set_max_sem_input(max_sem_input)
            # update the activation and clear the input of time-in-cycle and semantic units. 
            for unit in time_units:
                unit.update_act(gamma, delta)
                print 'input = ', str(unit.input), '\tact = ', str(unit.act), '\n'
                unit.clear_input()
            for unit in gate_units:
                unit.update_act()
                unit.clear_input()
            for unit in MLS_semantics:
                unit.update_act()
                print unit.name, ' ', str(unit.act)
                unit.clear_input()
            # update weights from time-in-comparison-cycle units to MLS semantics if iteration >= 3. 
            if iteration >= 3:
                for unit in time_units:
                    unit.adjust_links()
                for unit in gate_units:
                    unit.adjust_links()
        # after n iterations, if same_flag is False, then fire the local inhibitor, which inhibits time-in-comparison-cycle units and MLS semantics. 
        if not same_flag:
            active_unit = None
            max_act = 0.0
            for unit in time_units:
                if unit.act > max_act:
                    active_unit = unit
            active_unit.time_since_fired = 1
        for unit in time_units:
            unit.clear_inputandact()
        for semantic in MLS_semantics:
            semantic.clear_all()
        # for n further iterations, run the network. 
        for iteration in range(110):
            # three units (marking time-in-comparison-cycle) compete to become active. 
            # update the input of time-in-cycle and semantic units. 
            for unit in time_units:
                unit.update_input()
            for unit in gate_units:
                unit.update_input()
            for unit in MLS_semantics:
                unit.update_input()
            # get max sem input. 
            max_sem_input = 0.0
            for semantic in MLS_semantics:
                if semantic.input > max_sem_input:
                    max_sem_input = semantic.input
            # subtractive normalisation. 
            for semantic in MLS_semantics:
                if semantic.input < max_sem_input:
                    semantic.input -= max_sem_input
            # then update max_sem_input for divisive normalisation. 
            for semantic in MLS_semantics:
                semantic.set_max_sem_input(max_sem_input)
            # update the activation and clear the input of time-in-cycle and semantic units. 
            for unit in time_units:
                unit.update_act(gamma, delta)
                print 'input = ', str(unit.input), '\tact = ', str(unit.act), '\n'
                unit.clear_input()
            for unit in gate_units:
                unit.update_act()
                unit.clear_input()
            for unit in MLS_semantics:
                unit.update_act()
                print unit.name, ' ', str(unit.act)
                unit.clear_input()
            # update weights from time-in-comparison-cycle units to MLS semantics if iteration >= 3. 
            if iteration >= 3:
                for unit in time_units:
                    unit.adjust_links()
                for unit in gate_units:
                    unit.adjust_links()
        # after n iterations, end the learning cycle and clear all units. 
        for unit in time_units:
            unit.clear_all()
        for unit in gate_units:
            unit.clear_all()
        for unit in MLS_semantics:
            unit.clear_all()
    # END. The semantic unit connected to the time-in-comparison-cycle unit that fires first with activation to the settling unit is the "more" semantic, the semantic unit connected to the time-in-comparison-cycle unit that fires second with activation to the settling unit is the "less" semantic, and the semantic unit connected to the gating time-in-comparison-cycle unit is the "same" semantic. 
    # print settling unit's connections.
    for link in settling_unit.lower_connections:
        print 'Settling unit to ', link.mylowernode.name, ' weight = ', str(link.weight), '\n'
    print '\n'
    # print timing units' connections. 
    for unit in time_units:
        for link in unit.lower_connections:
            print unit.name, ' to ', link.mylowernode.name, ' weight = ', str(link.weight), '\n'
    print '\n'
    # print gating unit's connections. 
    for link in gate_units[0].output_nodes:
        print gate_units[0].name, ' to ', link.mylowernode.name, ' weight = ', str(link.weight), '\n'
    print '\n'

# function to print state of the network for use with learn_mag_circuit_neural() function directly below. 
def print_net(Enodes, Anodes, semantics):
    # print the state of all the nodes in the network. 
    for Enode in Enodes:
        print(Enode.name, '.input = ', str(Enode.input), ' ; .act = ', str(Enode.act), ' ; thresh = ', Enode.threshold, '\n')
    for Anode in Anodes:
        print(Anode.name, '.input = ', str(Anode.input), ' ; .act = ', str(Anode.act), '\n')
    for semantic in semantics:
        print(semantic.name, '.input = ', str(semantic.input), ' ; .act = ', str(semantic.act), '\n')
    print('\n')
    for link in Links:
        print('Weight between ', link.myhighernode.name, ' and ', link.mylowernode.name, ' = ', str(link.weight))

# function to learn basic magnitude comparison circuit that will support the output of the ent_magnitudeMoreLessSame() function in a more neural manner. It takes as input the number of learning trials you want to give it. 
def learn_mag_circuit_neural(learning_trials):
    # make the E nodes. 
    Enode1 = dataTypes.reg_E_Node('E1', [], [], [])
    Enode2 = dataTypes.reg_E_Node('E2', [], [], [])
    Enode3 = dataTypes.gaussian_E_Node('EG', [], [], [])
    Enodes = [Enode1, Enode2, Enode3]
    # make the A nodes. 
    Anodes = []
    for i in range(3):
        Anode = dataTypes.reg_A_Node(str(i), [], [], [])
        Anodes.append(Anode)
    # make the semantics.
    semantics = []
    for i in range(10):
        new_sem = dataTypes.MLS_sem(str(i), [], [])
        semantics.append(new_sem)
    # make stand-in POs.
    PO1 = dataTypes.basicTimingNode('PO1', [], [], [])
    PO2 = dataTypes.basicTimingNode('PO2', [], [], [])
    POs = [PO1, PO2]

    # connect stand-in POs to E nodes.
    Links = []
    for PO in POs:
        for Enode in Enodes:
            new_link = dataTypes.basicLink(PO, Enode, 1.0)
            Enode.higher_connections.append(new_link)
    # connect E nodes to A nodes. 
    for Enode in Enodes:
        Enode.lateral_connections = Enodes
        for Anode in Anodes:
            new_link = dataTypes.basicLink(Enode, Anode, random.uniform(.1, 1.0))
            Enode.lower_connections.append(new_link)
            Anode.higher_connections.append(new_link)
            Links.append(new_link)
    # connect the A nodes to semantics.
    for Anode in Anodes:
        Anode.lateral_connections = Anodes
        for semantic in semantics:
            new_link = dataTypes.basicLink(Anode, semantic, random.random())
            Anode.lower_connections.append(new_link)
            semantic.higher_connections.append(new_link)
            Links.append(new_link)

    learning_trials = 10
    for i in range(learning_trials):
        # set activation of POs.
        same_trial = random.random()
        if same_trial > .5:
            PO1.act = 1.0
            same_trial = False
        else:
            PO1.act, PO2.act = 0.5, 0.5
            same_trial = True
        # until the local inhibitor fires (i.e., while the first PO is active), update inputs, activations, and weights. 
        for i in range(110):
            # update inputs to all units. 
            for Enode in Enodes:
                Enode.update_input()
            for Anode in Anodes:
                Anode.update_input()
            for semantic in semantics:
                semantic.update_input()
            #pdb.set_trace()
            # get max_sem_input. 
            max_sem_input = 0.0
            for semantic in semantics:
                if semantic.input > max_sem_input:
                    max_sem_input = semantic.input
            # subtractive normalisation. 
            for semantic in semantics:
                if semantic.input < max_sem_input:
                    semantic.input -= max_sem_input
            # then update max_sem_input for divisive normalisation. 
            for semantic in semantics:
                semantic.set_max_sem_input(max_sem_input)
            # update activation and clear the input of all units. 
            for Enode in Enodes:
                Enode.update_act()
                Enode.clear_input()
            for Anode in Anodes:
                Anode.update_act()
                Anode.clear_input()
            for semantic in semantics:
                semantic.update_act()
                semantic.clear_input()
            # learning. 
            if i >= 20:
                for Enode in Enodes:
                    Enode.adjust_links()
                for Anode in Anodes:
                    Anode.adjust_links()
        # after n iterations, if same_trial is False, then fire the local inhibitor, which inhibits all units, and start time since last fired of the most active A unit. 
        if not same_trial:
            active_unit = None
            max_act = 0.0
            for Anode in Anodes:
                if Anode.act > max_act:
                    active_unit = Anode
            active_unit.time_since_fired = 1
        for Enode in Enodes:
            Enode.clear_input_and_act()
        for Anode in Anodes:
            Anode.clear_input_and_act
        for semantic in semantics:
            semantic.clear_all()
        # until the global inhibitor fires (i.e., while second PO is active), update inputs, activations, and weights. 
        for i in range(110):
            # update inputs to all units. 
            for Enode in Enodes:
                Enode.update_input()
            for Anode in Anodes:
                Anode.update_input()
            for semantic in semantics:
                semantic.update_input()
            # get max_sem_input. 
            max_sem_input = 0.0
            for semantic in semantics:
                if semantic.input > max_sem_input:
                    max_sem_input = semantic.input
            # subtractive normalisation. 
            for semantic in semantics:
                if semantic.input < max_sem_input:
                    semantic.input -= max_sem_input
            # then update max_sem_input for divisive normalisation. 
            for semantic in semantics:
                semantic.set_max_sem_input(max_sem_input)
            # update activation of all units. 
            for Enode in Enodes:
                Enode.update_act()
            for Anode in Anodes:
                Anode.update_act()
            for semantic in semantics:
                semantic.update_act()
            # learning. 
            if i >= 20:
                for Enode in Enodes:
                    Enode.adjust_links()
                for Anode in Anodes:
                    Anode.adjust_links() 

 very simple learning of energy net. 
def learn_energy_circuit(learning_trials):
    # architecture is 4 E nodes, 6 A nodes, and 10 semantics. 
    # make the guassian E nodes.
    Enode1 = dataTypes.gaussian_E_Node('E1', [], [], [], 1, .3)
    Enode2 = dataTypes.gaussian_E_Node('E2', [], [], [], 1, .1)
    Enode3 = dataTypes.gaussian_E_Node('E1', [], [], [], 2, .3)
    Enode4 = dataTypes.gaussian_E_Node('E2', [], [], [], 2, .1)
    Enodes = [Enode1, Enode2, Enode3, Enode4]
    # make the semantics.
    semantics = []
    for i in range(10):
        new_sem = dataTypes.MLS_sem(str(i), [], [])
        semantics.append(new_sem)
    # make proxy POs.
    PO1 = dataTypes.basicTimingNode('PO1', [], [], [])
    PO2 = dataTypes.basicTimingNode('PO2', [], [], [])
    POs = [PO1, PO2]
    # connect proxy POs to E nodes. 
    for PO in POs:
        for Enode in Enodes:
            new_link = dataTypes.basicLink(PO, Enode, 1.0)
            Enode.higher_connections.append(new_link)
    # connect the E nodes to semantics and update lateral_connections for E nodes (for lateral inhibition).
    for Enode in Enodes:
        Enode.lateral_connections = Enodes
        for semantic in semantics:
            new_link = dataTypes.basicLink(Enode, semantic, random.random())
            Enode.lower_connections.append(new_link)
            semantic.higher_connections.append(new_link)
    
    # leaning. 
    for i in range(learning_trials):
        # set activation of PO proxys.
        same_trial = random.random()
        if same_trial > .5:
            PO1.act = 1.0
            same_trial = False
        else:
            PO1.act, PO2.act = 1.0, 1.0
            same_trial = True
        #pdb.set_trace()
        # until the local inhibitor fires (i.e., while the first PO is active), update inputs, activations, and weights. 
        for i in range(110):
            # update inputs to all units. 
            for Enode in Enodes:
                Enode.update_input()
            for semantic in semantics:
                semantic.update_input()
            # get max_sem_input. 
            max_sem_input = 0.0
            for semantic in semantics:
                if semantic.input > max_sem_input:
                    max_sem_input = semantic.input
            # subtractive normalisation. 
            for semantic in semantics:
                if semantic.input < max_sem_input:
                    semantic.input -= max_sem_input
            # then update max_sem_input for divisive normalisation. 
            for semantic in semantics:
                semantic.set_max_sem_input(max_sem_input)
            #pdb.set_trace()
            # update activation and clear the input of all units. 
            for Enode in Enodes:
                Enode.update_act()
                Enode.clear_input()
            for semantic in semantics:
                semantic.update_act()
                semantic.clear_input()
            #pdb.set_trace()
            # learning. 
            if i >= 20:
                for Enode in Enodes:
                    Enode.adjust_links()
        # after n iterations, if same_trial is False, then fire the local inhibitor, which inhibits all units, and start time since last fired of the most active A unit. 
        if not same_trial:
            active_unit = None
            max_act = 0.0
            for Enode in Enodes:
                if Enode.act > max_act:
                    active_unit = Enode
            active_unit.time_since_fired = 1
        for Enode in Enodes:
            Enode.clear_input_and_act()
        for semantic in semantics:
            semantic.clear_all()
        # until the global inhibitor fires (i.e., while second PO is active), update inputs, activations, and weights. 
        for i in range(110):
            # update inputs to all units. 
            for Enode in Enodes:
                Enode.update_input()
            for semantic in semantics:
                semantic.update_input()
            # get max_sem_input. 
            max_sem_input = 0.0
            for semantic in semantics:
                if semantic.input > max_sem_input:
                    max_sem_input = semantic.input
            # subtractive normalisation. 
            for semantic in semantics:
                if semantic.input < max_sem_input:
                    semantic.input -= max_sem_input
            # then update max_sem_input for divisive normalisation. 
            for semantic in semantics:
                semantic.set_max_sem_input(max_sem_input)
            pdb.set_trace()
            # update activation of all units. 
            for Enode in Enodes:
                Enode.update_act()
                Enode.clear_input()
            for semantic in semantics:
                semantic.update_act()
                semantic.clear_input()
            #pdb.set_trace()
            # learning. 
            if i >= 20:
                for Enode in Enodes:
                    Enode.adjust_links()
        # now fire global inhibitor. 
        for Enode in Enodes:
            Enode.clear_all()
        for semantic in semantics:
            semantic.clear_all()
    # returns. 
    return [POs, Enodes, semantics]

# for visualisation. 
# print energy_net states.
def print_energy_net(POs, Enodes, semantics):
    counter = 1
    for PO in POs:
        print('PO', str(counter), ' act: ', str(PO.act))
        counter += 1
    counter = 1
    for Enode in Enodes:
        print('Enode', str(counter), ' input:', Enode.input)
        print('Enode', str(counter), ' act:', Enode.act)
        print('Enode', str(counter), ' above_weights:', str([x.weight for x in Enode.higher_connections]))
        print('Enode', str(counter), ' lower_weights:', str([x.weight for x in Enode.lower_connections]))
        counter += 1
    counter = 1
    for semantic in semantics:
        print('semantic', str(counter), ' input:', semantic.input)
        print('semantic', str(counter), ' act:', semantic.act)
        counter += 1



