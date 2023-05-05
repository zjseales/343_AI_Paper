__author__ = "Lech Szymanski"
__organization__ = "COSC343/AIML402, University of Otago"
__email__ = "lech.szymanski@otago.ac.nz"
__date__ = "September 2022"
__version__ = 1.1

import importlib
import numpy as np
import traceback
import sys
import gzip, pickle
from datetime import datetime
import os
import signal

maxTrainingEpochs = 500
maxActions = 3
numPlays = 5
startingLength = 2


def alarm_handler(signum, frame):
    raise RuntimeError("Time out")

def percepts_global_to_agent_frame_of_reference(percepts,rotation):

    if rotation == 90:
        percepts = np.rot90(percepts, axes=[0, 1])
    elif rotation == 270:
        percepts = np.rot90(percepts, axes=[1, 0])
    elif rotation == 180:
        percepts = np.rot90(np.rot90(percepts,axes=[0,1]),axes=[0,1])

    return percepts

def actions_agent_to_global_shift(action, rotation):

    # 000
    # 020
    # 010   0       a=-1  [0,-1]; a=0 [-1,0]; a=1 [0,1]         0 (-1)  270   0 (1)  90

    # 000
    # 120
    # 000   90      a=-1  [-1,0]; a=0 [0,1]; a=1 [1,0]          90 (-1) 0     90 (1) 180

    # 010
    # 020
    # 000   180     a=-1  [0,1]; a=0 [1,0]; a=1 [0,-1]          180 (-1)

    # 000
    # 021
    # 000   270     a=-1  [1,0]; a=0 [0,-1]; a=1 [-1,0]

    if action == 1:
        if rotation == 0:
            return 0,1
        elif rotation == 90:
            return 1,0
        elif rotation == 180:
            return 0,-1
        else:
            return -1,0
    elif action == -1:
        if rotation == 0:
            return 0,-1
        elif rotation == 90:
            return -1,0
        elif rotation == 180:
            return 0,1
        else:
            return 1,0
    elif action == 0:
        if rotation == 0:
            return 1,0
        elif rotation == 90:
            return 0,1
        elif rotation == 180:
            return -1,0
        else:
            return 0,-1



# Class avatar is a wrapper for the agent with extra bits required
# for runnin the game
class Avatar:

    # Initialise avatar for an agent of a given player
    def __init__(self,agent,player):
        self.agent = agent
        self.player = player

    # Reset the avatar variables for a new game
    def reset_for_new_game(self,nTurns):
        self.size = startingLength
        self.sizes = np.zeros((nTurns)).astype('uint32')
        self.hit = False
        self.dead = False
        self.body = []
        self.percepts = np.zeros((self.player.nFrames,self.player.fieldOfVision,self.player.fieldOfVision)).astype('int')

    def update_size_stats(self,turn):
        if not self.hit:
            self.sizes[turn] = self.size

    # Execute AgentFunction that maps percepts to actions
    def action(self, turn, percepts):

        if self.player.game.in_tournament:
            signal.signal(signal.SIGALRM, alarm_handler)
            signal.alarm(1)

        try:
            action = self.agent.AgentFunction(percepts)

        except Exception as e:
            if self.player.game.in_tournament:
                raise RuntimeError("Error! Failed to execute AgentFunction - %s" % str(e))
            else:
                print("Error! Failed to execute AgentFunction - %s" % str(e))
                traceback.print_exc()
                sys.exit(-1)

        if self.player.game.in_tournament:
            signal.alarm(0)

        if type(action) != int and type(action) != np.int64 and type(action) != np.int32 and type(action) != np.int8:
            if self.player.game.in_tournament:
                raise RuntimeError("Error! AgentFunction must return an integer")
            else:
                print("Error! AgentFunction must return an integer")
                traceback.print_exc()
                sys.exit(-1)

        if action not in [-1,0,1]:
            if self.player.game.in_tournament:
                raise RuntimeError("Error! The returned action must be an integer -1,0, or 1")
            else:
                print("Error! The returned action must be an integer -1,0, or 1, not %d" % action)
                traceback.print_exc()
                sys.exit(-1)

        return action

