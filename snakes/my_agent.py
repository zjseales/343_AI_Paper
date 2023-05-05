__author__ = "Zac Seales - 6687905"
__organization__ = "COSC343/AIML402, University of Otago"
__email__ = "seaza886@student.otago.ac.nz"

import numpy as np

agentName = "Dandelion"
perceptFieldOfVision = 3  # Choose either 3,5,7 or 9
perceptFrames = 1  # Choose either 1,2,3 or 4

# number of training generations against self and random
# can not be > 500 total training generations
trainingSchedule = [("self", 300), ("random", 200)]

# to test game without training
# trainingSchedule = None

# This is the class for your snake/agent
class Snake:
    '''
        Constructor: Initializes this agent's global values with the given arguments.
        Also creates a 'chromosome' matrix of random weight values and a bias values
        for each of the possible output actions. This chromosome will represent the
        parameters of the agents multi-class perceptron model. A genetic algorithm
        with optimization techniques will be used to 'evolve' the chromosome with (hopefully)
        better parameters - decided by a fitness (or loss) function.

        :param
            nPercepts - the number of percepts that the model receives
                        (defined by perceptFieldOfVision).
            actions   - A list of integers that defines all possible actions that the Agent can output.
    '''

    def __init__(self, nPercepts, actions):
        # initialize weights and bias values as random floats between 0 and 1
        self.chromosome = np.random.rand(len(actions), nPercepts + 1)

        # The number of percepts (Size of the field-of-vision squared)
        self.nPercepts = nPercepts
        # valid actions (-1, 0, or 1)
        self.actions = actions
        # all actions that were performed this turn (prevents spiraling)
        self.allActions = []
        # all percepts received this game (to prevent repetition/spiraling)
        self.allPercepts = []

    ''' 
        The Agent Function that governs the actions of this agent dependent on the percepts argument.
        Calculates a hypothesis value for each possible action and performs the action with 
        the largest hypothesis value.
    
        :param
            percepts - A matrix that defines the current state of the game within the snakes field-of-view.
        :return
            action - The action that the snake decides to make this turn.
    '''

    def AgentFunction(self, percepts):
        # convert to matrix because axis has size 1 bug occurs?
        percepts = np.asmatrix(percepts)

        listPercepts = []

        # iterate percepts and convert to a list.
        # inefficient but this makes the math easier.
        for a in range(len(percepts)):
            for b in range(len(percepts)):
                listPercepts.append(percepts[a, b])

        # Each action must have a perceptron model hypothesis value.
        hypotheses = []
        for t in range(len(self.actions)):
            hypotheses.append(calculateH(listPercepts, self.chromosome[t, :]))

        indexOfActionTaken = hypotheses.index(np.max(hypotheses))
        # record the action that is about to be performed
        self.allActions.append(self.actions[indexOfActionTaken])
        # record the current percepts
        self.allPercepts += listPercepts

        # return action with max hypothesis value
        return self.actions[indexOfActionTaken]
''' 
    Calculates the fitness of each snake in the population argument and returns a list of all fitness values.
        
    :param
        population - The population of snakes having their fitnesses evaluated.
    :return
        fitness - A list of all the fitness values from the population.  
'''
def evalFitness(population):
    # add incentives and consequences in the hopes that the GA will tend toward better results.
    noGrowthPenalty = 5
    lengthReward = 3

    N = len(population)

    # Fitness initialiser for all agents
    fitness = np.zeros((N))

    # This loop iterates over your agents in the old population - the purpose of this boiler plate
    # code is to demonstrate how to fetch information from the old_population in order
    # to score fitness of each agent
    for n, snake in enumerate(population):

        maxSize = np.max(snake.sizes)
        turnsAlive = np.sum(snake.sizes > 0)
        maxTurns = len(snake.sizes)

        fitness[n] = maxSize + turnsAlive / maxTurns

        # Add extra incentive to not dying
        if maxTurns == turnsAlive:
            fitness[n] += 1

        longest_run = 0
        current_run = 0
        max_percept_repeat = 0
        current_perc = 0

        # iterate all actions performed this game and penalizes
        # repetition of turning in the same direction
        for b in range(len(snake.allActions) - 1):
            # increase run size if this action and next action is the same 'turning' action
            if snake.allActions[b] == 1 | -1:
                if snake.allActions[b] == snake.allActions[b+1]:
                    current_run += 1
            elif current_run > longest_run:
                longest_run = current_run
                current_run = 0

            # analyze percept patterns up to a degree of 2
            if snake.allPercepts[b] == snake.allPercepts[b+1]:
                current_perc += 1
            elif b != len(snake.allActions)-2:
                if snake.allPercepts[b] == snake.allPercepts[b+2]:
                    current_perc += 1

            if current_perc > max_percept_repeat:
                max_percept_repeat = current_perc
                current_perc = 0
        # punish repetitive percepts
        for y in range(max_percept_repeat):
            fitness[n] -= 0.5 * y

        # Punishes repetitive turning
        if longest_run > 4:
          fitness[n] /= longest_run

        # penalizes no growth and incentivizes growth
        u = np.min(snake.sizes)
        if maxSize == u:
            fitness[n] -= noGrowthPenalty
        else:
            while (u + 1) < maxSize:
                fitness[n] += lengthReward * u
                u += 1

        # punishes repetitive left and right actions
        avg_run = np.mean(snake.allActions)
        if avg_run < -2:
            fitness[n] -= np.abs(avg_run)
        elif avg_run > 2:
            fitness[n] -= np.abs(avg_run)
        else:
            fitness[n] += (1 - avg_run) * 5

    return fitness

