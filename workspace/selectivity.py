# code to run some simple descriptives on a sim file.

import json, numpy
import pylab as plt
import pdb

# list of files to read memory data from.
state_list = ['batch_run100', 'batch_run200', 'batch_run300', 'batch_run400', 'batch_run500', 'batch_run600', 'batch_run700', 'batch_run800', 'batch_run900', 'batch_run1000', 'batch_run1100', 'batch_run1200', 'batch_run1300', 'batch_run1400', 'batch_run1500', 'batch_run1600', 'batch_run1700', 'batch_run1800', 'batch_run1900', 'batch_run2000', 'batch_run2100', 'batch_run2200', 'batch_run2300', 'batch_run2400', 'batch_run2500', 'batch_run2600', 'batch_run2700', 'batch_run2800', 'batch_run2900', 'batch_run3000', 'batch_run3100', 'batch_run3200', 'batch_run3300', 'batch_run3400', 'batch_run3500', 'batch_run3600', 'batch_run3700', 'batch_run3800', 'batch_run3900', 'batch_run4000', 'batch_run4100', 'batch_run4200', 'batch_run4300', 'batch_run4400', 'batch_run4500', 'batch_run4600', 'batch_run4700', 'batch_run4800', 'batch_run4900', 'batch_run5000']

# for each memory state in state_list, make a list of all predicate semantics, and add that list to the memory_list.
memory_list = []
for state in state_list:
    # load in the json file.
    myfile = open(state, 'r')
    myfile.seek(0)
    myfile.readline()
    props_master = json.loads(myfile.readline())
    # make a list of all the pred sem and relational status (whether the preds are part of a whole relation or not) from all the props in memory.
    pred_sem_list = []
    for prop in props_master:
        if prop['name'] != 'non_exist':
            rel_state = 1
        else:
            rel_state = 0
        for myRB in prop['RBs']:
            RB_info = [myRB['pred_sem'], rel_state]
            pred_sem_list.append(RB_info)
    # add the pred_sem_list ot memory_list.
    memory_list.append(pred_sem_list)

#pdb.set_trace()

# # break pred_sem_list into groups of 100 preds.
# groups_of_preds = []
# current_group = []
# for i in range(len(pred_sem_list)):
#     current_group.append(pred_sem_list[i])
#     # if current_group is 100 items long, add it to groups_of_preds.
#     if (i+1)%100 == 0:
#         # append current_group to groups_of_preds and clear current_group.
#         groups_of_preds.append(current_group)
#         current_group = []
# # and add the final set of items to groups_of_preds (assuming that your last set of preds was not exactly 100 items long).
# if len(current_group) > 0:
#     groups_of_preds.append(current_group)

# # break the pred_sem_list into sets. Every 25 preds, make a list of the last 100 preds.
# groups_of_preds = []
# current_group = []
# for i in range(len(pred_sem_list)):
#     # if current group is mod 25, then make a set of the last 100 preds (or just last n preds if number of preds is less than 100).
#     if (i+1)%25 == 0:
#         # collect the last 100 preds.
#         if i >= 99:
#             for j in range(i, i-100, -1):
#                 current_group.append(pred_sem_list[j])
#         else:
#             for j in range(i,i-(i+1), -1):
#                 current_group.append(pred_sem_list[j])
#         # append current_group to groups_of_preds and clear current_group.
#         groups_of_preds.append(current_group)
#         current_group = []
# # and add the final set of 100 items to groups_of_preds (assuming that your set of preds was not perfectly devisible by 25).
# for j in range(len(pred_sem_list)-1, len(pred_sem_list)-101, -1):
#     current_group.append(pred_sem_list[j])
# groups_of_preds.append(current_group)

# # clean up the tiny semantics.
# for pred_group in memory_list:
#     for prop in pred_group:
#         for sem in reversed(prop[0]):
#             if sem[1] < .51:
#                 prop[0].remove(sem)

