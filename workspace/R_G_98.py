# code to run simple sims of Rattermann and Gentner (1998). 
# takes in some sample representations, and makes rich and sparse cross-mapping problems. 

# imports. 
import random, json
import pdb

###########################################################################################
# FUNCTIONS. 
###########################################################################################

# function to load the state file. 
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

# create the range of semantics.
total_sem = 1000
sem_list = []
for semantic in range(total_sem):
    sem_name = 'semantic'+str(semantic)
    sem_list.append(sem_name)
# create the range of shape semantics.
total_shape_sem = 100
shape_sem_list = []
for semantic in range(total_shape_sem):
    sem_name = 'shape'+str(semantic)
    shape_sem_list.append(sem_name)

# fill in the objects of those relations. There should be 3 objects in the driver (a, b, c) and 3 objects in the recipient (x,y,z), such that rel(a,b)&rel(b,c) and rel(x,y)&rel(y,z). One item in driver should be identical to an item in the recipient with the caveat that it is not the relatinally equivalent item (i.e., a cannot be the same as x, b cannot be the same as y, and c cannot be the same as z). 
# generate the three driver objects. 
# select an order 3 numbers from between 1 and 10 to serve as absolute values on the critical dimension. 
nums = range(10)
nums = random.sample(nums, 3)
nums.sort()
obj_sem_list = []
for itr in range(3):
    # create an object with 15 semantics. 
    # 2 are the absolute dimensional values, 
    obj_sem = [['size', 1, 'size', 'nil', 'state'], ['size'+str(nums[itr]), 1, 'size', nums[itr], 'value']]
    # 8 are other absolute dimensions (including colour and shape), but ones that don't predict sticker location. 
    more_sem = [['width', 1, 'width', 'state'], ['width'+str(random.random()), 1, 'width', 'value'], ['height', 1, 'height', 'state'], ['height'+str(random.random()), 1, 'height', 'value'], ['depth', 1, 'depth', 'state'], ['depth'+str(random.random()), 1, 'depth', 'value'], ['colour', 1, 'colour', 'state'], ['black', 1, 'colour', 'value'], ['square', 1, 'shape', 'state'], ['square', 1, 'shape', 'value']]
    for sem in more_sem:
        obj_sem.append(sem)
    # 1 is position in the array ("left", "center", "right"). 
    if itr == 0:
        obj_sem.append(['left', 1, 'nil', 'nil'])
    elif itr == 1:
        obj_sem.append(['center', 1, 'nil', 'nil'])
    else:
        obj_sem.append(['right', 1, 'nil', 'nil'])
    # 4 are chosen at random. 
    more_sem = random.sample(sem_list, 4)
    for sem in more_sem:
        obj_sem.append([sem, 1.0, None, None])
    obj_sem_list.append(obj_sem)

# create the rich objects—as above, but with more semantics. 
nums = range(10)
nums = random.sample(nums, 3)
nums.sort()
obj_sem_list = []
for itr in range(3):
    # create an object with 45 semantics. 
    # 2 are the absolute dimensional values, 
    obj_sem = [['size', 1, 'size', 'nil', 'state'], ['size'+str(nums[itr]), 1, 'size', nums[itr], 'value']]
    # 8 are other absolute dimensions (including colour and shape), but ones that don't predict sticker location. 
    more_sem = [['width', 1, 'width', 'state'], ['width'+str(random.random()), 1, 'width', 'value'], ['height', 1, 'height', 'state'], ['height'+str(random.random()), 1, 'height', 'value'], ['depth', 1, 'depth', 'state'], ['depth'+str(random.random()), 1, 'depth', 'value'], ['colour', 1, 'colour', 'state'], ['black', 1, 'colour', 'value'], ['square', 1, 'shape', 'state'], ['square', 1, 'shape', 'value']]
    for sem in more_sem:
        obj_sem.append(sem)
    # 1 is position in the array ("left", "center", "right"). 
    if itr == 0:
        obj_sem.append(['left', 1, 'nil', 'nil'])
    elif itr == 1:
        obj_sem.append(['center', 1, 'nil', 'nil'])
    else:
        obj_sem.append(['right', 1, 'nil', 'nil'])
    # 4 are shape specific. 
    more_sem = random.sample(shape_sem_list, 4)
    for sem in more_sem:
        obj_sem.append([sem, 1.0, None, None])
    # 30 are chosen at random. 
    more_sem = random.sample(sem_list, 30)
    for sem in more_sem:
        obj_sem.append([sem, 1.0, None, None])
    obj_sem_list.append(obj_sem)



