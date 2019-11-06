# plots for video game sims. 

# imports. 
import json, numpy, random
import matplotlib.pyplot as plt
#plt.style.use('ggplot')
import matplotlib.gridspec as gridspec
import pdb

# Import tab20c colors
c = plt.get_cmap('tab20c').colors

from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial']
rcParams['font.size'] = 10

def autolabel(rects,ax):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        #pdb.set_trace()
        ax.text(rect.get_x() + rect.get_width()/2., 1*height, (height), ha='center', va='bottom')

###########################################################################
# BAR PLOTS. 
###########################################################################

gs = gridspec.GridSpec(1, 3, width_ratios=[1,2, 1])
gs.update(wspace=0.25, hspace=0.5)
# Breakout averages and high scores in one plot. 
n_conditions = 1
# means_human = (34, 176)
means_human = (34)
# std_humans = [45.41/5,0]
std_humans = [45.41/5]
# means_DORA = (94.59, 382)
means_DORA = (94.59)
# std_DORA = [76.72/5,0]
std_DORA = [76.72/5]
# means_DQN = (105.8, 315)
means_DQN = (105.8)
# std_DQN = [36.88/5,0]
std_DQN = [36.88/5]
# means_DQNPre = (15.5, 23)
means_DQNPre = (15.5)
# std_DQNPre = [2.97/5,0]
std_DQNPre = [2.97]
# means_NN = (30.69, 86)
means_NN = (30.69)
# std_NN = [16.30/5,0]
std_NN = [16.30/5]

# means_NNnoskip = (36.44, 91)
# means_NNnoskip = (36.44)
# std_NNnoskip = [14.87/5,0]
# std_NNnoskip = [14.87/5]

means_graphnet = (13.44)
std_graphnet = [4.87/5]

ax1 = plt.subplot(gs[0, 0])
index = numpy.arange(n_conditions)
bar_width = 0.15
opacity = 1.0
error_config = {'ecolor': '0.3'}
rects1 = ax1.bar(index, means_human, bar_width,
                alpha=opacity, color=c[6],
                label='Humans', yerr = std_humans, edgecolor = 'k')
rects2 = ax1.bar(index + bar_width, means_DORA, bar_width, alpha=opacity, color=c[0], label='DORA',yerr=std_DORA, edgecolor = 'k')
rects3 = ax1.bar(index + bar_width*2, means_DQN, bar_width, alpha=opacity, color=c[13], label='DQN', yerr = std_DQN, edgecolor = 'k')
rects4 = ax1.bar(index + bar_width*3, means_DQNPre, bar_width, alpha=opacity, color=c[14], label='DQNPre', yerr = std_DQNPre, edgecolor = 'k')
rects5 = ax1.bar(index + bar_width*4, means_NN, bar_width, alpha=opacity, color=c[15], label='DNN',yerr = std_NN, edgecolor = 'k')
rects6 = ax1.bar(index + bar_width*5, means_graphnet, bar_width, alpha=opacity, color=c[16], label='Graphnet', yerr=std_graphnet, edgecolor = 'k')
ax1.set_xlabel('')
ax1.set_ylabel('Score')
ax1.set_title('')
ax1.set_xticks(index + bar_width*4 / 2)
ax1.set_xticklabels(('Breakout\n100 test games avg.', 'Breakout\nhigh score'))
ax1.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)
ax1.set_ylim(0,200)
ax1.legend(bbox_to_anchor=(.025, 1), loc=2, borderaxespad=0.)
ax1.text(-.1,210, '(A)', fontsize=15)
# autolabel(rects1,ax1)
# autolabel(rects2,ax1)
# autolabel(rects3,ax1)
# autolabel(rects4,ax1)
# autolabel(rects5,ax1)
#plt.show()