# Class player holds all the agents for a given player
class Player:

    def __init__(self, game, player, playerFile,emptyMode=False):

        self.game = game
        self.player = player
        self.playerFile = playerFile
        self.nAgents = self.game.nAgents
        self.fitness = list()
        self.errorMsg = ""
        self.ready = False

        if emptyMode:
            return

        if not os.path.exists(playerFile):
            print("Error! Agent file '%s' not found" % self.playerFile)
            traceback.print_exc()
            sys.exit(-1)

        if len(playerFile) > 3 and playerFile[-3:].lower() == '.py':
            playerModule = playerFile[:-3]
        else:
            print("Error! Agent file %s needs a '.py' extension" % self.playerFile)
            traceback.print_exc()
            sys.exit(-1)

        # Import agent file as module
        if self.game.in_tournament:
            signal.signal(signal.SIGALRM, alarm_handler)
            signal.alarm(10)
        try:
            self.exec = importlib.import_module(playerModule)

        except Exception as e:
            if self.game.in_tournament:
                signal.alarm(0)
                self.errorMsg = str(e)
                return
            else:
                print("Error! Failed to load '%s'" % self.playerFile)
                traceback.print_exc()
                sys.exit(-1)

        if self.game.in_tournament:
            signal.alarm(0)

        if self.game.in_tournament:
            self.name = playerFile.split('.')[1]
        else:
            if hasattr(self.exec, 'agentName'):
                self.name = self.exec.agentName
            else:
                self.name = playerFile

        if not hasattr(self.exec,'perceptFieldOfVision'):
            if self.game.in_tournament:
                signal.alarm(0)
                self.errorMsg = "Agent is missing the 'perceptFieldOfVision' variable."
                return
            else:
                print("Error! Agent is missing the 'perceptFieldOfVision' variable.")
                traceback.print_exc()
                sys.exit(-1)

        self.fieldOfVision = int(self.exec.perceptFieldOfVision)
        if self.fieldOfVision not in [3,5,7,9]:
            if self.game.in_tournament:
                signal.alarm(0)
                self.errorMsg = "Agent's perceptFieldOfVision value must be an int from the set {3,5,7,9}."
                return
            else:
                print("Error! Agent's perceptFieldOfVision value must be an int from the set {3,5,7,9}.")
                traceback.print_exc()
                sys.exit(-1)

        self.nFrames = int(self.exec.perceptFrames)
        if self.nFrames not in [1,2,3,4]:
            if self.game.in_tournament:
                signal.alarm(0)
                self.errorMsg = "Agent's perceptFrames value must be an int from the set {1,2,3,4}."
                return
            else:
                print("Error! Agent's perceptFieldOfVision value must be an int from the set {1,2,3,4}.")
                traceback.print_exc()
                sys.exit(-1)

        if not hasattr(self.exec,'trainingSchedule'):
            if self.game.in_tournament:
                signal.alarm(0)
                self.errorMsg = "Agent is missing the 'trainingSchedule' variable."
                return
            else:
                print("Error! Agent is missing the 'trainingSchedule' variable.")
                traceback.print_exc()
                sys.exit(-1)

        self.trainingSchedule = self.exec.trainingSchedule

        if self.trainingSchedule is not None and not isinstance(self.trainingSchedule,list):
            if self.game.in_tournament:
                signal.alarm(0)
                self.errorMsg = "Agent's 'trainingSchedule' should be a list of (str,int) tuples."
                return
            else:
                print("Error! Agent's 'trainingSchedule' should be a list of (str,int) tuples.")
                traceback.print_exc()
                sys.exit(-1)

        if isinstance(self.trainingSchedule, list):

            totTrainEpochs = 0

            for trainSession in self.trainingSchedule:
                if not isinstance(trainSession,tuple) or len(trainSession) < 2 or not (isinstance(trainSession[0],str)) or not isinstance(trainSession[1],int):
                    if self.game.in_tournament:
                        signal.alarm(0)
                        self.errorMsg = "Agent's 'trainingSchedule' should be a list containing (str,int) tuples."
                        return
                    else:
                        print("Error! Agent's 'trainingSchedule' should be a list containing (str,int) tuples.")
                        traceback.print_exc()
                        sys.exit(-1)

                if trainSession[1] < 0:
                    if self.game.in_tournament:
                        signal.alarm(0)
                        self.errorMsg = "Agent's 'trainingSchedule' should be a list of (str,int) tuples, where int corresponds to the number of train generations."
                        return
                    else:
                        print("Error! Agent's 'trainingSchedule' should be a list of (str,int) tuples, where int corresponds to the number of train generations.")
                        traceback.print_exc()
                        sys.exit(-1)

                    totTrainEpochs += trainSession[1]

            if totTrainEpochs > maxTrainingEpochs:
                if self.game.in_tournament:
                    signal.alarm(0)
                    self.errorMsg = "Agent's 'trainingSchedule' cannot specify more than %d training epochs in total." % maxTrainingEpochs
                    return
                else:
                    print("Error! Agent's 'trainingSchedule' cannot specify more than %d training epochs in total." % maxTrainingEpochs)
                    traceback.print_exc()
                    sys.exit(-1)

        if self.trainingSchedule is None:
            self.trained = True
        else:
            self.trained = False

        # Create the initial population of agents by creating
        # new instance of the agent using provided MyCreature class
        agentFile = playerModule

        if self.game.in_tournament:
            agentFile = agentFile.replace('.', '/')

        self.savedAgent = agentFile + '.tar.gz'

        savedAgent = self.savedAgent

        if not os.path.exists(savedAgent) or (not self.game.in_tournament and os.path.getmtime(savedAgent) < os.path.getmtime("%s.py" % agentFile)):
            agents = list()
            for n in range(self.nAgents):
                if self.game.in_tournament:
                    signal.signal(signal.SIGALRM, alarm_handler)
                    signal.alarm(1)
                try:
                    #if self.trained and n>0:
                    #    agent = agents[-1]
                    #else:
                    agent = self.exec.Snake(nPercepts=self.fieldOfVision**2*self.nFrames, actions=[-1,0,1])
                except Exception as e:
                    if self.game.in_tournament:
                        signal.alarm(0)
                        self.errorMsg = str(e)
                        return
                    else:
                        print("Error! Failed to instantiate Snake() from '%s'" % self.playerFile)
                        traceback.print_exc()
                        sys.exit(-1)

                if self.game.in_tournament:
                    signal.alarm(0)
                agents.append(agent)
        else:
            with gzip.open(savedAgent,'r') as f:
                agents = pickle.load(f)
            self.trained = True

        # Convert list of agents to list of avatars
        try:
            self.agents_to_avatars(agents)
        except Exception as e:
            if self.game.in_tournament:
                signal.alarm(0)
                self.errorMsg = str(e)
                return
            else:
                print("Error! Failed to create a list of Snakes")
                traceback.print_exc()
                sys.exit(-1)

        self.ready = True

    # Convert list of agents to list of avatars
    def agents_to_avatars(self, agents):
        self.avatars = list()
        self.stats = list()

        for agent in agents:
            if type(agent) != self.exec.Snake:
                if self.game.in_tournament:
                    raise RuntimeError(
                        'Error! The new_population returned from newGeneration() must contain objects of Snake() type')
                else:
                    print("Error! The new_population returned form newGeneration() in '%s' must contain objects of Snake() type" %
                    self.playerFile)
                    traceback.print_exc()
                    sys.exit(-1)

            avatar = Avatar(agent,player=self)
            self.avatars.append(avatar)
            self.stats.append(dict())

    def avatar_to_agent_stats(self,avatar):
        agent = avatar.agent
        agent.sizes = avatar.sizes
        return agent

    # Get a new generation of agents
    def new_generation_agents(self,gen):

        # Record game stats in the agent objects
        old_population = list()
        for avatar in self.avatars:
            agent = self.avatar_to_agent_stats(avatar)
            old_population.append(agent)

        if self.playerFile != 'random_agent.py':
            sys.stdout.write("  avg_fitness: ")
            sys.stdout.flush()

        # Get a new population of agents by calling
        # the provided newGeneration method
        if self.game.in_tournament:
            signal.signal(signal.SIGALRM, alarm_handler)
            signal.alarm(4)

        try:
            result = self.exec.newGeneration(old_population)
        except Exception as e:
            if self.game.in_tournament:
                raise RuntimeError('Error! Failed to execute newGeneration(), %s' % str(e))
            else:
                print("Error! Failed to execute newGeneration() from '%s', %s" % (self.playerFile, str(e)))
                traceback.print_exc()
                sys.exit(-1)

        if self.game.in_tournament:
            signal.alarm(0)

        if type(result) != tuple or len(result) != 2:
            if self.game.in_tournament:
                raise RuntimeError('Error! The returned value form newGeneration() must be a 2-item tuple')
            else:
                print("Error! The returned value form newGeneration() in '%s.py' must be a 2-item tuple" % self.playerFile)
                traceback.print_exc()
                sys.exit(-1)

        (new_population, fitness) = result

        if type(new_population) != list:
            if self.game.in_tournament:
                raise RuntimeError('Error! The new_population returned form newGeneration() must be a list')
            else:
                print("Error! The new_population returned form newGeneration() in '%s.py' must be a list" % self.playerFile)
                traceback.print_exc()
                sys.exit(-1)

        try:
            fitness = float(fitness)
        except Exception as e:
            if self.game.in_tournament:
                raise RuntimeError('Error! The fitness returned form newGeneration() must be float or int')
            else:
                print("Error! The new_population returned form newGeneration() in '%s.py' must be a float or int" % self.playerFile)
                traceback.print_exc()
                sys.exit(-1)

        if len(new_population) != len(old_population):
            if self.game.in_tournament:
                raise RuntimeError('Error! The new_population returned form newGeneration() must contain %d items' % self.nAgents)
            else:
                print("Error! The new_population returned form newGeneration() in '%s.py' must contain %d items" % (self.playerFile, self.nAgents))
                traceback.print_exc()
                sys.exit(-1)

        if self.playerFile != 'random_agent.py':
            sys.stdout.write(" %.2e" % fitness)
            sys.stdout.flush()
        self.fitness.append(fitness)

        # Convert agents to avatars
        self.agents_to_avatars(new_population)

    def evaluate_fitness(self):

        agents = []
        for avatar in self.avatars:
            agent = self.avatar_to_agent_stats(avatar)
            agents.append(agent)

        try:
            fitness = self.exec.evalFitness(agents)
        except:
            if self.game.in_tournament:
                raise RuntimeError("Error! Failed to execute evalFitness() from '%s'" % self.playerFile)
            else:
                print("Error! Failed to execute evalFitness() from '%s'" % self.playerFile)
                traceback.print_exc()
                sys.exit(-1)

        if isinstance(fitness,np.ndarray):
            fitness = fitness.tolist()

        if not isinstance(fitness, list):
            if self.game.in_tournament:
                raise RuntimeError("Error! Function evalFitness() from '%s' must return a list" % self.playerFile)
            else:
                print("Error! Function evalFitness() from '%s' must return a list" % self.playerFile)
                traceback.print_exc()
                sys.exit(-1)

        if len(fitness) != len(agents):
            if self.game.in_tournament:
                raise RuntimeError(
                    "Error! Length of the list returned by evalFitness() from '%s' is %d; expecting the length to be %d." % (
                    self.playerFile, len(fitness), len(agents)))
            else:
                print(
                    "Error! Length of the list returned by evalFitness() from '%s' is %d; expecting the length to be %d." % (
                    self.playerFile, len(fitness), len(agents)))
                traceback.print_exc()
                sys.exit(-1)

        I = np.argsort(fitness)[::-1]
        self.avatars = np.array(self.avatars)[I].tolist()
        sys.stdout.write("  avg_fitness: ")
        sys.stdout.write(" %.2e\n\n" % np.mean(fitness))
        sys.stdout.flush()


    def save_trained(self):

        savedAgent = self.savedAgent

        sys.stdout.write("Saving last generation agents to %s..."  % self.savedAgent)
        sys.stdout.flush()
        agents = []
        for avatar in self.avatars:
            agents.append(avatar.agent)

        with gzip.open(savedAgent,'w') as f:
            pickle.dump(agents, f)
        sys.stdout.write("done\n")
        sys.stdout.flush()


