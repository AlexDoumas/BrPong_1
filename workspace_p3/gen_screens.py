# generate 500 screens.

import random 

objs = []
for i in range(500):
    go_to = random.choice([2,3])
    for j in range(go_to):
        new_obj = {'name': 'non_exist', 'RBs': [], 'set': 'memory', 'analog': i}
        width = round(random.random()*20)
        hight = round(random.random()*10)
        x = round(random.random()*300)
        y = round(random.random()*800)
        colour = random.choice([255, 155, 55, 100])
        new_obj['RBs'].append({'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj'+str(random.random()), 'object_sem': [['x_ext', 1, 'x_ext', 'nil', 'state'], ['x_ext'+str(width), 1, 'x_ext', width, 'value'], ['y_ext', 1, 'y_ext', 'nil', 'state'], ['y_ext'+str(hight), 1, 'y_ext', hight, 'value'], ['total_ext', 1, 'total_ext', 'nil', 'state'], ['total_ext'+str(width*hight), 1, 'total_ext', width*hight, 'value'], ['x', 1, 'x', 'nil', 'state'], ['x'+str(x), 1, 'x', width*hight, 'value'], ['y', 1, 'y', 'nil', 'state'], ['y'+str(x), 1, 'y', width*hight, 'value'], ['colour', 1, 'colour', 'nil', 'state'], [str(colour), 1, 'colour', colour, 'value']], 'P': 'non_exist'})
        objs.append(new_obj)

write_file = open('screens.py', 'w')
write_file.write('simType=\'sim_file\' \nsymProps = ' + str(objs))
    
    