# calculate selectivity metric. The selectivity metric is calculated as mean(weight(dimension&same/more/less)/(1+mean(all_other_sem))). 
# collect all this information for all preds in the system, for all preds that are NOT part of relations, and for all preds that are parts of relations. 
sel_met_list = [[0]]
RB_met_list = [[0]]
rel_met_list = [[0]]
for pred_group in memory_list:
    group_met = []
    RB_met = []
    rel_met = []
    for pred in pred_group:
        # for all props. 
        if len(pred[0]) > 0:
            numerator = []
            denomenator = []
            high_weight = 0.0
            high_dim = 'nil'
            for sem in pred[0]:
                if sem[0] == 'time' or sem[0] == 'X' or sem[0] == 'Y' or sem[0] == 'xvel' or sem[0] == 'yvel':
                    if sem[1] > high_weight:
                        high_dim = sem[0]
                        high_weight = sem[1]
            for sem in pred[0]:
                if sem[0] == high_dim or sem[0] == 'same' or sem[0] == 'more' or sem[0] == 'less':
                    if sem[1] > .9:
                        numerator.append(sem[1])
                else:
                    denomenator.append(sem[1])
            try:
                av_numer = sum(numerator)/float(len(numerator))
            except:
                pdb.set_trace()
            #av_numer = sum(numerator)/2 # as there are two semantics of interest (dimension & SDML). 
            if len(denomenator) > 0:
                av_denom = sum(denomenator)/float(len(denomenator))
            else:
                av_denom = 0.0
            # check if the current RB is part of a relation or not. 
            if pred[1] == 1:
                sel_met = float(av_numer)/(1+av_denom)
            else:
                sel_met = (float(av_numer)/(1+av_denom))/2.0
        else:
            #sel_met = 0
            sel_met = None
        if sel_met:
            group_met.append(sel_met)
        # for all props that are ONLY RBs. 
        if pred[1] == 0:
            if len(pred[0]) > 0:
                numerator = []
                denomenator = []
                high_weight = 0.0
                high_dim = 'nil'
                for sem in pred[0]:
                    if sem[0] == 'time' or sem[0] == 'X' or sem[0] == 'Y' or sem[0] == 'xvel' or sem[0] == 'yvel':
                        if sem[1] > high_weight:
                            high_dim = sem[0]
                            high_weight = sem[1]
                for sem in pred[0]:
                    if sem[0] == high_dim or sem[0] == 'same' or sem[0] == 'more' or sem[0] == 'less':
                        numerator.append(sem[1])
                    else:
                        denomenator.append(sem[1])
                av_numer = sum(numerator)/float(len(numerator))
                #av_numer = sum(numerator)/2 # as there are two semantics of interest (dimension & SDML). 
                if len(denomenator) > 0:
                    av_denom = sum(denomenator)/float(len(denomenator))
                else:
                    av_denom = 0.0
                # check if the current RB is part of a relation or not. 
                if pred[1] == 1:
                    sel_met = float(av_numer)/(1+av_denom)
                else:
                    sel_met = (float(av_numer)/(1+av_denom))/2.0
            else:
                sel_met = 0
            RB_met.append(sel_met)
        # for all props that are whole relations. 
        if pred[1] == 1:
            if len(pred[0]) > 0:
                numerator = []
                denomenator = []
                high_weight = 0.0
                high_dim = 'nil'
                for sem in pred[0]:
                    if sem[0] == 'time' or sem[0] == 'X' or sem[0] == 'Y' or sem[0] == 'xvel' or sem[0] == 'yvel':
                        if sem[1] > high_weight:
                            high_dim = sem[0]
                            high_weight = sem[1]
                for sem in pred[0]:
                    if sem[0] == high_dim or sem[0] == 'same' or sem[0] == 'more' or sem[0] == 'less':
                        if sem[1] > .9:
                            numerator.append(sem[1])
                    else:
                        denomenator.append(sem[1])
                av_numer = sum(numerator)/float(len(numerator))
                #av_numer = sum(numerator)/2 # as there are two semantics of interest (dimension & SDML). 
                if len(denomenator) > 0:
                    av_denom = sum(denomenator)/float(len(denomenator))
                else:
                    av_denom = 0.0
                # check if the current RB is part of a relation or not. 
                if pred[1] == 1:
                    sel_met = float(av_numer)/(1+av_denom)
                else:
                    sel_met = (float(av_numer)/(1+av_denom))/2.0
            else:
                sel_met = 0
            rel_met.append(sel_met)
    sel_met_list.append(group_met)
    if len(RB_met) > 0:
        RB_met_list.append(RB_met)
    else:
        RB_met_list.append([0])
    if len(rel_met) > 0:
        rel_met_list.append(rel_met)
    else:
        rel_met_list.append([0])