class SnakePlay:

    def __init__(self,game,showGame=None,saveGame=False):
        self.game = game
        self.map = np.zeros((self.game.gridSize, self.game.gridSize), dtype='int8')
        self.showGame = showGame
        self.saveGame = saveGame

        if self.saveGame:
            self.vis_map = np.zeros((self.game.gridSize, self.game.gridSize, 3, self.game.nTurns+1), dtype='int8')
        elif self.showGame is not None:
            self.vis_map = np.zeros((self.game.gridSize, self.game.gridSize, 3, 1), dtype='int8')


    def vis_update(self,i,players,food):

        if not self.saveGame:
            self.vis_map *= 0
            i = 0

        for k,player in enumerate(players):
            for avatar in player.avatars:
                if avatar.dead:
                    continue

                j = 1
                if avatar.hit:
                    j = -1

                for y,x in avatar.body:
                    self.vis_map[y,x,k,i] = 1*j

                y,x = avatar.head
                self.vis_map[y,x,k,i] = 2*j

        for y,x in food:
            self.vis_map[y, x, 2, i] = 1

        return self.vis_map[:,:,:,i]

    def manhattan_distance(self, x1,y1,x2,y2):
        x = np.min([np.abs(x1-x2),np.abs(x2-x1)])
        y = np.min([np.abs(y1-y2),np.abs(y2-y1)])

        return x+y


    def place_food(self, heads, food, N=1):
        candidates = []
        for y in range(self.game.gridSize):
            for x in range(self.game.gridSize):
                if self.map[y,x] == 0 and (y,x) not in food:
                    candidates += [(y,x)]
        candidates = np.array(candidates)
        I = self.game.rnd_fixed_seed.permutation(len(candidates))
        candidates = candidates[I]
        #candidates = np.argwhere(self.map==0)
        #distances = np.zeros((len(candidates)))
        placements = []

        #for i in range(len(candidates)):
        #    y2, x2 = candidates[i]
        #    for y1,x1 in heads:
        #        distances[i] += self.manhattan_distance(x1,y1,x2,y2)**2

        #    for y1,x1 in food:
        #        distances[i] += self.manhattan_distance(x1,y1,x2,y2)**2

        for n in range(N):
            #p = distances / np.sum(distances)

            #if len(p) < 1:
            #    break
            if len(candidates) < 1:
                break


            #i = self.game.rnd_fixed_seed.choice(np.arange(len(candidates)), size=1, p=p)[0]

            y,x = candidates[-1]
            candidates = candidates[:-1]

            placements += [(y,x)]

            #if i < (len(candidates)-1):
            #    candidates[i] = candidates[-1]
            #    distances[i] = distances[-1]

            #candidates = candidates[:-1]
            #distances = distances[:-1]

            #for i in range(len(candidates)):
            #    y2, x2 = candidates[i]
            #    distances[i] += self.manhattan_distance(x, y, x2, y2)**2

        return placements


    def play(self,players):

        heads1 = []
        heads2 = []

        nRegions = self.game.gridSize//5
        regions = []
        for y in range(nRegions):
            for x in range(nRegions):
                regions.append([x,y])


        #locations = np.zeros((self.game.gridSize,self.game.gridSize,2)).astype('int32')
        #for x in range(self.game.gridSize):
        #    for y in range(self.game.gridSize):
        #        locations[y,x,:]=[y,x]
        #locations = np.reshape(locations,(-1,2))

        #I = self.game.rnd_fixed_seed.permutation(len(locations))
        #locations = locations[I]
        I = self.game.rnd_fixed_seed.permutation(len(regions))
        regions= np.array(regions)[I]

        self.food = []
        # Reset avatars for a new game
        for k,player in enumerate(players):
            #avatar = p.avatars[indices[k]]
            for avatar in player.avatars:
                avatar.reset_for_new_game(self.game.nTurns)

                #while len(locations)>0:
                #    yh,xh = locations[-1]
                #    locations = locations[:-1]
                if len(regions)==0:
                    break

                yr,xr = regions[-1]
                regions = regions[:-1]
                yh = yr*5+2
                xh = xr*5+2
                #while len(regions)>0:
                #    yr,xr = regions[-1]

                    #ok = True
                    #for y,x in heads1+heads2:
                    #    d = self.manhattan_distance(x,y,xh,yh)
                    #    if d < avatar.size + 1:
                    #        ok = False
                    #        break
                    #if ok:
                    #    break

                rotation = self.game.rnd_fixed_seed.choice([0,90,180,270])

                if rotation==0:
                    jy = 1
                    jx = 0
                elif rotation ==90:
                    jy = 0
                    jx = -1
                elif rotation==180:
                    jy = -1
                    jx = 0
                else:
                    jy = 0
                    jx = 1

                if k==0:
                    j = 1
                else:
                    j = -1

                for z in range(avatar.size):
                    y = (yh+jy*z)%self.game.gridSize
                    x = (xh+jx*z)%self.game.gridSize
                    self.map[y,x] = (avatar.size-z)*j
                    avatar.body.append((y, x))

                avatar.head = (yh,xh)
                avatar.rotation = rotation
                if k==0:
                    heads1.append(avatar.head)
                else:
                    heads2.append(avatar.head)


        for yr in range(nRegions):
            for xr in range(nRegions):
                food_choices = []
                for j in range(0,5):
                    for i in range(0,5):
                        if self.map[yr*5+j,xr*5+i] == 0:
                            food_choices.append((yr*5+j, xr*5+i))
                I = self.game.rnd_fixed_seed.choice(np.arange(len(food_choices)))
                self.food.append(food_choices[I])


        #heads = heads1 + heads2
        #self.food = self.place_food(heads,food=[],N=self.game.nFoods)


        if self.showGame is not None:
            vis_map = self.vis_update(0,players,self.food)
            self.game.vis.show(vis_map, turn=0, titleStr=self.showGame)
        elif self.saveGame:
            self.vis_update(0,players,self.food)

        # Play the game over a number of turns
        for turn in range(self.game.nTurns):
            gameDone = True

            food_eaten = []

            # Create new agent map based on actions
            #new_agent_map = np.ndarray((self.gridSize,self.gridSize), dtype=object)

            # 000
            # 020
            # 010   0       a=-1  [0,-1]; a=0 [-1,0]; a=1 [0,1]         0 (-1)  270   0 (1)  90

            # 000
            # 120
            # 000   90      a=-1  [-1,0]; a=0 [0,1]; a=1 [1,0]          90 (-1) 0     90 (1) 180

            # 010
            # 020
            # 000   180     a=-1  [0,1]; a=0 [1,0]; a=1 [0,-1]          180 (-1)

            # 000
            # 021
            # 000   270     a=-1  [1,0]; a=0 [0,-1]; a=1 [-1,0]


            # Get actions of the agents
            # Reset avatars for a new game
            for k, player in enumerate(players):

                for avatar in player.avatars:

                    if avatar.dead:
                        continue

                    gameDone = False

                    # Percepts
                    percepts = np.zeros((avatar.player.fieldOfVision,avatar.player.fieldOfVision)).astype('int')

                    pBHalf = avatar.player.fieldOfVision // 2

                    if k==0:
                        jk=1
                    else:
                        jk=-1

                    # Add nearby agents to percepts
                    for i,io in enumerate(range(-pBHalf,pBHalf+1)):
                        for j,jo in enumerate(range(-pBHalf,pBHalf+1)):
                            y = (avatar.head[0] + io)
                            if y < 0:
                                y += self.game.gridSize
                            elif y >= self.game.gridSize:
                                y -= self.game.gridSize

                            x = (avatar.head[1] + jo)
                            if x < 0:
                                x += self.game.gridSize
                            elif x >= self.game.gridSize:
                                x -= self.game.gridSize

                            if self.map[y,x] != 0:
                                percepts[i,j] = jk*np.sign(self.map[y,x])

                            if (y,x) in self.food:
                                percepts[i,j] = 2

                            #percepts[i,j,1] = self.manhattan_distance(x,y,fx,fy)

                    #percepts[:,:,0] = np.sign(percepts[:,:,0])

                    #y,x = np.unravel_index(percepts[:, :, 1].argmin(), percepts[:, :, 1].shape)
                    #percepts[:,:,1] *= 0
                    #percepts[y,x,1] = 1

                    #if k==1:
                    #    percepts[:,:,0] *= -1

                    #percepts[percepts==0] = 0
                    #percepts[pBHalf,pBHalf,1] = avatar.rotation // 90

                    avatar.percepts[-1] = percepts

                    percepts = np.zeros((avatar.player.nFrames,avatar.player.fieldOfVision,avatar.player.fieldOfVision)).astype('int')

                    for f in range(avatar.player.nFrames):
                        percepts[f] = percepts_global_to_agent_frame_of_reference(avatar.percepts[f],avatar.rotation)

                    # Get action from agent
                    try:
                        action = avatar.action(turn+1,percepts)
                    except Exception as e:
                        if self.game.in_tournament:
                            #self.game_scores[p] = -self.nAgents
                            self.game.game_messages[k] = str(e)
                            self.game.game_play = False
                        else:
                            traceback.print_exc()
                            sys.exit(-1)

                    if not self.game.game_play:
                        break

                    y, x = actions_agent_to_global_shift(action,avatar.rotation)

                    for f in range(1,avatar.player.nFrames):
                        memory = avatar.percepts[f]
                        nY = np.shape(memory)[0]
                        nX = np.shape(memory)[1]
                        if y == 1:
                            for i in range(nY - 1):
                                memory[i, :] = memory[i + 1, :]
                            memory[-1, :] = 0
                        elif y == -1:
                            for i in range(1, nY):
                                memory[nY - i, :] = memory[nY - i - 1, :]
                            memory[0, :] = 0
                        elif x == 1:
                            for i in range(nX - 1):
                                memory[:, i] = memory[:, i + 1]
                            memory[:, -1] = 0
                        elif x == -1:
                            for i in range(1, nX):
                                memory[:, nX - i] = memory[:, nX - i - 1]
                            memory[:, 0] = 0
                        avatar.percepts[f-1] = memory


                    #x = avatar.position[0]
                    #y = avatar.position[1]

                    # 000
                    # 020
                    # 010   0       a=-1  [0,-1]; a=0 [-1,0]; a=1 [0,1]         0 (-1)  270   0 (1)  90

                    # 000
                    # 120
                    # 000   90      a=-1  [-1,0]; a=0 [0,1]; a=1 [1,0]          90 (-1) 0     90 (1) 180

                    # 010
                    # 020
                    # 000   180     a=-1  [0,1]; a=0 [1,0]; a=1 [0,-1]          180 (-1)

                    # 000
                    # 021
                    # 000   270     a=-1  [1,0]; a=0 [0,-1]; a=1 [-1,0]

                    # Action 0 is move left
                    if avatar.rotation == 0 or avatar.rotation==180:
                        if action == -1:
                           yd = 0
                           xd = -1
                        elif action == 0:
                           yd = -1
                           xd = 0
                        elif action == 1:
                           yd = 0
                           xd = 1
                    else:
                        if action == -1:
                           yd = -1
                           xd = 0
                        elif action == 0:
                           yd = 0
                           xd = 1
                        elif action == 1:
                           yd = 1
                           xd = 0

                    if avatar.rotation >= 180:
                        xd *= -1
                        yd *= -1

                    avatar.rotation += action*90
                    if avatar.rotation < 0:
                        avatar.rotation += 360
                    avatar.rotation %= 360

                    y, x = avatar.head

                    y += yd
                    x += xd

                    if y < 0:
                        y += self.game.gridSize
                    if x < 0:
                        x += self.game.gridSize

                    y %= self.game.gridSize
                    x %= self.game.gridSize

                    avatar.head = (y,x)

                    if (y,x) in self.food:
                        avatar.size += 1
                        food_eaten += [(y,x)]
                    else:
                        body = avatar.body
                        avatar.body = []
                        for y,x in body:
                            if self.map[y,x] > 0:
                                self.map[y,x] -= 1
                            elif self.map[y,x] < 0:
                                self.map[y,x] += 1

                            if self.map[y,x] != 0:
                                avatar.body.append((y,x))

            if not self.game.game_play:
                return None

            all_avatars = []
            for k, player in enumerate(players):
                for avatar in player.avatars:
                    if not avatar.hit:
                        all_avatars += [avatar]

            heads1 = []
            heads2 = []
            for i in range(len(all_avatars)):
                if all_avatars[i].dead:
                    continue

                for j in range(i+1,len(all_avatars)):

                    if all_avatars[j].dead:
                        continue

                    if all_avatars[i].head == all_avatars[j].head:
                        all_avatars[i].hit = True
                        all_avatars[j].hit = True

                if all_avatars[i].hit:
                    continue

                y,x = all_avatars[i].head

                if all_avatars[i].player.player == 0:
                    j = 1
                else:
                    j = -1

                if self.map[y,x] != 0:
                    all_avatars[i].hit = True
                else:
                    if j==1:
                        heads1.append(all_avatars[i].head)
                    else:
                        heads2.append(all_avatars[i].head)

            if gameDone:
                break

            # Reset avatars for a new game
            heads1 = []
            heads2 = []

            for k, player in enumerate(players):
                for avatar in player.avatars:
                    if avatar.hit:
                        continue

                    y,x = avatar.head

                    if k==0:
                       j=1
                       heads1.append(avatar.head)
                    else:
                       j=-1
                       heads2.append(avatar.head)

                    self.map[y,x] = avatar.size*j
                    avatar.body.append((y, x))
                    avatar.update_size_stats(turn)

            for (y,x) in food_eaten:
                try:
                    self.food.remove((y,x))
                except:
                    pass

            if len(self.food) < self.game.nFoods:
                self.food += self.place_food(heads1+heads2, self.food, N=self.game.nFoods - len(self.food))

            if self.showGame is not None:
                i = 0

                if self.saveGame:
                    i = turn+1
                vis_map = self.vis_update(i,players,self.food)
                self.game.vis.show(vis_map, turn=turn+1, titleStr=self.showGame)
                #self.game.vis.show(self.map, self.food, heads1+colheads1, heads2+colheads2, turn=self.turn+1, titleStr=self.showGame, collisions=collisions)
            elif self.saveGame:
                self.vis_update(turn+1,players,self.food)
            #needUpdate = False
            for k, player in enumerate(players):
                for avatar in player.avatars:
                    if avatar.dead:
                        continue

                    if avatar.hit:
                        for y, x in avatar.body:
                            self.map[y, x] = 0
                        avatar.body = []
                        avatar.dead = True

            self.turn = turn

        if self.saveGame:
            savePath = "saved"
            if not os.path.isdir(savePath):
                os.makedirs(savePath, exist_ok=True)

            now = datetime.now()
            # Month abbreviation, day and year
            saveStr = now.strftime("%b-%d-%Y-%H-%M-%S")
            if len(players) == 1:
                saveStr += "-%s" % (players[0].name)
                name2 = None
            else:
                saveStr += "-%s-vs-%s" % (players[0].name, players[1].name)
                name2 = players[1].name

            saveStr += ".pickle.gz"

            saveFile = os.path.join(savePath, saveStr)

            self.game.game_saves.append(saveFile)

            with gzip.open(saveFile, 'w') as f:
                pickle.dump((players[0].name, name2, self.vis_map), f)

        scores = []
        for k, player in enumerate(players):
            scores.append(0)
            for avatar in player.avatars:
                #if avatar.hit:
                #    continue

                scores[-1] += np.max(avatar.sizes)

        if len(scores) == 1:
            return scores[0]
        else:
            return scores[0]-scores[1]



