# basicRunDORA.py

# basic functions and core run code for a simple DORA run (i.e., mapping, retrieval, predication, schema induction, whole relation formation).

# Are you being run on an iPhone?
run_on_iphone = False

# imports.
import random, numbers, math, operator, copy, json
import numpy as np
import dataTypes
import DORA_GUI
import buildNetwork
if not run_on_iphone:
    import pygame
    from pygame.locals import *
import pdb

# Initialize pygame screen size to 1200x800.
#screen_width = 1200.0
#screen_height = 700.0

# class that performs all the run operations in DORA. In class form so that new operations (e.g., compression, predicate recognition) can be implemented as new functions in this class (under the phase set section).
class runDORA(object):
    def __init__(self, memory, parameters):
        self.memory = memory
        self.firingOrderRule = parameters['firingOrderRule']
        self.firingOrder = None # initialized to None.
        self.asDORA = parameters['asDORA']
        self.gamma = parameters['gamma']
        self.delta = parameters['delta']
        self.eta = parameters['eta']
        self.HebbBias = parameters['HebbBias']
        self.lateral_input_level = parameters['lateral_input_level']
        self.strategic_mapping = parameters['strategic_mapping']
        self.ignore_object_semantics = parameters['ignore_object_semantics']
        self.ignore_memory_semantics = parameters['ignore_memory_semantics']
        self.mag_decimal_precision = parameters['mag_decimal_precision']
        self.exemplar_memory = parameters['exemplar_memory']
        self.recent_analog_bias = parameters['recent_analog_bias']
        self.bias_retrieval_analogs = parameters['bias_retrieval_analogs']
        self.use_relative_act = parameters['use_relative_act']
        self.ho_sem_act_flow = parameters['ho_sem_act_flow'] # allows flow of activation; -1: only from regular semantics to higher-order semantics; 1: only from higher-order semantics to regular semantics; 0: in both directions
        self.tokenize = parameters['tokenize'] # ekaterina: the parameter for unpacking; if tokenize == True: create two copies of unpacked object in memory bound to two roles in two different analogs; if tokenize == False: create one object bound to two unpacked roles in one analog
        self.remove_uncompressed = parameters['remove_uncompressed']  # ekaterina: allows to choose whether to delete or to leave the original uncompressed structure from LTM after do_compress()
        self.remove_compressed = parameters['remove_compressed']  # ekaterina: allows to choose whether to delete or to leave the original compressed structure from LTM after do_unpacking()
        if run_on_iphone:
            self.doGUI = False
        else:
            self.doGUI = parameters['doGUI']
        self.screen = 0
        self.GUI_information = None # initialize to None.
        self.screen_width = parameters['screen_width']
        self.screen_height = parameters['screen_height']
        self.GUI_update_rate = parameters['GUI_update_rate']
        self.starting_iteration = parameters['starting_iteration']
        self.num_phase_sets_to_run = None
        self.count_by_RBs = None # initialize to None.
        self.local_inhibitor_fired = False # initialize to False.

    ######################################
    ###### DORA OPERATION FUNCTIONS ######
    ######################################
    # 1) Bring a prop or props into WM (driver). This step is completed by passing the variable memory as an argument to the function (memory contains the driver proposition(s)).
    # function to prepare runDORA object for a run.
    def initialize_run(self, mapping):
        # index memory.
        self.memory = indexMemory(self.memory)
        # set up driver and recipient.
        self.memory.driver.Groups = []
        self.memory.driver.Ps = []
        self.memory.driver.RBs = []
        self.memory.driver.POs = []
        self.memory.recipient.Groups = []
        self.memory.recipient.Ps = []
        self.memory.recipient.RBs = []
        self.memory.recipient.POs = []
        if mapping == True and self.exemplar_memory == True:
            self.memory = make_AM_copy(self.memory)
        else:
            self.memory = make_AM(self.memory)
        # initialize .same_RB_POs field for POs.
        self.memory = update_same_RB_POs(self.memory)
        # initialize GUI if necessary.
        if self.doGUI:
            self.screen, self.GUI_information = DORA_GUI.initialize_GUI(self.screen_width, self.screen_height, self.memory)
        # get PO SemNormalizations.
        for myPO in self.memory.POs:
            myPO.get_weight_length()

    # 2) Initialize activations and inputs of all units to 0.
    def initialize_network_state(self):
        self.memory = initialize_memorySet(self.memory)
        self.inferred_new_P = False

    # 3) Select firing order of RBs in the driver (for now this step is random or user determined).
    def create_firing_order(self):
        if len(self.memory.driver.RBs) > 0:
            self.count_by_RBs = True
        else:
            self.count_by_RBs = False
            # and randomly assign the PO firing order.
            self.firingOrder = []
            for myPO in self.memory.driver.POs:
                self.firingOrder.append(myPO)
            random.shuffle(self.firingOrder)
        if self.count_by_RBs:
            self.firingOrder = makeFiringOrder(self.memory, self.firingOrderRule)

    # function to perform steps 1-3 above.
    def do_1_to_3(self, mapping):
        self.initialize_run(mapping)
        self.initialize_network_state()
        self.create_firing_order()

    # 4) Enter the phase set. A phase set is each RB firing at least once (i.e., all RBs in firingOrder firing). It is in phase_sets you will do all of DORA's interesting operations (retrieval, mapping, learning, etc.). There is a function for each interesting operation.
    def do_map(self):
        # do initialize network operations (steps 1-3 above).
        self.memory = resetMappingUnits(self.memory)
        self.do_1_to_3(mapping=True)
        phase_sets = 3
        # if there are multiple relations in the driver (i.e., the number of P units is 2 or more), then switch to LISA mode, and set ignore_object_semantics to True.
        changed_mode = False
        changed_ig_obj_sem = False
        if len(self.memory.driver.Ps) >= 2 and self.strategic_mapping == True:
            # set asDORA mode to False if it is not already.
            if self.asDORA:
                self.asDORA = False
                changed_mode = True
            # set ignore_object_semantics to False if it is not already.
            if not self.ignore_object_semantics:
                self.ignore_object_semantics = True
                changed_ig_obj_sem = True
        # set up mapping hypotheses.
        # initialize (i.e., reset to empty) all the mappingHypotheses and mappingConnections.
        self.memory = resetMappingUnits(self.memory)
        # set up mappingHypotheses and mappingConnection units.
        self.memory = setupMappingUnits(self.memory)
        for phase_set in range(phase_sets):
            # if counting by RBs, then fire all RBs in self.firingOrder; otherwise fire POs in self.firingOrder
            if self.count_by_RBs:
                for currentRB in self.firingOrder:
                    # initialize phase_set_iterator and flags (local_inhibitor_fired).
                    phase_set_iterator = 1
                    self.local_inhibitor_fired = False
                    # 4.1-4.2) Fire the current RB in the firingOrder. Update the network in discrete time-steps until the globalInhibitor fires (i.e., the current active RB is inhibited by its inhibitor).
                    phase_set_iterator = 0
                    while self.memory.globalInhibitor.act == 0:
                        # 4.3.1-4.3.10) update network activations.
                        currentRB.act = 1.0
                        self.time_step_activations(phase_set, self.ignore_object_semantics, self.ignore_memory_semantics, retrieval_license=True) # ekaterina: added retrieval_license
                        # 4.3.11) Update mapping hypotheses.
                        self.memory = update_mappingHyps(self.memory)
                        # fire the local_inhibitor if necessary.
                        self.time_step_fire_local_inhibitor()
                        # update GUI.
                        phase_set_iterator += 1
                        if self.doGUI:
                            self.time_step_doGUI(phase_set_iterator)
                    # RB firing is OVER.
                    self.post_count_by_operations()
            else:
                # make sure you are operating asDORA.
                asLISA = False
                if not self.asDORA:
                    self.asDORA = True
                    asLISA = True
                # fire by POs.
                for currentPO in self.firingOrder:
                    # initialize phase_set_iterator and flags (local_inhibitor_fired).
                    phase_set_iterator = 1
                    self.local_inhibitor_fired = False
                    # 4.1-4.2) Fire the current RB in the firingOrder. Update the network in discrete time-steps until the globalInhibitor fires (i.e., the current active RB is inhibited by its inhibitor).
                    phase_set_iterator = 0
                    while self.memory.localInhibitor.act == 0:
                        # 4.3.1-4.3.10) update network activations.
                        currentPO.act = 1.0
                        self.time_step_activations(phase_set, self.ignore_object_semantics, self.ignore_memory_semantics, retrieval_license=True) # ekaterina: added retrieval_license
                        # 4.3.11) Update mapping hypotheses.
                        self.memory = update_mappingHyps(self.memory)
                        # fire the local_inhibitor if necessary.
                        self.time_step_fire_local_inhibitor()
                        # update GUI.
                        phase_set_iterator += 1
                        if self.doGUI:
                            self.time_step_doGUI(phase_set_iterator)
                    # PO firing is OVER.
                    self.post_count_by_operations()
                # if you were operating as LISA before starting to map with just POs, go back to as LISA (i.e., set self.asDORA back to False).
                if asLISA:
                    self.asDORA = False
            # phase set is OVER.
            self.post_phase_set_operations(retrieval_license=False, map_license=True)
        # if you changed mode or changed ignore_object_semantics, then change them back.
        if changed_mode:
            self.asDORA = True
        if changed_ig_obj_sem:
            self.ignore_object_semantics = False

    def do_retrieval(self):
        # do initialize network operations (steps 1-3 above).
        self.do_1_to_3(mapping=False)
        phase_sets = 1
        for phase_set in range(phase_sets):
            # fire all RBs in self.firingOrder, unless there are no RBs, in which case fire the POs in self.firingOrder.
            if len(self.memory.driver.RBs) > 0:
                for currentRB in self.firingOrder:
                    # initialize phase_set_iterator and flags (local_inhibitor_fired).
                    phase_set_iterator = 1
                    self.local_inhibitor_fired = False
                    # 4.1-4.2) Fire the current RB in the firingOrder. Update the network in discrete time-steps until the globalInhibitor fires (i.e., the current active RB is inhibited by its inhibitor).
                    while self.memory.globalInhibitor.act == 0:
                        # 4.3.1-4.3.10) update network activations.
                        currentRB.act = 1.0
                        self.time_step_activations(phase_set, self.ignore_object_semantics, self.ignore_memory_semantics, retrieval_license=True) # ekaterina: added retrieval_license
                        # 4.3.12) Run retrieval routines.
                        self.memory = retrieval_routine(self.memory, self.asDORA, self.gamma, self.delta, self.HebbBias, self.lateral_input_level, self.bias_retrieval_analogs)
                        # fire the local_inhibitor if necessary.
                        self.time_step_fire_local_inhibitor()
                        # update GUI.
                        phase_set_iterator += 1
                        if self.doGUI:
                            self.time_step_doGUI(phase_set_iterator)
                    # RB firing is OVER.
                    self.post_count_by_operations()
            else:
                # when you are retrieving by POs, you are firing the POs one at a time in the driver by default as the firing order is composed of POs only. As a consequence, when you are running in LISA mode and PO inhibitors are not updating, you will not get PO time sharing (i.e., a PO will keep firing forever, as it's inhibitor is not updating (in LISA mode PO inhibitors do not update)). So, you must move to DORA mode for retrieval.
                # set .asDORA to True.
                previous_mode = self.asDORA
                self.asDORA = True
                for currentPO in self.firingOrder:
                    # initialize phase_set_iterator and flags (local_inhibitor_fired).
                    phase_set_iterator = 1
                    self.local_inhibitor_fired = False
                    # 4.1-4.2) Fire the current RB in the firingOrder. Update the network in discrete time-steps until the globalInhibitor fires (i.e., the current active RB is inhibited by its inhibitor).
                    while self.memory.localInhibitor.act == 0:
                        # 4.3.1-4.3.10) update network activations.
                        currentPO.act = 1.0
                        self.time_step_activations(phase_set, self.ignore_object_semantics, self.ignore_memory_semantics, retrieval_license=True) # ekaterina: added retrieval_license
                        # 4.3.12) Run retrieval routines.
                        self.memory = retrieval_routine(self.memory, self.asDORA, self.gamma, self.delta, self.HebbBias, self.lateral_input_level, self.bias_retrieval_analogs)
                        # fire the local_inhibitor if necessary.
                        self.time_step_fire_local_inhibitor()
                        # update GUI.
                        phase_set_iterator += 1
                        if self.doGUI:
                            self.time_step_doGUI(phase_set_iterator)
                    # PO firing is OVER.
                    self.post_count_by_operations()
                # return the .asDORA setting to its previous state.
                self.asDORA = previous_mode
            # phase set is OVER.
            self.post_phase_set_operations(retrieval_license=True, map_license=False)

    def do_retrieval_v2(self):
        # do initialize network operations (steps 1-3 above).
        self.do_1_to_3(mapping=False)
        phase_sets = 1
        for phase_set in range(phase_sets):
            # fire all RBs in self.firingOrder, unless there are no RBs, in which case fire the POs in self.firingOrder.
            if len(self.memory.driver.RBs) > 0:
                for currentRB in self.firingOrder:
                    # initialize local_inhibitor_fired to False.
                    self.local_inhibitor_fired = False
                    # 4.1-4.2) Fire the current RB in the firingOrder. Update the network in discrete time-steps for 7 time steps (counted by the phase_set_iterator). The point of allowing only a few time steps is to let the most semantically similar POs get active.
                    phase_set_iterator = 0
                    while phase_set_iterator < 7:
                        # 4.3.1-4.3.10) update network activations.
                        currentRB.act = 1.0
                        self.time_step_activations(phase_set, self.ignore_object_semantics, self.ignore_memory_semantics, retrieval_license=True) # ekaterina: added retrieval_license
                        # 4.3.12) Run retrieval routines.
                        self.memory = retrieval_routine(self.memory, self.asDORA, self.gamma, self.delta, self.HebbBias, self.lateral_input_level, self.bias_retrieval_analogs)
                        # update GUI.
                        phase_set_iterator += 1
                        if self.doGUI:
                            self.time_step_doGUI(phase_set_iterator)
                    # RB firing is OVER.
                    self.post_count_by_operations()
            else:
                # when you are retrieving by POs, you are firing the POs one at a time in the driver by default as the firing order is composed of POs only. As a consequence, when you are running in LISA mode and PO inhibitors are not updating, you will not get PO time sharing (i.e., a PO will keep firing forever, as it's inhibitor is not updating (in LISA mode PO inhibitors do not update)). So, you must move to DORA mode for retrieval.
                # set .asDORA to True.
                previous_mode = self.asDORA
                self.asDORA = True
                for currentPO in self.firingOrder:
                    # initialize local_inhibitor_fired to False.
                    self.local_inhibitor_fired = False
                    # 4.1-4.2) Fire the current RB in the firingOrder. Update the network in discrete time-steps for 7 time steps (counted by the phase_set_iterator). The point of allowing only a few time steps is to let the most semantically similar POs get active.
                    phase_set_iterator = 0
                    while phase_set_iterator < 4:
                        # 4.3.1-4.3.10) update network activations.
                        currentPO.act = 1.0
                        self.time_step_activations(phase_set, self.ignore_object_semantics, self.ignore_memory_semantics, retrieval_license=True) # ekaterina: added retrieval_license
                        # 4.3.12) Run retrieval routines.
                        self.memory = retrieval_routine(self.memory, self.asDORA, self.gamma, self.delta, self.HebbBias, self.lateral_input_level, self.bias_retrieval_analogs)
                        # update GUI.
                        phase_set_iterator += 1
                        if self.doGUI:
                            self.time_step_doGUI(phase_set_iterator)
                    # PO firing is OVER.
                    self.post_count_by_operations()
                # return the .asDORA setting to its previous state.
                self.asDORA = previous_mode
            # phase set is OVER.
            self.post_phase_set_operations(retrieval_license=True, map_license=False)

        # operations for DORA's same/different/more/less detection using simple entropy. Find instances of same/different and more/less using entropy.
    def do_entropy_ops_within(self, pred_only):
        # within (entropy over items from the same analog in the driver/recipient) set entropy_ops are used to compute specific kinds of similarity/difference/magnitude over dimensions in the same analog in the driver.
        extend_SDML = True
        # set asDORA mode to True if it is not already.
        changed_mode = False
        if not self.asDORA:
            self.asDORA = True
            changed_mode = True
        # do initialize network operations (steps 1-3 above).
        self.do_1_to_3(mapping=False)
        # iterate through analogs in the driver.
        for analog in self.memory.driver.analogs:
            # for each analog, randomly select a pair of POs that both are strongly connected to a dimenions, and do an entropy comparison if applicable.
            # check if there are preds present.
            pred_present = False
            for presPO in analog.myPOs:
                if presPO.predOrObj == 1:
                    pred_present = True
                    break
            if len(analog.myPs) > 0:
                for myP in analog.myPs:
                    # initialise placeholders for PO pairs with matching semantics. These are used to check if SDM semantics are present in the current analog (when they are present and highly active, they inhibit the entropy mechanism; see code under comment: '#now random selection of pair of POs if any exist.').
                    match_int_dim = []
                    match_both_mag_sem = []
                    match_one_mag_sem = []
                    match_both_mag_sem_below = []
                    # check all PO pairs.
                    # find all predPOs.
                    pred_list = []
                    for myRB in myP.myRBs:
                        pred_list.append(myRB.myPred[0])
                    # check all PO pairs.
                    for myPO in pred_list:
                        for myPO2 in pred_list[pred_list.index(myPO)+1:]:
                            if (myPO is not myPO2) and (myPO.predOrObj == myPO2.predOrObj):
                                # check if they code the same dimension (are they both connected to a semantic unit coding a dimension with a weight near 1?), and whether any POs are connected to any SDM semantics (i.e., "more", "less", or "same") at all, or both are connected to SDM semantics below threshold.
                                intersect_dim, one_mag_sem_present, both_mag_sem_present, one_mag_sem_present_belowThresh, both_mag_sem_present_belowThresh = en_based_mag_checks(myPO, myPO2)
                                new_dict = {'PO1': myPO, 'PO2': myPO2, 'intersect_dim': intersect_dim, 'one_mag_sem_present': one_mag_sem_present, 'both_mag_sem_present': both_mag_sem_present, 'one_mag_sem_present_belowThresh': one_mag_sem_present_belowThresh, 'both_mag_sem_present_belowThresh': both_mag_sem_present_belowThresh}
                                if len(intersect_dim) >= 1:
                                    match_int_dim.append(new_dict)
                                if both_mag_sem_present:
                                    match_both_mag_sem.append(new_dict)
                                if one_mag_sem_present:
                                    match_one_mag_sem.append(new_dict)
                                if both_mag_sem_present_belowThresh:
                                    match_both_mag_sem_below.append(new_dict)
                    # now random selection of pair of POs if any exist.
                    # If SDM semantics are present, then no run. If no SDM semantics present and dimensions present, then run entropy ops. If SDM semantics kind of active, then find the best dimension and run entropy ops.
                    ent_pair = None
                    if len(match_both_mag_sem) >= 1:
                        ent_pair = None
                    elif len(match_one_mag_sem) > 0:
                        ent_pair = random.choice(match_one_mag_sem)
                    elif len(match_both_mag_sem_below) > 0:
                        ent_pair = random.choice(match_both_mag_sem_below)
                    elif len(match_int_dim) > 0:
                        ent_pair = random.choice(match_int_dim)
                    # now select and run appropriate en_op.
                    if ent_pair:
                        myPO, myPO2, intersect_dim, one_mag_sem_present, both_mag_sem_present, one_mag_sem_present_belowThresh, both_mag_sem_present_belowThresh = ent_pair['PO1'], ent_pair['PO2'], ent_pair['intersect_dim'], ent_pair['one_mag_sem_present'],  ent_pair['both_mag_sem_present'], ent_pair['one_mag_sem_present_belowThresh'], ent_pair['both_mag_sem_present_belowThresh']
                        self.memory = check_and_run_ent_ops_within(myPO, myPO2, intersect_dim, one_mag_sem_present, both_mag_sem_present, one_mag_sem_present_belowThresh, both_mag_sem_present_belowThresh, extend_SDML, pred_only, pred_present, self.memory, self.mag_decimal_precision)
            elif len(analog.myRBs) > 0:
                match_list = []
                # find all predPOs.
                pred_list = []
                for myRB in analog.myRBs:
                    pred_list.append(myRB.myPred[0])
                # check PO pairs.
                for myPO in pred_list:
                    for myPO2 in pred_list[pred_list.index(myPO)+1:]:
                        if (myPO is not myPO2) and (myPO.predOrObj == myPO2.predOrObj):
                            # check if they code the same dimension (are they both connected to a semantic unit coding a dimension with a weight near 1?), and whether any POs are connected to any SDM semantics (i.e., "more", "less", or "same") at all, or both are connected to SDM semantics below threshold.
                            intersect_dim, one_mag_sem_present, both_mag_sem_present, one_mag_sem_present_belowThresh, both_mag_sem_present_belowThresh = en_based_mag_checks(myPO, myPO2)
                            new_dict = {'PO1': myPO, 'PO2': myPO2, 'intersect_dim': intersect_dim, 'one_mag_sem_present': one_mag_sem_present, 'both_mag_sem_present': both_mag_sem_present, 'one_mag_sem_present_belowThresh': one_mag_sem_present_belowThresh, 'both_mag_sem_present_belowThresh': both_mag_sem_present_belowThresh}
                            if len(intersect_dim) >= 1:
                                match_list.append(new_dict)
                # Now the random selection of pair of POs if any exist.
                if len(match_list) >= 1:
                    ent_pair = random.choice(match_list)
                    myPO, myPO2, intersect_dim, one_mag_sem_present, both_mag_sem_present, one_mag_sem_present_belowThresh, both_mag_sem_present_belowThresh = ent_pair['PO1'], ent_pair['PO2'], ent_pair['intersect_dim'], ent_pair['one_mag_sem_present'],  ent_pair['both_mag_sem_present'], ent_pair['one_mag_sem_present_belowThresh'], ent_pair['both_mag_sem_present_belowThresh']
                    # now select and run appropriate en_op.
                    self.memory = check_and_run_ent_ops_within(myPO, myPO2, intersect_dim, one_mag_sem_present, both_mag_sem_present, one_mag_sem_present_belowThresh, both_mag_sem_present_belowThresh, extend_SDML, pred_only, pred_present, self.memory, self.mag_decimal_precision)
            else:
                match_list = []
                for myPO in analog.myPOs:
                    for myPO2 in analog.myPOs[analog.myPOs.index(myPO)+1:]:
                        if (myPO is not myPO2) and (myPO.predOrObj == myPO2.predOrObj):
                            # check if they code the same dimension (are they both connected to a semantic unit coding a dimension with a weight near 1?), and whether any POs are connected to any SDM semantics (i.e., "more", "less", or "same") at all, or both are connected to SDM semantics below threshold.
                            intersect_dim, one_mag_sem_present, both_mag_sem_present, one_mag_sem_present_belowThresh, both_mag_sem_present_belowThresh = en_based_mag_checks(myPO, myPO2)
                            if len(intersect_dim) >= 1:
                                new_dict = {'PO1': myPO, 'PO2': myPO2, 'intersect_dim': intersect_dim, 'one_mag_sem_present': one_mag_sem_present, 'both_mag_sem_present': both_mag_sem_present, 'one_mag_sem_present_belowThresh': one_mag_sem_present_belowThresh, 'both_mag_sem_present_belowThresh': both_mag_sem_present_belowThresh}
                                match_list.append(new_dict)
                # Now the random selection of pair of POs if any exist.
                if len(match_list) >= 1:
                    ent_pair = random.choice(match_list)
                    myPO, myPO2, intersect_dim, one_mag_sem_present, both_mag_sem_present, one_mag_sem_present_belowThresh, both_mag_sem_present_belowThresh = ent_pair['PO1'], ent_pair['PO2'], ent_pair['intersect_dim'], ent_pair['one_mag_sem_present'],  ent_pair['both_mag_sem_present'], ent_pair['one_mag_sem_present_belowThresh'], ent_pair['both_mag_sem_present_belowThresh']
                    # now select and run appropriate en_op.
                    self.memory = check_and_run_ent_ops_within(myPO, myPO2, intersect_dim, one_mag_sem_present, both_mag_sem_present, one_mag_sem_present_belowThresh, both_mag_sem_present_belowThresh, extend_SDML, pred_only, pred_present, self.memory, self.mag_decimal_precision)
        # done so change change mode back to LISA if you changed_mode is True.
        if changed_mode:
            self.asDORA = False

    def do_entropy_ops_between(self, retrieval_license=False):
        # between (entropy over mapped items across the driver and recipient) set entropy_operations are used to compute over-all similarity/difference between mapped items.
        ##########
        difference_ratio = 'undefined' # ekaterina
        # WAIT, DO I JUST WANNA DO SIMPLE SEMANTIC SIMILARITY CALCULATION USING SEMANTIC WEIGHTS? IF THEY MAP, COMPUTE THE SEMANTIC SIMILARITY BASED ON SEMANTIC WEIGHT VECTORS?
        # make sure that the .max_map_unit field has been filled in for all units.
        self.memory = get_max_map_units(self.memory)
        # compute entropy similarity for all mapped items across driver and recipient.
        for myPO in self.memory.driver.POs:
            # find the unit (if any) that myPO maps to.
            if myPO.max_map_unit:
                myPO2 = myPO.max_map_unit
                # activate the two POs, and let them activate their semntic units.
                myPO.act, myPO2.act = 1.0, 1.0
                for iter_i in range(10):
                    # update semantic inputs.
                    for semantic in self.memory.semantics:
                        semantic.update_input(self.memory, self.ho_sem_act_flow, retrieval_license, self.ignore_object_semantics, self.ignore_memory_semantics)
                    # update sematnic activations.
                    max_input = get_max_sem_input(self.memory)
                    for semantic in self.memory.semantics:
                        semantic.set_max_input(max_input)
                        semantic.update_act()
                # run basic ent_overall_same_diff() to compute the similarity_ratio between the mapped POs.
                difference_ratio = ent_overall_same_diff(self.memory.semantics)
                print (difference_ratio)
                # finally, clear the inputs and activations of all current units.
                self.memory = initialize_AM(self.memory)
        # and return difference_ratio.
        return difference_ratio

    def do_predication(self):
        # you have to be operating asDORA for predication routines, so make sure .asDORA is True while performing predication.
        asDORA_flag = False
        if not self.asDORA:
            # set .asDORA to True, and asDORA_flag to True.
            self.asDORA = True
            asDORA_flag = True
        # do initialize network operations (steps 1-3 above).
        self.do_1_to_3(mapping=False)
        phase_sets = 1
        for phase_set in range(phase_sets):
            # make a firingOrder out of all the objects in the driver. If count_by_RBs is False, it's just self.firingOrder, otherwise, you need to make it by finding all the object POs.
            if not self.count_by_RBs:
                firingOrder = self.firingOrder
            else:
                firingOrder = []
                for currentPO in self.memory.driver.POs:
                    if currentPO.predOrObj == 0:
                        firingOrder.append(currentPO)
            # fire all POs in firingOrder.
            for currentPO in firingOrder:
                # initialize phase_set_iterator and flags (local_inhibitor_fired).
                phase_set_iterator = 1
                self.local_inhibitor_fired = False
                # 4.1-4.2) Fire the current RB in the firingOrder. Update the network in discrete time-steps until the globalInhibitor fires (i.e., the current active RB is inhibited by its inhibitor).
                phase_set_iterator = 0
                made_new_pred = False
                while self.memory.localInhibitor.act == 0:
                    # 4.3.1-4.3.10) update network activations.
                    currentPO.act = 1.0
                    self.time_step_activations(phase_set, self.ignore_object_semantics, self.ignore_memory_semantics, retrieval_license=False) # ekaterina: added retrieval_license
                    # 4.3.13.1) Do predication.
                    self.memory, made_new_pred = predication_routine(self.memory, made_new_pred, self.gamma)
                    self.time_step_fire_local_inhibitor()
                    # update GUI.
                    phase_set_iterator += 1
                    if self.doGUI:
                        self.time_step_doGUI(phase_set_iterator)
                # PO firing is OVER.
                self.post_count_by_operations()
            # FOR DEBUGGING.
            # make sure that all new new RBs and their POs are in the same analog.
            for RB1 in self.memory.recipient.RBs:
                if RB1.inferred:
                    for RB2 in self.memory.recipient.RBs:
                        if RB2.inferred:
                            if RB1.myanalog is not RB2.myanalog:
                                # DEBUGGING FOR NOW. You can provide a fix if it proves necessary.
                                pdb.set_trace()
            # FOR DEBUGGING: Make sure for each RB that the pred and object are in the same analog.
            for myRB in self.memory.recipient.RBs:
                if myRB.myPred[0].myanalog is not myRB.myObj[0].myanalog:
                    pdb.set_trace()
            ###############################################################################
            # make sure that any new items (i.e., those in the newSet) are part of an analog, and that any newly predicated units that are based on driver units in the same analog, are themselves in the same analog (i.e., if two new predicates are based on two driver units from the same analog, then the new predicates should be in the same analog).
            # for each analog in the driver, make a list of all newSet objects that are based on POs from that analog.
            newSet_analogs = []
            for analog in self.memory.driver.analogs:
                new_analog_elements = []
                for myPO in analog.myPOs:
                    # if the recipient unit that myPO maps to has created a new unit (i.e., .my_made_unit field is not empty), then add the made unit from newSet to the new_analog_elements list.
                    if myPO.max_map_unit:
                        if myPO.max_map_unit.my_made_unit:
                            new_analog_elements.append(myPO.max_map_unit.my_made_unit)
                # add the new_analog_elements to the newSet_analogs list.
                newSet_analogs.append(new_analog_elements)
            # make a new analog object and fill in the appropriate elements based on newSet_analogs.
            for analog_elements in newSet_analogs:
                new_analog = dataTypes.Analog()
                for obj in analog_elements:
                    # add the new_analog to the object, the RB, and the pred, and vise versa.
                    obj.myanalog = new_analog
                    obj.myRBs[0].myanalog = new_analog
                    obj.myRBs[0].myPred[0].myanalog = new_analog
                    new_analog.myRBs.append(obj.myRBs[0])
                    new_analog.myPOs.append(obj)
                    new_analog.myPOs.append(obj.myRBs[0].myPred[0])
                # add the new_analog to memory.
                self.memory.analogs.append(new_analog)
            # do post_phase_set_operations().
            self.post_phase_set_operations(retrieval_license=False, map_license=False)
        # reset inferences (i.e., reset .inferred, .my_maker_unit, and .my_made_unit fields from all the newSet and recipient units).
        self.memory = reset_inferences(self.memory)
        # if asDORA_flag is True (i.e., the network was in LISA mode, but was converted to DORA mode for the duration of predication), then change .asDORA back to False.
        if asDORA_flag:
            self.asDORA = False

    def do_rel_form(self):
        # Only done with RBs, so only do if count_by_RBs is True.
        if self.count_by_RBs:
            # do initialize network operations (steps 1-3 above).
            self.do_1_to_3(mapping=False)
            phase_sets = 1
            # you are running do_rel_form(), so set the inferred_new_P variable to False
            inferred_new_P = False
            for phase_set in range(phase_sets):
                # fire all RBs in self.firingOrder.
                if len(self.memory.driver.RBs) > 0:
                    for currentRB in self.firingOrder:
                        # initialize phase_set_iterator and flags (local_inhibitor_fired).
                        phase_set_iterator = 1
                        self.local_inhibitor_fired = False
                        # 4.1-4.2) Fire the current RB in the firingOrder. Update the network in discrete time-steps until the globalInhibitor fires (i.e., the current active RB is inhibited by its inhibitor).
                        while self.memory.globalInhibitor.act == 0:
                            # 4.3.1-4.3.10) update network activations.
                            currentRB.act = 1.0
                            self.time_step_activations(phase_set, self.ignore_object_semantics, self.ignore_memory_semantics, retrieval_license=False) # ekaterina: added retrieval_license
                            # 4.3.13.2) Do whole-relation formation.
                            self.memory, inferred_new_P = rel_form_routine(self.memory, inferred_new_P)
                            # fire the local_inhibitor if necessary.
                            self.time_step_fire_local_inhibitor()
                            # update GUI.
                            phase_set_iterator += 1
                            if self.doGUI:
                                self.time_step_doGUI(phase_set_iterator)
                        # RB firing is OVER.
                        self.post_count_by_operations()
                    # a full phase_set has run.
                    # if a new P has been inferred, make sure it connects to at least 2 RBs, otherwise, delete it.
                    if inferred_new_P:
                        # the new P will be the last item in memory.Ps. Make sure it connects to at least 2 RBs.
                        if len(self.memory.Ps[-1].myRBs) >= 2:
                            # make a new analog that includes the new myP. Add the RB and its POs to the current P's analog, and delete the analog the RB currently belongs to.
                            # make the new analog.
                            new_analog = dataTypes.Analog()
                            # add the new P to the new_analog (and vise versa).
                            new_analog.myPs.append(self.memory.Ps[-1])
                            self.memory.Ps[-1].myanalog = new_analog
                            # for each RB connected to the new P, add that RB and its POs to the current P's analog.
                            old_analogs = []
                            for myRB in self.memory.Ps[-1].myRBs:
                                # new_analog is the new analog you want to add elements to.
                                # get the old_analog (which is the analog that RB currently belongs to).
                                old_analog = myRB.myanalog
                                # add the RB to new_analog (and vise versa).
                                new_analog.myRBs.append(myRB)
                                myRB.myanalog=new_analog
                                # remove the RB from old_analog.
                                old_analog.myRBs.remove(myRB)
                                # FOR DEBUGGING: I'm getting an odd error with looking for a non-existent object on every 4 runs or so. Throw up a try/except and see if you can catch the error.
                                try:
                                    old_analog.myPOs.remove(myRB.myObj[0])
                                except:
                                    pdb.set_trace()
                                ########################################################################
                                # FOR DEBUGGING: You've put all these operations in this block and commented them out above (see that the below commands are all commented out in the above 15 or so lines). You might want to delete this block and uncomment out the operations above when you fix the bug that your above try/except statement is catching.
                                new_analog.myPOs.append(myRB.myPred[0])
                                myRB.myPred[0].myanalog = new_analog
                                new_analog.myPOs.append(myRB.myObj[0])
                                myRB.myObj[0].myanalog = new_analog
                                old_analog.myPOs.remove(myRB.myPred[0])
                                ########################################################################
                                # keep a list of all items that have served as old_analogs.
                                if old_analog not in old_analogs:
                                    old_analogs.append(old_analog)
                            # add the new_analog to self.memory.analogs.
                            self.memory.analogs.append(new_analog)
                            # for each old_analog in old_analogs, if it is empty (i.e., if you've deleted all its tokens), delete it.
                            for old_analog in old_analogs:
                                if len(old_analog.myRBs) == 0 and len(old_analog.myPOs) == 0:
                                    self.memory.analogs.remove(old_analog)
                        else:
                            # delete the new P unit.
                            del(self.memory.Ps[-1])
                    # run post_phase_set_operations.
                    self.post_phase_set_operations(retrieval_license=False, map_license=False, inferred_new_P=True)

    def do_schematization(self):
        # Change asDORA mode to asDORA = True.
        oldasDORA = self.asDORA
        self.asDORA = True
        # Only done with RBs, so only do if count_by_RBs is True.
        if self.count_by_RBs:
            # do initialize network operations (steps 1-3 above).
            self.do_1_to_3(mapping=False)
            phase_sets = 1
            for phase_set in range(phase_sets):
                # fire all RBs in self.firingOrder.
                if len(self.memory.driver.RBs) > 0:
                    for currentRB in self.firingOrder:
                        # initialize phase_set_iterator and flags (local_inhibitor_fired).
                        phase_set_iterator = 1
                        self.local_inhibitor_fired = False
                        # 4.1-4.2) Fire the current RB in the firingOrder. Update the network in discrete time-steps until the globalInhibitor fires (i.e., the current active RB is inhibited by its inhibitor).
                        while self.memory.globalInhibitor.act == 0:
                            # 4.3.1-4.3.10) update network activations.
                            currentRB.act = 1.0
                            self.time_step_activations(phase_set, self.ignore_object_semantics, self.ignore_memory_semantics, retrieval_license=False) # ekaterina: added retrieval_license
                            # 4.3.13.3) Do schematization/predicate refinement.
                            self.memory = schematization_routine(self.memory, self.gamma, phase_set_iterator)
                            # fire the local_inhibitor if necessary.
                            self.time_step_fire_local_inhibitor()
                            # update GUI.
                            phase_set_iterator += 1
                            if self.doGUI:
                                self.time_step_doGUI(phase_set_iterator)
                        # RB firing is OVER.
                        self.post_count_by_operations()
                    # phase_set is over.
                    self.post_phase_set_operations(retrieval_license=False, map_license=False)
        # make sure that any new items (i.e., those in the newSet) are part of an analog.
        self.memory = newSet_items_to_analog(self.memory)
        # you're done with schematization, so switch back to oldasDORA state.
        self.asDORA = oldasDORA
        # FOR DEBUGGING: check if an RB has been made without two POs.
        for myRB in self.memory.newSet.RBs:
            if (len(myRB.myPred) < 1) and (len(myRB.myObj) < 1):
                pdb.set_trace()

    def do_rel_gen(self):
        # make sure that DORA is in DORA mode. Change .asDORA to true, but also save the current .asDORA state so that you can return to current .asDORA state at the end of generalisation.
        DORA_state = self.asDORA
        self.asDORA = True
        # Only done with RBs, so only do if count_by_RBs is True.
        if self.count_by_RBs:
            # find the analog in which all mapping driver units live.
            driver_analog = find_driver_analog_rel_gen(self.memory)
            self.group_recip_maps()
            # find the analog that contains the mapped recipient units so that it can be passed to the rel_gen_routine().
            recip_analog = find_recip_analog(self.memory)
            # do initialize network operations (steps 1-3 above).
            self.do_1_to_3(mapping=False)
            phase_sets = 1
            for phase_set in range(phase_sets):
                # fire all RBs in the driver analog that contains mapped elements.
                if len(driver_analog.myRBs) > 0:
                    for currentRB in driver_analog.myRBs:
                        # initialize phase_set_iterator and flags (local_inhibitor_fired).
                        phase_set_iterator = 1
                        self.local_inhibitor_fired = False
                        # 4.1-4.2) Fire the current RB in the firingOrder. Update the network in discrete time-steps until the globalInhibitor fires (i.e., the current active RB is inhibited by its inhibitor).
                        while self.memory.globalInhibitor.act == 0:
                            # 4.3.1-4.3.10) update network activations.
                            currentRB.act = 1.0
                            self.time_step_activations(phase_set, self.ignore_object_semantics, self.ignore_memory_semantics, retrieval_license=False) # ekaterina: added retrieval_license
                            # 4.3.14) Do relational inference.
                            self.memory = rel_gen_routine(self.memory, self.gamma, recip_analog)
                            # fire the local_inhibitor if necessary.
                            self.time_step_fire_local_inhibitor()
                            # update GUI.
                            phase_set_iterator += 1
                            if self.doGUI:
                                self.time_step_doGUI(phase_set_iterator)
                        # RB firing is OVER.
                        self.post_count_by_operations()
                    # phase_set is over.
                    self.post_phase_set_operations(retrieval_license=False, map_license=False)
        # make sure that any new items (i.e., those in the newSet) are part of an analog.
        self.memory = newSet_items_to_analog(self.memory) # ekaterina
        # return .asDORA state to starting .asDORA state.
        self.asDORA = DORA_state

    def do_compression(self):
        # make sure DORA is in DORA mode.
        DORA_state = self.asDORA
        self.asDORA = True

        # make sure there are objects bound to multiple preds, and make a list of those objects.
        self.memory = update_same_RB_POs(self.memory)
        to_compress_objects = find_objs_for_compression(self.memory.driver)

        if len(to_compress_objects) > 0:
            # do initialize network operations (steps 1-3 above).
            self.do_1_to_3(mapping=False)
            # set phase_set to 1 (NOTE: this step doesn't really matter, but I want to keep phase_set informatio for all operations).
            phase_set = 1
            # the list to store all the newly created RBs
            all_new_RBs = []
            # for each object in to_compress_objects, make a list of its RBs, and compress over the preds.
            for obj in to_compress_objects:
                # the object controls firing. Fire the object, and infer a copy of object and RB in emerging recipient. Then, fire each pred and learn compressed version in emerging recipient.
                # make a firing order of POs.
                firingOrder = [obj]
                for myPO in obj.same_RB_POs:
                    firingOrder.append(myPO)
                # get the analog of the current to_compress_object.
                current_obj_analog = obj.myanalog
                # for each compressed object, there will have a new RB in newSet that conjoins the object to the compressed pred. Initialise made_RB to None.
                made_RB = None
                # to make a telling name for made_RB
                name = ''
                compressed_PO = None
                # fire each object in the firing order until local inhibitor fires.
                for currentPO in firingOrder:
                    # initialize phase_set_iterator and flags (local_inhibitor_fired).
                    phase_set_iterator = 1
                    self.local_inhibitor_fired = False
                    # 4.1-4.2) Fire the current RB in the firingOrder. Update the network in discrete time-steps until the globalInhibitor fires (i.e., the current active RB is inhibited by its inhibitor).
                    # a new ho_sem semantic unit will be connected to the compressed predicate for each role (a predicate to compress)
                    ho_sem = None
                    while self.memory.localInhibitor.act == 0:
                        # 4.3.1-4.3.10) update network activations.
                        currentPO.act = 1.0
                        self.time_step_activations(phase_set, self.ignore_object_semantics, self.ignore_memory_semantics, retrieval_license=False) # ekaterina: added retrieval_license
                        # Do compression.
                        self.memory, made_RB, compressed_PO, ho_sem = compression_routine(self.memory, made_RB, compressed_PO, ho_sem, self.gamma)
                        # fire the local_inhibitor if necessary.
                        self.time_step_fire_local_inhibitor()
                        # update GUI.
                        if self.doGUI:
                            self.time_step_doGUI(phase_set_iterator)
                    # PO firing is OVER.
                    self.post_count_by_operations()

                    # list of all the newly created RBs
                    if made_RB not in all_new_RBs:
                        all_new_RBs.append(made_RB)

            # construct the rest of the proposition with the rest of the predicates and objects (if any) from the same analog as the predicates to compress
            other_POs, other_RBs = [], []
            for myPO in current_obj_analog.myPOs:
                if myPO.predOrObj == 0 and len(myPO.same_RB_POs) == 1:
                    other_POs.append(myPO)
            for myPO in other_POs:
                for myRB in myPO.myRBs:
                    other_RBs.append(myRB)

            # full_prop_simple variable indicates if the original proposition contains any other units beyond the ones needing compression
            full_prop_simple = False
            for rb in other_RBs:
                if rb.myParentPs:
                    full_prop_simple = True

            # full_prop_complex variable indicates whether the original analog has full propositions (with Ps), but all the predicates are compressed
            full_prop_complex = False
            if not full_prop_simple and current_obj_analog.myPs:
                full_prop_complex = True

            rest_of_RBs = []
            if full_prop_simple:
                # create copies of the rest of the objects with one role and their predicates
                rest_of_RBs = self.collect_the_rest(other_RBs)

            if full_prop_simple or full_prop_complex:
                # create a new P unit
                newPname = 'p_' + str(len(self.memory.Ps)+1)
                compression_P = dataTypes.PUnit(newPname, 'newSet', None, True, None)
                compression_P.mode = 0
                compression_P.act = 1.0

                self.memory.Ps.append(compression_P)
                self.memory.newSet.Ps.append(compression_P)

                # connect all the all_new_RBs (recruited by the compression routine) to the new P unit
                for made_RB in all_new_RBs:
                    compression_P.myRBs.append(made_RB)
                    made_RB.myParentPs.append(compression_P)

                # connect the original RBs (with the simple roles, if any) to the new P unit
                if rest_of_RBs:
                    for myRB in rest_of_RBs:
                        compression_P.myRBs.append(myRB)
                        myRB.myParentPs.append(compression_P)

            # if 'remove_uncompressed' is True delete the original uncompressed structure from LTM
            if self.remove_uncompressed:
                # remove the original uncompressed structures from memory since the compressed structure is unpackable; do it through the current_obj_analog
                for i in range(len(current_obj_analog.myPs)):
                    self.memory.Ps.remove(current_obj_analog.myPs[i])
                for i in range(len(current_obj_analog.myRBs)):
                    self.memory.RBs.remove(current_obj_analog.myRBs[i])
                for i in range(len(current_obj_analog.myPOs)):
                    self.memory.POs.remove(current_obj_analog.myPOs[i])

                # remove current_obj_analog as well
                self.memory.analogs.remove(current_obj_analog)

            # put all items in newSet in a new analog
            self.memory = newSet_items_to_analog(self.memory)
        else:
            print('\nThere are no objects to compress over in the driver.\n')

        # self.post_phase_set_operations(retrieval_license=False, map_license=False)

        # reset inferences (i.e., reset .inferred, .my_maker_unit, and .my_made_unit fields from all the newSet and recipient units).
        self.memory = reset_inferences(self.memory)

        # return .asDORA state to starting .asDORA state.
        self.asDORA = DORA_state

    # ekaterina: function to collect the rest of the units in the driver after the compression and conjoin them and the compressed part together
    def collect_the_rest(self, other_RBs):
        # do initialize network operations (steps 1-3 above).
        self.do_1_to_3(mapping=False)
        phase_set = 1
        newRBs = []
        for rb in other_RBs:
            # fire the object and the predicate of each RB, infer a copy of each and also recruit a copy of RB in emerging recipient
            firingOrder = []
            firingOrder.append(rb.myPred[0])
            firingOrder.append(rb.myObj[0])

            # the copy of the current RB for the emerging proposition
            new_RB = None
            # fire each PO in the firing order until local inhibitor fires
            for currentPO in firingOrder:
                # initialize phase_set_iterator and flags (local_inhibitor_fired).
                phase_set_iterator = 1
                self.local_inhibitor_fired = False
                # 4.1-4.2) Fire the current RB in the firingOrder. Update the network in discrete time-steps until the globalInhibitor fires (i.e., the current active RB is inhibited by its inhibitor).
                while self.memory.localInhibitor.act == 0:
                    # 4.3.1-4.3.10) update network activations.
                    currentPO.act = 1.0
                    self.time_step_activations(phase_set, self.ignore_object_semantics, self.ignore_memory_semantics, retrieval_license=False)
                    # infer copies of POs and connect them to a newly recruited RB
                    self.memory, new_RB = infer_RB(self.memory, new_RB)
                    self.memory, new_RB = infer_PO(self.memory, new_RB, self.gamma)
                    # fire the local_inhibitor if necessary
                    self.time_step_fire_local_inhibitor()
                    # update GUI
                    if self.doGUI:
                        self.time_step_doGUI(phase_set_iterator)
                self.post_count_by_operations()
                # to make sure this function is reusable by the same tokens in do_unpacking()
                currentPO.my_made_unit = None
                currentPO.my_made_units = []
            # add the newly recruited RB to the list
            newRBs.append(new_RB)
        return newRBs

    # ekaterina: for .do_unpacking(); creates copies of other objects (the ones bound to simple roles) and binds them to the correct roles in the emerging recipient
    def bind_others_to_unpacked(self, other_POs, made_RBs):
        # do initialize network operations
        self.do_1_to_3(mapping=False)
        phase_set = 1
        # fire the rest of the objects in the original proposition to get them recruit copies of themselves and bind them to the unpacked roles
        firingOrder = []
        for po in other_POs:
            if po.predOrObj == 0:
                firingOrder.append(po)

        # fire each PO in the firing order until local inhibitor fires
        for currentPO in firingOrder:
            # print(currentPO.name)
            # initialize phase_set_iterator and flags (local_inhibitor_fired).
            phase_set_iterator = 1
            self.local_inhibitor_fired = False
            # 4.1-4.2) Fire the current RB in the firingOrder. Update the network in discrete time-steps until the globalInhibitor fires (i.e., the current active RB is inhibited by its inhibitor).
            while self.memory.localInhibitor.act == 0:
                # 4.3.1-4.3.10) update network activations.
                currentPO.act = 1.0
                self.time_step_activations(phase_set, self.ignore_object_semantics, self.ignore_memory_semantics, retrieval_license=False)
                # find the most active PO
                most_active_PO = get_most_active_unit(self.memory.driver.POs)
                # this is the RB which was created with the unpacked predicate and that still does not have an object
                made_RB = most_active_PO.same_RB_POs[0].my_made_unit.myRBs[0]
                # make a copy of the object in the driver that was bound to a simple role and bind it to the simpler's role copy
                self.memory, made_RB = infer_PO(self.memory, made_RB, self.gamma)
                # fire the local_inhibitor if necessary.
                self.time_step_fire_local_inhibitor()
                # update GUI.
                if self.doGUI:
                    self.time_step_doGUI(phase_set_iterator)

            # the RB with the object and its role learns a connection to the correct P unit
            self.memory = update_same_RB_POs(self.memory)
            if most_active_PO.predOrObj == 0:
                for rb in self.memory.newSet.RBs:
                    if not rb.myParentPs: # an RB which has not connection to any P units yet
                        # print('rb.name: ' + rb.name)
                        for p in self.memory.newSet.Ps: # checking both Ps in the newSet
                            # print('p.name: ' + p.name)
                            if rb.myPred[0].my_maker_unit != p.myRBs[0].myPred[0].my_maker_unit: # and whose predicate is not made by the same PO unit which made the predicate already bound to an object in the other RB of this P
                                p.myRBs.append(rb)
                                rb.myParentPs.append(p)

            # PO firing is OVER.
            self.post_count_by_operations()

    def do_unpacking(self):
        # make sure DORA is in DORA mode.
        DORA_state = self.asDORA
        self.asDORA = True

        # make a list predicates (if any) with higher-order semantics
        to_unpack_preds = find_preds_to_unpack(self.memory.driver)

        # perform unpacking if there are any such predicates
        if len(to_unpack_preds) > 0:
            # do initialize network operations (steps 1-3 above).
            self.do_1_to_3(mapping=False)
            # set phase_set to 1 (NOTE: this step doesn't really matter, but I want to keep phase_set informatio for all operations).
            phase_set = 1
            # for each predicate in to_unpack_preds, add its object to the firing order and create copies of everything to unpack in prop
            for pred in to_unpack_preds:
                # the predicate controls firing. Fire the predicate and learn an unpacked version for each ho_sem in emerging recipient; then fire object bound to the compressed predicate and infer a copy of it in an energing recipient
                # make a firing order of POs.
                firingOrder = [pred]
                for myPO in pred.same_RB_POs:
                    firingOrder.append(myPO)
                # get the analog of the current to_unpack_pred
                current_pred_analog = pred.myanalog
                # each compressed predicate will need two new RBs that bound the roles unpacked from the compressed predicate to the object
                made_RBs = []
                # fire each PO in the firing order until local inhibitor fires
                for currentPO in firingOrder:
                    # print(currentPO.name)
                    # initialize phase_set_iterator and flags (local_inhibitor_fired).
                    phase_set_iterator = 1
                    self.local_inhibitor_fired = False
                    # 4.1-4.2) Fire the current RB in the firingOrder. Update the network in discrete time-steps until the globalInhibitor fires (i.e., the current active RB is inhibited by its inhibitor).
                    # ho_sem = None
                    while self.memory.localInhibitor.act == 0:
                        # 4.3.1-4.3.10) update network activations.
                        currentPO.act = 1.0
                        self.time_step_activations(phase_set, self.ignore_object_semantics, self.ignore_memory_semantics, retrieval_license=True) # retrieval_license needs to be TRUE to UNPACK the compressed predicate
                        # do unpacking
                        self.memory, made_RBs, hoSemCount = unpacking_routine(self.memory, made_RBs, currentPO, self.gamma, self.tokenize)
                        # fire the local_inhibitor if necessary.
                        self.time_step_fire_local_inhibitor()
                        # update GUI.
                        if self.doGUI:
                            self.time_step_doGUI(phase_set_iterator)
                    # PO firing is OVER.
                    self.post_count_by_operations()
                    # print(made_RBs)

                # construct the rest of the proposition with the rest of the predicates and objects from the same analog as the predicates to unpack
                other_POs, other_RBs = [], [] # lists to store those that were NOT used during unpacking
                for myPO in current_pred_analog.myPOs:
                    if myPO not in firingOrder:
                        other_POs.append(myPO)
                for myPO in other_POs:
                    for myRB in myPO.myRBs:
                        if myRB not in other_RBs and myRB != pred.myRBs:
                            other_RBs.append(myRB)

            # create copies of the rest of the objects and predicates
            made_RBs = self.bind_others_to_unpacked(other_POs, made_RBs)

            # self.tokenize == False: all the unpacked propositions are housed in one new analog
            # self.tokenize == True: multiple analogs will house the unpacked propositions - one prop per analog
            if not self.tokenize:
                # put all items in newSet in a new analog
                self.memory = newSet_items_to_analog(self.memory)
            else: # if self.tokenize
                for p in self.memory.newSet.Ps: # how many analogs we need - one per proposition
                    # create an analog
                    new_analog = dataTypes.Analog()
                    self.memory.analogs.append(new_analog)
                    # add Ps from newSet to the new analog
                    new_analog.myPs.append(p)
                    p.myanalog = new_analog
                    # add RBs from newSet to the new analog
                    for rb in p.myRBs:
                        new_analog.myRBs.append(rb)
                        rb.myanalog = new_analog
                        # add POs from newSet to the new analog
                        for pred in rb.myPred:
                            new_analog.myPOs.append(pred)
                            pred.myanalog = new_analog
                        for obj in rb.myObj:
                            new_analog.myPOs.append(obj)
                            obj.myanalog = new_analog

            # remove the original compressed structures from memory; do it through the current_pred_analog
            if self.remove_compressed:
                for i in range(len(current_pred_analog.myPs)):
                    self.memory.Ps.remove(current_pred_analog.myPs[i])
                for i in range(len(current_pred_analog.myRBs)):
                    self.memory.RBs.remove(current_pred_analog.myRBs[i])
                for i in range(len(current_pred_analog.myPOs)):
                    self.memory.POs.remove(current_pred_analog.myPOs[i])

            # remove current_pred_analog as well
            self.memory.analogs.remove(current_pred_analog)
        else:
            print('There are no predicates in the memory that could be unpacked')

        # reset inferences (i.e., reset .inferred, .my_maker_unit, and .my_made_unit fields from all the newSet and recipient units).
        self.memory = reset_inferences(self.memory)

        # return .asDORA state to starting .asDORA state.
        self.asDORA = DORA_state

    ######################################################################
    ######################################################################
    ######################################################################

    ######################################
    ###### DORA TIME_STEP FUNCTIONS ######
    ######################################
    # functions implementing operations performed during a single time-step in DORA.
    # function to perform basic network activation update for a time_step in the phase set.
    def time_step_activations(self, phase_set, ignore_object_semantics=False, ignore_memory_semantics=False, retrieval_license=False): # ekaterina: added retrieval_license
        # initialize the input to all tokens and semantic units.
        self.memory = initialize_input(self.memory)
        # 4.3.2) Update modes of all P units in the driver and the recipient.
        if self.count_by_RBs:
            for myP in self.memory.driver.Ps:
                myP.get_Pmode()
            for myP in self.memory.recipient.Ps:
                myP.get_Pmode()
        # 4.3.3) Update input to driver token units.
        self.memory = update_driver_inputs(self.memory, self.asDORA, self.lateral_input_level)
        # 4.3.4-5) Update input to and activation of PO and RB inhibitors.
        for myRB in self.memory.driver.RBs:
            myRB.update_inhibitor_input()
            myRB.update_inhibitor_act()
        # update PO inhibitor act only if in DORA mode (i.e., asDORA == True).
        for myPO in self.memory.driver.POs:
            myPO.update_inhibitor_input()
            if self.asDORA:
                myPO.update_inhibitor_act()
        for myRB in self.memory.recipient.RBs:
            myRB.update_inhibitor_input()
            #RB.update_inhibitor_act()
        for myPO in self.memory.recipient.POs:
            myPO.update_inhibitor_input()
            if self.asDORA:
                myPO.update_inhibitor_act()
        # 4.3.6-7) Update input and activation of local and global inhibitors.
        self.memory.localInhibitor.checkDriverPOs(self.memory)
        self.memory.globalInhibitor.checkDriverRBs(self.memory)
        # 4.3.8) Update input to semantic units.
        for semantic in self.memory.semantics:
            # ignore input to semantic units from POs in object mode if ignore_object_semantics==True (i.e., if DORA is focusing on relational properties (from Hummel & Holyoak, 2003)).
            semantic.update_input(self.memory, self.ho_sem_act_flow, retrieval_license, ignore_object_semantics, ignore_memory_semantics)
        # 4.3.9) Update input to all tokens in the recipient and emerging recipient (i.e., newSet).
        self.memory = update_recipient_inputs(self.memory, self.asDORA, phase_set, self.lateral_input_level, self.ignore_object_semantics)
        self.memory = update_newSet_inputs(self.memory)
        # 4.3.10) Update activations of all units in the driver, recipient, and newSet, and all semanticss.
        self.memory = update_activations_run(self.memory, self.gamma, self.delta, self.HebbBias, phase_set)

    # function to fire the local inhibitor if necessary.
    def time_step_fire_local_inhibitor(self):
        if self.asDORA and self.memory.localInhibitor.act >= 0.99 and not self.local_inhibitor_fired:
            self.memory = self.memory.localInhibitor.fire_local_inhibitor(self.memory)
            self.local_inhibitor_fired = True

    # function to do GUI.
    def time_step_doGUI(self, phase_set_iterator):
        if self.doGUI:
            # check for keypress for pause.
            debug = False
            pause = False
            for event in pygame.event.get():
                if not hasattr(event,'key'):
                    continue
                elif event.key == K_p and event.type == KEYDOWN:
                    # graphics are paused, wait for unpause.
                    pause = True
            if pause:
                wait = True
                while wait:
                    for event2 in pygame.event.get():
                        if event2.type == KEYDOWN:
                            if event2.key == K_p:
                                pause = False
                                wait = False
                            elif event2.key == K_d:
                                # enter debug.
                                debug = True
            ###########################################################
            ############### ENTER DEBUGGING DURING RUN! ###############
            # for DEBUGGING, enters set_trace() after a GUI pause.
            ###########################################################
            if debug:
                pdb.set_trace()
            # check for update GUI.
            if phase_set_iterator % self.GUI_update_rate == 0:
                # update_GUI.
                self.screen, self.memory = DORA_GUI.run_GUI(self.screen, self.GUI_information, self.memory, False)

    ####################################################
    #    DORA POST COUNT_BY AND PHASE_SET FUNCTIONS    #
    ####################################################
    # function to perform operations that occur after PO (if firing by POs) or RB (if firing by RBs) fires (i.e., what we're calling "count_by" operations as they occur after the firing of of the token you're firing (or counting) by).
    def post_count_by_operations(self):
        # fire the globalInhibitor.
        self.memory = self.memory.globalInhibitor.fire_global_inhibitor(self.memory)
        # reset the memory.localInhibitor.act and memory.globalInhibitor.act back to 0.0.
        self.memory.localInhibitor.act = 0.0
        self.memory.globalInhibitor.act = 0.0
        # reset the RB and PO inhibitors.
        for myRB in self.memory.RBs:
            myRB.reset_inhibitor()
        for myPO in self.memory.POs:
            myPO.reset_inhibitor()

    # functions to perform post-phase_set operations.
    def post_phase_set_operations(self, retrieval_license, map_license, inferred_new_P=False):
        # if you were doing retrieval (i.e., if retrieval_license is True), then use the Luce choice axiom here to retrieve items from memorySet into the recipient.
        if retrieval_license:
            self.memory = retrieve_tokens(self.memory, self.bias_retrieval_analogs, self.use_relative_act)
        # reset the mode of all P units in the recipient back to neutral (i.e., 0);
        for myP in self.memory.recipient.Ps:
            myP.initialize_Pmode()
        # reset the activation and input of all units back to 0.
        self.memory = initialize_AM(self.memory)
        # if you made a new P during relation formation, name it with the name of all its RBs.
        if inferred_new_P:
            # the new P is the last P in memory.Ps. Name it.
            name_string = ''
            # NOTE: I've added a try/except here because I got an odd error once that I've been unable to recreate. I'm leaving it here just in case it pops up again.
            try:
                len(self.memory.Ps[-1].myRBs)
            except:
                print('\nHey, you got a an error awhile ago that you were unable to reproduce. Basically, it seems you learned a P unit with no RBs (or something to that effect). You added a try/except to catch it in case it popped up again. It has. You will want to look very carefully at what happened with the latest P unit that has been made.\n')
                pdb.set_trace()
            for myRB in self.memory.Ps[-1].myRBs:
                name_string = name_string+'+'+myRB.name
            self.memory.Ps[-1].name = name_string
        # remove all links between POs and semantics that are below threshold (=0.01), and round up any connections that are above 0.999.
        self.memory = del_small_link(self.memory, 0.1)
        self.memory = round_big_link(self.memory, 0.9)
        # 5) If mapping is licenced, update the mapping connections and update the max_map field for all driver and recipient tokens.
        if map_license:
            # update mapping connections.
            self.memory = update_mappingConnections(self.memory, self.eta)
            # update max_map fields.
            self.memory = get_max_maps(self.memory)
            # reset hypotheses back to 0.0
            self.memory = reset_mappingHyps(self.memory)
        # recalibrate PO weights.
        #self.memory = calibrate_weight(self.memory)

    # the kludgy comparitor function that runs after the phase set.
    def do_kludge_comparitor(self):
        # run kludgy comparitor.
        # make sure I have RBs.
        if self.count_by_RBs:
            # comparitor all pairs of preds in driver and recipient. Make all driver pred pairs that are either connected to same P, or not connected to a myP.
            # first, the driver.
            driver_pred_pairs = []
            for PO1 in self.memory.driver.POs:
                if PO1.predOrObj == 1:
                    PO1.get_index(self.memory)
                    for PO2 in self.memory.driver.POs[PO1.my_index+1::]:
                        if PO2.predOrObj == 1:
                            for RB1 in PO1.myRBs:
                                break_flag = False
                                for RB2 in PO2.myRBs:
                                    if (len(RB1.myParentPs) == 0) and(len(RB2.myParentPs) == 0):
                                        # both POs are connected to RBs with no Ps, so comparitor them.
                                        driver_pred_pairs.append([PO1,PO2])
                                        break_flag = True
                                        break
                                    elif RB1.myParentPs[0] is RB2.myParentPs[0]:
                                        # the two POs share a P unit, so comparitor them.
                                        driver_pred_pairs.append([PO1,PO2])
                                        break_flag = True
                                        break
                                if break_flag:
                                    break
            # now the recipient POs.
            recipient_pred_pairs = []
            for PO1 in self.memory.recipient.POs:
                if PO1.predOrObj == 1:
                    PO1.get_index(self.memory)
                    for PO2 in self.memory.recipient.POs[PO1.my_index+1::]:
                        if PO2.predOrObj == 1:
                            for RB1 in PO1.myRBs:
                                break_flag = False
                                for RB2 in PO2.myRBs:
                                    if RB1.myParentPs[0] is RB2.myParentPs[0]:
                                        # the two POs share a P unit, so comparitor them.
                                        recipient_pred_pairs.append([PO1,PO2])
                                        break_flag = True
                                        break
                                    elif (len(RB1.myParentPs) == 0) and(len(RB2.myParentPs) == 0):
                                        # both POs are connected to RBs with no Ps, so comparitor them.
                                        recipient_pred_pairs.append([PO1,PO2])
                                        break_flag = True
                                        break
                                if break_flag:
                                    break
            # now run the comparitor on all driver and recipient pairs.
            for pair in driver_pred_pairs:
                self.memory = kludgey_comparitor(pair[0], pair[1], self.memory)
            for pair in recipient_pred_pairs:
                self.memory = kludgey_comparitor(pair[0], pair[1], self.memory)

    # function for use during relational generalisation. This function groups all recipient units that map to driver tokens into a single analog.
    def group_recip_maps(self):
        # find all analogs in the recipient that have mapped units and add them to the analog_list.
        analog_list = []
        for myPO in self.memory.POs:
            if myPO.max_map > 0.0:
                # add the analog that PO is in to analog_list (assuming it is not already in there).
                if myPO.myanalog not in analog_list:
                    analog_list.append(myPO.myanalog)
        for myRB in self.memory.RBs:
            if myRB.max_map > 0.0:
                # add the analog that PO is in to analog_list (assuming it is not already in there).
                if myRB.myanalog not in analog_list:
                    analog_list.append(myRB.myanalog)
        for myP in self.memory.Ps:
            if myP.max_map > 0.0:
                # add the analog that PO is in to analog_list (assuming it is not already in there).
                if myP.myanalog not in analog_list:
                    analog_list.append(myP.myanalog)
        # if necessary (i.e., if analog_list contains multiple analogs), combine all analogs in analog_list into a single analog.
        if len(analog_list) > 1:
            new_analog = dataTypes.Analog()
            for analog in analog_list:
                # add all the POs, RBs, and Ps from the analogs in analog_list to the new_analog.
                for myPO in analog.myPOs:
                    # add the PO to new_analog and update the .myanalog information for that myPO.
                    new_analog.myPOs.append(myPO)
                    myPO.myanalog = new_analog
                for myRB in analog.myRBs:
                    # add the PO to new_analog and update the .myanalog information for that myPO.
                    new_analog.myRBs.append(myRB)
                    myRB.myanalog = new_analog
                for myP in analog.myPs:
                    # add the P to new_analog and update the .myanalog information for that myP.
                    new_analog.myPs.append(myP)
                    myP.myanalog = new_analog
                # and now delete the old analog from self.memory.analogs.
                analog_index = self.memory.analogs.index(analog)
                self.memory.analogs.pop(analog_index)
                del(analog)
            # ekaterina: newly created analog needs to be added to the memory
            self.memory.analogs.append(new_analog)

