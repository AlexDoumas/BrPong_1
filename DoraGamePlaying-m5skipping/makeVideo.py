import matplotlib.animation as animation
import numpy as np
from pylab import *

#make a video of the given numpy frames with the given name
def makeVideo(frames,filename):
  plt.close('all')
  fig = plt.figure()
  ax = fig.add_subplot(111)
  im = ax.imshow(frames[0])
  
  def update_img(n):
    im.set_data(frames[n])
    return im
  
  ani = animation.FuncAnimation(fig,update_img,len(frames),interval=30)
  writer = animation.writers['imagemagick'](fps=30)

  ani.save(filename,writer='imagemagick',dpi=100)
  
if(__name__ == "__main__"):
  frames = [np.random.rand(300,300) for i in range(300)]
  print animation.writers.list()
  makeVideo(frames,'test.gif')