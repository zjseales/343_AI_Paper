__author__ = "Lech Szymanski"
__organization__ = "COSC343/AIML402, University of Otago"
__email__ = "lech.szymanski@otago.ac.nz"
__date__ = "July 2022"


import pylab as pl
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from skimage.transform import resize
import os



class chess_board:
    
    def __init__(self, size=8):
        # Check if the queen png is in the folder, if not,
        # will draw red dots instead
        if os.path.exists('queen.png'):
            self.image = plt.imread('queen.png')
            self.image = resize(self.image, (48, 48))
        else:
            self.image = None
        self.size = size
        #Create a new figure
        self.plfig=pl.figure(dpi=100,figsize=(48*(self.size)*2/100,48*(self.size)*2/100))
        #Create a new subplot
        self.plax = self.plfig.add_subplot(111)
        #Create bitmap for the chessboard
        b = np.ones((size,size))
        b[1::2,1::2]=0
        b[0::2, 0::2]=0

        #Plot the chessboard
        self.plax.matshow(b, cmap=pl.cm.gray)
        pl.xticks([])
        pl.yticks([])
        pl.ion()
        pl.show()        
        self.scatter_handle = []

    def nonattacking_pairs(self, c):

       # There can be len(c) choose 2 total nonattacking_pairs
       nonattacking_pairs = self.size*(self.size-1)/2

       # Iterate over chromosome indexes...
       for i in range(len(c)):
          # Get the queen position, compute
          # row and column
          q1_index = c[i]
          q1_row = int(q1_index/self.size)
          q1_col = q1_index%self.size

          # Iterate over chromosome indexes larger than i
          for j in range(i+1,len(c)):
              # Get the queen position, compute
              # row and column
              q2_index = c[j]
              q2_row = int(q2_index/self.size)

              if q2_row == q1_row:
                  # Pair on the same row
                  nonattacking_pairs -= 1
                  continue

              q2_col = q2_index%self.size

              if q2_col == q1_col:
                  # Pair on the same column
                  nonattacking_pairs -= 1
                  continue

              if np.abs(q2_row-q1_row) == np.abs(q1_col - q2_col):
                  #Pair on a diagonal
                  nonattacking_pairs -= 1
                  continue

       return nonattacking_pairs

    #Show state of the board (encoded as an array of 8 queens with position
    #from the bottom of the board in each column)
    def show_state(self,c):
        for h in self.scatter_handle:
            h.remove()
        self.scatter_handle = []
        #The queens are shown as red dots on the chessboard
        #self.scatter_handle.append(self.plax.scatter(x=np.arange(self.size),y=[self.size-i for i in c], s=40, c='r'))
        for i,l in enumerate(c):
            offset = np.sum(l==np.array(c[:i]))
            if self.image is None:
                y = int(l / self.size)
                x = l % self.size
                self.scatter_handle.append(self.plax.scatter(x=x,y=y, s=40, c='r'))
            else:
                self.scatter_handle.append(self.plax.add_artist(AnnotationBbox(OffsetImage(self.image), (l%self.size+0.05*offset, int(l/self.size)+0.05*offset), frameon=False)))

        self.plfig.canvas.draw()
        # Close any open figures, and start a new one
        pl.pause(0.01)
        time.sleep(0.01)


if __name__ == '__main__':
    #Create instance of chess board visualisation
    size = 8
    board = chess_board(size=size)
    #Show 5 different random queen distributions
    for i in range(0,10):
        # Generate random chromosome by generating
        # random permutation of size*size indexes
        # and then picking the first size-indexex
        c = np.random.permutation(size*size)[:size]
        #Show the new state
        board.show_state(c.tolist())
        time.sleep(0.5)