######################################################################

#######################################
######### CORE DORA FUNCTIONS #########
#######################################
# function to make AM without making copies of items in LTM.
# noinspection PyPep8Naming
def make_AM(memory):
    # for each token, if it is in an AM set (driver, recipient), then make sure all sub-tokens are also in that set. Make sure that all tokens from the same analog are in the same set or in memory (i.e., tokens from the same analog CANNOT be in different AM sets). run findDriverRecipient().
    # for each token unit, make sure all subtokens are in the same set. Also, make sure that if a token is to enter recipient, that it checks to make sure none of it's subtokens are in the driver, and, if they are, that it remains in memory.
    for Group in memory.Groups:
        if Group.set != 'memory':
            # make sure all subtokens are in the same set.
            Group = set_sub_tokens(Group)
    for myP in memory.Ps:
        if myP.set != 'memory':
            # make sure all subtokens are in the same set.
            myP = set_sub_tokens(myP)
    for myRB in memory.RBs:
        if myRB.set != 'memory':
            # make sure all subtokens are in the same set.
            myRB = set_sub_tokens(myRB)
    for myPO in memory.POs:
        if myPO.set != 'memory':
            # make sure all subtokens are in the same set.
            myPO = set_sub_tokens(myPO)
    # and bring all the copied items from memory into AM (i.e., into driver/recipient).
    memory = findDriverRecipient(memory)
    # returns.
    return memory