''' 
    Calculates the 'perceptron-model hypothesis value' for the given arguments.

    :param 
        percepts - A list representing the current percepts.
        chromosome - A list of a given actions weight and bias values. (A row from the self.chromosome matrix)
    :return
        h - The hypothesis value calculated from the input arguments.
'''
def calculateH(percepts, chromosome):
    h = 0
    # add percepts multiplied by chromosome weights
    for i in range(len(percepts)):
        h += percepts[i] * chromosome[i]
    # add the bias and return
    h += chromosome[len(chromosome) - 1]
    return h


'''
    Uses Genetic Algorithm parent crossover techniques to create a new population of chromosomes
    which will govern the agent behaviour for the next game. The parent chromosomes 
    are given by the snakes which played the previous game.

    :param 
        old_population - The population of "Snake" agents from the previous game.
    :return
        new_population - A tuple containing the new population of snake chromosome as well as 
                         the average fitness level of the previous population.
'''
def newGeneration(old_population):
    # This function should return a tuple consisting of:
    # - a list of the new_population of snakes that is of the same length as the old_population,
    # - the average fitness of the old population

    # The population size for the GA algorithm
    popSize = len(old_population)

    nPercepts = old_population[0].nPercepts
    actions = old_population[0].actions

    fitness = evalFitness(old_population)

    # Set up a tuple list of parent chromosomes and their fitness levels
    chromosomeList = list()
    for n, snake in enumerate(old_population):
        chromosomeList.append((snake.chromosome, fitness[n]))

    # sorts the list by fitness level (simplifies parent selection)
    chromosomeList.sort(key=lambda pair: pair[1])

    # Create new population list...
    new_population = list()
    for n in range(popSize):

        # Create new snake
        new_snake = Snake(nPercepts, actions)

        # Implement elitism, always keep top 5 percent of fittest individuals
        if n < (popSize / 10):
            chr, fit = chromosomeList[len(chromosomeList) - (n + 1)]
            new_snake.chromosome = chr
        else:
            # Parent Selection:
            #   Tournament Selection, includes unfittest snakes if population size >= 40
            subsetSize = np.random.randint(len(chromosomeList) / 10, len(chromosomeList) / 4)
            startIndex = np.random.randint(0, len(chromosomeList) - subsetSize - 1)

            # Retrieve a subset of parents (parents are already sorted, so we can directly
            # pick the last two that get added to the subset).
            parent1 = chromosomeList[startIndex + subsetSize]
            parent2 = chromosomeList[startIndex + subsetSize - 1]

            chr1, fit1 = parent1
            chr2, fit2 = parent2

            # uniform crossover
            for p in range(len(new_snake.actions)):
                for q in range(new_snake.nPercepts + 1):
                    x = np.random.randint(1, 500)
                    # mutation
                    if x == np.random.randint(1, 500):
                        new_snake.chromosome[p, q] = np.random.rand()
                    elif q % 2 == 0:
                        new_snake.chromosome[p, q] = chr1[p, q]
                    else:
                        new_snake.chromosome[p, q] = chr2[p, q]

        # Add the new snake to the new population
        new_population.append(new_snake)

    # computes the average fitness and returns it along with the new population
    avg_fitness = np.mean(fitness)
    # saves average fitness values to a file, so they can be displayed graphically
    with open("fitnesses.txt", "a") as file:
       file.writelines("%.3f \n" % avg_fitness)
    file.close()

    return (new_population, avg_fitness)