# additional analysis.
# number of one POs, RBs, and full Ps.
num_by_state = []
for pred_group in memory_list:
    state_num = [0,0,0]
    for prop in pred_group:
        if prop[1] == 1:
            state_num[2]+=1
        elif len(prop[0])>0:
            state_num[1]+=1
        else:
            state_num[0]+=1
    num_by_state.append(state_num)
for state in num_by_state:
    state_num = num_by_state.index(state)+1
    state_num *= 100
    print str(state_num) + ': ' + str(state)
# plot the number of POs, RBs, and Ps at each learning interval. 
# make an array of the POs (the 0th item in each state). 
# you could use list comp (e.g., [x[0] for x in num_by_state]), but I'm going to play with numpy. 

num_by_state = numpy.array(num_by_state)
POs = num_by_state[:,0]
RBs = num_by_state[:,1]
Ps = num_by_state[:,2]
x_length = len(num_by_state)
x = numpy.arange(0,x_length*50, 50)
#POs,=plt.plot(x,POs, 'k.', linewidth=3.0, label='objects')
RBs,=plt.plot(x,RBs, 'k--', linewidth=3.0, label='single-place predicates')
Ps,=plt.plot(x,Ps, 'k-', linewidth=3.0, label='whole relations')
plt.legend([RBs, Ps], ['single-place predicates', 'whole relations'])
plt.xlabel('iteration')
plt.ylabel('number of representations in LTM')
# set the range of the axes.
plt.axis([0,2500,0,250])
plt.grid(False)
plt.show()

# calculate the mean sel_met for each memory state.
# for all props. 
sel_met_avgs = []
for met in sel_met_list:
    avg = sum(met)/float(len(met))
    sel_met_avgs.append(avg)
#print sel_met_avgs
x_length = len(sel_met_avgs)
x = numpy.arange(0,x_length*50, 50)
y = sel_met_avgs
# draw the lines on the graph.
DORA,=plt.plot(x,y, 'k-', label='DORA')
#plt.legend(handles=[DORA, Humans])
#plt.axis([-.1,4.5,0,1])
# label the axes.
plt.xlabel('iteration')
plt.ylabel('selectivity')
plt.grid(False)
plt.show()

# for all RBs. 
sel_met_avgs = []
for met in RB_met_list:
    avg = sum(met)/float(len(met))
    sel_met_avgs.append(avg)
#print sel_met_avgs
x_length = len(sel_met_avgs)
x = numpy.arange(0,x_length*50, 50)
y = sel_met_avgs
# draw the lines on the graph.
DORA,=plt.plot(x,y, 'r--', label='DORA')
#plt.legend(handles=[DORA, Humans])
#plt.axis([-.1,4.5,0,1])
# label the axes.
plt.xlabel('iteration')
plt.ylabel('selectivity')
plt.grid(False)
plt.show()

# for all whole relations. 
sel_met_avgs = []
for met in rel_met_list:
    avg = sum(met)/float(len(met))
    sel_met_avgs.append(avg)
print sel_met_avgs
x_length = len(sel_met_avgs)
x = numpy.arange(0,x_length*50, 50)
y = sel_met_avgs
# draw the lines on the graph.
DORA,=plt.plot(x,y, 'r--', label='DORA')
#plt.legend(handles=[DORA, Humans])
#plt.axis([-.1,4.5,0,1])
# label the axes.
plt.xlabel('iteration')
plt.ylabel('selectivity')
plt.grid(False)
plt.show()

#pdb.set_trace()