# function to make sure all sub-tokens of a token to enter AM are in the same set. Function also checks that any item to enter the recipient, does not have driver sub-tokens.
def set_sub_tokens(token):
    # check what kind of token you're dealing with.
    if token.my_type == 'Group':
        # if you're dealing with a Group, then for each of it's sub-groups, sub-Ps, and sub-RBs, set that sub_token.set to the same set as the Group, and run set_sub_tokens on that sub-token.
        # check to make sure that if the Group is in the recipient, none of it's subtokens are in the driver.
        go_on = True
        if token.set == 'recipient':
            go_on = check_sub_tokens(token)
        if go_on:
            for Group_under in token.myChildGroups:
                Group_under.set = token.set
                Group_under = set_sub_tokens(Group_under)
            for myP in token.myPs:
                myP.set = token.set
                myP = set_sub_tokens(myP)
            for myRB in token.myRBs:
                myRB.set = token.set
                myRB = set_sub_tokens(myRB)
        else:
            # set the token.set to 'memory'.
            token.set = 'memory'
    elif token.my_type == 'P':
        # if you're dealing with a P, then for each of it's RBs, set that myRB.set to the same set as the P, and run set_sub_tokens on the myRB.
        # check to make sure that if the P is in the recipient, none of it's subtokens are in the driver.
        go_on = True
        if token.set == 'recipient':
            go_on = check_sub_tokens(token)
        if go_on:
            for myRB in token.myRBs:
                myRB.set = token.set
                myRB = set_sub_tokens(myRB)
        else:
            # set the token.set to 'memory'.
            token.set = 'memory'
    elif token.my_type == 'RB':
        # if you're dealing with a RB, then for each of it's child-Ps and POs, set that token.set to the same set as the RB, and run set_sub_tokens on the the sub-token.
        # check to make sure that if the RB is in the recipient, none of it's subtokens are in the driver.
        go_on = True
        if token.set == 'recipient':
            go_on = check_sub_tokens(token)
        if go_on:
            if len(token.myPred) > 0:
                token.myPred[0].set = token.set
                token.myPred[0] = set_sub_tokens(token.myPred[0])
            if len(token.myObj) > 0:
                token.myObj[0].set = token.set
                token.myObj[0] = set_sub_tokens(token.myObj[0])
            elif len(token.myChildP) > 0:
                token.myChildP[0].set = token.set
                token.myChildP[0] = set_sub_tokens(token.myChildP[0])
        else:
            # set the token.set to 'memory'.
            token.set = 'memory'
    # returns.
    return token

# function to check all sub-tokens of a token bound for the recipient, to make sure that none are in the driver.
def check_sub_tokens(token):
    # set the go_on_flag to True (indicating that that there are no driver sub-tokens of a recipient super-token).
    go_on_flag = True
    # make sure you're dealing with a recipient token (this is a redundent check, but is here for safety).
    if token.set == 'recipient':
        # make sure all sub-tokens are NOT in the driver.
        if token.my_type == 'Group':
            # make sure none of my sub-groups (or their sub-tokens) are in the driver.
            for sub_group in token.myGroups:
                if sub_group.set == 'driver':
                    # set token.set to 'memory', go_on_flag to False, and break the loop.
                    token.set = 'memory'
                    go_on_flag = False
                    break
                else:
                    # make sure none of the sub-token of the sub-group are in the driver.
                    go_on_flag = check_sub_tokens(sub_group)
                    # if go_on_flag is now False (i.e., the token has sub-tokens in the driver), token.set should be set to 'memory' (as it should not be retrieved into the recipient).
                    if not go_on_flag:
                        token.set = 'memory'
            # if go_on_flag is still True, make sure none of my Ps (or their sub-tokens) are in the driver.
            if go_on_flag:
                for myP in token.myPs:
                    if myP.set == 'driver':
                        # set token.set to 'memory', go_on_flag to False, and break the loop.
                        token.set = 'memory'
                        go_on_flag = False
                        break
                    else:
                        # make sure none of the sub-token of the sub-group are in the driver.
                        go_on_flag = check_sub_tokens(myP)
                        # if go_on_flag is now False (i.e., the token has sub-tokens in the driver), token.set should be set to 'memory' (as it should not be retrieved into the recipient).
                        if not go_on_flag:
                            token.set = 'memory'
            # if go_on_flag is still True, make sure none of my RBs (or their sub-tokens) are in the driver.
            if go_on_flag:
                for myRB in token.myRBs:
                    if myRB.set == 'driver':
                        # set token.set to 'memory', go_on_flag to False, and break the loop.
                        token.set = 'memory'
                        go_on_flag = False
                        break
                    else:
                        # make sure none of the sub-token of the sub-group are in the driver.
                        go_on_flag = check_sub_tokens(myRB)
                        # if go_on_flag is now False (i.e., the token has sub-tokens in the driver), token.set should be set to 'memory' (as it should not be retrieved into the recipient).
                        if not go_on_flag:
                            token.set = 'memory'
        elif token.my_type == 'P':
            # make sure none of my RBs (or their sub-tokens) are in the driver.
            for myRB in token.myRBs:
                if myRB.set == 'driver':
                    # set token.set to 'memory', go_on_flag to False, and break the loop.
                    token.set = 'memory'
                    go_on_flag = False
                    break
                else:
                    # make sure none of the sub-token of the sub-group are in the driver.
                    go_on_flag = check_sub_tokens(myRB)
                    # if go_on_flag is now False (i.e., the token has sub-tokens in the driver), token.set should be set to 'memory' (as it should not be retrieved into the recipient).
                    if not go_on_flag:
                        token.set = 'memory'
        elif token.my_type == 'RB':
            # make sure none of my POs are in the driver.
            if token.myPred[0].set == 'driver':
                # set token.set to 'memory' and go_on_flag to False.
                token.set = 'memory'
                go_on_flag = False
            # make sure you only check the objs of RBs not taking a child P as an argument.
            if len(token.myObj) > 0:
                if token.myObj[0].set == 'driver':
                    # set token.set to 'memory' and go_on_flag to False.
                    token.set = 'memory'
                    go_on_flag = False
    # returns.
    return go_on_flag

# function to make copies of items from memory to enter AM.
def make_AM_copy(memory):
    # go through memory and make a list of all analogs to be copied. For each item, if it is to be retrieved into AM, then check if its analog is in the list of analogs to enter AM. If not, add it.
    analogs_to_copy = []
    for analog in memory.analogs:
        # check if the analog is to be copied, and if so, copy it.
        copy_analog_flag = check_analog_for_tokens_to_copy(analog)
        if copy_analog_flag and (analog not in analogs_to_copy):
            analogs_to_copy.append(analog)
    # now copy all analogs from analogs_to_copy into memory.
    for analog in analogs_to_copy:
        memory = copy_analog(analog, memory)
    # and bring all the copied items from memory into AM (i.e., into driver/recipient).
    memory = findDriverRecipient(memory)
    # returns.
    return memory

# function to check an analog for whether it contains any tokens to copy.
def check_analog_for_tokens_to_copy(analog):
    # check if analog is to be copied. Go through all tokens in the analog and see whether the .set field of any is NOT 'memory'. If it is not, break the loop and copy the analog to analogs_to_copy.
    copy_analog_flag = False
    # first check all the Groups.
    if not copy_analog_flag:
        for Group in analog.myGroups:
            if Group.set != 'memory':
                # set copy_analog_flag to True and break the loop.
                copy_analog_flag = True
                break
    # if copy_analog_flag is still False, check the Ps.
    if not copy_analog_flag:
        for myP in analog.myPs:
            if myP.set != 'memory':
                # set copy_analog_flag to True and break the loop.
                copy_analog_flag = True
                break
    # if copy_analog_flag is still False, check the RBs.
    if not copy_analog_flag:
        for myRB in analog.myRBs:
            if myRB.set != 'memory':
                # set copy_analog_flag to True and break the loop.
                copy_analog_flag = True
                break
    # if copy_analog_flag is still False, check the POs.
    if not copy_analog_flag:
        for myPO in analog.myPOs:
            if myPO.set != 'memory':
                # set copy_analog_flag to True and break the loop.
                copy_analog_flag = True
                break
    # return copy_analog_flag
    return copy_analog_flag

# function to copy a to be retrieved analog and it's elements into AM.
def copy_analog(analog, memory):
    # make a copy of the analog. NOTE: you can't use copy here because of recursion issues, so you're rolling your own copy code. Maybe there's a package for this, but then you're you, so you're not looking it up.
    new_analog = dataTypes.Analog()
    # make all tokens from the to be copied analog.
    new_analog, memory = copy_analog_tokens(analog, new_analog, memory)
    # in the original analog, set the .set field of each element to 'memory'.
    analog = clear_set(analog)
    # for each token in the copied analog, if a token is to be retrieved, then make sure all tokens below it are also to be retrieved (e.g., if a P is to be retrieved into 'recipient', make sure all RBs and POs connected to those RBs also have their .set field set to 'recipient).
    new_analog = retrieve_all_relevant_tokens(new_analog)
    # for each token in the copied analog, delete any token that is not be be retrieved (i.e., the .set field is 'memory') (I don't think you need this part: AND there are no higher tokens that are to be retrieved (e.g., a PO has no RBs to be retrieved)), delete that token. Make sure all items above and below that token have that token removed from their list of connections (e.g., a to be deleted RB is removed as a connection its parent and child Ps, and its predicate and object POs).
    new_analog = delete_unretrieved_tokens(new_analog)
    # place copied analog into memory.
    memory.analogs.append(new_analog)
    # returns.
    return memory

# function to make all tokens from the to be copied analog.
def copy_analog_tokens(analog, new_analog, memory):
    # start with Ps. (1) make the P. (2) then make each RB. Connect the RB to the P. (3) For each RB's POs, (4) check if a PO by that name already exists in new_analog.myPOs, and if so, connect that PO to currentRB, otherwise, make the PO, and connect it to the RB. Then, for each RB without Ps, start with (3) above. Then, for each PO without RBs, start with (4) above.
    for myP in analog.myPs:
        # make a copy of the P.
        copy_P = dataTypes.PUnit(myP.name, myP.set, new_analog, False, new_analog)
        # put the copied P in new_analog and in memory.
        new_analog.myPs.append(copy_P)
        memory.Ps.append(copy_P)
        # make copy_P's RB units.
        for myRB in myP.myRBs:
            # make a copy of the RB.
            copy_RB = dataTypes.RBUnit(myRB.name, myRB.set, new_analog, False, new_analog)
            # put the copy_RB in new_analog and in memory.
            new_analog.myRBs.append(copy_RB)
            memory.RBs.append(copy_RB)
            # connect the copy_RB to copy_P and vise versa.
            copy_RB.myParentPs.append(copy_P)
            copy_P.myRBs.append(copy_RB)
            # make the RBs pred (if it does not already exist). Check if a pred with the same name as myRB.myPred[0] already exists in new_analog.myPOs.
            make_new_PO = True
            for myPO in new_analog.myPOs:
                if myPO.name == myRB.myPred[0].name:
                    # the PO is already in new_analog, so just connect it to the copy_RB.
                    myPO.myRBs.append(copy_RB)
                    copy_RB.myPred.append(myPO)
                    # set make_new_PO flag to False.
                    make_new_PO = False
                    break
            # if the PO does not already exist in the new_analog, then make it.
            if make_new_PO:
                # make the RB's pred.
                copy_pred = dataTypes.POUnit(myRB.myPred[0].name, myRB.myPred[0].set, new_analog, False, new_analog, 1)
                # put the copy_pred in new_analog and in memory.
                new_analog.myPOs.append(copy_pred)
                memory.POs.append(copy_pred)
                # connect the copy_pred to copy_RB and vise versa.
                copy_pred.myRBs.append(copy_RB)
                copy_RB.myPred.append(copy_pred)
                # make all the semantic connections for copy_pred.
                for link in myRB.myPred[0].mySemantics:
                    # create a new link for the copy_pred.
                    new_link = dataTypes.Link(copy_pred, None, link.mySemantic, link.weight)
                    # add the new_link to memory.Links, new_pred.semantics, and link.mySemantic.myPOs.
                    memory.Links.append(new_link)
                    copy_pred.mySemantics.append(new_link)
                    link.mySemantic.myPOs.append(new_link)
            # make the RBs object (if it does not already exist).
            make_new_PO = True
            for myPO in new_analog.myPOs:
                if myPO.name == myRB.myObj[0].name:
                    # the PO is already in new_analog, so just connect it to the copy_RB.
                    myPO.myRBs.append(copy_RB)
                    copy_RB.myObj.append(myPO)
                    # set make_new_PO flag to False.
                    make_new_PO = False
                    break
            # if the PO does not already exist in the new_analog, then make it.
            if make_new_PO:
                # make the RB's object.
                copy_obj = dataTypes.POUnit(myRB.myObj[0].name, myRB.myObj[0].set, new_analog, False, new_analog, 0)
                # put the copy_obj in new_analog and in memory.
                new_analog.myPOs.append(copy_obj)
                memory.POs.append(copy_obj)
                # connect the copy_obj to copy_RB and vise versa.
                copy_obj.myRBs.append(copy_RB)
                copy_RB.myObj.append(copy_obj)
                # make all the semantic connections for copy_obj.
                for link in myRB.myObj[0].mySemantics:
                    # create a new link for the copy_obj.
                    new_link = dataTypes.Link(copy_obj, None, link.mySemantic, link.weight)
                    # add the new_link to memory.Links, copy_obj.semantics, and link.mySemantic.myPOs.
                    memory.Links.append(new_link)
                    copy_obj.mySemantics.append(new_link)
                    link.mySemantic.myPOs.append(new_link)
    # now make all RBs that don't have Ps.
    for myRB in analog.myRBs:
        if len(myRB.myParentPs) == 0:
            # make a copy of the RB.
            copy_RB = dataTypes.RBUnit(myRB.name, myRB.set, new_analog, False, new_analog)
            # put the copy_RB in new_analog and in memory.
            new_analog.myRBs.append(copy_RB)
            memory.RBs.append(copy_RB)
            # make the RBs pred (if it does not already exist). Check if a pred with the same name as myRB.myPred[0] already exists in new_analog.myPOs.
            make_new_PO = True
            for myPO in new_analog.myPOs:
                if myPO.name == myRB.myPred[0].name:
                    # the PO is already in new_analog, so just connect it to the copy_RB.
                    myPO.myRBs.append(copy_RB)
                    copy_RB.myPred.append(myPO)
                    # set make_new_PO flag to False.
                    make_new_PO = False
                    break
            # if the PO does not already exist in the new_analog, then make it.
            if make_new_PO:
                # make the RB's pred.
                copy_pred = dataTypes.POUnit(myRB.myPred[0].name, myRB.myPred[0].set, new_analog, False, new_analog, 1)
                # put the copy_pred in new_analog and memory.
                new_analog.myPOs.append(copy_pred)
                memory.POs.append(copy_pred)
                # connect the copy_pred to copy_RB and vise versa.
                copy_pred.myRBs.append(copy_RB)
                copy_RB.myPred.append(copy_pred)
                # make all the semantic connections for copy_pred.
                for link in myRB.myPred[0].mySemantics:
                    # create a new link for the copy_pred.
                    new_link = dataTypes.Link(copy_pred, None, link.mySemantic, link.weight)
                    # add the new_link to memory.Links, new_pred.semantics, and link.mySemantic.myPOs.
                    memory.Links.append(new_link)
                    copy_pred.mySemantics.append(new_link)
                    link.mySemantic.myPOs.append(new_link)
            # make the RBs object (if it does not already exist).
            make_new_PO = True
            for myPO in new_analog.myPOs:
                if myPO.name == myRB.myObj[0].name:
                    # the PO is already in new_analog, so just connect it to the copy_RB.
                    myPO.myRBs.append(copy_RB)
                    copy_RB.myObj.append(myPO)
                    # set make_new_PO flag to False.
                    make_new_PO = False
                    break
            # if the PO does not already exist in the new_analog, then make it.
            if make_new_PO:
                # make the RB's object.
                copy_obj = dataTypes.POUnit(myRB.myObj[0].name, myRB.myObj[0].set, new_analog, False, new_analog, 0)
                # put the copy_obj in new_analog and memory.
                new_analog.myPOs.append(copy_obj)
                memory.POs.append(copy_obj)
                # connect the copy_obj to copy_RB and vise versa.
                copy_obj.myRBs.append(copy_RB)
                copy_RB.myObj.append(copy_obj)
                # make all the semantic connections for copy_obj.
                for link in myRB.myObj[0].mySemantics:
                    # create a new link for the copy_obj.
                    new_link = dataTypes.Link(copy_obj, None, link.mySemantic, link.weight)
                    # add the new_link to memory.Links, copy_obj.semantics, and link.mySemantic.myPOs.
                    memory.Links.append(new_link)
                    copy_obj.mySemantics.append(new_link)
                    link.mySemantic.myPOs.append(new_link)
    # make all POs that don't have RBs.
    for myPO in analog.myPOs:
        if len(myPO.myRBs) == 0:
            make_new_PO = True
            for checkPO in new_analog.myPOs:
                if checkPO.name == myPO.name:
                    # the PO is already in new_analog, so set make_new_PO flag to False.
                    make_new_PO = False
                    break
            # if the PO does not already exist in the new_analog, then make it.
            if make_new_PO:
                # make the RB's object.
                copy_obj = dataTypes.POUnit(myPO.name, myPO.set, new_analog, False, new_analog, 0)
                # put the copy_obj in new_analog and memory.
                new_analog.myPOs.append(copy_obj)
                memory.POs.append(copy_obj)
                # make all the semantic connections for copy_obj.
                for link in myPO.mySemantics:
                    # create a new link for the copy_obj.
                    new_link = dataTypes.Link(copy_obj, None, link.mySemantic, link.weight)
                    # add the new_link to memory.Links, copy_obj.semantics, and link.mySemantic.myPOs.
                    memory.Links.append(new_link)
                    copy_obj.mySemantics.append(new_link)
                    link.mySemantic.myPOs.append(new_link)
    # returns.
    return new_analog, memory

# function to clear .set field for all tokens in an analog.
def clear_set(analog):
    for Group in analog.myGroups:
        Group.set = 'memory'
    for myP in analog.myPs:
        myP.set = 'memory'
    for myRB in analog.myRBs:
        myRB.set = 'memory'
    for myPO in analog.myPOs:
        myPO.set = 'memory'
    # returns.
    return analog

