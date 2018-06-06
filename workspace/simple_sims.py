# this simulation runs basic success and failure for N&B and R&G. 

# imports. 
import random
import numpy as np
import pdb

# There are a number correct, based on successful relation retrieval. Trials with successful full relation retrieval are based on pull_reps_v2 code. 
age4 = .4
age5 = .7
age6 = .925
age3_5 = .35
age4_5 = .575
age5_5 = .925

# function to run a simple simulation with a number correct in some number of trials, a probability of guessing correctly, and a proportion of trials that are incorrect. 
def do_selection(correct, guess_prob, incorrect):
    # see if you get the trial wrong at the onset.
    rand1 = random.random()
    if rand1 < incorrect:
        correct = 0
    else:
        rand2 = random.random()
        if rand2 < correct:
            correct = 1
        else: 
            rand3 = random.random()
            if rand3 < guess_prob:
                correct = 1
            else:
                correct = 0
    # return correct. 
    return correct

# N&B. 
# simulate age 4. 
# You are correct each time a proper relation is used. You are 50/50 otherwise as you guess on failure.
age4_all = []
for i in range(100):
    child = []
    for trial in range(10):
        correct = do_selection(age4, .5, 0.0)
        child.append(correct)
    # calculate the proportion correct. 
    prop_correct = np.mean(child)
    # add the prop_correct to age4_all.
    age4_all.append(prop_correct)
# simulate age 5. 
# You are correct each time a proper relation is used. You are 50/50 otherwise as you guess on failure.
age5_all = []
for i in range(100):
    child = []
    for trial in range(10):
        correct = do_selection(age5, .5, 0.0)
        child.append(correct)
    # calculate the proportion correct. 
    prop_correct = np.mean(child)
    # add the prop_correct to age5_all.
    age5_all.append(prop_correct)
# simulate age 6. 
# You are correct each time a proper relation is used. You are 50/50 otherwise as you guess on failure.
age6_all = []
for i in range(100):
    child = []
    for trial in range(10):
        correct = do_selection(age6, .5, 0.0)
        child.append(correct)
    # calculate the proportion correct. 
    prop_correct = np.mean(child)
    # add the prop_correct to age6_all.
    age6_all.append(prop_correct)
# print the output. 
print 'Age4: ' + str(np.mean(age4_all))
print 'Age5: ' + str(np.mean(age5_all))
print 'Age6: ' + str(np.mean(age6_all))
print '\n\n'

# R&G. 
# Simple trials. 
# simulate age 3.5. 
# You are correct each time a proper relation is used. You are 33/67 otherwise as you guess on failure. 
age3_5_all_s = []
for i in range(100):
    child = []
    for trial in range(10):
        correct = do_selection(age3_5, .33, 0.0)
        child.append(correct)
    # calculate the proportion correct. 
    prop_correct = np.mean(child)
    # add the prop_correct to age3_5_all_s.
    age3_5_all_s.append(prop_correct)
# simulate age 3.5. 
# You are correct each time a proper relation is used. You are 33/67 otherwise as you guess on failure. 
age4_5_all_s = []
for i in range(100):
    child = []
    for trial in range(10):
        correct = do_selection(age4_5, .33, 0.0)
        child.append(correct)
    # calculate the proportion correct. 
    prop_correct = np.mean(child)
    # add the prop_correct to age4_5_all_s.
    age4_5_all_s.append(prop_correct)
# simulate age 5.5. 
# You are correct each time a proper relation is used. You are 33/67 otherwise as you guess on failure. 
age5_5_all_s = []
for i in range(100):
    child = []
    for trial in range(10):
        correct = do_selection(age5_5, .33, 0.0)
        child.append(correct)
    # calculate the proportion correct. 
    prop_correct = np.mean(child)
    # add the prop_correct to age5_5_all_s.
    age5_5_all_s.append(prop_correct)
# Rich trials. 
# simulate age 3.5. 
# You are correct each time a proper relation is used. You are 33/67 otherwise as you guess on failure. 
age3_5_all_r = []
for i in range(100):
    child = []
    for trial in range(10):
        correct = do_selection(age3_5, .33, 0.33)
        child.append(correct)
    # calculate the proportion correct. 
    prop_correct = np.mean(child)
    # add the prop_correct to age3_5_all_r.
    age3_5_all_r.append(prop_correct)
# simulate age 3.5. 
# You are correct each time a proper relation is used. You are 33/67 otherwise as you guess on failure. 
age4_5_all_r = []
for i in range(100):
    child = []
    for trial in range(10):
        correct = do_selection(age4_5, .33, 0.33)
        child.append(correct)
    # calculate the proportion correct. 
    prop_correct = np.mean(child)
    # add the prop_correct to age4_5_all_r.
    age4_5_all_r.append(prop_correct)
# simulate age 5.5. 
# You are correct each time a proper relation is used. You are 33/67 otherwise as you guess on failure. 
age5_5_all_r = []
for i in range(100):
    child = []
    for trial in range(10):
        correct = do_selection(age5_5, .33, 0.33)
        child.append(correct)
    # calculate the proportion correct. 
    prop_correct = np.mean(child)
    # add the prop_correct to age5_5_all_r.
    age5_5_all_r.append(prop_correct)
# print the output. 
print 'Age3.5(simple): ' + str(np.mean(age3_5_all_s))
print 'Age4.5(simple): ' + str(np.mean(age4_5_all_s))
print 'Age5.5(simple): ' + str(np.mean(age5_5_all_s))
print 'Age3.5(rich): ' + str(np.mean(age3_5_all_r))
print 'Age4.5(rich): ' + str(np.mean(age4_5_all_r))
print 'Age5.5(rich): ' + str(np.mean(age5_5_all_r))


