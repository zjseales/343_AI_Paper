__author__ = "Lech Szymanski"
__organization__ = "COSC343/AIML402, University of Otago"
__email__ = "lech.szymanski@otago.ac.nz"
__date__ = "August 2022"

import tkinter as tk
from tkinter import filedialog
import sys, getopt
from snakes import SnakeGame

def main(argv):
    # Load the defaults
    from settings import game_settings

    # Check of arguments from command line
    try:
        opts, args = getopt.getopt(argv, "r:f:l:",["res=", "fast=", "load="])
    except getopt.GetoptError:
        print("Error! Invalid argument.")
        sys.exit(2)

    # Process command line arguments
    loadGame = None
    for opt, arg in opts:
        if opt in ("-r", "--res"):
            res = arg.split('x')
            if len(res) != 2:
               print("Error! The -r/res= argument must be followed with <width>x<height> specifiction of resolution (no spaces).")
               sys.exit(-1)

            game_settings['visResolution'] = (int(res[0]), int(res[1]))
        elif opt in ("-f", "--fast"):
            game_settings['visSpeed'] = arg

        elif opt in ("-l", "--load"):
            loadGame = arg

    if game_settings['visSpeed'] != 'normal' and game_settings['visSpeed'] != 'fast' and game_settings['visSpeed'] != 'slow':
        print("Error! Invalid setting '%s' for visualisation speed.  Valid choices are 'slow','normal',fast'" % game_settings['visSpeed'])
        sys.exit(-1)

    if loadGame is None:
       # If load game wasn't specified in the command line arguments then
       # open a dialog box in the 'saved' folder
       root = tk.Tk()
       root.withdraw()

       loadGame = filedialog.askopenfilename(initialdir="../Submissions_2020")

    # Load a previously saved game
    SnakeGame.load(loadGame,visResolution=game_settings['visResolution'],
               visSpeed=game_settings['visSpeed'])


if __name__ == "__main__":
   main(sys.argv[1:])