# function to make sure all lower tokens of a to be retrieved into AM token in an analog are also set to be retrieved.
def retrieve_all_relevant_tokens(analog):
    # check each token, and if it is to be retrieved into AM (i.e., .set is NOT 'memory), make sure all tokens below it are also be be retrieved into AM.
    for Group in analog.myGroups:
        if Group.set != 'memory':
            Group = retrieve_lower_tokens(Group)
    for myP in analog.myPs:
        if myP.set != 'memory':
            myP = retrieve_lower_tokens(myP)
    for myRB in analog.myRBs:
        if myRB.set != 'memory':
            myRB = retrieve_lower_tokens(myRB)
    for myPO in analog.myPOs:
        if myPO.set != 'memory':
            myPO = retrieve_lower_tokens(myPO)
    # returns.
    return analog

# function to make sure all a token's sub-tokens are in the proper .set
def retrieve_lower_tokens(token):
    # check what kind of token you're dealing with.
    if token.my_type == 'Group':
        # if you're dealing with a Group, then for each of it's sub-groups, sub-Ps, and sub-RBs, set that sub_token.set to the same set as the Group, and run retrieve_lower_tokens on that sub-token.
        for Group_under in token.myChildGroups:
            Group_under.set = token.set
            Group_under = retrieve_lower_tokens(Group_under)
        for myP in token.myPs:
            myP.set = token.set
            myP = retrieve_lower_tokens(myP)
        for myRB in token.myRBs:
            myRB.set = token.set
            myRB = retrieve_lower_tokens(myRB)
    if token.my_type == 'P':
        # if you're dealing with a P, then for each of it's RBs, set that myRB.set to the same set as the P, and run retrieve_lower_tokens on the myRB.
        for myRB in token.myRBs:
            myRB.set = token.set
            myRB = retrieve_lower_tokens(myRB)
    if token.my_type == 'RB':
        # if you're dealing with a RB, then for each of it's child-Ps and POs, set that token.set to the same set as the RB, and run retrieve_lower_tokens on the the sub-token.
        token.myPred[0].set = token.set
        token.myPred[0] = retrieve_lower_tokens(token.myPred[0])
        if len(token.myObj) > 0:
            token.myObj[0].set = token.set
            token.myObj[0] = retrieve_lower_tokens(token.myObj[0])
        elif len(token.myChildP) > 0:
            token.myChildP[0].set = token.set
            token.myChildP[0] = retrieve_lower_tokens(token.myChildP[0])
    # returns.
    return token

# function to delete unretrieved tokens from a copied analog.
def delete_unretrieved_tokens(analog):
    # go through each token in the analog. If it is unretrieved (i.e., token.set == 'memory'), delete that token and make sure you also delete that token from any tokens to which is is connected. NOTE: You don't need to worry about connections between POs and semantics, as the semantics copied POs are connected to are themselves copied and it doesn't matter if they are deleted. You'll replace these copied semantics with the original semantics using replace_copied_semantics() later in the check_analog_for_tokens_to_copy() function.
    for Group in analog.myGroups:
        if Group.set == 'memory':
            analog = delete_token(Group, analog)
    for myP in analog.myPs:
        if myP.set == 'memory':
            analog = delete_token(myP, analog)
    for myRB in analog.myRBs:
        if myRB.set == 'memory':
            analog = delete_token(myRB, analog)
    for myPO in analog.myPOs:
        if myPO.set == 'memory':
            analog = delete_token(myPO, analog)
    # returns.
    return analog

# function to delete a token from an analog.
def delete_token(token, analog):
    # figure out what kind of unit token is, then delete the token and delete instances of that token from any units it is connected to.
    if token.my_type == 'Group':
        # delete the Group from its ParentGroups, ChildGroups, Ps, and RBs.
        for pGroup in token.myParentGroups:
            pGroup.myChildGroups.remove(token)
        for cGroup in token.myChildGroups:
            cGroup.myParentGroups.remove(token)
        for myP in token.myPs:
            myP.myGroups.remove(token)
        for myRB in token.myRBs:
            myRB.myGroups.remove(token)
        # delete the Group iteself from analog.
        # NOTE: You don't need to delete the analog from memory, because you haven't added the analog to memory yet. It is still just a copied analog
        analog.myGroups.remove(token)
    elif token.my_type == 'P':
        # delete the P from its Groups, ParentRBs, and ChildRBs.
        for Group in token.myGroups:
            Group.myPs.remove(token)
        for ParentRB in token.myParentRBs:
            ParentRB.myChildP.remove(token)
        for ChildRB in token.myRBs:
            ChildRB.myParentPs.remove(token)
        # delete the P iteself.
        analog.myPs.remove(token)
    elif token.my_type == 'RB':
        # delete the RB from its ParentPs, Pred, and either ChildP or Object.
        for ParentP in token.myParentPs:
            ParentP.myRBs.remove(token)
        for pred in token.myPred:
            # if you are removing an RB, make sure that the PO connected to that RB also has the RB's second PO removed from its .same_RB_POs field. That is, a PO knows what other POs share RBs with it (so that it does not inhibit them during LISA mode). If an RB is deleted, the two POs sharing that RB no longer do. (RECALL: in a single analog, if two instances of a role-binding occur, the same PO tokens and same RB token is used to instantiate both (e.g., if L1(x) occurs twice in the same analog, then L1, x and L1+x are used in both instances). As a consequence, if an RB is deleted, then it means that the Pred and object are not linked by an RB in the current analog, and, as such, that neither PO should appear in the other PO's .same_RB_POs field.)
            # first, check to make sure the RB takes an object as an argument. A P as an argument will not appear in myPO.same_RB_POs as a P is NOT a myPO.
            if len(token.myObj) > 0:
                pred.same_RB_POs.remove(token.myObj[0])
            pred.myRBs.remove(token)
        for ChildP in token.myChildP:
            ChildP.myParentRBs.remove(token)
        for obj in token.myObj:
            # delete the token's pred from the object's .same_RB_POs field.
            obj.same_RB_POs.remove(token.myPred[0])
            obj.myRBs.remove(token)
        # delete the RB iteself.
        analog.myRBs.remove(token)
    elif token.my_type == 'PO':
        # delete the PO from its RBs.
        for myRB in token.myRBs:
            if token.predOrObj == 1:
                myRB.myPred.remove(token)
            else:
                myRB.myObj.remove(token)
        # delete the PO iteself.
        analog.myPOs.remove(token)
    # returns.
    return analog

# function to replace semantics in a new PO with the original memory.semantics versions.
def replace_copied_semantics(myPO, semantics):
    # for each Link in my .mySemantics, find the original semantic with the same name as .mySemantic.name, and replace .mySemantic with the original semantic from memory.
    for Link in myPO.mySemantics:
        # search each semantic in memory.semantics for the one with the same name as Link.mySemantic. Once you have found that semantic, replace Link.mySemantic with the semantic from memory, and break the for loop.
        for semantic in semantics:
            if semantic.name == Link.mySemantic.name:
                Link.mySemantic = semantic
                semantic.myPOs.append(Link)
                break # break the for loop.
    # returns.
    return myPO, semantics

# function to find token in memory whose set is driver or recipient in order to construct the driver and recipient sets for the run. Returns driver and recipient sets.
def findDriverRecipient(memory):
    # first clear out the memory.driver and memory.recipient fields.
    memory.driver.Groups, memory.driver.Ps, memory.driver.RBs, memory.driver.POs, memory.driver.analogs = [], [], [], [], []
    memory.recipient.Groups, memory.recipient.Ps, memory.recipient.RBs, memory.recipient.POs, memory.recipient.analogs = [], [], [], [], []
    # for each Group, P, RB, and PO, if the set is driver, put in in the driverSet, otherwise, elif the set is recipient, put it in the recipientSet.
    for Group in memory.Groups:
        if Group.set == 'driver':
            memory.driver.Groups.append(Group)
            # reset the .copy_for_DR field back to False.
            Group.copy_for_DR = False
            # now add the analog to driver.analogs if it is not already there.
            if Group.myanalog not in memory.driver.analogs:
                memory.driver.analogs.append(Group.myanalog)
        elif Group.set == 'recipient':
            memory.recipient.Groups.append(Group)
            # reset the .copy_for_DR field back to False.
            Group.copy_for_DR = False
            # now add the analog to recipient.analogs if it is not already there.
            if Group.myanalog not in memory.recipient.analogs:
                memory.recipient.analogs.append(Group.myanalog)
    for myP in memory.Ps:
        if myP.set == 'driver':
            memory.driver.Ps.append(myP)
            # reset the .copy_for_DR field back to False.
            myP.copy_for_DR = False
            # now add the analog to driver.analogs if it is not already there.
            if myP.myanalog not in memory.driver.analogs:
                memory.driver.analogs.append(myP.myanalog)
        elif myP.set == 'recipient':
            memory.recipient.Ps.append(myP)
            # reset the .copy_for_DR field back to False.
            myP.copy_for_DR = False
            # now add the analog to recipient.analogs if it is not already there.
            if myP.myanalog not in memory.recipient.analogs:
                memory.recipient.analogs.append(myP.myanalog)
    for myRB in memory.RBs:
        if myRB.set == 'driver':
            memory.driver.RBs.append(myRB)
            # reset the .copy_for_DR field back to False.
            myRB.copy_for_DR = False
            # now add the analog to driver.analogs if it is not already there.
            if myRB.myanalog not in memory.driver.analogs:
                memory.driver.analogs.append(myRB.myanalog)
        elif myRB.set == 'recipient':
            memory.recipient.RBs.append(myRB)
            # reset the .copy_for_DR field back to False.
            myRB.copy_for_DR = False
            # now add the analog to recipient.analogs if it is not already there.
            if myRB.myanalog not in memory.recipient.analogs:
                memory.recipient.analogs.append(myRB.myanalog)
    for myPO in memory.POs:
        if myPO.set == 'driver':
            memory.driver.POs.append(myPO)
            # now add the analog to driver.analogs if it is not already there.
            if myPO.myanalog not in memory.driver.analogs:
                memory.driver.analogs.append(myPO.myanalog)
        elif myPO.set == 'recipient':
            memory.recipient.POs.append(myPO)
            # now add the analog to recipient.analogs if it is not already there.
            if myPO.myanalog not in memory.recipient.analogs:
                memory.recipient.analogs.append(myPO.myanalog)
    # returns.
    return memory

# make firing order.
def makeFiringOrder(memory, rule):
    # set the firing order of the driver using rule.
    # right now, the only rule is random, the default.
    # you should add pragmatics.
    if rule == 'by_top_random':
        # arrange RBs randomly within Ps or Groups.
        if len(memory.driver.Groups) > 0:
            # arrange by Groups.
            # randomly arrange the Groups.
            Gorder = memory.driver.Groups
            random.shuffle(Gorder)
            # now select RBs from Porder.
            firingOrder = []
            Porder = []
            for Group in Gorder:
                # order my Ps.
                for myP in Group.myPs:
                    Porder.append(myP)
            # now add the RBs from each P in Porder to firingOrder.
            for myP in Porder:
                for myRB in myP.myRBs:
                    # add RB to firingOrder.
                    firingOrder.append(myRB)
        elif len(memory.driver.Ps) > 0: # arrange by Ps.
            # randomly arrange the Ps.
            Porder = memory.driver.Ps
            random.shuffle(Porder)
            # now select RBs from Porder.
            firingOrder = []
            for myP in Porder:
                for myRB in myP.myRBs:
                    # add RB to firingOrder.
                    firingOrder.append(myRB)
        else:
            # arrange RBs or POs randomly.
            firingOrder = []
            if len(memory.driver.RBs) > 0:
                for myRB in memory.driver.RBs:
                    firingOrder.append(myRB)
                random.shuffle(firingOrder)
            else:
                # arrange by POs.
                for myPO in memory.driver.POs:
                    firingOrder.append(myPO)
                random.shuffle(firingOrder)
    else: # use a totally random firing order.
        # if not rule == 'totally_random':
        #     print ('\nYou have not input a valid firing rule. I am arranging RBs at random.\n') # ekaterina
        firingOrder = []
        if len(memory.driver.RBs) > 0:
            for myRB in memory.driver.RBs:
                firingOrder.append(myRB)
            random.shuffle(firingOrder)
        else:
            # arrange by POs.
            for myPO in memory.driver.POs:
                firingOrder.append(myPO)
            random.shuffle(firingOrder)
    # returns.
    return firingOrder

# index all items in memory.
def indexMemory(memory):
    for Group in memory.Groups:
        Group.get_index(memory)
    for myP in memory.Ps:
        myP.get_index(memory)
    for myRB in memory.RBs:
        myRB.get_index(memory)
    for myPO in memory.POs:
        myPO.get_index(memory)
    # returns.
    return memory

# update all the .same_RB_POs for all POs in memory.
def update_same_RB_POs(memory):
    # clear the same_RB_PO field of all POs in memory.
    for myPO in memory.POs:
        myPO.same_RB_POs = []
    # update the .same_RB_PO field of POs by iterating through RBs, and adding objects to pred's field and preds to object's field.
    for myRB in memory.RBs:
        # if there is an object and a pred, add the pred to object's .same_RB_POs, and object to pred's .same_RB_POs.
        if (len(myRB.myObj) > 0) and (len(myRB.myPred) > 0):
            myRB.myObj[0].same_RB_POs.append(myRB.myPred[0])
            myRB.myPred[0].same_RB_POs.append(myRB.myObj[0])
    # returns.
    return memory

# a function to clear activation and input to all driver, recipient, newSet, and semantic units (i.e., everything in active memory, AM).
def initialize_AM(memory):
    for Group in memory.driver.Groups:
        Group.initialize_act()
    for myP in memory.driver.Ps:
        myP.initialize_act()
    for myRB in memory.driver.RBs:
        myRB.initialize_act()
    for myPO in memory.driver.POs:
        myPO.initialize_act()
    for Group in memory.recipient.Groups:
        Group.initialize_act()
    for myP in memory.recipient.Ps:
        myP.initialize_act()
    for myRB in memory.recipient.RBs:
        myRB.initialize_act()
    for myPO in memory.recipient.POs:
        myPO.initialize_act()
    for Group in memory.newSet.Groups:
        Group.initialize_act()
    for myP in memory.newSet.Ps:
        myP.initialize_act()
    for myRB in memory.newSet.RBs:
        myRB.initialize_act()
    for myPO in memory.newSet.POs:
        myPO.initialize_act()
    for semantic in memory.semantics:
        semantic.initializeSem()
    # returns.
    return memory

# a function to clear the activation and input to all units in the network.
def initialize_memorySet(memory):
    for Group in memory.Groups:
        Group.initialize_act()
    for myP in memory.Ps:
        myP.initialize_act()
    for myRB in memory.RBs:
        myRB.initialize_act()
    for myPO in memory.POs:
        myPO.initialize_act()
    # returns.
    return memory

# initialize input to all driver, recipient, newSet and semantic units.
def initialize_input(memory):
    for Group in memory.driver.Groups:
        Group.initialize_input(0.0)
    for myP in memory.driver.Ps:
        myP.initialize_input(0.0)
    for myRB in memory.driver.RBs:
        myRB.initialize_input(0.0)
    for myPO in memory.driver.POs:
        myPO.initialize_input(0.0)
    for Group in memory.recipient.Groups:
        Group.initialize_input(0.0)
    for myP in memory.recipient.Ps:
        myP.initialize_input(0.0)
    for myRB in memory.recipient.RBs:
        myRB.initialize_input(0.0)
    for myPO in memory.recipient.POs:
        myPO.initialize_input(0.0)
    for Group in memory.newSet.Groups:
        Group.initialize_input(0.0)
    for myP in memory.newSet.Ps:
        myP.initialize_input(0.0)
    for myRB in memory.newSet.RBs:
        myRB.initialize_input(0.0)
    for myPO in memory.newSet.POs:
        myPO.initialize_input(0.0)
    for semantic in memory.semantics:
        semantic.initialize_input(0.0)
    # returns.
    return memory

# update the activations of all units in driver, recipient, and newSet.
def update_activations_run(memory, gamma, delta, HebbBias, phase_set):
    for Group in memory.driver.Groups:
        Group.update_act(gamma, delta, HebbBias)
    for myP in memory.driver.Ps:
        myP.update_act(gamma, delta, HebbBias)
    for myRB in memory.driver.RBs:
        myRB.update_act(gamma, delta, HebbBias)
    for myPO in memory.driver.POs:
        myPO.update_act(gamma, delta, HebbBias)
    for Group in memory.recipient.Groups:
        Group.update_act(gamma, delta, HebbBias)
    for myP in memory.recipient.Ps:
        myP.update_act(gamma, delta, HebbBias)
    for myRB in memory.recipient.RBs:
        myRB.update_act(gamma, delta, HebbBias)
    for myPO in memory.recipient.POs:
        myPO.update_act(gamma, delta, HebbBias)
    for Group in memory.newSet.Groups:
        Group.update_act(gamma, delta, HebbBias)
    for myP in memory.newSet.Ps:
        myP.update_act(gamma, delta, HebbBias)
    for myRB in memory.newSet.RBs:
        myRB.update_act(gamma, delta, HebbBias)
    for myPO in memory.newSet.POs:
        myPO.update_act(gamma, delta, HebbBias)
    # get the max input to any semantic unit, then update semantic activations.
    max_input = get_max_sem_input(memory)
    for semantic in memory.semantics:
        semantic.set_max_input(max_input)
        semantic.update_act()
    # returns.
    return memory

# update the activation of all units in memory that are NOT in driver, recipient, or newSet. (For use in retrieval.)
def update_acts_memory(memory, gamma, delta, HebbBias):
    for Group in memory.Groups:
        if Group.set == 'memory':
            Group.update_act(gamma, delta, HebbBias)
    for myP in memory.Ps:
        if myP.set == 'memory':
            myP.update_act(gamma, delta, HebbBias)
    for myRB in memory.RBs:
        if myRB.set == 'memory':
            myRB.update_act(gamma, delta, HebbBias)
    for myPO in memory.POs:
        if myPO.set == 'memory':
            myPO.update_act(gamma, delta, HebbBias)
    # returns.
    return memory

# update inputs to driver units.
def update_driver_inputs(memory, asDORA, lateral_input_level):
    # update inputs to all driver units.
    for Group in memory.driver.Groups:
        Group.update_input_driver(memory, asDORA)
    for myP in memory.driver.Ps:
        if myP.mode == 1:
            myP.update_input_driver_parent(memory, asDORA)
        elif myP.mode == -1:
            myP.update_input_driver_child(memory, asDORA)
    for myRB in memory.driver.RBs:
        myRB.update_input_driver(memory, asDORA)
    for myPO in memory.driver.POs:
        myPO.update_input_driver(memory, asDORA)
    # returns
    return memory

# update inputs to recipient units.
def update_recipient_inputs(memory, asDORA, phase_set, lateral_input_level, ignore_object_semantics):
    # update inputs to all recipient units.
    for Group in memory.recipient.Groups:
        Group.update_input_driver(memory, asDORA)
    for myP in memory.recipient.Ps:
        if myP.mode == 1:
            myP.update_input_recipient_parent(memory, asDORA, phase_set, lateral_input_level)
        elif myP.mode == -1:
            myP.update_input_recipient_child(memory, asDORA, phase_set, lateral_input_level)
    for myRB in memory.recipient.RBs:
        myRB.update_input_recipient(memory, asDORA, phase_set, lateral_input_level)
    for myPO in memory.recipient.POs:
        myPO.update_input_recipient(memory, asDORA, phase_set, lateral_input_level, ignore_object_semantics)
    # returns.
    return memory

# update newSet inputs.
def update_newSet_inputs(memory):
    # units in NewSet have input 1 if the token that made them in the driver is active above threshold, 0 otherwise.
    threshold = .75
    for Group in memory.newSet.Groups:
        if Group.my_maker_unit.act > threshold:
            Group.act = 1.0
        else:
            Group.act = 0.0
    for myP in memory.newSet.Ps:
        if myP.my_maker_unit.act > threshold:
            myP.act = 1.0
        else:
            myP.act = 0.0
    for myRB in memory.newSet.RBs:
        if myRB.my_maker_unit:
            if myRB.my_maker_unit.act > threshold:
                myRB.act = 1.0
            else:
                myRB.act = 0.0
    for myPO in memory.newSet.POs:
        if myPO.my_maker_unit:
            if myPO.my_maker_unit.act > threshold:
                myPO.act = 1.0
            else:
                myPO.act = 0.0
    # returns.
    return memory

# update input to all memorySet units that are not in driver, recipient, or newSet (used during retreival).
def update_memory_inputs(memory, asDORA, lateral_input_level):
    # for all units not in driver, recipient, or newSet (i.e., units with set != driver, recipient, or newSet), update input. Units in memory update as units in recipient.
    # set phase_set to 2.
    phase_set = 2
    for Group in memory.Groups:
        if Group.set == 'memory':
            Group.update_input_recipient(memory, asDORA, phase_set, lateral_input_level)
    for myP in memory.Ps:
        if myP.set == 'memory':
            # NOTE: I think it might be best to avoid modes altogether when working in retieval mode. This version of the code reflects this assumption.
            myP.update_input_recipient_parent(memory, asDORA, phase_set, lateral_input_level)
    for myRB in memory.RBs:
        if myRB.set == 'memory':
            myRB.update_input_recipient(memory, asDORA, phase_set, lateral_input_level)
    for myPO in memory.POs:
        if myPO.set == 'memory':
            myPO.update_input_recipient(memory, asDORA, phase_set, lateral_input_level) # update with phase_set = 2 so that myPO units also take top down input from RBs.
    # returns.
    return memory

# get the max input to semantics unit in the network.
def get_max_sem_input(memory):
    max_input = 0.0
    for semantic in memory.semantics:
        if semantic.myinput > max_input:
            max_input = semantic.myinput
    # returns.
    return max_input

# function to delete links between semantics and POs that are less than threshold.
def del_small_link(memory, threshold):
    for link in memory.Links:
        # if the link is less than threshold, then delete the link from the PO and the semantic, and remove the link from memory.Links.
        if link.weight < threshold:
            link.myPO.mySemantics.remove(link)
            link.mySemantic.myPOs.remove(link)
            memory.Links.remove(link)
    # returns.
    return memory

# function to round up to 1.0 any links between semantics and POs that are above a certain threshold.
def round_big_link(memory, threshold):
    for link in memory.Links:
        if link.weight > threshold:
            link.weight = 1.0
    # returns.
    return memory

# check if the requirements for entropy based same/different/more/less are met.
def entropy_samediff_requirements(memory):
    do_entropy_SDML = False
    # make sure that the most active PO in driver and recipient have activation above 0.6 and map to one-another.
    #PO1 = get_most_active_unit(memory.driver.POs)
    #PO2 = get_most_active_unit(memory.recipient.POs)
    #if PO1.act >= 0.6 and PO2.act >= 0.6:
    #    if PO1.max_map_unit is PO2:
    #        do_entropy_SMDL = True
    # returns.
    return do_entropy_SDML

# check if the requirements for predication are met.
def predication_requirements(memory):
    # make sure that all driver POs map to units in the recipient that don't have RBs, and that those mappings are above threshold(=.8).
    # get the max_maps and max_map_units.
    memory = get_max_maps(memory)
    memory = get_max_map_units(memory)
    do_predication = False
    for myPO in memory.driver.POs:
        # make sure that my max_map is at least .8, and the unit to which I map maximally has no RBs.
        if myPO.max_map > .8 and len(myPO.max_map_unit.myRBs) < 1:
            do_predication = True
        else:
            do_predication = False
            break
    # returns.
    return do_predication

# check if the reqiurements for relation-formation are met.
def rel_form_requirements(memory):
    # make sure that there are at least 2 RBs in the recipient that both map to RBs in the driver with mapping connections above 0.8, and that are NOT already connected to a P unit.
    do_rel_form = False
    RBs_meeting_requirements = 0
    for myRB in memory.recipient.RBs:
        for mappingConnection in myRB.mappingConnections:
            if mappingConnection.weight >= .8:
                if len(mappingConnection.recipientToken.myParentPs) < 1:
                    # increment the RBs_meeting_requirements variable by 1.
                    RBs_meeting_requirements += 1
                    # if RBs_meeting_requirements is greater or equal to 2, then set do_rel_form to True.
                    if RBs_meeting_requirements >= 2:
                        do_rel_form = True
                        break
    # returns.
    return do_rel_form

# check if requirements for schema induction are met.
def schema_requirements(memory):
    do_schematize = True
    # make sure that all driver and recipient units that map to a recipient/driver (respectively) unit (i.e., have a mapping connection above 0.0) are also above threshold(=.7). Also, make sure that any token that meets the requirement for schematisation also has all its lower-order tokens (e.g., RBs and POs in the case of Ps, POs in the case of RBs) and higher-order tokens (e.g., PS in the case of RBs) have mapping connections above threshold as well.
    threshold = 0.7
    for myP in memory.driver.Ps:
        if 0 < myP.max_map < threshold:
            do_schematize = False
            break
        else:
            # make sure that the RBs and POs also meet requirements.
            for myRB in myP.myRBs:
                # make sure RBs and POs meet requirment.
                if myRB.max_map < threshold:
                    do_schematize = False
                    break
                elif myRB.myPred[0].max_map < threshold:
                    do_schematize = False
                    break
                elif myRB.myObj[0].max_map < threshold:
                    do_schematize = False
                    break
            if not do_schematize:
                break
    if do_schematize:
        for myRB in memory.driver.RBs:
            if 0 < myRB.max_map < threshold:
                do_schematize = False
                break
            else:
                # make sure that POs and Ps also meet requirments.
                if myRB.myPred[0].max_map < threshold:
                    do_schematize = False
                    break
                elif myRB.myObj[0].max_map < threshold:
                    do_schematize = False
                    break
                elif len(myRB.myParentPs) > 0:
                    if myRB.myParentPs[0].max_map < threshold:
                        do_schematize = False
                        break
    if do_schematize:
        for myPO in memory.driver.POs:
            if 0 < myPO.max_map < threshold:
                do_schematize = False
                break
    if do_schematize:
        for myP in memory.recipient.Ps:
            if 0 < myP.max_map < threshold:
                do_schematize = False
                break
            else:
                # make sure that the RBs and POs also meet requirements.
                for myRB in myP.myRBs:
                    # make sure RBs and POs meet requirment.
                    if myRB.max_map < threshold:
                        do_schematize = False
                        break
                    elif myRB.myPred[0].max_map < threshold:
                        do_schematize = False
                        break
                    elif myRB.myObj[0].max_map < threshold:
                        do_schematize = False
                        break
                if not do_schematize:
                    break
    if do_schematize:
        for myRB in memory.recipient.RBs:
            if 0 < myRB.max_map < threshold:
                do_schematize = False
                break
            else:
                # make sure that POs and Ps also meet requirments.
                if myRB.myPred[0].max_map < threshold:
                    do_schematize = False
                    break
                elif myRB.myObj[0].max_map < threshold:
                    do_schematize = False
                    break
                elif len(myRB.myParentPs) > 0:
                    if myRB.myParentPs[0].max_map < threshold:
                        do_schematize = False
                        break
    if do_schematize:
        for myPO in memory.recipient.POs:
            if 0 < myPO.max_map < threshold:
                do_schematize = False
                break
    # returns.
    return do_schematize

# check if requirements for relational generalization are met.
def rel_gen_requirements(memory):
    threshold = 0.7
    do_inference = False
    # make sure that at least one driver unit maps to a recipient unit.
    for myP in memory.driver.Ps:
        if myP.max_map > 0.0:
            do_inference = True
            break
    if not do_inference:
        for myRB in memory.driver.RBs:
            if myRB.max_map > 0.0:
                do_inference = True
                break
    if not do_inference:
        for myPO in memory.driver.POs:
            if myPO.max_map > 0.0:
                do_inference = True
                break
    # now make sure that for units in the driver that do map, the mapping is above threshold(=.7).
    if do_inference:
        for myP in memory.driver.Ps:
            if threshold > myP.max_map > 0.0:
                do_inference = False
                break
    if do_inference:
        for myRB in memory.driver.RBs:
            if threshold > myRB.max_map > 0.0:
                do_inference = False
                break
    if do_inference:
        for myPO in memory.driver.POs:
            if threshold > myPO.max_map > 0.0:
                do_inference = False
                break
    # returns.
    return do_inference