# Pong in one plot. 
n_conditions = 2
means_human = (14, 14)
std_human = [0, 16.00/5]
means_DORAq = (21, 18.49)
std_DORAq = [0, 5.27/5]
means_DQN = (0,0.0)
std_DQN = [0, 0]
means_DQNPre = (0,0.0)
std_DQNPre = [0, 0]
means_NN = (0,0.0)
std_NN = [0, 0]
means_graphnet = (0,0.0)
std_graphnet = [0, 0/5]
ax2 = plt.subplot(gs[0, 1])
index = numpy.arange(n_conditions)
bar_width = 0.15
opacity = 1.0
error_config = {'ecolor': '0.3'}
rects1 = ax2.bar(index, means_human, bar_width,
                alpha=opacity, color=c[6],
                label='Humans', yerr = std_human, edgecolor = 'k')
rects2 = ax2.bar(index + bar_width, means_DORAq, bar_width, alpha=opacity, color=c[0], label='DORA', yerr = std_DORAq, edgecolor = 'k')
rects3 = ax2.bar(index + bar_width*2, means_DQN, bar_width, alpha=opacity, color=c[13], label='DQN', yerr = std_DQN, edgecolor = 'k')
rects4 = ax2.bar(index + bar_width*3, means_DQNPre, bar_width, alpha=opacity, color=c[14], label='DQNPre', yerr = std_DQNPre, edgecolor = 'k')
rects5 = ax2.bar(index + bar_width*4, means_NN, bar_width, alpha=opacity, color=c[15], label='DNN', yerr = std_NN, edgecolor = 'k')
rects6 = ax2.bar(index + bar_width*5, means_graphnet, bar_width, alpha=opacity, color=c[16], label='graphnet', yerr = std_graphnet, edgecolor = 'k')
#ax2.set_xlabel('Game Type')
ax2.set_ylabel('Score')
ax2.set_title('')
ax2.set_xticks(index + bar_width*4 / 2)
ax2.set_xticklabels(('Pong\nFirst game', 'Pong\nfirst 100 games avg.'))
ax2.spines['right'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax2.text(-.1,23.25, '(B)', fontsize=15)
#ax2.legend(bbox_to_anchor=(.825, 1), loc=2, borderaxespad=0.)
#autolabel(rects1,ax2)
#autolabel(rects2,ax2)
autolabel(rects3,ax2)
autolabel(rects4,ax2)
autolabel(rects5,ax2)
autolabel(rects6,ax2)
#plt.show()

# Back to breakout in a matched plot. 
n_conditions = 1
means_human = (32.3)
std_human = [5.7]
means_DORAq = (81.4)
std_DORAq = [66.72/5]
means_DQN = (0.5)
std_DQN = [.01]
means_DQNPre = (0.7)
std_DQNPre = [.01]
means_NN = (0.3)
std_NN = [.01]
means_graphnet = (0.8)
std_graphnet = [.01]
ax3 = plt.subplot(gs[0, -1])
index = numpy.arange(n_conditions)
bar_width = 0.15
opacity = 1.0
error_config = {'ecolor': '0.3'}
rects1 = ax3.bar(index, means_human, bar_width,
                alpha=opacity, color=c[6],
                label='Humans', yerr = std_human, edgecolor = 'k')
rects2 = ax3.bar(index + bar_width, means_DORAq, bar_width, alpha=opacity, color=c[0], label='DORA', yerr = std_DORAq, edgecolor = 'k')
rects3 = ax3.bar(index + bar_width*2, means_DQN, bar_width, alpha=opacity, color=c[13], label='DQN', edgecolor = 'k')
rects4 = ax3.bar(index + bar_width*3, means_DQNPre, bar_width, alpha=opacity, color=c[14], label='DQNPre', edgecolor = 'k')
rects5 = ax3.bar(index + bar_width*4, means_NN, bar_width, alpha=opacity, color=c[15], label='DNN', edgecolor = 'k')
rects6 = ax3.bar(index + bar_width*5, means_graphnet, bar_width, alpha=opacity, color=c[16], label='graphnet', edgecolor = 'k')
ax3.set_xlabel('Return to Breakout\nFirst 100 games avg. ')
ax3.set_ylabel('Score')
ax3.set_title('')
ax3.set_xticklabels((''))
ax3.set_xticks(index + bar_width*4 / 2)
ax3.spines['right'].set_visible(False)
ax3.spines['top'].set_visible(False)
ax3.set_ylim(0,200)
#ax.set_xticklabels(('Back to\nBreakout\nGame 1'))
ax3.text(-.1,210, '(C)', fontsize=15)
#ax3.legend(borderaxespad=0.,loc='upper center', bbox_to_anchor=(-2.25, 1.25),  shadow=False, ncol=5)

#autolabel(rects1,ax3)
#autolabel(rects2,ax3)
autolabel(rects3,ax3)
autolabel(rects4,ax3)
autolabel(rects5,ax3)
autolabel(rects6,ax3)

#gs.tight_layout()
#plt.subplots_adjust(wspace=0.005)
plt.show()

#############################################################
# plot of CLEVR Breakout to Pong generalisation and ablation sims with original DORA simulation 1 results.
gs = gridspec.GridSpec(1, 3, width_ratios=[1,2, 1])
gs.update(wspace=0.25, hspace=0.5)
# Breakout averages and high scores in one plot. 
n_conditions = 1
# means_DORAq = (94.59, 382)
# std_DORAq = [76.72/5,0]
# means_DORAc = (79.47, 404)
# std_DORAc = [59.89/5,0]
# means_DORAbrlearn = (9.68, 20)
# std_DORAbrlearn = [3.35/5.0, 0]
# means_DORAbrgen = (53.34, 244)
# std_DORAbrgen = [35.21/5.0, 0]
means_DORAq = (94.59)
std_DORAq = [76.72/5]
means_DORAc = (79.47)
std_DORAc = [59.89/5]
means_DORAbrlearn = (9.68)
std_DORAbrlearn = [3.35/5.0]
means_DORAbrgen = (53.34)
std_DORAbrgen = [35.21/5.0]
ax1 = plt.subplot(gs[0, 0])
index = numpy.arange(n_conditions)
bar_width = 0.15
opacity = 1.0
error_config = {'ecolor': '0.3'}
rects1 = ax1.bar(index, means_DORAq, bar_width, alpha=opacity, color=c[0], label='qDORA_sim1',yerr=std_DORAq, edgecolor = 'k')
rects2 = ax1.bar(index + bar_width, means_DORAc, bar_width, alpha=opacity, color=c[3], label='CLEVR_DORA',yerr=std_DORAc, edgecolor = 'k')
rects3 = ax1.bar(index + bar_width*2, means_DORAbrlearn, bar_width, alpha=opacity, color=c[8], label='learn_ablated_DORA', yerr = std_DORAbrlearn, edgecolor = 'k')
rects4 = ax1.bar(index + bar_width*3, means_DORAbrgen, bar_width, alpha=opacity, color=c[11], label='gen_ablated_DORA',yerr=std_DORAbrgen, edgecolor = 'k')
ax1.set_xlabel('')
ax1.set_ylabel('Score')
ax1.set_title('')
ax1.set_xticks(index + bar_width*4 / 2)
ax1.set_xticklabels(('Breakout\n100 test games avg.', 'Breakout\nhigh score'))
ax1.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)
ax1.set_ylim(0,200)
ax1.legend(bbox_to_anchor=(.025, 1), loc=2, borderaxespad=0.)
ax1.text(-.1,210, '(A)', fontsize=15)
#ax1.text(-.1,435, '(a)', fontsize=15)
#plt.show()

