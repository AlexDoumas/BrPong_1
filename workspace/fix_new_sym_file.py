# imports. 
import random, json

# open the file. 
myfile = open('symFileFixed', 'r')
exec (myfile.readline())
symProps = json.loads(myfile.readline())

# add a time stamp to each object. 
for prop in symProps:
    for myRB in prop['RBs']:
        myRB['object_sem'].append(['time', 1, 'time', 'nil', 'state'])
        # select a random number between 1 and 200. 
        my_value = round(random.random()*20)
        time_value = 'time'+str(my_value)
        myRB['object_sem'].append([time_value, 1, 'time', my_value, 'value'])
        # now delete xVel and yVel. 
        for semantic in reversed(myRB['object_sem']):
            if semantic[2] == 'XVel' or semantic[2] == 'YVel':
                myRB['object_sem'].remove(semantic)
            if semantic[2] == 'X' and semantic[4] == 'value':
                semantic[3] += random.random()*20
                semantic[3] = round(semantic[3])
                semantic[0] = 'X'+str(semantic[3])
            if semantic[2] == 'Y' and semantic[4] == 'value':
                semantic[3] += random.random()*20
                semantic[3] = round(semantic[3])
                semantic[0] = 'Y'+str(semantic[3])

# now write all the sym_props to a file.
write_file = open('new_sym_file.py', 'w')
write_file.write('simType=\'sym_file\' \nsymProps = ' + str(symProps))