# get the max mapping weight for all driver and recipient units.
def get_max_maps(memory):
    for Group in memory.driver.Groups:
        max_map = 0.0
        for mappingConnection in Group.mappingConnections:
            if mappingConnection.weight > max_map:
                max_map = mappingConnection.weight
        Group.max_map = max_map
    for myP in memory.driver.Ps:
        max_map = 0.0
        for mappingConnection in myP.mappingConnections:
            if mappingConnection.weight > max_map:
                max_map = mappingConnection.weight
        myP.max_map = max_map
    for myRB in memory.driver.RBs:
        max_map = 0.0
        for mappingConnection in myRB.mappingConnections:
            if mappingConnection.weight > max_map:
                max_map = mappingConnection.weight
        myRB.max_map = max_map
    for myPO in memory.driver.POs:
        max_map = 0.0
        for mappingConnection in myPO.mappingConnections:
            if mappingConnection.weight > max_map:
                max_map = mappingConnection.weight
        myPO.max_map = max_map
    for Group in memory.recipient.Groups:
        max_map = 0.0
        for mappingConnection in Group.mappingConnections:
            if mappingConnection.weight > max_map:
                max_map = mappingConnection.weight
        Group.max_map = max_map
    for myP in memory.recipient.Ps:
        max_map = 0.0
        for mappingConnection in myP.mappingConnections:
            if mappingConnection.weight > max_map:
                max_map = mappingConnection.weight
        myP.max_map = max_map
    for myRB in memory.recipient.RBs:
        max_map = 0.0
        for mappingConnection in myRB.mappingConnections:
            if mappingConnection.weight > max_map:
                max_map = mappingConnection.weight
        myRB.max_map = max_map
    for myPO in memory.recipient.POs:
        max_map = 0.0
        for mappingConnection in myPO.mappingConnections:
            if mappingConnection.weight > max_map:
                max_map = mappingConnection.weight
        myPO.max_map = max_map
    # returns.
    return memory

# initialize (i.e., reset to empty) all the mappingHypotheses and mappingConnections.
def resetMappingUnits(memory):
    # delete all mappingHypothesis and mappingConnection units.
    memory.mappingHypotheses = []
    memory.mappingConnections = []
    # delete the mappingHypotheses and mappingConnections fields of all driver and recipient units.
    for Group in memory.driver.Groups:
        Group.mappingHypotheses = []
        Group.mappingConnections = []
    for myP in memory.driver.Ps:
        myP.mappingHypotheses = []
        myP.mappingConnections = []
    for myRB in memory.driver.RBs:
        myRB.mappingHypotheses = []
        myRB.mappingConnections = []
    for myPO in memory.driver.POs:
        myPO.mappingHypotheses = []
        myPO.mappingConnections = []
    for Group in memory.recipient.Groups:
        Group.mappingHypotheses = []
        Group.mappingConnections = []
    for myP in memory.recipient.Ps:
        myP.mappingHypotheses = []
        myP.mappingConnections = []
    for myRB in memory.recipient.RBs:
        myRB.mappingHypotheses = []
        myRB.mappingConnections = []
    for myPO in memory.recipient.POs:
        myPO.mappingHypotheses = []
        myPO.mappingConnections = []
    # returns.
    return memory

# reset the .mappingHypotheses, .mappingConnections, and .max_map of all tokens.
def reset_mappings(memory):
    for Group in memory.Groups:
        Group.mappingHypotheses = []
        Group.mappingConnections = []
        Group.max_map = 0.0
        Group.max_map_unit = None
    for myP in memory.Ps:
        myP.mappingHypotheses = []
        myP.mappingConnections = []
        myP.max_map = 0.0
        myP.max_map_unit = None
    for myRB in memory.RBs:
        myRB.mappingHypotheses = []
        myRB.mappingConnections = []
        myRB.max_map = 0.0
        myRB.max_map_unit = None
    for myPO in memory.POs:
        myPO.mappingHypotheses = []
        myPO.mappingConnections = []
        myPO.max_map = 0.0
        myPO.max_map_unit = None
    # returns.
    return memory

# set up mappingHypotheses and mappingConnection units.
def setupMappingUnits(memory):
    # set up mapping hypothesis and mapping connection units for every driver token and every token of the same type in the recipient.
    for P_dri in memory.driver.Ps:
        # for every recipient P unit create a mapping hypothesis and mapping connection.
        for P_rec in memory.recipient.Ps:
            # create a mapping conneciton unit.
            new_map_unit = dataTypes.mappingConnection(P_dri, P_rec, 0.0)
            # connect new_map_unit to driver and recipient mappingConnections fields.
            P_dri.mappingConnections.append(new_map_unit)
            P_rec.mappingConnections.append(new_map_unit)
            # add new_hyp unit to memory.mappingConnections.
            memory.mappingConnections.append(new_map_unit)
            # create a mapping hypothesis unit.
            new_hyp = dataTypes.mappingHypothesis(P_dri, P_rec, new_map_unit)
            # connect new_hyp to driver and recipient mappingHypotheses fields.
            P_dri.mappingHypotheses.append(new_hyp)
            P_rec.mappingHypotheses.append(new_hyp)
            # add new_hyp unit to memory.mappingHypotheses.
            memory.mappingHypotheses.append(new_hyp)
    for RB_dri in memory.driver.RBs:
        # for every recipient RB unit create a mapping hypothesis and mapping connection.
        for RB_rec in memory.recipient.RBs:
            # create a mapping conneciton unit.
            new_map_unit = dataTypes.mappingConnection(RB_dri, RB_rec, 0.0)
            # connect new_map_unit to driver and recipient mappingConnections fields.
            RB_dri.mappingConnections.append(new_map_unit)
            RB_rec.mappingConnections.append(new_map_unit)
            # add new_hyp unit to memory.mappingConnections.
            memory.mappingConnections.append(new_map_unit)
            # create a mapping hypothesis unit.
            new_hyp = dataTypes.mappingHypothesis(RB_dri, RB_rec, new_map_unit)
            # connect new_hyp to driver and recipient mappingHypotheses fields.
            RB_dri.mappingHypotheses.append(new_hyp)
            RB_rec.mappingHypotheses.append(new_hyp)
            # add new_hyp unit to memory.mappingHypotheses.
            memory.mappingHypotheses.append(new_hyp)
    for PO_dri in memory.driver.POs:
        # for every recipient PO of the same type (pred or obj) create a mapping hypothesis and mapping connection.
        for PO_rec in memory.recipient.POs:
            # create mapping connection unit.
            new_map_unit = dataTypes.mappingConnection(PO_dri, PO_rec, 0.0)
            # connect new_map_unit to driver and recipient mappingConnections fields.
            PO_dri.mappingConnections.append(new_map_unit)
            PO_rec.mappingConnections.append(new_map_unit)
            # add new_map_unit to memory.mappingConnections.
            memory.mappingConnections.append(new_map_unit)
            # and if the POs are of the same type, also create mapping hypothesis unit.
            if PO_dri.predOrObj == PO_rec.predOrObj:
                # create a mapping hypothesis unit.
                new_hyp = dataTypes.mappingHypothesis(PO_dri, PO_rec, new_map_unit)
                # connect new_hyp to driver and recipient mappingHypotheses fields.
                PO_dri.mappingHypotheses.append(new_hyp)
                PO_rec.mappingHypotheses.append(new_hyp)
                # add new_hyp unit to memory.mappingHypotheses.
                memory.mappingHypotheses.append(new_hyp)
    # returns.
    return memory

# update the mapping hypotheses.
def update_mappingHyps(memory):
    for hypothesis in memory.mappingHypotheses:
        hypothesis.update_hyp(memory)
    # returns.
    return memory

# reset the values of the mapping hypotheses.
def reset_mappingHyps(memory):
    for hyp in memory.mappingHypotheses:
        hyp.hypothesis = 0.0
        hyp.max_hyp = 0.0
    # returns.
    return memory

# update mapping connections.
def update_mappingConnections(memory, eta):
    # first step: divisively normalize all mapping hypotheses. For each mappng hypothesis divide it by the highest hypothesis of either unit involved in that hypothesis. For example, for the mapping hypothesis between P[i] and P[j] divide by max(max(hypothesis involving P[i]), max(hypothesis involving P[j])).
    for hypothesis in memory.mappingHypotheses:
        hypothesis.max_hyp = hypothesis.hypothesis
        for hyp in hypothesis.driverToken.mappingHypotheses:
            if hyp.hypothesis > hypothesis.max_hyp:
                hypothesis.max_hyp = hyp.hypothesis
        for hyp2 in hypothesis.recipientToken.mappingHypotheses:
            if hyp2.hypothesis > hypothesis.max_hyp:
                hypothesis.max_hyp = hyp2.hypothesis
    # now do the divisive normalization by dividing hypothesis.hypothesis by max_hyp.
    for hypothesis in memory.mappingHypotheses:
        if hypothesis.max_hyp > 0:
            hypothesis.hypothesis /= hypothesis.max_hyp
    # second step: subractively normalize each hypothesis. For each hypothesis, look at all hypotheses of the driver and recipient unit sharing the hypothesis. Find the largest hypothesis in either the shared driver or recipient that is NOT the hypothesis itself. Subtract by that value.
    for hypothesis in memory.mappingHypotheses:
        hypothesis.max_hyp = 0.0
        max_hyp = 0.0
        for hyp in hypothesis.driverToken.mappingHypotheses:
            if (hyp.hypothesis > max_hyp) and (not (hyp is hypothesis)):
                max_hyp = hyp.hypothesis
        for hyp2 in hypothesis.recipientToken.mappingHypotheses:
            if (hyp2.hypothesis > max_hyp) and (not (hyp2 is hypothesis)):
                max_hyp = hyp2.hypothesis
        if max_hyp > 0:
            hypothesis.max_hyp = max_hyp
    for hypothesis in memory.mappingHypotheses:
        hypothesis.hypothesis -= hypothesis.max_hyp
        # update the mappingConnections using the corresponding mappingHypothesis.
        hypothesis.myMappingConnection.weight += (eta*(1.1-hypothesis.myMappingConnection.weight)*hypothesis.hypothesis)
        # and mapping connections are hard limited to between 0 and 1.
        if hypothesis.myMappingConnection.weight > 1:
            hypothesis.myMappingConnection.weight = 1
        elif hypothesis.myMappingConnection.weight < 0:
            hypothesis.myMappingConnection.weight = 0
    # returns.
    return memory

# update max_map_unit (i.e., the unit I most map to).
def get_max_map_units(memory):
    # for each token in driver and recipient, get its hightest mapping connection and place the weight of that connection in .max_map.
    for Group in memory.driver.Groups:
        max_map = 0.0
        max_map_unit = None
        for mapping in Group.mappingConnections:
            if mapping.weight > max_map:
                max_map = mapping.weight
                max_map_unit = mapping.recipientToken
        # update .max_map.
        Group.max_map = max_map
        Group.max_map_unit = max_map_unit
    for myP in memory.driver.Ps:
        max_map = 0.0
        max_map_unit = None
        for mapping in myP.mappingConnections:
            if mapping.weight > max_map:
                max_map = mapping.weight
                max_map_unit = mapping.recipientToken
        # update .max_map.
        myP.max_map = max_map
        myP.max_map_unit = max_map_unit
    for myRB in memory.driver.RBs:
        max_map = 0.0
        max_map_unit = None
        for mapping in myRB.mappingConnections:
            if mapping.weight > max_map:
                max_map = mapping.weight
                max_map_unit = mapping.recipientToken
        # update .max_map.
        myRB.max_map = max_map
        myRB.max_map_unit = max_map_unit
    for myPO in memory.driver.POs:
        max_map = 0.0
        max_map_unit = None
        for mapping in myPO.mappingConnections:
            if mapping.weight > max_map:
                max_map = mapping.weight
                max_map_unit = mapping.recipientToken
        # update .max_map.
        myPO.max_map = max_map
        myPO.max_map_unit = max_map_unit
    for Group in memory.recipient.Groups:
        max_map = 0.0
        max_map_unit = None
        for mapping in Group.mappingConnections:
            if mapping.weight > max_map:
                max_map = mapping.weight
                max_map_unit = mapping.recipientToken
        # update .max_map.
        Group.max_map = max_map
        Group.max_map_unit = max_map_unit
    for myP in memory.recipient.Ps:
        max_map = 0.0
        max_map_unit = None
        for mapping in myP.mappingConnections:
            if mapping.weight > max_map:
                max_map = mapping.weight
                max_map_unit = mapping.driverToken
        # update .max_map.
        myP.max_map = max_map
        myP.max_map_unit = max_map_unit
    for myRB in memory.recipient.RBs:
        max_map = 0.0
        max_map_unit = None
        for mapping in myRB.mappingConnections:
            if mapping.weight > max_map:
                max_map = mapping.weight
                max_map_unit = mapping.driverToken
        # update .max_map.
        myRB.max_map = max_map
        myRB.max_map_unit = max_map_unit
    for myPO in memory.recipient.POs:
        max_map = 0.0
        max_map_unit = None
        for mapping in myPO.mappingConnections:
            if mapping.weight > max_map:
                max_map = mapping.weight
                max_map_unit = mapping.driverToken
        # update .max_map.
        myPO.max_map = max_map
        myPO.max_map_unit = max_map_unit
    # returns.
    return memory

# function to do run the network during retieval.
def retrieval_routine(memory, asDORA, gamma, delta, HebbBias, lateral_input_level, bias_retrieval_analogs):
    # update input to memorySet units.
    memory = update_memory_inputs(memory, asDORA, lateral_input_level)
    # update activation of memorySet units.
    memory = update_acts_memory(memory, gamma, delta, HebbBias)
    if bias_retrieval_analogs:
        # for each analog, track the total activation of its units if they are in memory (i.e., if the analog is not already in driver or recipient).
        for analog in memory.analogs:
            analog.total_act = 0.0
            for myP in analog.myPs:
                if myP.set == 'memory':
                    analog.total_act += myP.act
            for myRB in analog.myRBs:
                if myRB.set == 'memory':
                    analog.total_act += myRB.act
            for myPO in analog.myPOs:
                if myPO.set == 'memory':
                    analog.total_act += myPO.act
            analog.sum_num_units()
    else:
        # track the most active P, RB, and PO units in memory.
        for myP in memory.Ps:
            if myP.set == 'memory':
                if myP.act > myP.max_act:
                    myP.max_act = myP.act
        for myRB in memory.RBs:
            if myRB.set == 'memory':
                if myRB.act > myRB.max_act:
                    myRB.max_act = myRB.act
        for myPO in memory.POs:
            if myPO.set == 'memory':
                if myPO.act > myPO.max_act:
                    myPO.max_act = myPO.act
        # returns.
    return memory

# function to retrieve tokens from memory. Takes as arguments the memory set, and a bias_retrieval_analogs flag that if True, biases retrieval towards whole analogs.
def retrieve_tokens(memory, bias_retrieval_analogs, use_relative_act):
    # if bias_retrieval_analogs is true, bias towards retrieving whole analogs. Otherwise, default to no bias (myPs, RBs, and POs stand some odds of being retrieved regardless of their interconnectivity (of course, if a token is retrieved, all tokens below it that the token is connected to are also retrieved)).
    if use_relative_act:
        # retrieve using relative activation of propositions.
        if bias_retrieval_analogs:
            # retrieve whole analogs. Create a normalised retrieval score for each analog (i.e., analog.total_act/analog.num_units), and make a list of all analog activations.
            analog_activation_list = []
            for analog in memory.analogs:
                # make sure analog has a .total_act and .num_units > 0.
                if analog.total_act > 0 and analog.num_units > 0:
                    # calculate analog.normalised_retrieval_act and add that to sum_normalised_analogs.
                    analog.normalised_retrieval_act = analog.total_act/analog.num_units
                    analog_activation_list.append(analog.normalised_retrieval_act)
            # retrieve analogs with a probability calculated as a function of the ratio of the specific analog's normalised activation to the average normalised activation of all active analogs. Find the average and highest normalised activation for analogs.
            avg_analog_norm_act = np.mean(analog_activation_list)
            high_analog_norm_act = max(analog_activation_list)
            avg_analog_norm_act = (high_analog_norm_act+avg_analog_norm_act)/2
            # transform all retrieval activations using a sigmoidal function with a threshold around high_analog_norm_act.
            for analog in memory.analogs:
                if analog.total_act > 0:
                    analog.normalised_retrieval_act = 1/(1 + math.exp(10*(analog.normalised_retrieval_act-avg_analog_norm_act)))
            # get the sum of all transformed noralised analog activations.
            sum_analog_norm_act = sum(analog_activation_list)
            # retrieve analogs using the Luce choice rule appled to transformed activations.
            for analog in memory.analogs:
                # if analog has a .total_act and .num_units > 0, then calculate the retrieve_prob.
                if analog.total_act > 0 and analog.num_units > 0:
                    retrieve_prob = analog.normalised_retrieval_act/sum_analog_norm_act
                    randomNum = random.random()
                    if retrieve_prob >= randomNum:
                        # retrieve the analog and all it's tokens.
                        retrieve_analog_contents(analog)
    else:
        # retirieve using the old Luce choice axiom.
        if bias_retrieval_analogs:
            # retrieve whole analogs. Create a normalised retrieval score for each analog (i.e., analog.total_act/analog.num_units) and sum up all normalised retrieval scores for each analog in memory.
            sum_normalised_analogs = 0.0
            for analog in memory.analogs:
                # make sure analog has a .total_act and .num_units > 0.
                if analog.total_act > 0 and analog.num_units > 0:
                    # calculate my num_units.
                    analog.sum_num_units()
                    # calculate analog.normalised_retrieval_act and add that to sum_normalised_analogs.
                    analog.normalised_retrieval_act = analog.total_act/analog.num_units
                    sum_normalised_analogs += analog.normalised_retrieval_act
            # retrieve analogs using the Luce choice axiom.
            for analog in memory.analogs:
                # if analog has a .total_act and .num_units > 0, then calculate the retrieve_prob via Luce choice.
                if analog.total_act > 0 and analog.num_units > 0:
                    retrieve_prob = analog.normalised_retrieval_act/sum_normalised_analogs
                    randomNum = random.random()
                    if retrieve_prob >= randomNum:# / 1.5: # ekaterina
                        # retrieve the analog and all it's tokens.
                        retrieve_analog_contents(analog)
        else:
            # get sum of all max_acts of all P, RB and P units in memorySet.
            P_sum, RB_sum, PO_sum = 0.0, 0.0, 0.0
            for myP in memory.Ps:
                P_sum += myP.max_act
            for myRB in memory.RBs:
                RB_sum += myRB.max_act
            for myPO in memory.POs:
                PO_sum += myPO.max_act
            # for each P, RB, and PO in memorySet (i.e., NOT in driver, recipient, or newSet), retrieve it (and the proposition attached to it) into recipient according to the Luce choice rule.
            # P units.
            for myP in memory.Ps:
                # make sure that the P is in memory and that P_sum > 0 (so you don't get a divide by 0 error).
                if (myP.set == 'memory') and (P_sum > 0):
                    retrieve_prob = myP.max_act/P_sum
                    randomNum = random.random()
                    if retrieve_prob > randomNum:
                        # retrieve P and all units attached into recipient.
                        myP.set = 'recipient'
                        # add the RBs.
                        for myRB in myP.myRBs:
                            myRB.set = 'recipient'
                            # add the POs.
                            myRB.myPred[0].set = 'recipient'
                            # if it has an object add that object.
                            if len(myRB.myObj) >= 1:
                                myRB.myObj[0].set = 'recipient'
                            else: # add it's child myP.
                                myRB.myChildP[0].set = 'recipient'
            # RB units.
            for myRB in memory.RBs:
                # make sure that the RB is in memory and that RB_sum > 0 (so you don't get a divide by 0 error).
                if (myRB.set == 'memory') and (RB_sum > 0):
                    retrieve_prob = myRB.max_act/RB_sum
                    randomNum = random.random()
                    if retrieve_prob > randomNum:
                        # retrieve RB and all units attached into recipient.
                        myRB.set = 'recipient'
                        # add the Ps.
                        for myP in myRB.myParentPs:
                            myP.set = 'recipient'
                        # add the POs.
                        myRB.myPred[0].set = 'recipient'
                        # if it has an object add that object.
                        if len(myRB.myObj) >= 1:
                            myRB.myObj[0].set = 'recipient'
                        else: # add it's child myP.
                            myRB.myChildP[0].set = 'recipient'
            # PO units.
            for myPO in memory.POs:
                # make sure that the PO is in memory and that PO_sum > 0 (so you don't get a divide by 0 error).
                if (myPO.set == 'memory') and (PO_sum > 0):
                    retrieve_prob = myPO.max_act/PO_sum
                    randomNum = random.random()
                    if retrieve_prob > randomNum:
                        # retrieve PO and all units attached into recipient.
                        myPO.set = 'recipient'
                        memory.recipient.POs.append(myPO)
                        # add the RBs.
                        for myRB in myPO.myRBs:
                            myRB.set = 'recipient'
                            # add the RB's P unit if it exists.
                            if len(myRB.myParentPs) > 0:
                                myRB.myParentPs[0].set = 'recipient'
    # returns.
    return memory

# funtion to retrieve all of the contents of an analog from memory into the recipient.
def retrieve_analog_contents(analog):
    for myP in analog.myPs:
        myP.set = 'recipient'
    for myRB in analog.myRBs:
        myRB.set = 'recipient'
    for myPO in analog.myPOs:
        myPO.set = 'recipient'

# Take as input a set of nodes of a specific type (e.g., memory.POs, or memory.recipient.RBs) and return most active unit.
def get_most_active_unit(tokens):
    # make sure that you've passed a non-empty array.
    if len(tokens) > 0:
        active_token = tokens[0]
        for token in tokens:
            if token.act > active_token.act:
                active_token = token
        # make sure that you're actually returning an active unit (not just the first token if all token have the same activation (e.g., 0.0)).
        if active_token.act < .01:
            active_token = None
    else:
        active_token = None
    # returns.
    return active_token

# Take as input a set of P units and a tag specifying 'parent' or 'child', and return most active unit of that type.
def get_most_active_Punit(tokens, tag):
    if tag == 'parent':
        desired_mode = 1
    elif tag == 'child':
        desired_mode = -1
    else:
        desired_mode = 0
    activity = 0.0
    active_token = None
    for token in tokens:
        if token.act > activity and token.mode == desired_mode:
            active_token = token
            activity = token.act
    # returns.
    return active_token

# Take as input a unit, and return its mappingConnection link with the greatest weight. If it maps to no unit (i.e., mappingConnection.weight == 0), return 'null'.
def get_my_max_map(unit):
    max_map = unit.mappingConnections[0]
    for mapping in unit.mappingConnections:
        if mapping.weight > max_map.weight:
            max_map = mapping
    # if the unit I most map to has weight 0, return null, else return unit I most map to.
    if max_map.weight == 0:
        max_map = 'null'
    return max_map

# Take as input a unit, and return the unit to which it maps. If it maps to no unit, return 'null'.
def get_my_max_map_unit(unit):
    max_map = unit.mappingConnections[0]
    for mapping in unit.mappingConnections:
        if mapping.weight > max_map.weight:
            max_map = mapping
    # if the unit I most map to has weight 0, return null, else return unit I most map to.
    if max_map.weight == 0:
        max_map_unit = 'null'
    else:
        # if I am in driver, return recipientToken, otherwise, return driverToken.
        if unit.set == 'driver':
            max_map_unit = max_map.recipientToken
        else:
            max_map_unit = max_map.driverToken
    return max_map_unit

# function to do all the necessary checks for entropy/energy based magnitude comparison.
def en_based_mag_checks(myPO, myPO2):
    # check if they code the same dimension (are they both connected to a semantic unit coding a dimension with a weight near 1?), and whether any POs are connected to any SDM semantics (i.e., "more", "less", or "same").
    # first, do they code for intersecting dimensions.
    intersect_dim = list(set([x.mySemantic.dimension for x in myPO.mySemantics if x.mySemantic.dimension and x.weight > .9]).intersection([y.mySemantic.dimension for y in myPO2.mySemantics if y.mySemantic.dimension and y.weight > .9]))
    # second, does either PO have connections to any SDM semantics with weights above threshold(=.9), or do both connnect to any SDM semantics below threshold(=.9).
    one_mag_sem_present = False
    both_mag_sem_present = False
    one_mag_sem_present_belowThresh = False
    both_mag_sem_present_belowThresh = False
    # check myPO and then myPO2 for mag sem above threshold(=.9). If you find any set one_mag_sem_present to True.
    for link in myPO.mySemantics:
        if link.mySemantic.name == 'same' or link.mySemantic.name == 'different' or link.mySemantic.name == 'more' or link.mySemantic.name == 'less':
            if link.weight > .9:
                one_mag_sem_present = True
                break
    for link in myPO2.mySemantics:
        if link.mySemantic.name == 'same' or link.mySemantic.name == 'different' or link.mySemantic.name == 'more' or link.mySemantic.name == 'less':
            if link.weight > .9:
                if one_mag_sem_present:
                    both_mag_sem_present = True
                    break
                else:
                    one_mag_sem_present = True
                    break
    # check if there are mag_sem in eachPO that are below threshold (=.9). If there are any, then set one_mag_sem_present_belowThresh to True, and if there are such sem in both, then set both_mag_sem_present_belowThresh to True.
    for link in myPO.mySemantics:
        if link.mySemantic.name == 'same' or link.mySemantic.name == 'different' or link.mySemantic.name == 'more' or link.mySemantic.name == 'less':
            if link.weight < .9:
                one_mag_sem_present_belowThresh = True
                break
    for link in myPO2.mySemantics:
        if link.mySemantic.name == 'same' or link.mySemantic.name == 'different' or link.mySemantic.name == 'more' or link.mySemantic.name == 'less':
            if link.weight < .9:
                if one_mag_sem_present_belowThresh == True:
                    both_mag_sem_present_belowThresh = True
                    break
                else:
                    one_mag_sem_present_belowThresh = True
                    break
    # third, find the dimension of highest over-lap. That is, find the semantic that codes the 'value' for each dimension in intersect_dim with the highest weight.
    # for each PO find the 'state' and 'value' semantics for each dimension in intersect_dim.
    high_dim = []
    high_dim_weight = 0.0
    for dim in intersect_dim:
        # add the weights of the 'value' semantics for the current dim for both myPO and myPO2. Make sure to add the weights of the most strongly connected dimensional semantics.
        dim_weights1 = [x for x in myPO.mySemantics if x.mySemantic.dimension == dim and x.mySemantic.ont_status == 'value']
        dim_weight1 = [x for x in dim_weights1 if x.weight == max(x.weight for x in dim_weights1)]
        dim_weights2 = [x for x in myPO2.mySemantics if x.mySemantic.dimension == dim and x.mySemantic.ont_status == 'value']
        dim_weight2 = [x for x in dim_weights2 if x.weight == max(x.weight for x in dim_weights2)]
        # get the current_weight by adding the weights of the dim_weight1 and dim_weight2 links as long as there are links in dim_weight1 and dim_weight2 (i.e., dim_weight1 and dim_weight2 are not empty; dim_weight1 and dim_weight2 will be empty if the current POs are not connected to any absolute dimensional values). Otherwise, current_weight is just 0.0.
        if len(dim_weight1) > 0 and len(dim_weight2) > 0:
            current_weight = dim_weight1[0].weight + dim_weight2[0].weight
        else:
            current_weight = 0.0
        if current_weight > high_dim_weight:
            high_dim = [dim]
            high_dim_weight = current_weight
        elif current_weight == high_dim_weight and current_weight > 0:
            # add the current dim to high_dim array.
            high_dim.append(dim)
    # flip a coin to select dimension from high_dim array as long as there are elements in the array, and then set intersect_dim to a list containing only high_dim.
    if len(high_dim) > 0:
        high_dim = random.sample(high_dim, 1)
        intersect_dim = high_dim
    else:
        intersect_dim = []
    # return the intersect_dim and mag_sem_present.
    return intersect_dim, one_mag_sem_present, both_mag_sem_present, one_mag_sem_present_belowThresh, both_mag_sem_present_belowThresh

# function to check whether to run entropy based magnitude comparison (within) and to run ntropy based magnitude comparison (within) if appropriate.
def check_and_run_ent_ops_within(myPO, myPO2, intersect_dim, one_mag_sem_present, both_mag_sem_present, one_mag_sem_present_belowThresh, both_mag_sem_present_belowThresh, extend_SDML, pred_only, pred_present, memory, mag_decimal_precision):
    # run energy based mag comparison. NOTE1: basic_en_based_mag_comparison() and basic_en_based_mag_refinement() do the same thing, but basic_en_based_mag_refinement() is faster when mag sem are already present (no need to build connections) and so is used when it can be (mag_sem_present_belowThresh). NOTE2: There is a separate call to basic_en_based_mag_refinement() for POs that are objects so that refinement does not work on objects when preds_only is True.
    if not one_mag_sem_present and not both_mag_sem_present_belowThresh and (myPO.predOrObj == 1) and (len(intersect_dim) >= 1):
        # no SDM sem present, so run mag_comparison.
        memory = basic_en_based_mag_comparison(myPO, myPO2, intersect_dim, memory, mag_decimal_precision)
    elif (myPO.predOrObj == 1) and not both_mag_sem_present and extend_SDML==True:
        if one_mag_sem_present or one_mag_sem_present_belowThresh:
            # there are mag_sem present at a high-level (multiple or strongly connected), so refine based on the strongest connected dimension.
            memory = basic_en_based_mag_refinement(myPO, myPO2, memory)
    elif (myPO.predOrObj == 0) and (len(intersect_dim) >= 1 and pred_only == False) and (pred_present == False) and not one_mag_sem_present:
        # no SDM present, so run mag_comparison on objects.
        memory = basic_en_based_mag_comparison(myPO, myPO2, intersect_dim, memory, mag_decimal_precision)
    # returns.
    return memory

