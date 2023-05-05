__author__ = "Lech Szymanski"
__organization__ = "COSC343/AIML402, University of Otago"
__email__ = "lech.szymanski@otago.ac.nz"
__date__ = "July 2022"

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import time

class eightpuzzle:

    # Initialise the eight puzzle environment
    #
    # Input: mode - string specifying easy, medium or hard mode
    def __init__(self, mode='hard'):
        self.plot_handles = []
        self.mode = mode
        if self.mode == 'hard':
            self.init_state = [7,2,4,5,0,6,8,3,1]
        elif self.mode == 'medium':
            self.init_state = [0, 2, 5, 7, 4, 3, 6, 1, 8]
        elif self.mode == 'easy':
            self.init_state = [1, 5, 4, 7, 0, 2, 3, 6, 8]
        else:
            raise ValueError(
                "The mode '%s' is not supported. Supported modes are ('easy', 'medium', 'hard')." % (
                    mode))

    # Reset
    def reset(self):
        return self.init_state

    def walk(self,n):
        s = [0,1,2,3,4,5,6,7,8]
        aprev = None
        for i in range(n):
            a = self.actions(s)
            while True:
                j = np.random.randint(0, len(a))
                if aprev is None or aprev != a[j]:
                    s = self.step(s,a[j])
                    aprev = a[j]
                    n = n+1
                    break
        return s

    def goal(self):
        return [0,1,2,3,4,5,6,7,8]

    def isgoal(self, s):
        for i in range(9):
            if s[i] != i:
                return False

        return True

    def actions(self, s):
        a = []
        I = np.where(np.array(s)==0)[0][0]

        if I%3 != 0:
            a += [0]

        if I<6:
            a += [1]

        if I%3 != 2:
            a += [2]

        if I>2:
            a+= [3]

        return a

    def step(self,s,a):
        a_valid = self.actions(s)
        s = list(s)
        if a in a_valid:
            I = np.where(np.array(s)==0)[0][0]
            if a == 0:
                Iswitch = I-1
            elif a == 1:
                Iswitch = I+3
            elif a == 2:
                Iswitch = I+1
            else:
                Iswitch = I-3


            s[I] = s[Iswitch]
            s[Iswitch] = 0

        return s

    def show(self,s=None,a=None):
        import warnings
        warnings.filterwarnings("ignore", ".*GUI is implemented.*")

        if s==None:
            s = self.init_state

        if not self.plot_handles or not plt.fignum_exists(self.fh.number):
            self.plot_handles = []
            self.fh = plt.figure(figsize=(6, 6), dpi=100)
            self.h = self.fh.add_subplot(1,1,1)

            for x in range(4):
                self.h.plot([x, x],[0, 3],'k')

            for y in range(4):
                self.h.plot([0, 3],[y, y],'k')
            self.h.set_facecolor((0.8, 0.8, 0.8))
            self.h.get_xaxis().set_visible(False)
            self.h.get_yaxis().set_visible(False)
            self.h.set_xlim([0, 3])
            self.h.set_ylim([0, 3])

        plt.ion()
        plt.show()

        s = list(s)
        n = 0
        while True:
            for ph in self.plot_handles:
                ph.remove()

            self.plot_handles = []

            for i in range(len(s)):
                x = i%3
                y = 2-np.floor(i/3)

                if s[i]>0:
                    self.plot_handles.append(self.h.add_patch(patches.Rectangle((x+0.1,y+0.1), 0.8, 0.8,facecolor="white", edgecolor="black")))
                    self.plot_handles.append(self.h.text(x+0.5, y+0.5, "%d" % s[i], fontsize=20,verticalalignment='center',horizontalalignment='center'))

            plt.draw()
            plt.pause(0.25)
            time.sleep(0.25)

            if a is None or n>=len(a):
                break

            s = self.step(s,a[n])
            n += 1

        plt.ioff()
        plt.show()

