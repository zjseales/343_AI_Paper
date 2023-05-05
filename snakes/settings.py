__author__ = "Lech Szymanski"
__organization__ = "COSC343/AIML402, University of Otago"
__email__ = "lech.szymanski@otago.ac.nz"
__date__ = "August 2022"

# You can manipulate these defaults to change the game parameters.

game_settings = {

   #File implementing the agent playing as player 1
   "player1": "my_agent.py",

   # File implementing the agent playing as player 2
   "player2": "random_agent.py",

   # Size of the game grid
   "gridSize": 50,

   # Number of snakes on a plane
   "nSnakes": 40,

   # Number of turns per game
   "nTurns": 100,

   # Speed of visualisation ('slow','normal','fast')
   "visSpeed": 'normal',

   # Visualisation resolution
   "visResolution": (720, 480),

   "saveFinalGames": True,

   "seed": 0   # seed for game choices, None for random seed
}