# function to do basic energy/entropy based magnitude comparison when no magnitude semantics are present.
def basic_en_based_mag_comparison(myPO, myPO2, intersect_dim, memory, mag_decimal_precision=0):
    # find the semantic links connecting to the absolute dimensional value.
    sem_link_PO = [link for link in myPO.mySemantics if (link.mySemantic.dimension == intersect_dim[0]) and link.mySemantic.ont_status == 'value']
    sem_link_PO2 = [link for link in myPO2.mySemantics if (link.mySemantic.dimension == intersect_dim[0]) and link.mySemantic.ont_status == 'value']
    # if the dimension is numeric (e.g., height-10), then get the average value of all dimensional values in the sem_links_PO and sem_link_PO2 and assign these to extent1 and extent2 respectively.
    if isinstance(sem_link_PO[0].mySemantic.amount, numbers.Number):
        extent1 = sum([link.mySemantic.amount for link in sem_link_PO])/float(len(sem_link_PO))
        extent2 = sum([link.mySemantic.amount for link in sem_link_PO2])/float(len(sem_link_PO2))
    else:
        # otherwise, given that the dimension is non-numeric (e.g., colour-red), then set extent1 and extent2 to the respective values (e.g., red, green) of the 'value' semantics for the compared POs.
        extent1 = sem_link_PO[0].mySemantic.amount
        extent2 = sem_link_PO2[0].mySemantics.amount
    # compute ent_magnitudeMoreLessSame().
    more, less, same_flag, iterations = ent_magnitudeMoreLessSame(extent1, extent2, mag_decimal_precision)
    # find any other dimensional semantics with high weights so that the weights can be reduced by the entropy process.
    other_sem_links_PO = [link for link in myPO.mySemantics if (link.mySemantic.dimension is not None) and (link.mySemantic.dimension != intersect_dim[0])]
    other_sem_links_PO2 = [link for link in myPO2.mySemantics if (link.mySemantic.dimension is not None) and (link.mySemantic.dimension != intersect_dim[0])]
    sem_link_PO += other_sem_links_PO
    sem_link_PO2 += other_sem_links_PO2
    # connect the two POs to the appropraite relative magnitude semantics (based on the invariant patterns detected just above).
    if more == extent2:
        # call attach_mag_semantics() with myPO2 as firstPO and myPO as secondPO.
        memory = attach_mag_semantics(same_flag, myPO2, myPO, sem_link_PO2, sem_link_PO, memory)
    else:
        # call attach_mag_semantics() with myPO as firstPO and myPO2 as secondPO.
        memory = attach_mag_semantics(same_flag, myPO, myPO2, sem_link_PO, sem_link_PO2, memory)
    # return memory.
    return memory

# function to do basic energy/entropy based magnitude refinement when magnitude semantics are already present.
def basic_en_based_mag_refinement(myPO, myPO2, memory):
    # if there are magnitude semantics present, and there are some matching dimensions, then activate the appropriate magnitude semantics and matching dimensions, and adjust weights as appropriate (i.e., turn on the appropriate magnitude semantics for each PO, and adjust weight accordingly).
    mag_decimal_precision = 1
    # find the dimension on which they match if there is one.
    match_dim = list(set([x.mySemantic.dimension for x in myPO.mySemantics if x.mySemantic.dimension and x.mySemantic.ont_status == 'state' and x.weight > .9]).intersection([y.mySemantic.dimension for y in myPO2.mySemantics if y.mySemantic.dimension and y.mySemantic.ont_status == 'state' and y.weight > .9]))
    # if there is a single matching dimension, then find value on that dimension for each object and update magnitude semantic weights; elif there are multiple matching dimensions, find the matching dimension that each PO is most strongly connected to, and update magnitude semantic weights.
    if len(match_dim) == 1:
        # find the semantic links connecting to the absolute dimensional value.
        sem_link_PO = [link for link in myPO.mySemantics if (link.mySemantic.dimension == match_dim[0]) and link.mySemantic.ont_status == 'state']
        sem_link_PO2 = [link for link in myPO2.mySemantics if (link.mySemantic.dimension == match_dim[0]) and link.mySemantic.ont_status == 'state']
        # find value on that dimension for each object and then update magnitude semantic weights.
        PO1_dim_val, PO2_dim_val = 0.0, 0.0
        for link in myPO.myRBs[0].myObj[0].mySemantics:
            if link.mySemantic.dimension == match_dim[0] and link.mySemantic.ont_status == 'value' and link.mySemantic.amount != None:
                PO1_dim_val = link.mySemantic.amount
                break
        for link in myPO2.myRBs[0].myObj[0].mySemantics:
            if link.mySemantic.dimension == match_dim[0] and link.mySemantic.ont_status == 'value'and link.mySemantic.amount != None:
                PO2_dim_val = link.mySemantic.amount
                break
        # compute ent_magnitudeMoreLessSame().
        more, less, same_flag, iterations = ent_magnitudeMoreLessSame(PO1_dim_val, PO2_dim_val, mag_decimal_precision)
        # connect the two POs to the appropraite relative magnitude semantics (based on the invariant patterns detected just above).
        if more == PO2_dim_val:
            # call update_mag_semantics() with myPO2 as firstPO and myPO as secondPO.
            memory = update_mag_semantics(same_flag, myPO2, myPO, sem_link_PO2[0], sem_link_PO[0], memory)
        else:
            # call update_mag_semantics() with myPO as firstPO and myPO2 as secondPO.
            memory = update_mag_semantics(same_flag, myPO, myPO2, sem_link_PO[0], sem_link_PO2[0], memory)
    else:
        # find the matching dimension that each PO is most strongly connected to, and then update magnitude semantic weights.
        max_dim = None
        max_valuePO1 = 0.0
        current_dim_weight = 0.0
        for link in myPO.mySemantics:
            if isinstance(link.mySemantic.amount, (int, float, complex)):
                if link.weight > current_dim_weight:
                    max_dim = link.mySemantic.dimension
                    max_valuePO1 = link.mySemantic.amount
                    current_dim_weight = link.weight
        if max_dim:
            max_valuePO2 = 0.0
            current_dim_weight = 0.0
            for link in myPO2.mySemantics:
                if (link.mySemantic.dimension == max_dim) and (isinstance(link.mySemantic.amount, (int, float, complex))):
                    if link.weight > current_dim_weight:
                        max_valuePO2 = link.mySemantic.amount
                        current_dim_weight = link.weight
        # if there are max_dim values, use current max_dim and values to compute ent_magnitudeMoreLessSame().
        if max_dim:
            more, less, same_flag, iterations = ent_magnitudeMoreLessSame(max_valuePO1, max_valuePO2, mag_decimal_precision)
            # find the semantic links connecting to the absolute dimensional value.
            sem_link_PO = [link for link in myPO.mySemantics if (link.mySemantic.dimension == max_dim) and link.mySemantic.ont_status == 'state']
            sem_link_PO2 = [link for link in myPO2.mySemantics if (link.mySemantic.dimension == max_dim) and link.mySemantic.ont_status == 'state']
            # connect the two POs to the appropraite relative magnitude semantics (based on the invariant patterns detected just above).
            if more == max_valuePO2:
                # call update_mag_semantics() with myPO2 as firstPO and myPO as secondPO.
                memory = update_mag_semantics(same_flag, myPO2, myPO, sem_link_PO2[0], sem_link_PO[0], memory)
            else:
                # call update_mag_semantics() with myPO as firstPO and myPO2 as secondPO.
                memory = update_mag_semantics(same_flag, myPO, myPO2, sem_link_PO[0], sem_link_PO2[0], memory)
    # return memory.
    return memory

# function calculates more/less/same from two codes of extent based on entropy and competion.
def ent_magnitudeMoreLessSame(extent1, extent2, mag_decimal_precision=0):
    # convert extents to whole numbers using the mag_decimal_precision variable, rounding, and adding 1 (mag_decimal_precision and rouding to make decimal values into whole numbers, and adding 1 to account for the possibility that someone has used 0 values for magnitudes).
    extent1_rounded = round(extent1*(pow(100, mag_decimal_precision)))+1
    extent2_rounded = round(extent2*(pow(100, mag_decimal_precision)))+1
    # take two representations of extent, and have them compete.
    # first build a simple entropyNet with the extents as lower-level nodes.
    entropyNet = dataTypes.entropyNet()
    # populate the entropyNet.
    entropyNet.fillin(extent1_rounded, extent2_rounded)
    # until the network settles (i.e., only one output node is active for 3 iterations), keep running.
    entropyNet.runEntropyNet(0.3, 0.1)
    # the active output node is 'more', and the inactive output node is 'less', or the two extents are equal or 'same'.
    # there is a relation between the settling delta, and the size of the magnitude difference. The network settles with a higher between POs as the delta between extents increases (of course). There exists some level at which a delta is imperceptible, which could be only when the delta is 0 (i.e., it's imperceptible because it can't be perceived), or some higher value. That value is a free parameter. Right now, we set that parameter to 0.09.
    theta = 0.09
    if abs(entropyNet.outputs[0].act - entropyNet.outputs[1].act) < theta:
        # treat the extents as 'same'.
        more = 'NONE'
        less = 'NONE'
        same_flag = True
    elif entropyNet.outputs[0].act > entropyNet.outputs[1].act:
        more = extent1
        less = extent2
        same_flag = False
    elif entropyNet.outputs[0].act < entropyNet.outputs[1].act:
        more = extent2
        less = extent1
        same_flag = False
    # return more, less, a flag indicating whether the values are the same (called same_flag), and the number of iterations to settling (stored in entropyNet.settled_iters).
    return more, less, same_flag, entropyNet.settled_iters

# Function to attache magnitude semantics to POs for use with entropy_ops.
def attach_mag_semantics(same_flag, firstPO, secondPO, sem_link_PO, sem_link_PO2, memory):
    # NOTE: In this function, firstPO is the larger and secondPO is the smaller (unless same_flag is True, in which case the two are equal).
    # NOTE: I think that the following bit of code is redundent, but it's here just in case to make sure that no magnitude semantics are attached to the POs if either of them are already attached to a magnitude semantic. Check if either PO is attached to 'more' or 'less' or 'same', and if so, set attach_mag_sem_flag to False.
    attach_mag_sem_flag = True
    for semantic in firstPO.mySemantics:
        if semantic.mySemantic.name == 'more' or semantic.mySemantic.name == 'less' or semantic.mySemantic.name == 'same':
            attach_mag_sem_flag = False
    # if attach_mag_sem_flag is True, then go ahead and attach magnitude semantics.
    if attach_mag_sem_flag:
        if same_flag:
            # connect both POs to the 'same' semantic.
            # find the 'same' semantic (if it does not exist, create it).
            sem_exist_flag = False
            for semantic in memory.semantics:
                if semantic.name == 'same':
                    # connect the semantic to both POs.
                    new_link1 = dataTypes.Link(firstPO, [], semantic, 1.0)
                    firstPO.mySemantics.append(new_link1)
                    semantic.myPOs.append(new_link1)
                    memory.Links.append(new_link1)
                    new_link2 = dataTypes.Link(secondPO, [], semantic, 1.0)
                    secondPO.mySemantics.append(new_link2)
                    semantic.myPOs.append(new_link2)
                    memory.Links.append(new_link2)
                    # set sem_exist_flag to True and break.
                    sem_exist_flag = True
                    break
            # if the 'same semantic does not exist, make it and connect it to the two POs.
            if not sem_exist_flag:
                # you have the create the semantics.
                same_semantic = dataTypes.Semantic('same', 'nil', None, 'SDM')
                memory.semantics.append(same_semantic)
                # create links between POs and 'same'.
                PO1_link = dataTypes.Link(firstPO, [], same_semantic, 1.0)
                firstPO.mySemantics.append(PO1_link)
                same_semantic.myPOs.append(PO1_link)
                memory.Links.append(PO1_link)
                PO2_link = dataTypes.Link(secondPO, [], same_semantic, 1.0)
                secondPO.mySemantics.append(PO2_link)
                same_semantic.myPOs.append(PO2_link)
                memory.Links.append(PO2_link)
        else:
            # connect firstPO to 'more' and secondPO to 'less'.
            # find the 'more' and 'less' semantics (if they do not exist, create them).
            sem_exist_flag = False
            sem_added = 0
            for semantic in memory.semantics:
                if semantic.name == 'more':
                    # connect the sementic to firstPO.
                    new_link = dataTypes.Link(firstPO, [], semantic, 1.0)
                    firstPO.mySemantics.append(new_link)
                    semantic.myPOs.append(new_link)
                    memory.Links.append(new_link)
                    # set the sem_exist flag to True, and check if you've connected both 'more' and 'less' semantics (i.e., sem_added == 2). If yes, then break.
                    sem_exist_flag = True
                    sem_added += 1
                    if sem_added == 2:
                        break
                elif semantic.name == 'less':
                    # connect the sementic to secondPO.
                    new_link = dataTypes.Link(secondPO, [], semantic, 1.0)
                    secondPO.mySemantics.append(new_link)
                    semantic.myPOs.append(new_link)
                    memory.Links.append(new_link)
                    # set the sem_exist flag to True, and check if you've connected both 'more' and 'less' semantics (i.e., sem_added == 2). If yes, then break.
                    sem_exist_flag = True
                    sem_added += 1
                    if sem_added == 2:
                        break
            if not sem_exist_flag:
                # you have the create the semantics.
                more_semantic = dataTypes.Semantic('more', 'nil', None, 'SDM')
                less_semantic = dataTypes.Semantic('less', 'nil', None, 'SDM')
                memory.semantics.append(more_semantic)
                memory.semantics.append(less_semantic)
                # create links between firstPO and 'more'.
                more_link = dataTypes.Link(firstPO, [], more_semantic, 1.0)
                firstPO.mySemantics.append(more_link)
                more_semantic.myPOs.append(more_link)
                memory.Links.append(more_link)
                # create links between secondPO and 'less'.
                less_link = dataTypes.Link(secondPO, [], less_semantic, 1.0)
                secondPO.mySemantics.append(less_link)
                less_semantic.myPOs.append(less_link)
                memory.Links.append(less_link)
        # reduce weight to absolute value semantics to .5 (as this process constitutes a comparison).
        for link in sem_link_PO:
            link.weight /= 2
        for link in sem_link_PO2:
            link.weight /= 2
    # return memory.
    return memory

# function to update the connections to magnitude semantics during the basic_en_based_mag_refinement() function.
def update_mag_semantics(same_flag, firstPO, secondPO, sem_link_PO, sem_link_PO2, memory):
    # NOTE: In this function, firstPO is the larger and secondPO is the smaller (unless same_flag is True, in which case the two are equal).
    if same_flag:
        # update the connections of both POs to the 'same' semantic and the sem_link_PO semantic, and halve weights to other semantics.
        found_same = False
        for link in firstPO.mySemantics:
            if link is sem_link_PO:
                link.weight = 1.0
            elif link.mySemantic.name == 'same':
                link.weight = 1.0
                found_same = True
            else:
                link.weight /= 2
        if not found_same:
            # connect firstPO to same semantic.
            for semantic in memory.semantics:
                if semantic.name == 'same':
                    # connect the samentic to firstPO.
                    new_link = dataTypes.Link(firstPO, [], semantic, 1.0)
                    firstPO.mySemantics.append(new_link)
                    semantic.myPOs.append(new_link)
                    memory.Links.append(new_link)
                    break
        found_same = False
        for link in secondPO.mySemantics:
            if link is sem_link_PO:
                link.weight = 1.0
            elif link.mySemantic.name == 'same':
                link.weight = 1.0
                found_same = True
            else:
                link.weight /= 2
        if not found_same:
            # connect secondPO to same semantic.
            for semantic in memory.semantics:
                if semantic.name == 'same':
                    # connect the samentic to secondPO.
                    new_link = dataTypes.Link(firstPO, [], semantic, 1.0)
                    secondPO.mySemantics.append(new_link)
                    semantic.myPOs.append(new_link)
                    memory.Links.append(new_link)
                    break
    else:
        # update the connections of firstPO to the 'more' semantic and the sem_link_PO semantic, and halve weights to other semantics.
        found_more = False
        for link in firstPO.mySemantics:
            if link is sem_link_PO:
                link.weight = 1.0
            elif link.mySemantic.name == 'more':
                link.weight = 1.0
                found_more = True
            else:
                link.weight /= 2
        if not found_more:
            # connect firstPO to more semantic.
            for semantic in memory.semantics:
                if semantic.name == 'more':
                    # connect the samentic to firstPO.
                    new_link = dataTypes.Link(firstPO, [], semantic, 1.0)
                    firstPO.mySemantics.append(new_link)
                    semantic.myPOs.append(new_link)
                    memory.Links.append(new_link)
                    break
        # update the connections of secondPO to the 'less' semantic and the sem_link_PO semantic, and halve weights to other semantics.
        found_less = False
        for link in secondPO.mySemantics:
            if link is sem_link_PO2:
                link.weight = 1.0
            elif link.mySemantic.name == 'less':
                link.weight = 1.0
                found_less = True
            else:
                link.weight /= 2
        if not found_less:
            # connect secondPO to less semantic.
            for semantic in memory.semantics:
                if semantic.name == 'less':
                    # connect the samentic to secondPO.
                    new_link = dataTypes.Link(firstPO, [], semantic, 1.0)
                    secondPO.mySemantics.append(new_link)
                    semantic.myPOs.append(new_link)
                    memory.Links.append(new_link)
                    break
    # done.
    return memory

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
    diff_array = list(map(operator.sub, error_array, act_array))
    sum_diff = sum(diff_array)
    sum_act = sum(act_array)
    # make sure that you're not dividing by 0 (which can happen if you've tried to compute entropy for empty objects).
    if sum_act > 0:
        difference_ratio = float(sum_diff)/float(sum_act)
    else:
        difference_ratio = 'undefined'
    # return the difference_ratio.
    return difference_ratio

# prediction routine.
def predication_routine(memory, made_new_pred, gamma):
    # if you have made a new pred (i.e., made_new_pred == True), then learn connections between that pred and active semantics. Otherwise, check if the most active recipient PO meets predication requirements, and if so, infer a new pred.
    if made_new_pred:
        # for each active semantic, learn connections between that semantic and the new pred (NOTE: the new pred is the last PO in memory.POs).
        for semantic in memory.semantics:
            connected_to_newPO = False
            # check all the semantic's Links. If any of the semantic Links are to the new PO, set connected_to_newPO to True (i.e., don't bother making a Link for the current semantic and the new PO because one already exits), and update the connection between the new PO and the current semantic.
            for Link in semantic.myPOs:
                if memory.newSet.POs[-1] == Link.myPO:
                    # update the connection weight.
                    Link.weight += (1*(Link.mySemantic.act-Link.weight)*gamma)
                    connected_to_newPO = True
            # if not connected_to_newPO, then learn a connection if semantic.act > 0.
            if (not connected_to_newPO) and (semantic.act > 0):
                # infer a new Link for new pred and active semantic.
                new_Link = dataTypes.Link(memory.newSet.POs[-1], 'nil', semantic, 0.0)
                # update the weight of the Link.
                new_Link.weight = 1*(semantic.act-0)*gamma
                # connect new Link to semantic and new pred and add Link to memory.Links.
                memory.newSet.POs[-1].mySemantics.append(new_Link)
                semantic.myPOs.append(new_Link)
                memory.Links.append(new_Link)
    else:
        # get the most active recipient PO.
        active_rec_PO = get_most_active_unit(memory.recipient.POs)
        # make sure that there is actually and active_rec_PO (i.e., active_rec_PO != None), of you'll have a crash when trying to check the active_rec_PO.predOrObj.
        if active_rec_PO is not None:
            # if the most active unit is an object and is active above threshold(=.6), and the unit I map to most in the driver is also active above threshold, and our mapping connection is above .75, then infer new pred and RB and connect new pred to new RB, and new RB to active recipient object, and set made_new_pred to True.
            if active_rec_PO.predOrObj == 0 and active_rec_PO.act > .6:
                mapping_connection = get_my_max_map(active_rec_PO)
                if mapping_connection != 'null':
                    if mapping_connection.driverToken.act > .6 and (mapping_connection.weight > .75):
                        # copy the recipient object into the newSet.
                        # make a new object as a copy of active_rec_PO, and fill in .my_maker_unit and .my_made_unit fields for the new object and for active_rec_PO.
                        new_obj = dataTypes.POUnit(active_rec_PO.name, 'newSet', 'null', True, 'null', 0)
                        new_obj.my_maker_unit = active_rec_PO
                        active_rec_PO.my_made_unit = new_obj
                        # fill in the semantics.
                        for link in active_rec_PO.mySemantics:
                            # create a new link between link.mySemantic and new_obj
                            new_link = dataTypes.Link(new_obj, None, link.mySemantic, link.weight)
                            # add the new_link to memory, to new_obj, and to link.mySemantic.
                            memory.Links.append(new_link)
                            new_obj.mySemantics.append(new_link)
                            link.mySemantic.myPOs.append(new_link)
                        # add the new_obj to memory and to newSet.
                        memory.POs.append(new_obj)
                        memory.newSet.POs.append(new_obj)
                        # infer new pred and new myRB.
                        # give the new PO the name 'nil' + the len(memory.POs)+1.
                        new_PO_name = 'nil' + str(len(memory.POs)+1)
                        new_pred = dataTypes.POUnit(new_PO_name, 'newSet', 'null', True, 'null', 1)
                        new_RB_name = RB_name=new_PO_name+'+'+new_obj.name
                        new_RB = dataTypes.RBUnit(new_RB_name, 'newSet', 'null', True, 'null')
                        # connect new_pred to new RB and vise versa.
                        new_pred.myRBs.append(new_RB)
                        new_RB.myPred.append(new_pred)
                        # connect new_obj to RB and vise versa.
                        new_RB.myObj.append(new_obj)
                        new_obj.myRBs.append(new_RB)
                        # add new_pred and new_RB to memory, and to newSet.
                        # NOTE: you are NOT connecting these units to an analog now. They will be connected to a new analog at the end of predication.
                        memory.POs.append(new_pred)
                        memory.RBs.append(new_RB)
                        memory.newSet.POs.append(new_pred)
                        memory.newSet.RBs.append(new_RB)
                        # update the made_new_pred flag to True.
                        made_new_pred = True
    # returns.
    return memory, made_new_pred

# form new relation (myP unit).
def rel_form_routine(memory, inferred_new_P):
    # check to see if a new P has been inferred (i.e, inferred_new_P == True).
    # If not, AND there are no other active Ps in the recipient, infer a new P unit in the recipient.
    # Connect the new P to recipient RBs active above threshold(=.8).
    if inferred_new_P:
        # the new P is the last inferred P, so the last unit in recipient.Ps.
        # connect the newP to active RBs above threshold and not already connected to the P unit (and vise verasa).
        for myRB in memory.recipient.RBs:
            if (myRB.act >= .8) and (myRB not in memory.recipient.Ps[-1].myRBs):
                # connect RB and the new P unit, and update the P unit's .myanalog field if the field is empty.
                memory.recipient.Ps[-1].myRBs.append(myRB)
                myRB.myParentPs.append(memory.recipient.Ps[-1])
                if not memory.recipient.Ps[-1].myanalog:
                    # set the new P's .myanalog to the current RB's analog.
                    memory.recipient.Ps[-1].myanalog = myRB.myanalog
                    # add the new P to the analog's .myPs list.
                    myRB.myanalog.myPs.append(memory.recipient.Ps[-1])
    else:
        # name of the new P should be RB1+RB2+...RBx. For now leave blank and name after phase set.
        my_name = ''
        new_P = dataTypes.PUnit(my_name, 'recipient', None, True, None) # NOTE: .myanalog field is left blank for now and updated if the new P sticks around (i.e., if it connects to multiple RBs). The updating is done in the .do_rel_form() function above.
        # (my_name, my_set, analog, inferred_now, myanalog)
        memory.Ps.append(new_P)
        memory.recipient.Ps.append(new_P)
        # set inferred_new_P to True.
        inferred_new_P = True
    # returns.
    return memory, inferred_new_P

