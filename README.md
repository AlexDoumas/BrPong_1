ReadMe—DORA. 

The following provides detail on how to work with the DORA model code provided in this repository. The readMe assumes knowledge of the DORA model (see references for links to relevant papers). 

The first part provides details on how to run learning sims reported in Doumas, Puebla, Martin, and Hummel (Relation learning…). The second part provides details on more detailed interaction with the DORA model. 

Part 1: Simulations

All representation learning and generalisation uses files in the workspace folder. 

A version of the model after representation learning is available in the file batch_run_full. This file is in the form of a json dump produced by the save state function in the DORA menu (see below for information on the DORA menus, and see the section on sim files below for information on how to read these files). 

To quick run learning in the model you can either use the visual preprocessor (ws2_dora.py) to generate DORA objects from pixel images. 

To simulate relation learning, open DORA.py. In the main menu, load the correct sim file (either the one you generated using the visual pre_processor or breakout_objects.py) by pressing ‘L’, and typing the name of the file you’d like to load (e.g., breakout_objects.py), then run DORA by pressing ‘R’. In the run menu, press ‘R’ for (r)un DORA and then ‘D’ for (D)ORA controlled mode. The simulation will run for 5000 iterations. After the run, you can view the results of learning using the (v)iew Network option in the run menu, or return to the main menu by pressing ‘E’, and then save the current network state by pressing ’S’. 

The output of the save operation will create a json dump (in plain text) of the state of the DORA network. 

Part 2: Working with the DORA network. 

The workspace file has all the code necessary to use the basic DORA network. 

The DORA main menu

When you run DORA (by running the DORA.py file) you enter the main DORA menu. Your terminal window should now look something like this: 

***** DORA *****
Vers  0.2.3
Path =  pythonDORA/currentVers

----- MAIN MENU ----- 

(L)oad sim file
sim file in memory is  <open file 'testsim2.py', mode 'r' at 0x10048fa50>
(C)lear loaded sim file
(S)ave current memory state
Load (O)ld memory state
output is written to  None
(D)esignate file to WRITE to
Load (P)arameter file
(B)atch run
(R)un
(Q)uit
DORA>

The DORA main menu lists the options available to you as a user. To execute an option  enter the letter in parens embedded in the option name at the DORA> prompt. For example, to load a sim file, then enter ‘l’ (or ‘L’) at the DORA> prompt and hit enter. The load sim file option will then be activated. 

The following elaborates on the main menu options. 

(L)oad sim file allows you to load a new sim file (instructions on creating sim files are given in the ‘Creating Sim Files’ section below). Entering L will activate the load sim file option. You will be prompted to enter the name of the sim file to load. You must enter the name of a sim file that is saved in the currentVers folder. If you enter a valid sim file name, DORA will load that sim file for run. If you do not enter a valid sim file name, an error message is displayed and you will be returned to the main menu. 

Under the (L)oad sim file option in the menu the name of the current sim file in memory is displayed. If you load a new sim file, the name of the new sim file you have loaded should be displayed. 

(C)lear loaded sim file will clear the current sim file in memory. 

(S)ave current memory state will save the current state of DORA’s memory so that you can load it again later. The output of a save is a json dump of dictionaries specifying the collections of units that make up particular propositions in the model. Details of the format of these dictionaries appears in the sim file section below. 

Under the (S)ave current memory state option in the menu, the name of the file to which the memory will be written should it be saved is given. The default location is ‘None’. See the (D)esignate file to write to option below for instructions on how to set file to write memory state to. 

Load (O)ld memory state allows you to load a previously saved memory state. 

(D)esignate file to write to allows you to set the file to which DORA will write its memory state. The file must exist in the currentVers folder. If no file by the name you enter exists in currentVers, DORA will create a file by that name in currentVers. 

Load (P)arameter file allows you to load a new parameter file. The default parameters are described in the ‘DORA’s Run Menu’ section below. How to create a parameter file is described in the ‘Creating Parameter Files’ section below. 

(B)atch run allows you to run a series of simulations in batch (i.e., run several simulations in sequence). Unfortuanately, this option is not yet available in python DORA. 

(R)un enters DORA’s run menu. The run menu is elaborated in the ‘DORA’s Run Menu’ section below. 

(Q)uit will quit python DORA. Any unsaved memory states are lost. 

DORA’s Run Menu

When you execute the (R)un option from the main menu, you enter DORA’s main run menu. Your terminal should look something like this: 

--- DORA RUN MENU --- 
(P)arameters
(V)iew network
(R)un DORA
(E)xit back to MainMenu

Run_DORA>

The following elaborates on the menu options. 

(P)arameters allows the user to view parameter settings. 