# Class that runs the entire game
class SnakeGame:

    # Initialises the game
    def __init__(self, gridSize, nTurns, nFoods, nAgents, saveFinalGames=True,seed=None, tournament=False):

        self.rnd = np.random.RandomState()
        self.gridSize = gridSize
        self.nTurns = nTurns
        self.nActions = 3
        self.game_play = True
        self.in_tournament = tournament
        self.nFoods = nFoods
        self.nAgents = nAgents
        self.saveFinalGames = saveFinalGames
        self.rnd_fixed_seed = np.random.RandomState(seed)#game_rnd_seed)

    # Update the stats for the visualiser
    def update_vis_agents(self,players,creature_state):
        for p in range(2):
            for n in range(self.nAgents):
                i = n + p * self.nAgents
                avatar = players[p].avatars[n]

                creature_state[i, 0] = avatar.position[0]
                creature_state[i, 1] = avatar.position[1]
                creature_state[i, 2] = avatar.alive
                creature_state[i, 3] = p
                creature_state[i, 4] = avatar.size

    # Run the game
    def run(self,player1File, player2File,visResolution=(720,480), visSpeed='normal',savePath="saved",
            trainers=[("random_agent.py","random")]):

        self.players = list()

        self.game_messages = ['', '']
        self.game_scores = [0, 0]
        self.game_saves = list()

        # Load player 1
        if player1File is not None:
            try:
                self.players.append(Player(self,len(self.players),player1File))
            except Exception as e:
                if self.in_tournament:
                    self.players.append(Player(self,0,player1File,self.nAgents,emptyMode=True))
                    self.game_messages[0] = "Error! Failed to create a player with the provided code"
                else:
                    print('Error! ' + str(e))
                    sys.exit(-1)

            if not self.players[0].ready:
                self.game_scores[0] = -self.nAgents
                if self.players[0].errorMsg != "":
                    self.game_messages[0] = self.players[0].errorMsg

                self.game_play = False
            elif not self.players[0].trained:
                self.players[0] = self.train(self.players[0],visResolution,visSpeed,savePath,trainers)
                if self.players[0] is None:
                    self.game_scores[0] = -self.nAgents
                    self.game_play = False

            # Load player 2
        if player2File is not None:
            try:
                self.players.append(Player(self,len(self.players),player2File))
            except Exception as e:
                if self.in_tournament:
                    self.players.append(Player(self,1,player2File,self.nAgents,emptyMode=True,trainers=trainers))
                    self.game_messages[1] = "Error! Failed to create a player with the provided MyAgent.py code"
                else:
                    print('Error! ' + str(e))
                    sys.exit(-1)

            if not self.players[1].ready:
                self.game_scores[1] = -self.nAgents
                if self.players[1].errorMsg != "":
                    self.game_messages[1] = self.players[0].errorMsg

                self.game_play = False
            elif not self.players[1].trained:
                self.players[1] = self.train(self.players[1],visResolution,visSpeed,savePath)
                if self.players[1] is None:
                    self.game_scores[1] = -self.nAgents
                    self.game_play = False

        if not self.game_play:
            return



        shows = [1,2,3,4,5]

        if self.saveFinalGames:
            saves = shows
        else:
            saves = []

        self.play(self.players,shows,saves,visResolution,visSpeed,savePath)


    def train(self,player,visResolution=(720,480), visSpeed='normal',savePath="saved",
              trainers=[("random","randomPlayer"), ("hunter","hunterPlayer")]):

        playerNumber = player.player
        trainingSchedule = player.trainingSchedule

        tot_gens = 0
        for op, gens in trainingSchedule:
            tot_gens += gens


        if tot_gens > maxTrainingEpochs:
            tot_gens = maxTrainingEpochs

        gens_count = 0

        for op, gens in trainingSchedule:

            if gens_count + gens > tot_gens:
                gens = tot_gens - gens_count

            if gens==0:
                break

            if op == 'random':
                opFile = 'random_agent.py'
            elif op == 'self':
                opFile = None
            else:
                opFile = op

            opponentNumber = (player.player + 1) % 2

            # Load opponent
            players = [player]

            if op == 'self':
                #opponent = player
                sys.stdout.write("\nTraining %s against self for %d generations...\n" % (player.name, gens))
                #players.append(opponent)
            elif op is not None:
                try:
                    opponent = Player(self, opponentNumber, playerFile=opFile)
                except Exception as e:
                    if self.in_tournament:
                        self.game_messages[playerNumber] = "Error! Failed to create opponent '%s' in training" % op
                        return None
                    else:
                        print('Error! ' + str(e))
                        sys.exit(-1)

                if not opponent.ready:
                    self.game_scores[player.player] = -self.nAgents
                    if player.errorMsg != "":
                        self.game_messages[player.player] = player.errorMsg
                    return None

                sys.stdout.write("\nTraining %s against %s for %d generations...\n" % (player.name, op, gens))
                players.append(opponent)
            else:
                sys.stdout.write("\nTraining %s in single-player mode for %d generations...\n" % (player.name, gens))
            sys.stdout.write("------")


            self.play(players,[], [], visResolution, visSpeed, savePath, trainGames=(gens,gens_count,tot_gens))


            #if opFile == player.playerFile:
            #    if self.game_scores[player.player] > self.game_scores[opponentNumber]:
            #        save_player = player
            #    else:
            #        save_player = opponent
            #else:
            #    save_player = player


            if not self.game_play:
                return None

            gens_count += gens
            if gens_count >= tot_gens:
                break

            #try:
            #    save_player.save_trained(train_temp)
            #except Exception as e:
            #    if self.in_tournament:
            #        self.game_messages[playerNumber] = "Error! Failed to save training results."
            #        return None
            #    else:
            #        traceback.print_exc()
            #        sys.exit(-1)

        try:
            player.save_trained()
        except Exception as e:
            if self.in_tournament:
                self.game_messages[playerNumber] = "Error! Failed to save training results."
                return None
            else:
                traceback.print_exc()
                sys.exit(-1)

        return player

    def play(self,players, show_games, save_games, visResolution=(720,480), visSpeed='normal',savePath="saved",trainGames=None):

        if len(show_games)>0 and not self.in_tournament:
            import vis_pygame as vis
            playerStrings = []
            for p in players:
                playerStrings += [p.name]

            self.vis = vis.visualiser(speed=visSpeed,playerStrings=playerStrings,
                                  resolution=visResolution)

        if trainGames is None:
            nRuns = len(show_games)
        else:
            gens, gens_count, tot_gens = trainGames
            nRuns = gens

        # Play the game a number of times
        for game in range(1, nRuns + 1):
            if trainGames is None:
                if len(players)==1:
                    if game==1:
                        sys.stdout.write("\nTournament (single-player mode) %s!" % (players[0].name))
                else:
                    if game==1:
                        sys.stdout.write("\nTournament %s vs. %s!!!" % (players[0].name, players[1].name))
                sys.stdout.write("\n  Game %d..." % (game))

            else:
                sys.stdout.write("\n  Gen %3d/%d..." % (game+gens_count, tot_gens))

            if trainGames is None and game in show_games and not self.in_tournament:
                showGame = "Snakes on a plane!"
            else:
                showGame = None

            if trainGames is None and game in save_games:
                saveGame = True
            else:
                saveGame = False

            sgame = SnakePlay(self,showGame,saveGame)
            gameResult = sgame.play(players)

            if gameResult is None:
                if self.in_tournament:
                    return
                else:
                    print("Error! No game result!")
                    traceback.print_exc()
                    sys.exit(-1)

            if trainGames is None:
                score = gameResult
                if len(players) > 1:
                    if score>0:
                        sys.stdout.write("won by %s (orange) with" % (players[0].name))
                    elif score<0:
                        sys.stdout.write("won by %s (purlpe) with" % (players[1].name))
                        score *= -1
                    else:
                        sys.stdout.write("tied with")


                sys.stdout.write(" score=%02d after %d turn" % (np.abs(score),sgame.turn+1))
                if sgame.turn!=0:
                    sys.stdout.write("s")
                sys.stdout.write(".")
                sys.stdout.flush()
            else:
                #for avatar in players[0].avatars:
                #    avatar.average_gen_stats()

                try:
                    if game + gens_count < tot_gens:
                        players[0].new_generation_agents(game+gens_count)
                    else:
                        players[0].evaluate_fitness()
                except Exception as e:
                    if self.in_tournament:
                        self.game_scores[p] = -self.nAgents
                        self.game_messages[p] = str(e)
                        self.game_play = False
                    else:
                        traceback.print_exc()
                        sys.exit(-1)

                #vis_map = sgame.vis_map[:,:,:sgame.turn + 2]
                #vis_fh = sgame.vis_fh[:, :sgame.turn + 2]


    # Play visualisation of a saved game
    @staticmethod
    def load(loadGame,visResolution=(720,480), visSpeed='normal'):
        import vis_pygame as vis

        if not os.path.isfile(loadGame):
            print("Error! Saved game file '%s' not found." % loadGame)
            sys.exit(-1)

        # Open the game file and read data
        try:
            with gzip.open(loadGame) as f:
              (player1Name,player2Name,vis_map) = pickle.load(f)
        except:
            print("Error! Failed to load %s." % loadGame)

        playerStrings = [player1Name]
        if player2Name is not None:
            playerStrings += [player2Name]

        # Create an instance of visualiser
        v = vis.visualiser(speed=visSpeed, playerStrings=playerStrings,resolution=visResolution)

        # Show visualisation
        titleStr = "Snakes on a plane! %s" % os.path.basename(loadGame)
        for t in range(vis_map.shape[3]):
            v.show(vis_map[:,:,:,t], turn=t, titleStr=titleStr)