# schematization routine.
def schematization_routine(memory, gamma, phase_set_iterator):
    # for each driver token unit, if that unit is most active unit of its type (e.g., most active P), and maps to a recipient unit, then check if you have caused a unit to be inferred in newSet. If you have caused a unit to be inferred, then set that newSet unit's activation to 1.0, and update connections to other newSet units (myPs to RBs, RBs to Ps and POs, POs to RBs), and for POs to semantic units. If not, then cause a new unit to be inferred.
    # first, find most active myP for parent Ps.
    most_active_P = get_most_active_Punit(memory.driver.Ps, 'parent')
    # make sure I've returned a unit.
    if most_active_P:
        # if most_active_P has caused a unit to be inferred in newSet, update the newSet unit, otherwise, infer a newSet unit corresponding to most_active_P.
        if most_active_P.my_made_unit:
            # if I am active above threshold, update my newSet unit (set activation to 1.0, connect to active newSet RBs).
            if most_active_P.act > .4:
                most_active_P.my_made_unit.act = 1.0
                for myRB in memory.newSet.RBs:
                    if myRB.act > .5:
                        # connect any active newSet RB and most_active_P's inferred unit as parent myP.
                        # conect as parent if units not already connected.
                        if not myRB in most_active_P.my_made_unit.myRBs:
                            most_active_P.my_made_unit.myRBs.append(myRB)
                            myRB.myParentPs.append(most_active_P.my_made_unit)
        else: # I have not caused a unit to be inferred.
            # check if I am active above threshold (=.4), and I map to a recipient unit above threshold (=.75).
            if (most_active_P.act >= .4) and (most_active_P.max_map >= .75):
                # infer a newSet P unit (with activation 1.0) and add it to memory. Set the value of the .myanalog field to 'null', as you will create an analog to house all newSet units at the end of the .doSchematization() routine above.
                newSet_new_P = dataTypes.PUnit('nil', 'newSet', 0, True, 'null')
                newSet_new_P.mode = most_active_P.mode
                newSet_new_P.act = 1.0
                newSet_new_P.my_maker_unit = most_active_P
                most_active_P.my_made_unit = newSet_new_P
                memory.Ps.append(newSet_new_P)
                memory.newSet.Ps.append(newSet_new_P)
    # Second, find most active P for child Ps.
    most_active_P = get_most_active_Punit(memory.driver.Ps, 'child')
    # make sure I've returned a unit.
    if most_active_P:
        # if most_active_P has caused a unit to be inferred in newSet, update the newSet unit, otherwise, infer a newSet unit corresponding to most_active_P.
        if most_active_P.my_made_unit:
            # if I am active above threshold, update my newSet unit (set activation to 1.0, connect to active newSet RBs).
            if most_active_P.act > .4:
                most_active_P.my_made_unit.act = 1.0
                for myRB in memory.newSet.RBs:
                    if myRB.act > .5:
                        # connect any active newSet RB and most_active_P's inferred unit as child myP.
                        # conect as child if units not already connected.
                        if not myRB in most_active_P.my_made_unit.myRBs:
                            most_active_P.my_made_unit.myParentRBs.append(myRB)
                            myRB.myChildP.append(most_active_P.my_made_unit)
        else: # I have not caused a unit to be inferred.
            # check if I am active above threshold (=.4), and I map to a recipient unit above threshold (=.75).
            if (most_active_P.act >= .4) and (most_active_P.max_map >= .75):
                # infer a newSet P unit (with activation 1.0) and add it to memory. Set the value of the .myanalog field to 'null', as you will create an analog to house all newSet units at the end of the .doSchematization() routine above.
                newSet_new_P = dataTypes.PUnit('nil', 'newSet', 0, True, 'null')
                newSet_new_P.mode = most_active_P.mode
                newSet_new_P.act = 1.0
                newSet_new_P.my_maker_unit = most_active_P
                most_active_P.my_made_unit = newSet_new_P
                memory.Ps.append(newSet_new_P)
                memory.newSet.Ps.append(newSet_new_P)
    # find most active myRB.
    most_active_RB = get_most_active_unit(memory.driver.RBs)
    # if most_active_RB has caused a unit to be inferred in newSet, update the newSet unit, otherwise, infer a newSet unit corresponding to most_active_RB.
    if most_active_RB:
        if most_active_RB.my_made_unit:
            # update my newSet unit (set activation to 1.0, connect to active newSet POs).
            most_active_RB.my_made_unit.act = 1.0
            # I don't think you need to do learning for Ps as you do it for Ps above.
            #for PO in memory.newSet.POs:
            for myPO in memory.newSet.POs:
                if myPO.act > .5:
                    # connect as pred or object if not already connected.
                    if myPO.predOrObj == 1:
                        if not myPO in most_active_RB.my_made_unit.myPred:
                            most_active_RB.my_made_unit.myPred.append(myPO)
                            myPO.myRBs.append(most_active_RB.my_made_unit)
                    elif myPO.predOrObj == 0:
                        if not myPO in most_active_RB.my_made_unit.myObj:
                            most_active_RB.my_made_unit.myObj.append(myPO)
                            myPO.myRBs.append(most_active_RB.my_made_unit)
        else: # I have not caused a unit to be inferred.
            # check if I am active above threshold (=.4), and I map to a recipient unit above threshold (=.75).
            if (most_active_RB.act >= .4) and (most_active_RB.max_map >= .75):
                # infer a newSet RB unit (with activation 1.0) and add it to memory. Set the value of the .myanalog field to 'null', as you will create an analog to house all newSet units at the end of the .doSchematization() routine above.
                newSet_new_RB = dataTypes.RBUnit('nil', 'newSet', 0, True, 'null')
                newSet_new_RB.act = 1.0
                newSet_new_RB.my_maker_unit = most_active_RB
                most_active_RB.my_made_unit = newSet_new_RB
                memory.RBs.append(newSet_new_RB)
                memory.newSet.RBs.append(newSet_new_RB)
    # find most active myPO.
    most_active_PO = get_most_active_unit(memory.driver.POs)
    # if most_active_PO has caused a unit to be inferred in newSet, update the newSet unit, otherwise, infer a newSet unit corresponding to most_active_PO.
    if most_active_PO:
        if most_active_PO.my_made_unit:
            # update my newSet unit (set activation to 1.0, connect to active semantics).
            most_active_PO.my_made_unit.act = 1.0
            for semantic in memory.semantics:
                # check if I am connected to the newSet myPO. If yes, update my connection based on semantic activation. If not, and I am active, infer a connection.
                connected_to_newSetPO = False
                # check all the semantic's Links. If any of the semantic Links are to the newSet_PO, set connected_to_newSetPO to True (i.e., don't bother making a Link for the current semantic and the newSet_PO because one already exits), and update the connection between the newSet_PO and the current semantic.
                for Link in semantic.myPOs:
                    if most_active_PO.my_made_unit == Link.myPO:
                        # update the connection weight.
                        Link.weight += (1*(Link.mySemantic.act-Link.weight)*gamma)
                        connected_to_newSetPO = True
                # if not connected_to_newPO, then learn a connection if semantic.act > 0.
                if (not connected_to_newSetPO) and (semantic.act > 0):
                    # infer a new Link for new PO and active semantic.
                    new_Link = dataTypes.Link(most_active_PO.my_made_unit, 'nil', semantic, 0.0)
                    # update the weight of the Link.
                    new_Link.weight = 1*(semantic.act-0)*gamma
                    # connect new Link to semantic and new pred and add Link to memory.Links.
                    most_active_PO.my_made_unit.mySemantics.append(new_Link)
                    semantic.myPOs.append(new_Link)
                    memory.Links.append(new_Link)
        else: # I have not caused a unit to be inferred.
            # check if I am active above threshold (=.4), and I map to a recipient unit above threshold (=.75).
            if (most_active_PO.act >= .4) and (most_active_PO.max_map >= .75):
                # infer a newSet PO unit (with activation 1.0) and add it to memory. Set the value of the .myanalog field to 'null', as you will create an analog to house all newSet units at the end of the .doSchematization() routine above.
                # give the new PO the name 'nil' + the len(memory.POs)+1.
                new_PO_name = 'nil' + str(len(memory.POs)+1)
                newSet_new_PO = dataTypes.POUnit(new_PO_name, 'newSet', 0, True, 'null', most_active_PO.predOrObj)
                newSet_new_PO.act = 1.0
                newSet_new_PO.my_maker_unit = most_active_PO
                most_active_PO.my_made_unit = newSet_new_PO
                memory.POs.append(newSet_new_PO)
                memory.newSet.POs.append(newSet_new_PO)
    # returns.
    return memory

# function to perform relational generalization.
def rel_gen_routine(memory, gamma, recip_analog):
    # for relational generalization: Recall that only RBs in the driver from the analog that contains mapped tokens are firing. If active driver unit maps to no unit in the recipient, then infer a unit in recipient, set it's activation to 1, and attach it to active units above and below itself (e.g., connect new RBs to Ps and POs, new POs to RBs and semantics, etc.) to which it is NOT already connected. Make sure to mark that the new unit is inferred from the active driver unit (i.e., update .my_made_unit of driver unit and .my_maker_unit of new recipient unit). Newly inferred tokens become part of the same analog as the items in the recipient that map to the analog in the driver that contains the tokens that are currently driving relational generalisation. For example, if the tokens in the driver are part of analog 1, and analog 1 elements map to items in the recipient that are in analog 3, the newly inferred units in the recipient become part of analog 3.
    # start with the PO units. Find the most active driver PO, and make sure that it is both active above .5 and does not map to anything.
    active_PO = get_most_active_unit(memory.driver.POs)
    if active_PO is not None:
        if active_PO.act >= .5 and active_PO.max_map == 0:
            # if the active unit has not made a unit (i.e., my_made_unit is empty), then make a new unit in recipient to correspond to active unit. Otherwise (i.e., if active unit HAS made a new unit), update the connections between the active unit's made unit and other active recipient units.
            if active_PO.my_made_unit is None:
                # infer a new PO in recipient of same type as active driver PO, and set activation to 1.
                mytype = active_PO.predOrObj
                # give the new PO the name 'nil' + the len(memory.POs)+1.
                new_PO_name = 'nil' + str(len(memory.POs)+1)
                new_PO = dataTypes.POUnit(new_PO_name, 'recipient', None, True, recip_analog, mytype)
                new_PO.act = 1
                # update the .my_made_unit for driver unit and .my_maker_unit for new recipient unit.
                active_PO.my_made_unit = new_PO
                new_PO.my_maker_unit = active_PO
                # add new PO to memory and memory.recipient.
                memory.POs.append(new_PO)
                memory.recipient.POs.append(new_PO)
                memory.newSet.POs.append(new_PO)
            else:
                # update connections between the new unit and below units.
                # new unit is a PO, so update connections to semantics.
                # set activation of new PO to 1.
                active_PO.my_made_unit.act = 1
                # update connections between the new recipient unit and active semantics.
                # for each active semantic, learn connections between that semantic and the new myPO.
                for semantic in memory.semantics:
                    connected_to_newPO = False
                    # check all the semantic's Links. If any of the semantic Links are to the new PO, set connected_to_newPO to True (i.e., don't bother making a Link for the current semantic and the new PO because one already exits), and update the connection between the new PO and the current semantic.
                    for Link in semantic.myPOs:
                        if active_PO.my_made_unit == Link.myPO:
                            # update the connection weight.
                            Link.weight += (1*(Link.mySemantic.act-Link.weight)*gamma)
                            connected_to_newPO = True
                            #print (Link.mySemantic.name)
                            #print (Link.weight)
                    # if not connected_to_newPO, then learn a connection if semantic.act > 0.
                    if (not connected_to_newPO) and (semantic.act > 0):
                        # infer a new Link for new PO and active semantic.
                        new_Link = dataTypes.Link(active_PO.my_made_unit, 'nil', semantic, 0.0)
                        # update the weight of the Link.
                        new_Link.weight = 1*(semantic.act-0)*gamma
                        # connect new Link to semantic and new pred and add Link to memory.Links.
                        active_PO.my_made_unit.mySemantics.append(new_Link)
                        semantic.myPOs.append(new_Link)
                        memory.Links.append(new_Link)
    # move to the RB units. Find the most active driver RB, and make sure that it is both active above .5 and does not map to anything.
    active_RB = get_most_active_unit(memory.driver.RBs)
    if active_RB is not None:
        if active_RB.act >= .5 and active_RB.max_map == 0:
            # if the active unit has not made a unit (i.e., my_made_unit is empty), then make a new unit in recipient to correspond to active unit. Otherwise (i.e., if active unit HAS made a new unit), update the connections between the active unit's made unit and other active recipient units.
            if active_RB.my_made_unit is None:
                # infer a new RB in recipient, and set activation to 1.
                new_RB = dataTypes.RBUnit('nil', 'recipient', None, True, recip_analog)
                new_RB.act = 1
                # update the .my_made_unit for driver unit and .my_maker_unit for new recipient unit.
                active_RB.my_made_unit = new_RB
                new_RB.my_maker_unit = active_RB
                # add new RB to memory and memory.recipient.
                memory.RBs.append(new_RB)
                memory.recipient.RBs.append(new_RB)
                memory.newSet.RBs.append(new_RB)
            else:
                # update connections between the new unit and other recipient units below.
                # new unit is a RB, so update connections to POs.
                # set activation of new RB to 1.
                active_RB.my_made_unit.act = 1
                # Find the most active PO and connect to the new unit if not already connected, and PO is active above 0.7.
                most_active_PO = get_most_active_unit(memory.recipient.POs)
                if most_active_PO:
                    if most_active_PO.act >= .7:
                        if (not most_active_PO in active_RB.my_made_unit.myPred) and most_active_PO.predOrObj == 1:
                            most_active_PO.myRBs.append(active_RB.my_made_unit)
                            active_RB.my_made_unit.myPred.append(most_active_PO)
                        elif (not most_active_PO in active_RB.my_made_unit.myObj) and most_active_PO.predOrObj == 0:
                            most_active_PO.myRBs.append(active_RB.my_made_unit)
                            active_RB.my_made_unit.myObj.append(most_active_PO)
    # finally, the P units.
    # first, the P units in child mode. Find the most active driver P in child mode, and make sure that it is both active above .5 and does not map to anything.
    active_P = get_most_active_Punit(memory.driver.Ps, 'child')
    # make sure that the returned active P is actually there (i.e., there is an active P in child mode).
    if active_P:
        if active_P.act >= .5 and active_P.max_map == 0:
            # if the active unit has not made a unit (i.e., my_made_unit is empty), then make a new unit in recipient to correspond to active unit. Otherwise (i.e., if active unit HAS made a new unit), update the connections between the active unit's made unit and other active recipient units.
            if active_P.my_made_unit is None:
                # infer a new P in recipient, make sure it is in child mode, and set its activation to 1.
                new_P = dataTypes.PUnit('nil', 'recipient', None, True, recip_analog)
                new_P.mode = -1
                new_P.act = 1
                # update the .my_made_unit for driver unit and .my_maker_unit for new recipient unit.
                active_P.my_made_unit = new_P
                new_P.my_maker_unit = active_P
                # add new P to memory and memory.recipient.
                memory.Ps.append(new_P)
                memory.recipient.Ps.append(new_P)
                memory.newSet.Ps.append(new_P)
            else:
                # update connections between the new unit and other recipient units.
                # set activation of new P to 1.
                active_P.my_made_unit.act = 1
                # new unit is a P in child mode, so update connections to RBs above. Find the most active RB and connect to the new unit if not already connected, and RB is active above 0.7.
                most_active_RB = get_most_active_unit(memory.recipient.RBs)
                if most_active_RB.act >= .7 and (not most_active_RB in active_P.my_made_unit.myParentRBs):
                    active_P.my_made_unit.myParentRBs.append(most_active_RB)
                    most_active_RB.myChildP.append(active_P.my_made_unit)
    # now for the P units in parent mode. Find the most active driver P in parent mode, and make sure that it is both active above .5 and does not map to anything.
    active_P = get_most_active_Punit(memory.driver.Ps, 'parent')
    # make sure that the returned active P is actually there (i.e., there is an active P in parent mode).
    if active_P:
        if active_P.act >= .5 and active_P.max_map == 0:
            # if the active unit has not made a unit (i.e., my_made_unit is empty), then make a new unit in recipient to correspond to active unit. Otherwise (i.e., if active unit HAS made a new unit), update the connections between the active unit's made unit and other active recipient units.
            if active_P.my_made_unit is None:
                # infer a new P in recipient, make sure it is in parent mode, and set its activation to 1.
                new_P = dataTypes.PUnit('nil', 'recipient', None, True, recip_analog)
                new_P.mode = 1
                new_P.act = 1
                # update the .my_made_unit for driver unit and .my_maker_unit for new recipient unit.
                active_P.my_made_unit = new_P
                new_P.my_maker_unit = active_P
                # add new P to memory and memory.recipient.
                memory.Ps.append(new_P)
                memory.recipient.Ps.append(new_P)
                memory.newSet.Ps.append(new_P)
            else:
                # update connections between the new unit and other recipient units.
                # set activation of new P unit to 1.
                active_P.my_made_unit.act = 1
                # new unit is a P in parent mode, so update connections to RBs below. Find the most active RB and connect to the new unit if not already connected, and RB is active above 0.5, and RB is not already connected to another P unit.
                most_active_RB = get_most_active_unit(memory.recipient.RBs)
                if most_active_RB.act >= .5 and (not most_active_RB in active_P.my_made_unit.myRBs) and len(most_active_RB.myParentPs) < 1:
                    active_P.my_made_unit.myRBs.append(most_active_RB)
                    most_active_RB.myParentPs.append(active_P.my_made_unit)
    # returns.
    return memory

# ekaterina: function to assist .do_compression() and .do_unpacking(); recruits a new RB unit
def infer_RB(memory, new_RB):
    # if there is no new_RB, make one and assign it to new_RB
    if not new_RB:
        made_RB_name = 'rb_' + str(len(memory.RBs)+1)
        newSet_new_RB = dataTypes.RBUnit(made_RB_name, 'newSet', None, True, None)
        newSet_new_RB.act = 1.0
        memory.RBs.append(newSet_new_RB)
        memory.newSet.RBs.append(newSet_new_RB)
        new_RB = newSet_new_RB
    return memory, new_RB

# ekaterina: function to assist .do_compression() and .do_unpacking(); recruits a new PO unit which learns connections to the semantics and to the RB unit
def infer_PO(memory, new_RB, gamma):
    # find the most active PO, and if that PO has already caused a PO to be inferred in newSet, learn connections between the inferred PO and active semantics and the new_RB, or otherwise infer a PO in newSet to match the most active PO
    most_active_PO = get_most_active_unit(memory.driver.POs)
    # print(most_active_PO)
    if most_active_PO.my_made_unit:
        # update my newSet unit (set activation to 1.0, connect to active semantics).
        most_active_PO.my_made_unit.act = 1.0
        for semantic in memory.semantics:
            # check if I am connected to the newSet myPO. If yes, update my connection based on semantic activation. If not, and I am active, infer a connection.
            connected_to_newSetPO = False
            # check all the semantic's Links. If any of the semantic Links are to the newSet_PO, set connected_to_newSetPO to True (i.e., don't make a Link for the current semantic and the newSet_PO because one already exits), and update the connection between the newSet_PO and the current semantic by a simple Hebbian rule.
            for Link in semantic.myPOs:
                if most_active_PO.my_made_unit == Link.myPO:
                    # update the connection weight.
                    Link.weight += (1*(Link.mySemantic.act-Link.weight)*gamma)
                    connected_to_newSetPO = True

            # if not connected_to_newPO, then learn a connection if semantic.act > 0.
            if (not connected_to_newSetPO) and (semantic.act > 0):
                # infer a new Link for new PO and active semantic.
                new_Link = dataTypes.Link(most_active_PO.my_made_unit, 'nil', semantic, 0.0)
                # update the weight of the Link.
                new_Link.weight = 1*(semantic.act-0)*gamma
                # connect new Link to semantic and new pred and add Link to memory.Links.
                most_active_PO.my_made_unit.mySemantics.append(new_Link)
                semantic.myPOs.append(new_Link)
                memory.Links.append(new_Link)

        # learn connection between inferred PO and new_RB if none already exists
        if most_active_PO.predOrObj == 1:
            if most_active_PO.my_made_unit not in new_RB.myPred:
                new_RB.myPred.append(most_active_PO.my_made_unit)
                most_active_PO.my_made_unit.myRBs.append(new_RB)
        else:
            if most_active_PO.my_made_unit not in new_RB.myObj:
                new_RB.myObj.append(most_active_PO.my_made_unit)
                most_active_PO.my_made_unit.myRBs.append(new_RB)
    else: # I have not caused a unit to be inferred.
        # infer a newSet PO unit (with activation 1.0) and add it to memory. Set the value of the .myanalog field to 'null', as you will create an analog to house all newSet units at the end of the .doCompression() routine
        # give the new PO the name
        # new_PO_name = 'new_' + most_active_PO.name
        new_PO_name = 'po_' + str(len(memory.POs)+1)
        newSet_new_PO = dataTypes.POUnit(new_PO_name, 'newSet', 0, True, 'null', most_active_PO.predOrObj)
        newSet_new_PO.act = 1.0
        newSet_new_PO.my_maker_unit = most_active_PO
        most_active_PO.my_made_unit = newSet_new_PO

        memory.POs.append(newSet_new_PO)
        memory.newSet.POs.append(newSet_new_PO)

    return memory, new_RB

# function to find objects in the driver that are bound to multiple preds.
def find_objs_for_compression(driver):
    objs_for_compression = []
    for myPO in driver.POs:
        # if the PO is an object and has multiple preds (i.e., the length of the .same_RB_POs field is 2 or more), then add it to objs_for_compression array.
        if myPO.predOrObj == 0 and len(myPO.same_RB_POs) >= 2:
            objs_for_compression.append(myPO)
    # returns.
    return objs_for_compression

# ekaterina: performs compression operations
def compression_routine(memory, made_RB, compressed_PO, ho_sem, gamma):
    # find the most active PO
    most_active_PO = get_most_active_unit(memory.driver.POs)
        # if there is no made_RB, make one, and set made_RB to that RB.
    if not made_RB:
        made_RB_name = 'rb_' + str(len(memory.RBs)+1)
        made_RB = dataTypes.RBUnit(made_RB_name, 'newSet', None, True, None)
        made_RB.act = 1.0

        memory.RBs.append(made_RB)
        # add to the emerging recipient proxy, newSet
        memory.newSet.RBs.append(made_RB)

        # recruit a PO unit to serve as the compressed predicate
        newPOname = ''
        # a name for a new cumulative predicate which consists of names of all the active predicates
        for pred in most_active_PO.same_RB_POs:
            newPOname += pred.name
        compressed_PO = dataTypes.POUnit(newPOname, 'newSet', None, True, None, 1)
        compressed_PO.act = 1.0

        # add to memory
        memory.POs.append(compressed_PO)

        # add to the emerging recipient proxy, newSet
        memory.newSet.POs.append(compressed_PO)

        # learn connection between made_RB and compressed predicate
        made_RB.myPred.append(compressed_PO)
        compressed_PO.myRBs.append(made_RB)

    # if the most active PO has already caused a PO to be inferred in newSet, learn connections between the inferred PO and active semantics, otherwise infer a PO to match the most active PO.
    if most_active_PO.predOrObj == 0 and most_active_PO.my_made_unit:
        most_active_PO.my_made_unit.act = 1.0
        for semantic in memory.semantics:
            # check if I am connected to the newly recruited PO unit. If yes, update my connection based on semantic activation. If not, and I am active, infer a connection.
            connected_to_newSetPO = False
            # check all the semantic's Links. If any of the semantic Links are to the newSet_PO, set connected_to_newSetPO to True (i.e., don't make a Link for the current semantic and the newSet_PO because one already exits), and update the connection between the newSet_PO and the current semantic by a simple Hebbian rule.
            for Link in semantic.myPOs:
                if most_active_PO.my_made_unit == Link.myPO:
                    # update the connection weight.
                    Link.weight += (1*(Link.mySemantic.act-Link.weight)*gamma)
                    connected_to_newSetPO = True

            # if the semantic is not connected to the newly created PO, learn a connection if semantic.act > 0 and the semantic is not higher-order
            if (not connected_to_newSetPO) and (semantic.act > 0) and (semantic.ont_status != 'HO'):
                # infer a new Link for new PO and active semantic.
                new_Link = dataTypes.Link(most_active_PO.my_made_unit, 'nil', semantic, 0.0)
                # update the weight of the Link.
                new_Link.weight = 1*(semantic.act-0)*gamma
                # connect new Link to semantic and new pred and add Link to memory.Links.
                most_active_PO.my_made_unit.mySemantics.append(new_Link)
                semantic.myPOs.append(new_Link)
                memory.Links.append(new_Link)
    # for a predicate to be compressed: if ho_sem unit is already recruited make it iteratively learn weighted connections to regular semantic units that are active together with the corresponding active predicate
    elif most_active_PO.predOrObj == 1 and ho_sem:
        # if a semantic of a predicate is already connected to a higher order semantic, update the connection weight between them; the weights are stored in ho_sem
        for link in most_active_PO.mySemantics:
            if link.mySemantic in ho_sem.semConnect:
                semIndex = ho_sem.semConnect.index(link.mySemantic)
                currWeight = ho_sem.semConnectWeights[semIndex]
                ho_sem.semConnectWeights[semIndex] += (1*(link.mySemantic.act-currWeight)*gamma)
            else: # if not connected yet, learn a connection if semantic.act > 0
                if link.mySemantic.act > 0:
                    ho_sem.semConnect.append(link.mySemantic)
                    link.mySemantic.semConnect.append(ho_sem)
                    # weight between semantic and ho_sem are stored in the ho_sem in the list .semConnectWeights; initialize the weight
                    semIndex = ho_sem.semConnect.index(link.mySemantic)
                    ho_sem.semConnectWeights[semIndex] = 1*(link.mySemantic.act-0)*gamma

    else: # I have not caused a unit to be inferred (for object) or has not created an ho_sem (for predicate)
        # infer a newSet PO unit (with activation 1.0) and add it to memory. Set the value of the .myanalog field to 'null', as you will create an analog to house all newSet units at the end of the .doCompression() routine above.
        if most_active_PO.predOrObj == 0:
            # name for the object
            new_PO_name = 'po_' + str(len(memory.POs)+1)
            # new_PO_name = 'new_' + most_active_PO.name
            newSet_new_PO = dataTypes.POUnit(new_PO_name, 'newSet', None, True, None, 0)
            newSet_new_PO.act = 1.0
            newSet_new_PO.my_maker_unit = most_active_PO
            most_active_PO.my_made_unit = newSet_new_PO
            # add now PO unit to memory
            memory.POs.append(newSet_new_PO)

            # add to the emerging recipient proxy, newSet
            memory.newSet.POs.append(newSet_new_PO)

            # learn connection between made_RB and the newly created copy of the object
            made_RB.myObj.append(newSet_new_PO)
            newSet_new_PO.myRBs.append(made_RB)

        # if the most active PO is a pred, recruit a new higher-order semantic, and set ho_sem to that semantic.
        else: # if most_active_PO.predOrObj == 1:
            # check if this ho_sem already exists in memory; if it does not, recruit a new higher-order semantic unit
            sem_name = 'ho_sem_' + most_active_PO.name
            recruitHO = True
            for sem in memory.semantics:
                if sem.name == sem_name:
                    recruitHO = False
                    ho_sem = sem
            if recruitHO:
                ho_sem = dataTypes.Semantic(sem_name, None, None, 'HO')
                memory.semantics.append(ho_sem)

            # learn a connection between the new HO semantic and compressed_PO
            newLink = dataTypes.Link(compressed_PO, 'nil', ho_sem, 1.0)
            compressed_PO.mySemantics.append(newLink)
            ho_sem.myPOs.append(newLink)
            memory.Links.append(newLink)

    return memory, made_RB, compressed_PO, ho_sem

# ekaterina: function to find compressed predicates -- the ones with higher-order semantics
def find_preds_to_unpack(driver):
    preds_to_unpack = []
    for myPO in driver.POs:
        # add predicate connected to ho_sems to the list
        if myPO.predOrObj == 1:
            for link in myPO.mySemantics:
                if link.mySemantic.ont_status == 'HO':
                    preds_to_unpack.append(myPO)
                    break
    return preds_to_unpack

# ekaterina: helper function for .unpacking_routine(); creates a new PO unit
def create_PO(memory, most_active_PO):
    new_PO_name = 'po_' + str(len(memory.POs)+1)
    newSet_new_PO = dataTypes.POUnit(new_PO_name, 'newSet', 0, True, 'null', most_active_PO.predOrObj)
    newSet_new_PO.act = 1.0
    newSet_new_PO.my_maker_unit = most_active_PO
    most_active_PO.my_made_units.append(newSet_new_PO)
    memory.POs.append(newSet_new_PO)
    memory.newSet.POs.append(newSet_new_PO)
    return memory, newSet_new_PO