(V)iew network allows the user to view the network and network state in the terminal. Executing the (V)iew option will execute the view menu, which is elaborated below in the ‘DORA’s View Menu’ section. Note, the view network option in the terminal is a text based GUI and is separate from the DORA GUI that displays the network during runs. 

(E)xit returns the user to the Main Menu. 

(R)un DORA begins a DORA run. Once entered, the user is prompted to: 

Run in (D)ORA controlled mode
or
Run in (U)ser controlled mode

Running in (D)ORA controlled mode will auto run the model using details from the parameter file. The model will run in the specified order of operations for the specified number of iterations and then exit to the run menu again. From there you can view the results of the run, or save the results to file by (E)xiting the the main menu, and invoking the (S)ave option. 

Running in (U)ser controlled mode enters the User Controlled Run Menu. Here the user has a set of options to manually control the run of the model. Upon entering (U)ser controlled mode, your terminal should look something like this: 

* * * User Controlled Run * * *

(R)etrieve; (M)ap; (P)redicate; (F)orm new relation; (G)eneralize; (S)chematize, (B)etween set entropy operations, (W)ithin set entropy operations, (Co)mpression, (C)lear inferences/mappings, (U)pdate names
(Ch)ange Driver/Recipient
(Sw)ap DORA and LISA mode. Currently asDORA is True
(Ig)nore object semantics (a LISA property that only works in LISA mode). Currently ignore_object_semantics is False
(V)iew the network
(E)xit to main Run_Menu
Run_DORA>


The following elaborates on the menu options. 

(R)etrieve executes retrieval. 

(M)ap executes mapping. 

(P)redicate executes predicate learning. (NOTE: predication only works with objects not already bound to predicates. Running predication without unbound objects in the driver and recipient will produce no result.) 

(F)orm new relation executes form whole relation learning. 

(G)eneralize executes relational generalization. 

(S)chematize executes schema induction. 

(W)ithin set entropy operations. Runs the entropy operations. 

(C)lear inferences/mappings clears the mappings DORA has made, and reinitializes (i.e., clears) the emerging recipient (NOTE: inferred units are still stored in memory). Essentially this operation clears active memory. 

(U)pdate names will update naming of newly inferred units. 

(Ch)ange Driver/Recipient (enter ‘ch’ or ‘CH’ to perform the (Ch)ange Driver/Recipient action) allows the user to clear driver and recipient sets, place different propositions in memory into the driver and/or recipient, or swap the driver and recipient sets. 

(Sw)ap DORA and LISA mode (enter ‘sw’ or ‘SW’) swaps the items currently in driver and recipient. 

(Ig)nore object semantics is a property of the LISA model (Hummel & Holyoak, 2003) that allows the model to favour predicates for driving inference. The property is not used in the current simulations, but is included for completeness. 

(V)iew network allows the user to view the network and network state in the terminal. Executing the (V)iew option will execute the view menu, which is elaborated below in the ‘DORA’s View Menu’ section. Note, the view network option in the terminal is a text based GUI and is separate from the DORA GUI that displays the network during runs. 

View Network Menu

The View Network Menu allows the user to view the network at various levels of detail. Upon entering the View Network Menu, the terminal should display: 

View network (A)ctivations, (N)etwork state, (M)appings, or (B)ack to Run_Menu>

(A)ctivations will show the current activations and inputs to all driver and recipient token units and the semantic units. 

(N)etwork state will produce the following prompt: 

(D)river, (R)ecipient, (M)emory, or (B)ack to view menu>

(D)river will display all the propositions in the driver in the form: 

P  1 .  lovesJohnMary
loverJohn-- Pred_name: lover (lover1-1, lover2-1, lover3-1, ) -- Obj_name:John (john1-1, john2-1, john3-1, )
belovedMary-- Pred_name: beloved (beloved1-1, beloved2-1, beloved3-1, ) -- Obj_name:Mary (mary1-1, mary2-1, mary3-1, )

where P x indicates the place of the proposition in the driver (e.g., P 1 indicates the first proposition), followed by the name of the P unit (if one exists). Each of the following lines gives information about an RB and its predicate and object in the form: 

RB_name-- Pred_name: predname (predsemantics) -- Obj_name: objname (objsemantics) 

Where RB_name is a variable giving the name of the RB (if one exists), predname is a variable giving the name of the pred unit (if one exists), predsemantics is a variable giving the names and weights of the pred unit’s semantics, objname is a variable giving the name of the object unit, and objsemantics is a variable giving the names and weights of the object unit’s semantics. 

(R)ecipient will display the propositions in the recipient in the above form. 

(M)emory will display all the propositions in memory in the above form. 

(B)ack will move the user up a menu level. 

Creating Parameter Files

A parameter file in DORA is a text file formatted as a dictionary data type (if you don’t know what that means, no worries). The basic format of a parameter file looks like: 