# Pong in one plot. 
n_conditions = 2
means_DORAq = (21, 18.49)
std_DORAq = [0, 5.27/5]
means_DORAc = (21, 19.9)
std_DORAc = [0, 3.99/5]
means_DORAbrlearn = (0, 0.0)
std_DORAbrlearn = [0, 0]
means_DORAbrgen = (0, 0.0)
std_DORAbrgen = [0,0]

ax2 = plt.subplot(gs[0, 1])
index = numpy.arange(n_conditions)
bar_width = 0.15
opacity = 1.0
error_config = {'ecolor': '0.3'}
rects1 = ax2.bar(index, means_DORAq, bar_width,
                alpha=opacity, color=c[0],
                label='qDORA_sim1', yerr = std_DORAq, edgecolor = 'k')
rects2 = ax2.bar(index + bar_width, means_DORAc, bar_width, alpha=opacity, color=c[3], label='CLEVR_DORA', yerr = std_DORAc, edgecolor = 'k')
rects3 = ax2.bar(index + bar_width*2, means_DORAbrlearn, bar_width, alpha=opacity, color=c[8], label='learn_ablated_DORA', yerr = std_DORAbrlearn, edgecolor = 'k')
rects4 = ax2.bar(index + bar_width*3, means_DORAbrgen, bar_width, alpha=opacity, color=c[11], label='gen_ablated_DORA', yerr = std_DORAbrgen, edgecolor = 'k')
#ax2.set_xlabel('Game Type')
ax2.set_ylabel('Score')
ax2.set_title('')
ax2.set_xticks(index + bar_width*3 / 2)
ax2.set_xticklabels(('Pong\nFirst game', 'Pong\nfirst 100 games avg.'))
ax2.spines['right'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax2.text(-.1,23.25, '(B)', fontsize=15)
#ax2.text(-.1,12, '(b)', fontsize=15)
#ax2.legend(bbox_to_anchor=(.825, 1), loc=2, borderaxespad=0.)
#autolabel(rects1,ax2)
#autolabel(rects2,ax2)
autolabel(rects3,ax2)
autolabel(rects4,ax2)
#autolabel(rects5,ax2)
#plt.show()

# Back to breakout in a matched plot. 
n_conditions = 1
means_DORAq = (81.4)
std_DORAq = [66.72/5]
means_DORAc = (88.43)
std_DORAc = [75.55/5]
means_DORAbrlearn = (9.68)
std_DORAbrlearn = [3.35/5.0]
means_DORAbrgen = (6.45)
std_DORAbrgen = [3.52/5.0]
ax3 = plt.subplot(gs[0, -1])
index = numpy.arange(n_conditions)
bar_width = 0.15
opacity = 1.0
error_config = {'ecolor': '0.3'}
rects1 = ax3.bar(index, means_DORAq, bar_width, alpha=opacity, color=c[0], label='qDORA_sim1',yerr=std_DORAq, edgecolor = 'k')
rects2 = ax3.bar(index + bar_width, means_DORAc, bar_width, alpha=opacity, color=c[3], label='CLEVR_DORA',yerr=std_DORAc, edgecolor = 'k')
rects3 = ax3.bar(index + bar_width*2, means_DORAbrlearn, bar_width, alpha=opacity, color=c[8], label='learn_ablated_DORA',yerr=std_DORAbrlearn, edgecolor = 'k')
rects4 = ax3.bar(index + bar_width*3, means_DORAbrgen, bar_width, alpha=opacity, color=c[11], label='gen_ablated_DORA',yerr=std_DORAbrgen, edgecolor = 'k')
ax3.set_xlabel('Return to Breakout\nFirst 100 games avg. ')
ax3.set_ylabel('Score')
ax3.set_title('')
ax3.set_xticklabels((''))
ax3.set_xticks(index + bar_width*4 / 2)
ax3.spines['right'].set_visible(False)
ax3.spines['top'].set_visible(False)
ax3.set_ylim(0,200)
ax3.text(-.1,210, '(C)', fontsize=15)
#ax.set_xticklabels(('Back to\nBreakout\nGame 1'))
#ax3.text(-.1,430, '(c)', fontsize=15)
#ax3.legend(borderaxespad=0.,loc='upper center', bbox_to_anchor=(-2.25, 1.25),  shadow=False, ncol=5)

#autolabel(rects1,ax3)
#autolabel(rects2,ax3)
#autolabel(rects3,ax3)
#autolabel(rects4,ax3)

#gs.tight_layout()
#plt.subplots_adjust(wspace=0.005)
plt.show()

############################################################
# supplemental plot showing results of trianing with Pong and generalising to Breakout.
gs = gridspec.GridSpec(1, 3, width_ratios=[1,2, 1])
gs.update(wspace=0.25, hspace=0.5)
# Pong averages and high scores in one plot. 
n_conditions = 1
# means_DORAq = (94.59, 382)
# std_DORAq = [76.72/5,0]
# means_DORAc = (79.47, 404)
# std_DORAc = [59.89/5,0]
# means_DORAbrlearn = (9.68, 20)
# std_DORAbrlearn = [3.35/5.0, 0]
# means_DORAbrgen = (53.34, 244)
# std_DORAbrgen = [35.21/5.0, 0]
means_DORAq = (13.38)
std_DORAq = [6.51/5]
ax1 = plt.subplot(gs[0, 0])
index = numpy.arange(n_conditions)
bar_width = 0.15
opacity = 1.0
error_config = {'ecolor': '0.3'}
rects1 = ax1.bar(index, means_DORAq, bar_width, alpha=opacity, color=c[0], label='DORA',yerr=std_DORAq, edgecolor = 'k')
ax1.set_xlabel('')
ax1.set_ylabel('Score')
ax1.set_title('')
ax1.set_xticks(index)
ax1.set_xticklabels(('Pong 100 test games avg.', ''))
ax1.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)
ax1.set_ylim(0,21)
ax1.legend(bbox_to_anchor=(.025, 1), loc=2, borderaxespad=0.)
ax1.text(-.1,22, '(A)', fontsize=15)
#ax1.text(-.1,435, '(a)', fontsize=15)
#plt.show()

