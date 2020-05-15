# supplamenal plots. 

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

# N&B. 
labels = ['Age 4', 'Age 5', 'Age 6']
human_means = [.68, .8, .92]
DORA_means = [.7, .81, .95]

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, human_means, width, label='Humans')
rects2 = ax.bar(x + width/2, DORA_means, width, label='DORA')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Proportion Correct')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

fig.tight_layout()

plt.show()


# R&G. 
gs = gridspec.GridSpec(1, 2, width_ratios=[1,1])
gs.update(wspace=0.25, hspace=0.5)
# Sparce condition. 
labels = ['Age 3.5', 'Age 4.5', 'Age 5.5']
human_means = [.55, .63, .93]
DORA_means = [.58, .68, .92]

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

ax1 = plt.subplot(gs[0, 0])
rects1 = ax1.bar(x - width/2, human_means, width, label='Humans')
rects2 = ax1.bar(x + width/2, DORA_means, width, label='DORA')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax1.set_ylabel('Proportion Correct')
ax1.set_xticks(x)
ax1.set_xticklabels(labels)
ax1.legend()
ax1.set_ylim(0,1)

# Rich condition. 
labels = ['Age 3.5', 'Age 4.5', 'Age 5.5']
human_means = [.32, .38, .66]
DORA_means = [.39, .45, .63]

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

ax2 = plt.subplot(gs[0, 1])
rects1 = ax2.bar(x - width/2, human_means, width, label='Humans')
rects2 = ax2.bar(x + width/2, DORA_means, width, label='DORA')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax2.set_ylabel('Proportion Correct')
ax2.set_xticks(x)
ax2.set_xticklabels(labels)
ax2.legend()
ax2.set_ylim(0,1)

fig.tight_layout()

plt.show()