parameters = {
'asDORA': True,
'gamma': 0.3,
'delta': 0.1,
'eta': 0.9,
'HebbBias': 0.5,
'run_order': ['cdr', 'selectP', 'selectRB', 'selectPO', 'r', 'm', 's', 'c'],
'run_cyles': 40,
'write_on_iteration': 10,
'firingOrderRule': 'random',
'screen_width': 1200,
'screen_height': 700,
'doGUI': True,
'GUI_update_rate': 1}

In order to change any of the parameter values, simply edit the parameter value in the text file, save it, and load it in the main menu. 

Alternately, if you’re feeling more adventurous, you can open the DORA.py text file (the file containing the main run code for DORA) and edit the default parameters directly. The default parameters are initialized beginning on line 23 of the file. 

Creating and Interpreting Sim Files

Sim files specify the information necessary to build the DORA network. In the sim files units in T1 (PO units) are labeled as pred units or object units. These labels as well as names given to the units (and all other units) are for the purposes of making the sim files easier to read and to write. They are not used by the model during processing. 

Making a proposition involves  filling in a python dictionary with the following keys: 

'name':  
'RBs': 
'set': 
'analog': 

The ‘name’ key specifies the name of the proposition (the name carries no information for the model, but is useful for the modeller in keeping track of propositions during simulations), the ‘set’ key specifies what set it defaults to (either driver, recipient, or memory (NOTE: driver and recipient propositions are also part of memory, they simply start in the driver/recipient upon run), and the ‘analog’ key specifies what analog a proposition belongs to (NOTE: analog numbering starts with 0 for each set (i.e., the first analog in driver is 0, the second 1, and so forth; the first analog in recipient is 0, the second 1, and so forth)). 

The ‘RB’ key contains dictionaries with the following keys: 

'pred_name':
'pred_sem': 
'higher_order': 
’object_name':  
'object_sem':  
'P': 

The ‘pred_name’ key specifies the name of the pred unit (again, the name carries no information for the model, but can be useful for the modeller in keeping track of units during simulations), the ‘pred_sem’ key specifies the semantics of the pred unit (with semantic names in quotes and separated by commas, and all between brackets (e.g., to specify the semantics, ‘big’, ‘tall’, grey’: [‘big’, ‘tall’, grey’])), the ‘higher_order’ key specifies whether the argument of that pred is another proposition or not (True if the argument is another proposition, False otherwise), the ‘object_name’ key specifies the name of the object unit (‘nil’ if there is none (e.g., if the argument is another proposition)), the ‘object_sem’ key specifies the object semantics (with semantic names in quotes and separated by commas, and all between brackets (e.g., to specify the semantics, ‘big’, ‘tall’, grey’: [‘big’, ‘tall’, grey’])), and the ‘P’ key specifies the number of the proposition that the pred unit takes as an argument, given the argument is a proposition, and ‘nil’ otherwise. 

For example, here are four propositions, two in the driver and two in the recipient, with one higher order proposition in both the driver and the recipient. Each proposition is specified with the information between the curly braces ({}). 

simType='sim_file'
symProps = [{'name': 'lovesJohnMary', 'RBs': [{'pred_name': 'lover', 'pred_sem': ['lover1', 'lover2', 'lover3'], 'higher_order': False, 'object_name': 'John', 'object_sem': ['john1', 'john2', 'john3'], 'P': 'nil'}, {'pred_name': 'beloved', 'pred_sem': ['beloved1', 'beloved2', 'beloved3'], 'higher_order': False, 'object_name': 'Mary', 'object_sem': ['mary1', 'mary2', 'mary3'], 'P': 'nil'}], 'set': 'driver', 'analog': 0},

{'name': 'knowsKentlovesJohnMary', 'RBs': [{'pred_name': 'knower', 'pred_sem': ['knower1', 'knower2', 'knower3'], 'higher_order': False, 'object_name': 'Kent', 'object_sem': ['kent1', 'kent2', 'kent3'], 'P': 'nil'}, {'pred_name': 'known', 'pred_sem': ['known1', 'known2', 'known3'], 'higher_order': True, 'object_name': 'nil', 'object_sem': [], 'P': 'lovesJohnMary'}], 'set': 'driver', 'analog': 0}, 

{'name': 'lovesSusanBill', 'RBs': [{'pred_name': 'lover', 'pred_sem': ['lover1', 'lover2', 'lover3'], 'higher_order': False, 'object_name': 'Susan', 'object_sem': ['susan1', 'susan2', 'mary3'], 'P': 'nil'}, {'pred_name': 'beloved', 'pred_sem': ['beloved1', 'beloved2', 'beloved3'], 'higher_order': False, 'object_name': 'Bill', 'object_sem': ['bill1', 'bill2', 'john1'], 'P': 'nil'}], 'set': 'recipient', 'analog': 0}, 

{'name': 'knowsHanslovesSusanBill', 'RBs': [{'pred_name': 'knower', 'pred_sem': ['knower1', 'knower2', 'knower3'], 'higher_order': False, 'object_name': 'Hans', 'object_sem': ['hans1', 'hans2', 'john3q'], 'P': 'nil'}, {'pred_name': 'known', 'pred_sem': ['known1', 'known2', 'known3'], 'higher_order': True, 'object_name': 'nil', 'object_sem': [], 'P': 'lovesSusanBill'}], 'set': 'recipient', 'analog': 0}]

NOTE: It is necessary that all sim files for use in running DORA (either in DORA or User mode) must begin with the statement simType='sim_file’(if loading from a sim file formatted as above) or  simType=‘json_file’(if loading from a json dump—e.g., a saved DORA memory state). 

It is also possible to create sim files were the weights between POs and their semantics are specified directly, and in which semantics code for absolute metric (e.g., pixel) values (NOTE: for saving on memory and readability, when an absolute metric property such as some pixels is encoded by semantic features, instead of storing each pixel as a feature, a single feature specifying the extent of the property (e.g., 10 pixels or 100 pixels) is used; this information is unpacked into real units during processing). This format also appears in the saves of DORA’s memory state after simulations like those reported in Doumas et al., XXXX. Each semantic is specified by a list (rather than a string, as above), in the form [‘name’, weight, extent, property, type], where ‘name’ is the name of the semantic (again, the name carries no information for the model, but can be useful for the modeller in keeping track of units during simulations), weight specifies the weight between the semantic and the predicate or object (any real valued number between 0 and 1 inclusive), extent specifies the extent (as an integer) of the metric property or ‘nil’, otherwise, property is either set to the source of the metric dimension (e.g., the extent of effort of the inferior rectus muscle in pixels), or ‘nil’ otherwise, extent is the absolute value of the metric property (a real number; as noted above, this value is unpacked into real nodes during processing), and type is set to either ‘value’, if the semantic encodes a compressed metric property like pixels, or ’state’, for all other features. 

You can also create sim files with propositions that are only single-place predicates (i.e., objects bound to predicates linked by a RB unit, with no P unit), or unbound objects (i.e., objects bound to no predicates). Below are examples of how to create such propositions. 

An example of propositions without P units: 

symProps = [{'name': ‘non_exist’, 'RBs': [{'pred_name': 'lover', 'pred_sem': ['lover1', 'lover2', 'lover3'], 'higher_order': False, 'object_name': 'John', 'object_sem': ['john1', 'john2', 'john3'], 'P': 'nil'}, {'pred_name': 'beloved', 'pred_sem': ['beloved1', 'beloved2', 'beloved3'], 'higher_order': False, 'object_name': 'Mary', 'object_sem': ['mary1', 'mary2', 'mary3'], 'P': 'nil'}], 'set': 'driver', 'analog': 0}, 

{'name': ‘non_exist’, 'RBs': [{'pred_name': 'lover', 'pred_sem': ['lover1', 'lover2', 'lover3'], 'higher_order': False, 'object_name': 'John', 'object_sem': ['john1', 'john2', 'john3'], 'P': 'nil'}, {'pred_name': 'beloved', 'pred_sem': ['beloved1', 'beloved2', 'beloved3'], 'higher_order': False, 'object_name': 'Mary', 'object_sem': ['mary1', 'mary2', 'mary3'], 'P': 'nil'}], 'set': 'recipient', 'analog': 0}]

Notice that the slot for the P unit is filled with ‘non_exist’, indicating that the proposition contains no P unit. 

An example of propositions without RB units: 

symProps = [{'name': ‘non_exist’, 'RBs': [{'pred_name': ‘non_exist’, 'pred_sem': [], 'higher_order': False, 'object_name': 'John', 'object_sem': ['john1', 'john2', 'john3'], 'P': 'nil'}], 'set': 'driver', 'analog': 0}, 

{'name': 'non_exist', 'RBs': [{'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'John2', 'object_sem': ['john1', 'john4', 'john5'], 'P': 'nil'}], 'set': 'recipient', 'analog': 0}]

Notice that the slot for the P unit is filled with ‘non_exist’, indicating that the proposition contains no P unit, and that the slot for the Pred unit name is filled with ‘non_exist’, indicating that the proposition contains object units not bound to pred units. 

After model runs, D 

References
For details of the DORA model see:
Doumas, Hummel, & Sandhofer (2008). A theory of the discovery and predication of relational concepts (Appendix A). Psychological Review, 115, 1-43. 
Doumas, Martin, Puebla, & Hummel (XXXX). 