# Breakout in one plot. 
n_conditions = 2
means_DORAq = (71, 76.31)
std_DORAq = [0, 78.5/5]

ax2 = plt.subplot(gs[0, 1])
index = numpy.arange(n_conditions)
bar_width = 0.75
opacity = 1.0
error_config = {'ecolor': '0.3'}
rects1 = ax2.bar(index, means_DORAq, bar_width,
                alpha=opacity, color=c[0],
                label='qDORA', yerr = std_DORAq, edgecolor = 'k')
#ax2.set_xlabel('Game Type')
ax2.set_ylabel('Score')
ax2.set_title('')
ax2.set_xticks(index)
ax2.set_xticklabels(('Breakout\nFirst game', 'Breakout\nfirst 100 games avg.'))
ax2.spines['right'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax2.set_ylim(0,150)
ax2.text(-.1,158, '(B)', fontsize=15)
#ax2.text(-.1,12, '(b)', fontsize=15)
#ax2.legend(bbox_to_anchor=(.825, 1), loc=2, borderaxespad=0.)
#autolabel(rects1,ax2)
#autolabel(rects2,ax2)
#autolabel(rects3,ax2)
#autolabel(rects4,ax2)
#autolabel(rects5,ax2)
#plt.show()

# Back to Pong in a matched plot. 
n_conditions = 1
means_DORAq = (14.2)
std_DORAq = [6.66/5]
ax3 = plt.subplot(gs[0, -1])
index = numpy.arange(n_conditions)
bar_width = 0.15
opacity = 1.0
error_config = {'ecolor': '0.3'}
rects1 = ax3.bar(index, means_DORAq, bar_width, alpha=opacity, color=c[0], label='qDORA',yerr=std_DORAq, edgecolor = 'k')
ax3.set_xlabel('Return to Pong\nFirst 100 games avg. ')
ax3.set_ylabel('Score')
ax3.set_title('')
ax3.set_xticklabels((''))
ax3.set_xticks(index)
ax3.spines['right'].set_visible(False)
ax3.spines['top'].set_visible(False)
ax3.set_ylim(0,21)
ax3.text(-.1,22, '(C)', fontsize=15)
#ax.set_xticklabels(('Back to\nBreakout\nGame 1'))
#ax3.text(-.1,430, '(c)', fontsize=15)
#ax3.legend(borderaxespad=0.,loc='upper center', bbox_to_anchor=(-2.25, 1.25),  shadow=False, ncol=5)

#autolabel(rects1,ax3)
#autolabel(rects2,ax3)
#autolabel(rects3,ax3)
#autolabel(rects4,ax3)

#gs.tight_layout()
#plt.subplots_adjust(wspace=0.005)
plt.show()