# ekaterina: function to perform unpacking operations
def unpacking_routine(memory, made_RBs, currentPO, gamma, tokenize):
    # find the most active PO
    most_active_PO = get_most_active_unit(memory.driver.POs)
    # count how many POs are needed -- as many as ho_sems are connected to the compressed predicate
    if most_active_PO.predOrObj == 0: # most_active_PO is an object
        for pred in most_active_PO.same_RB_POs: # for all predicates bound to the current object find the one with ho sems and count them
            hoSemCount = count_ho_sem(pred)
            if hoSemCount > 0:
                break
    else: # most_active_PO is the compressed predicate, count its ho sems
        hoSemCount = count_ho_sem(most_active_PO)

    # if made_RBs is an empty list, make new RBs, one for each unpacked (and simple originally) role
    if not made_RBs:
        for i in range(2*hoSemCount): # each higher-order semantic yields two simple predicates when everything is unpacked, thus, we need 2 new RBs for each
            memory, made_RB = infer_RB(memory, None)
            made_RBs.append(made_RB)

    # if the most active PO has already caused a PO to be inferred in newSet, learn connections between the inferred PO and active semantics and the made_RB, or otherwise infer a PO in newSet to match the most active PO.
    if most_active_PO.my_made_units:
        for i in range(len(most_active_PO.my_made_units)):
            most_active_PO.my_made_units[i].act = 1.0

        # if most_active_PO is an object, teach its copies (stored in most_active_PO.my_made_units) connections to most_active_PO's semantics
        if most_active_PO.predOrObj == 0:
            for inferredPO in most_active_PO.my_made_units: # for each PO unit inferred by the most_active_PO
                for semantic in memory.semantics:
                    # check if I am connected to the newSet myPO. If yes, update my connection based on semantic activation. If not, and I am active, infer a connection.
                    connected_to_inferredPO = False
                    # check all the semantic's Links. If any of the semantic Links are to the newSet_PO, set connected_to_newSetPO to True (i.e., don't make a Link for the current semantic and the newSet_PO because one already exits), and update the connection between the newSet_PO and the current semantic by a simple Hebbian rule.
                    for Link in semantic.myPOs:
                        if inferredPO == Link.myPO:
                            # update the connection weight.
                            Link.weight += (1*(Link.mySemantic.act-Link.weight)*gamma)
                            connected_to_inferredPO = True

                    # if not connected_to_newPO, then learn a connection if semantic.act > 0.
                    if (not connected_to_inferredPO) and (semantic.act > 0):
                        # infer a new Link for new PO and active semantic.
                        new_Link = dataTypes.Link(inferredPO, 'nil', semantic, 0.0)
                        # update the weight of the Link.
                        new_Link.weight = 1*(semantic.act-0)*gamma
                        # connect new Link to semantic and new pred and add Link to memory.Links.
                        inferredPO.mySemantics.append(new_Link)
                        semantic.myPOs.append(new_Link)
                        memory.Links.append(new_Link)

        else: # if most_active_PO is the compressed predicate, teach POs inferred by it (they will play unpacked roles) connections to semantics; for that use connections between each ho_sem and regular semantics
            ho_sems = []
            for link in most_active_PO.mySemantics:
                if link.mySemantic.ont_status == 'HO':
                    ho_sems.append(link.mySemantic)
            i = 0
            for ho in ho_sems: # for each ho_sem all the regular semantics connected to it need to be connected to one of the unpacked predicates
                for j in range(i, 4, 2): # each higer-order semantic helps to create two unpacked predicates -- one in each of the RBs
                    inferredPO = most_active_PO.my_made_units[j] # current unpacked predicate, one in each of the leftmost and then rightmost RBs (see notes 7.feb.22 for details)
                    for semantic in ho.semConnect:
                        connected_to_inferredPO = False
                        for Link in semantic.myPOs:
                            if Link.myPO == inferredPO:
                                # update the connection weight.
                                Link.weight += (1*(Link.mySemantic.act-Link.weight)*gamma)
                                connected_to_inferredPO = True

                        if (not connected_to_inferredPO) and (semantic.act > 0):
                            # infer a new Link for new PO and active semantic.
                            new_Link = dataTypes.Link(inferredPO, 'nil', semantic, 0.0)
                            # update the weight of the Link.
                            new_Link.weight = 1*(semantic.act-0)*gamma
                            # connect new Link to semantic and new pred and add Link to memory.Links.
                            inferredPO.mySemantics.append(new_Link)
                            semantic.myPOs.append(new_Link)
                            memory.Links.append(new_Link)

                            # while this semantic is active, mark the simpler role as a maker unit for the inferred PO: needed for .bind_others_to_unpacked()
                            for Link in semantic.myPOs:
                                if Link.myPO.set == 'driver':
                                    inferredPO.my_maker_unit = Link.myPO
                                    Link.myPO.my_made_unit = inferredPO
                i += 1

    else: # I have not caused any units to be inferred
        # infer PO units (with activation 1.0) by the number of ho_sems and add them to memory;
        # new_POs is the list of newly recruited PO units on this step; we need the list to make sure we can create 1, 2, 4, etc. copies of the most_active_PO unit
        new_POs = []
        if most_active_PO.predOrObj == 0: # if it is an object (whose roles are unpacked) we need only as many copies of it as there are HOs
        # tokenize = True: the object creates multiple copies of itself (by the number of HO-semantics) and the propositions with its copies will all be in different analogs
        # tokenize = False: the object creates only one copy of itself (for all unpacked propositions) and all unpacked propositions will be in the same analog
            if tokenize:
                how_many_copies = hoSemCount
            else:
                how_many_copies = 1
        else:
            how_many_copies = 2*hoSemCount # if it is a predicate, make twice as many copies
        for i in range(how_many_copies): # each higher-order semantic yields two simple predicates when everything is unpacked
            memory, newSet_new_PO = create_PO(memory, most_active_PO)
            new_POs.append(newSet_new_PO)

        # making sure the object in non-tokenize condition binds its copy to multiple RBs and recruits as many Ps as needed;
        # we need the same copy of the object to be twice on the list
        if how_many_copies == 1:
            how_many_copies = hoSemCount
            new_POs.append(newSet_new_PO)

        # learn the connection between the current made_RB[i] and the newly created copy of the most_active_PO (predicate or object)
        for i in range(how_many_copies):
            # learn the connection between the current made_RB[i] and the newly created copy of the object
            if new_POs[i].predOrObj == 0:
                made_RBs[i].myObj.append(new_POs[i])
                new_POs[i].myRBs.append(made_RBs[i])

                # make sure the original proposition had a P unit, if yes -- create one for the unpacked version of the proposition
                if most_active_PO.myRBs[0].myParentPs:
                    # also, recruit a P unit and make new_RB[i] learn  the connection to it -- we need 2 new P units, one for each copy of an object
                    newPname = 'p_' + str(len(memory.Ps)+1)
                    unpack_P = dataTypes.PUnit(newPname, 'newSet', None, True, None)
                    unpack_P.act = 1.0

                    # mark the P in the driver as a maker unit of the newly recruited P in the emerging recipient
                    unpack_P.my_maker_unit = most_active_PO.myRBs[0].myParentPs[0]
                    most_active_PO.myRBs[0].myParentPs[0].my_made_unit = unpack_P

                    # connect newly recruited P to the current made_RB
                    unpack_P.myRBs.append(made_RBs[i])
                    made_RBs[i].myParentPs.append(unpack_P)

                    # add newly recruited P to the memory lists
                    memory.Ps.append(unpack_P)
                    memory.newSet.Ps.append(unpack_P)
            else:
                made_RBs[i].myPred.append(new_POs[i])
            new_POs[i].myRBs.append(made_RBs[i])
    return memory, made_RBs, hoSemCount

# ekaterina: function to count the number of higher-order semantics connected to the compressed predicate
def count_ho_sem(myPred):
    hoSemCount = 0 # to count the number of ho_sems
    for link in myPred.mySemantics:
        if link.mySemantic.ont_status == 'HO':
            hoSemCount += 1
    return hoSemCount

# function to find the analog in the recipient that contains all the mapped recipient units. Currently for use only with rel_gen_routine() function.
def find_recip_analog(memory):
    # search through the POs in the recipient and find their analog. (You only need to search the POs because all recipient units that map have already been compiled into a single analog, and all analogs contain at least POs.)
    for myPO in memory.recipient.POs:
        if myPO.max_map > 0.0:
            recip_analog = myPO.myanalog
            break
    # returns.
    return recip_analog

# function to find the analog in the driver that contains all the mapped driver units. Currently for use only with do_rel_gen() routine from the runDORA object.
def find_driver_analog_rel_gen(memory):
    # search through the POs in the driver and find their analog. (You only need to search the POs because all driver units that map are from a single analog, and all analogs contain at least POs.)
    for myPO in memory.driver.POs:
        if myPO.max_map > 0.0:
            driver_analog = myPO.myanalog
            break
    # returns.
    return driver_analog

# function to put items in newSet into an analog
def newSet_items_to_analog(memory):
    # create a new analog.
    new_analog = dataTypes.Analog()
    # put all the Ps, RBs, and POs in new set into new_analog.
    for myP in memory.newSet.Ps:
        new_analog.myPs.append(myP)
        myP.myanalog = new_analog
    for myRB in memory.newSet.RBs:
        new_analog.myRBs.append(myRB)
        myRB.myanalog = new_analog
    for myPO in memory.newSet.POs:
        new_analog.myPOs.append(myPO)
        myPO.myanalog = new_analog
    # put new_analog into memory.
    memory.analogs.append(new_analog)
    # returns.
    return memory

# function to fix high weight of predicate to 1. This function updates the weights of the most strongly connected semantic(s) of the pred to 1.0.
def calibrate_weight(memory):
    for myPO in memory.driver.POs:
        max_weight_links = []
        max_weight = 0.0
        for link in myPO.mySemantics:
            if link.weight >= max_weight:
                max_weight_links.append(link)
                max_weight = link.weight
        # if the highest weight is less than 1, then recalibrate weights.
        if max_weight < 1:
            for link in max_weight_links:
                link.weight = 1.0
    # return memory.
    return memory

# function to update names for all token units in memory.
def update_Names_all(memory):
    for myPO in memory.POs:
        PO_name = ''
        # name me after my most weighted semantics.
        most_weighted_sem = 0.0
        for Link in myPO.mySemantics:
            if Link.weight > most_weighted_sem:
                most_weighted_sem = Link.weight
        for Link in myPO.mySemantics:
            if Link.weight == most_weighted_sem:
                myPO.name += '&'
                myPO.name += Link.mySemantic.name
    for myRB in memory.RBs:
        RB_name = myRB.myPred[0].name + '+' + myRB.myObj[0].name
        myRB.name = myRB.name
    for myP in memory.Ps:
        P_name = ''
        for myRB in myP.myRBs:
            P_name += '+'
            P_name += myRB.name
        myP.name = P_name
    # returns.
    return memory

# function to update names for all token units in memory with name 'nil'.
def update_Names_nil(memory):
    for myPO in memory.POs:
        if myPO.name == 'nil' or 'nil' in myPO.name:
            myPO.name = ''
            # name me after my most weighted semantics.
            most_weighted_sem = 0.0
            for Link in myPO.mySemantics:
                if Link.weight > most_weighted_sem:
                    most_weighted_sem = Link.weight
            for Link in myPO.mySemantics:
                if Link.weight == most_weighted_sem:
                    myPO.name += '&'
                    myPO.name += Link.mySemantic.name
    for myRB in memory.RBs:
        if myRB.name == 'nil' or 'nil' in myRB.name:
            if len(myRB.myObj) > 0:
                RB_name = myRB.myPred[0].name + '+' + myRB.myObj[0].name
            elif len(myRB.myChildP) > 0:
                RB_name = myRB.myPred[0].name + '+' + myRB.myChildP[0].name
            else:
                RB_name = 'somethingWrongWithThisRB'
            myRB.name = RB_name
    for myP in memory.Ps:
        if myP.name == 'nil' or 'nil' in myP.name:
            P_name = ''
            for myRB in myP.myRBs:
                P_name += '+'
                P_name += myRB.name
            myP.name = P_name
    # returns.
    return memory

# function to give names to newSet Ps, RBs, and POs after inference.
def give_Names_inferred(memory):
    for myPO in memory.newSet.POs:
        PO_name = ''
        # name me after my most weighted semantics.
        most_weighted_sem = 0.0
        for Link in myPO.mySemantics:
            if Link.weight > most_weighted_sem:
                most_weighted_sem = Link.weight
        for Link in myPO.mySemantics:
            if Link.weight == most_weighted_sem:
                myPO.name += '&'
                myPO.name += Link.mySemantic.name
    for myRB in memory.newSet.RBs:
        RB_name = myRB.myPred.name + '+' + myRB.myObj.name
        myRB.name = myRB.name
    for myP in memory.newSet.Ps:
        P_name = ''
        for myRB in myP.myRBs:
            P_name += '+'
            P_name += myRB.name
        myP.name = P_name
    for Group in memory.newSet.Ps:
        Group_name = ''
        for myP in Group.myRBs:
            Group_name += '+'
            Group_name += myP.name
        Group.name = Group_name
    # returns.
    return memory

# function to clear the set field of every token in memory (i.e., to clear WM).
def clearTokenSet(memory):
    # for each P, RB, and PO, clear the set field.
    for Group in memory.Groups:
        Group.set = 'memory'
    for myP in memory.Ps:
        myP.set = 'memory'
    for myRB in memory.RBs:
        myRB.set = 'memory'
    for myPO in memory.POs:
        myPO.set = 'memory'
    # returns.
    return memory

# function to clear the driver.
def clearDriverSet(memory):
    # for each P, RB, and PO, clear the set field.
    for Group in memory.driver.Groups:
        Group.set = 'memory'
    for myP in memory.driver.Ps:
        myP.set = 'memory'
    for myRB in memory.driver.RBs:
        myRB.set = 'memory'
    for myPO in memory.driver.POs:
        myPO.set = 'memory'
    # now clear the memory.driver fields.
    memory.driver.Ps = []
    memory.driver.RBs = []
    memory.driver.POs = []
    # returns.
    return memory

# function to clear the recipient.
def clearRecipientSet(memory):
    # for each P, RB, and PO, clear the set field.
    for Group in memory.recipient.Groups:
        Group.set = 'memory'
    for myP in memory.recipient.Ps:
        myP.set = 'memory'
    for myRB in memory.recipient.RBs:
        myRB.set = 'memory'
    for myPO in memory.recipient.POs:
        myPO.set = 'memory'
    # now clear the memory.recipient fields.
    memory.recipient.Ps = []
    memory.recipient.RBs = []
    memory.recipient.POs = []
    # returns.
    return memory

# reset the .inferred, .my_made_unit, .my_maker_unit field of all tokens.
def reset_inferences(memory):
    for Group in memory.Groups:
        Group.inferred = False
        Group.my_made_unit = None
        Group.my_maker_unit = None
    for myP in memory.Ps:
        myP.inferred = False
        myP.my_made_unit = None
        myP.my_maker_unit = None
    for myRB in memory.RBs:
        myRB.inferred = False
        myRB.my_made_unit = None
        myRB.my_maker_unit = None
    for myPO in memory.POs:
        myPO.inferred = False
        myPO.my_made_unit = None
        myPO.my_maker_unit = None
    # returns.
    return memory

# fucntion to clear the my_maker_ and my_made_unit of all tokens in memory. Used after learning is returns and WM is cleared.
def reset_maker_made_units(memory):
    for Group in memory.Groups:
        Group.my_maker_unit = None
        Group.my_made_unit = None
    for myP in memory.Ps:
        myP.my_maker_unit = None
        myP.my_made_unit = None
    for myRB in memory.RBs:
        myRB.my_maker_unit = None
        myRB.my_made_unit = None
    for myPO in memory.POs:
        myPO.my_maker_unit = None
        myPO.my_made_unit = None
    # returns.
    return memory

# function to add a token and all it's child tokens to driver or recipient.
def add_tokens_to_set(memory, token_num, token_type, the_set):
    # put the token and all tokens under it into the set.
    # if the token is a P, then add it's RBs, and each RBs args, and if the arg is a P, then repeat the process for that P's RBs and the RBs' args.
    if token_type == 'analog':
        # add all the analog's P units.
        for myP in memory.analogs[token_num].myPs:
            myP.set = the_set
        # add all the analog's RB units.
        for myRB in memory.analogs[token_num].myRBs:
            myRB.set = the_set
        # add all the analog's PO units.
        for myPO in memory.analogs[token_num].myPOs:
            myPO.set = the_set
    elif token_type == 'P':
        # add the P.
        memory.Ps[token_num].set = the_set
        # add my RBs.
        for myRB in memory.Ps[token_num].myRBs:
            # add the myRB.
            myRB.set = the_set
            myRB.myPred[0].set = the_set
            # add the RB's argument.
            if len(myRB.myObj) > 0:
                myRB.myObj[0].set = the_set
            else:
                myRB.myChildP[0].get_index(memory)
                new_token_num = myRB.myChildP[0].my_index
                memory = add_tokens_to_set(memory, new_token_num, 'P', the_set)
    elif token_type == 'RB':
        # add the myRB.
        memory.RBs[token_num].set = the_set
        # add the RB's pred.
        # edited for DEBUGGING.
        if len(memory.RBs[token_num].myPred[0].set) < 1:
            pdb.set_trace()
        memory.RBs[token_num].myPred[0].set = the_set
        # add the RB's argument.
        if len(memory.RBs[token_num].myObj) > 0:
            memory.RBs[token_num].myObj[0].set = the_set
        else:
            memory.RBs[token_num].myChildP[0].get_index(memory)
            new_token_num = memory.RBs[token_num].myChildP[0].my_index
            memory = add_tokens_to_set(memory, new_token_num, 'P', the_set)
    elif token_type == 'PO':
        # add the PO.
        memory.POs[token_num].set = the_set
    # returns.
    return memory

# function implementing kludgey comparitor/compariter (used in Doumas et al., 2008, adopted from Hummel & Biederman, 1992).
def kludgey_comparitor(PO1, PO2, memory):
    # this comparitor is based on Hummel & Biederman, 1992. When two predicates are compared, it looks for any semantics they share that correspond to a dimension. If it finds none, it does nothing. If it finds some, then it does a literal comparison of their values. If they are the same, then it attaches the semantics 'same' and 'dimension_name' (where 'dimension_name is a variable correponding to the name of the dimension upon which the comparitor performed the comparison). If they are different, then it attaches the semantics 'more' and 'dimension_name' to the PO unit with the semantic coding the larger value on the dimension, and 'less' and 'dimension_name' to the PO with the semantic coding the smaller value on the dimension.
    # find the largest semantic connection weight for both PO1 and PO2.
    PO1.get_max_semantic_weight()
    PO2.get_max_semantic_weight()
    # find the semantics more/less/same, or make them if they do not exist.
    more, less, same = None, None, None
    for semantic in memory.semantics:
        if semantic.name == 'more':
            more = semantic
        elif semantic.name == 'less':
            less = semantic
        elif semantic.name == 'same':
            same = semantic
    if not more:
        # make a 'more' semantic.
        more = dataTypes.Semantic('more', dimension='comparative')
        memory.semantics.append(more)
    if not less:
        # make a 'less' semantic.
        less = dataTypes.Semantic('less', dimension='comparative')
        memory.semantics.append(less)
    if not same:
        # make a 'same' semantic.
        same = dataTypes.Semantic('same', dimension='comparative')
        memory.semantics.append(same)
    # check for a common dimension in the most strongly connected semantics of PO1 and PO2.
    for link1 in PO1.mySemantics:
        # don't operate on comparative semantics (i.e., 'more', 'less', 'same').
        if (link1.mySemantic.name != 'more') and (link1.mySemantic.name != 'less') and (link1.mySemantic.name != 'same'):
            for link2 in PO2.mySemantics:
                # don't operate on comparative semantics (i.e., 'more', 'less', 'same').
                if (link2.mySemantic.name != 'more') and (link2.mySemantic.name != 'less') and (link2.mySemantic.name != 'same'):
                    if (link1.weight == PO1.max_sem_weight) and (link2.weight == PO2.max_sem_weight):
                        if (link1.mySemantic.dimension == link2.mySemantic.dimension) and (link1.mySemantic.dimension != 'nil'):
                            # run the simple comparitor.
                            if link1.mySemantic.amount > link2.mySemantic.amount:
                                # connect PO1 to 'more' and PO2 to 'less'.
                                new_link_more = dataTypes.Link(PO1, None, more, 1.0)
                                PO1.mySemantics.append(new_link_more)
                                more.myPOs.append(new_link_more)
                                memory.Links.append(new_link_more)
                                new_link_less = dataTypes.Link(PO2, None, less, 1.0)
                                PO2.mySemantics.append(new_link_less)
                                less.myPOs.append(new_link_less)
                                memory.Links.append(new_link_less)
                            elif link1.mySemantic.amount < link2.mySemantic.amount:
                                # connect PO1 to 'less' and PO2 to 'more'.
                                new_link_less = dataTypes.Link(PO1, None, less, 1.0)
                                PO1.mySemantics.append(new_link_less)
                                less.myPOs.append(new_link_less)
                                memory.Links.append(new_link_less)
                                new_link_more = dataTypes.Link(PO2, None, more, 1.0)
                                PO2.mySemantics.append(new_link_more)
                                more.myPOs.append(new_link_more)
                                memory.Links.append(new_link_more)
                            elif link1.mySemantic.amount == link2.mySemantic.amount:
                                # they are equal, connect both PO1 and PO2 to 'same'.
                                new_link_same1 = dataTypes.Link(PO1, None, same, 1.0)
                                PO1.mySemantics.append(new_link_same1)
                                same.myPOs.append(new_link_same1)
                                memory.Links.append(new_link_same1)
                                new_link_same2 = dataTypes.Link(PO2, None, same, 1.0)
                                PO2.mySemantics.append(new_link_same2)
                                same.myPOs.append(new_link_same2)
                                memory.Links.append(new_link_same2)
    # reset the .max_sem_weight of the POs to None.
    PO1.max_sem_weight = None
    PO1.max_sem_weight = None
    # returns.
    return memory

# function to switch the contents of driver and recipient.
def swap_driverRecipient(memory):
    memory.driver, memory.recipient = memory.recipient, memory.driver
    # update the set information for units in new driver/recipient.
    for Group in memory.driver.Groups:
        Group.set = 'driver'
    for myP in memory.driver.Ps:
        myP.set = 'driver'
    for myRB in memory.driver.RBs:
        myRB.set = 'driver'
    for myPO in memory.driver.POs:
        myPO.set = 'driver'
    for Group in memory.recipient.Groups:
        Group.set = 'recipient'
    for myP in memory.recipient.Ps:
        myP.set = 'recipient'
    for myRB in memory.recipient.RBs:
        myRB.set = 'recipient'
    for myPO in memory.recipient.POs:
        myPO.set = 'recipient'
    # returns.
    return memory

# function to make sure that the .myanalog data in all tokens is consistent.
def check_analog_consistency(memory):
    # go through each analog and make sure that all tokens in that analog have that analog in their .myanalog field. If yes, fine. Otherwise, ...

    # returns.
    return memory

# function to write memory state to a sym file for storage. Takes as arguments the current memory object, and a file_name, which is the name of the file to which the memory state should be written.
def write_memory_to_symfile(memory, file_name):
    #create an array of dicts.
    sym_dicts = []
    # for each analog.
    analog_counter = 0
    for analog in memory.analogs:
        # for each P in the analog, make a sym file entry for that P and all its connected tokens, and write that sym entry to the open text file.
        for myP in analog.myPs:
            # as long as the current P is NOT part of a higher-order relation (its .myParentRBs is empty), then make a sym entry for it. Otherwide, don't bother making a sym entry for it, as it will get made when the higher-order P it is part of has it's sym entry made.
            if len(myP.myParentRBs) == 0:
                # make a sym_dict with the current myP.
                new_sym_dicts = create_dict_P(myP, analog_counter)
                # for higher order Ps, you might get back multiple dicts in new_sym_dicts, so add them all to sym_dicts.
                for sym_dict in new_sym_dicts:
                    sym_dicts.append(sym_dict)
        # for each RB in the analog that has no parentP, make a sym file entry for that RB and all its connected tokens, and write that sym entry to the open text file..
        for myRB in analog.myRBs:
            # if myRB.myParentPs is empty, then make a sym_dict from myRB.
            if len(myRB.myParentPs) == 0:
                sym_dict = create_dict_RB(myRB, analog_counter)
                # add the new sym_dict to sym_dicts.
                sym_dicts.append(sym_dict)
        # for each PO in the analog that has no RBs, make a sym file entry for that PO, and write that sym entry to the open text file.
        for myPO in analog.myPOs:
            # if myPO.myRBs is empty, then make a sym_dict from myPO.
            if len(myPO.myRBs) == 0:
                sym_dict = create_dict_PO(myPO, analog_counter)
                # add the new sym_dict to sym_dicts.
                sym_dicts.append(sym_dict)
        # update the analog_counter, so that the next analog in memory has a new number associated with it in the 'analog' field of the sym file.
        analog_counter +=1
    # write all of sym_dicts to text file called file_name using json.
    json.dump(sym_dicts, open(file_name, 'w'))
    # now prepend 'simType='sym_file' symProps = '. NOTE: This process is clunky, because you have to write all the json information to a textfile first as the json.dump() function requires a second argument (the open() component), and thus writes over the content of the text file, and consequently does not allow prepended text information. Prepending information to a text file requires rewriting the text file.
    with open(file_name, 'r+') as f:
        old_text = f.read() # read all the contents of f into a new variable.
        f.seek(0) # go back to the start of f.
        f.write('simType=\'json_sym\' \n' + old_text)

# function to create a sym_dict from a P unit.
def create_dict_P(myP, analog_counter):
    # create an array of the RB dicts made from the current P's RBs.
    new_sym_dicts = []
    RBs = []
    for myRB in myP.myRBs:
        new_RB_dict, p_dict = create_RB_dict(myRB, analog_counter)
        RBs.append(new_RB_dict)
        if p_dict:
            # add p_dict to the array of new_sym_dicts
            new_sym_dicts.append(p_dict)
    # create the new_sym_dicts.
    new_sym_dict = {'name': myP.name, 'RBs': RBs, 'set': 'memory', 'analog': analog_counter}
    new_sym_dicts.append(new_sym_dict)
    # return the new_sym_dicts.
    return new_sym_dicts

# function to create a sym_dict from a RB unit.
def create_dict_RB(myRB, analog_counter):
    # make a sym_dict from the current RB.
    RB_dict, p_dict = create_RB_dict(myRB, analog_counter)
    # make a new sym_dict using the new RB_dict.
    new_sym_dict = {'name': 'non_exist', 'RBs': [RB_dict], 'set': 'memory', 'analog': analog_counter}
    # return new_sym_dict.
    return new_sym_dict

# function to create a sym_dict from a PO unit.
def create_dict_PO(myPO, analog_counter):
    # first get an array of obj semantics.
    obj_sems = []
    for link in myPO.mySemantics:
        # capture both the name of the semantic and the weight of the semantic to the PO in an array.
        # also, if the semantic codes for a dimension, then encode that information in sem_info.
        if link.mySemantic.dimension == 'nil':
            sem_info = [link.mySemantic.name, link.weight]
        else:
            sem_info = [link.mySemantic.name, link.weight, link.mySemantic.dimension, link.mySemantic.amount]
        obj_sems.append(sem_info)
    # make new sym_dict.
    new_sym_dict = {'name': 'non_exist', 'RBs': [{'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': myPO.name, 'object_sem': obj_sems, 'P': 'non_exist'}], 'set': 'memory', 'analog': analog_counter}
    # return new_sym_dict.
    return new_sym_dict

# function to create the RB_dict section of the sym_dict.
def create_RB_dict(myRB, analog_counter):
    # get the pred semantics.
    pred_sems = []
    for link in myRB.myPred[0].mySemantics:
        # capture both the name of the semantic and the weight of the semantic to the PO in an array.
        # also, if the semantic codes for a dimension, then encode that information in sem_info.
        if link.mySemantic.dimension == None: # ekaterina changed 'nil' to None
            if link.mySemantic.ont_status == 'HO': # ekaterina: also take care of higher order semantics and their connections to regular semantics
                regSems = []
                for sem in link.mySemantic.semConnect:
                    regSems.append(sem.name)
                sem_info = [link.mySemantic.name, link.weight, None, None, link.mySemantic.ont_status, regSems]
            else:
                sem_info = [link.mySemantic.name, link.weight, None, None, None]
        else:
            sem_info = [link.mySemantic.name, link.weight, link.mySemantic.dimension, link.mySemantic.amount, link.mySemantic.ont_status]
        pred_sems.append(sem_info)
    # check if the RB has a higher order argument.
    # if it has a higher order argument, then set higher_order to True, and create and empty object.
    # else, set higher_order to False, and get the object semantics.
    if len(myRB.myObj) == 0:
        higher_order = True
        object_name = 'non_exist'
        object_sems = [] # there are no semantics.
        # if there is a child P, then create a new sym_dict with that P unit, and set P_name, to the name of that P_unit.
        p_dict = create_dict_P(myRB.myChildP, analog_counter)
        P_name = myRB.myChildP.name
    else:
        higher_order = False
        object_name = myRB.myObj[0].name
        object_sems = []
        for link in myRB.myObj[0].mySemantics:
            # capture both the name of the semantic and the weight of the semantic to the PO in an array.
            # also, if the semantic codes for a dimension, then encode that information in sem_info.
            if link.mySemantic.dimension == 'nil':
                sem_info = [link.mySemantic.name, link.weight]
            else:
                sem_info = [link.mySemantic.name, link.weight, link.mySemantic.dimension, link.mySemantic.amount]
            object_sems.append(sem_info )
        P_name = 'non_exist'
        # create an empty p_dict to pass back (it should be immediately deleted by the function calling this (create_RB_dict) function).
        p_dict = None
    # now make the RB_dict
    RB_dict = {'pred_name': myRB.myPred[0].name, 'pred_sem': pred_sems, 'higher_order': higher_order, 'object_name': object_name, 'object_sem': object_sems, 'P': P_name}
    # and return the RB_dict--and, if necessry, the p_dict.
    return RB_dict, p_dict

# ekaterina: clears the newSet
def clear_NewSet(memory):
    # for each P, RB, and PO, clear the set field
    for Group in memory.newSet.Groups:
        Group.set = 'memory'
    for myP in memory.newSet.Ps:
        myP.set = 'memory'
    for myRB in memory.newSet.RBs:
        myRB.set = 'memory'
    for myPO in memory.newSet.POs:
        myPO.set = 'memory'
    # now clear the memory.newSet fields
    memory.newSet.Ps = []
    memory.newSet.RBs = []
    memory.newSet.POs = []

    return memory

def print_analog(analog): # ekaterina
    print('Analog: ' + str(analog))
    for p in analog.myPs:
        print('P: ' + p.name)
        for rb in p.myRBs:
            print('RB: ' + rb.name)
            for po in rb.myPred:
                print('Pred: ' + po.name)
            for po in rb.myObj:
                print('Obj: ' + po.name)
        print('\n')

# ekaterina: add a category to the objects of an analog in the driver as a new semantic
def add_category(memory, category):
    if category not in memory.semantics:
        new_sem = dataTypes.Semantic(category)
        memory.semantics.append(new_sem)
    else:
        for sem in memory.semantics:
            if sem.name == category:
                new_sem = sem

    for cPO in memory.driver.POs:
        if cPO.predOrObj == 0:
            new_link = dataTypes.Link(cPO, [], new_sem, 1)
            memory.Links.append(new_link)
            cPO.mySemantics.append(new_link)
            new_sem.myPOs.append(new_link)

    return memory

# ekaterina: extract the category of the exemplar in the recipient
def extract_category(memory, cat1, cat2):
    retrieved_cat = ''
    if memory.recipient.POs:
        for po in memory.recipient.POs:
            for link in po.mySemantics:
                if link.mySemantic.name == cat1 or link.mySemantic.name == cat2:
                    retrieved_cat = link.mySemantic.name
                    break
    return retrieved_cat
