# test script for neural simple energy circuit learning. 
import dataTypes
import random, pdb

# very simple learning of energy net. 
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
            #pdb.set_trace()
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
    # counter = 1
    # for semantic in semantics:
    #     print('semantic', str(counter), ' input:', semantic.input)
    #     print('semantic', str(counter), ' act:', semantic.act)
    #     counter += 1




energy_net = learn_energy_circuit(20)
pdb.set_trace()