def main(argv):
    # Load the defaults
    from settings import game_settings

    # Check of arguments from command line
    #try:
    #    opts, args = getopt.getopt(argv, "p:r:v:s:f:l:g:",["players=", "res=", "vis=", "save=", "fast=", "load=", "games="])
    #except getopt.GetoptError:
    #    print("Error! Invalid argument.")
    #    sys.exit(2)

    # Process command line arguments
    #loadGame = None
    #for opt, arg in opts:
    #    if opt in ("-p", "--players"):
    #        players = arg.split(',')
    #        if len(players) != 2:
    #           print("Error! The -p/players= argument must be followed with two comma separated file name (no spaces).")
    #           sys.exit(-1)

    #        game_settings['player1'] = players[0]
    #        game_settings['player2'] = players[1]

    #    elif opt in ("-r", "--res"):
    #        res = arg.split('x')
    #        if len(res) != 2:
    #           print("Error! The -r/res= argument must be followed with <width>x<height> specifiction of resolution (no spaces).")
    #           sys.exit(-1)

    #        game_settings['visResolution'] = (int(res[0]), int(res[1]))
    #    elif opt in ("-v", "--vis"):
    #        if arg[0] == '[' and arg[-1] != ']':
    #            print(
    #                "Error! The -v/vis= argument must be followed with [...] giving the list of games to visualise (no spaces).")
    #            sys.exit(-1)
    #        game_settings['show_games'] = list()
    #        if len(arg)>2:
    #            arg = arg[1:-1]
    #            games = arg.split(',')
    #            for g in games:
    #                game_settings['show_games'].append(int(g))

    #    elif opt in ("-s", "--save"):
    #        if arg[0] == '[' and arg[-1] != ']':
    #            print(
    #                "Error! The -s/save= argument must be followed with [...] giving the list of games to save (no spaces).")
    #            sys.exit(-1)
    #        game_settings['save_games'] = list()
    #        if len(arg)>2:
    #            arg = arg[1:-1]
    #            games = arg.split(',')
    #            for g in games:
    #                game_settings['save_games'].append(int(g))
    #    elif opt in ("-f", "--fast"):
    #        game_settings['visSpeed'] = arg

    #    elif opt in ("-l", "--load"):
    #        loadGame = arg

    #    elif opt in ("-g", "--games"):
    #        game_settings['nGames'] = int(arg)

    if game_settings['gridSize'] < 5:
        print("Error! Invalid setting '%d' for gridSize.  Must be at least 5" % game_settings['gridSize'])
        sys.exit(-1)

    gridRegions = game_settings['gridSize'] // 5
    gridRegions = gridRegions**2

    if gridRegions < game_settings['nSnakes']:
        print("Error! Invalid setup with gridSize=%d and nSnakes=%d settings." %  (game_settings['gridSize'],  game_settings['nSnakes']))
        minGridSize = int(np.ceil(np.sqrt(game_settings['nSnakes']*2)))*5
        maxSnakes = gridRegions//2
        print("Either increase gridSize to %d or reduce nSnakes to %d." %  (minGridSize,  maxSnakes))

        sys.exit(-1)




    if game_settings['visSpeed'] != 'normal' and game_settings['visSpeed'] != 'fast' and game_settings['visSpeed'] != 'slow':
        print("Error! Invalid setting '%s' for visualisation speed.  Valid choices are 'slow','normal',fast'" % game_settings['visSpeed'])
        sys.exit(-1)

    if not 'player1' in game_settings and not 'player2' in game_settings:
        print("Error! At least one player agent must be specified in settings.py.")
        sys.exit(-1)
    elif not 'player1' in game_settings:
        game_settings['player1'] = game_settings['player2']
        game_settings['player2'] = None
    elif not 'player2' in game_settings:
        game_settings['player2'] = None



    # Create a new game and run it
    g = SnakeGame(gridSize=game_settings['gridSize'],
                nTurns=game_settings['nTurns'],nFoods=game_settings['nSnakes'],
                nAgents=game_settings['nSnakes'],
                saveFinalGames=game_settings['saveFinalGames'],
                seed=game_settings['seed'])

    g.run(game_settings['player1'],
          game_settings['player2'],
          visResolution=game_settings['visResolution'],
           visSpeed=game_settings['visSpeed'])

    #else:
        # Load a previously saved game
    #    Game.load(loadGame,visResolution=game_settings['visResolution'],
    #           visSpeed=game_settings['visSpeed'])



if __name__ == "__main__":
   main(sys.argv[1:])

