from chess_board import chess_board
import numpy as np
import random

#important variables
initPop = 1000
numGenerations = 100000
initQueens = []

#Initialise the board
board = chess_board()

#Initialise a population with random and valid chromosomes.
for x in range(initPop):
    position = np.random.randint(0, 64)
    currQueen = []
    currQueen.append(position)
    y = 1
    while y < 8:
        position = np.random.randint(0,64)
        isEqual = 0
        #check if position is already taken
        for z in range(len(currQueen)):
            if position == currQueen[z]:
                isEqual = 1
                break
        #either add or repeat process
        if isEqual == 0:
            currQueen.append(position)
            y += 1

    #add final current state to list of initial states
    initQueens.append(currQueen)

allBoards = initQueens

for x in range(numGenerations):
    fitnessLevels = []
    fitnessTotal = 0
    best = allBoards[0]
    for y in range(len(allBoards)):
        f = board.nonattacking_pairs(allBoards[y])
        fitnessLevels.append(f)
        fitnessTotal += f
        if f > board.nonattacking_pairs(best):
            best = allBoards[y]

    board.show_state(best)

    if board.nonattacking_pairs(best) == 28:
        print(best)
        print("puzzle solved")
        exit(0)

    newPop = []
    '''
    #normalize fitness levels
    for q in range(len(fitnessLevels)):
        fitnessLevels[q] = fitnessLevels[q] / fitnessTotal
    '''
    #create children
    for z in range(initPop):

        possibleChildren = []
        possibleFitnesses = []
        newchild = allBoards[np.random.randint(0, len(allBoards))]
        possibleChildren.append(newchild)
        possibleFitnesses.append(board.nonattacking_pairs(newchild))

        p1 = 0
        p2 = 0

        n = np.random.randint(1, 10)

        #create a random subset list of possible parents
        for l in range(n):
            newchild = allBoards[np.random.randint(0, len(allBoards))]
            alreadyin = 0
            for k in range(len(possibleChildren)):
                if newchild == possibleChildren[k]:
                    alreadyin = 1
            if alreadyin == 1:
                l -= 1
            else:
                possibleChildren.append(newchild)
                possibleFitnesses.append(board.nonattacking_pairs(newchild))

        i1 = -1
        m1 = -1
        i2 = -1
        m2 = -2

        #get indices of the 2 max fitnesses in the random subset
        for p in range(len(possibleChildren)):
            if possibleFitnesses[p] > m1:
                m1 = possibleFitnesses[p]
                i1 = p
            elif possibleFitnesses[p] > m2:
                m2 = possibleFitnesses[p]
                i2 = p

        p1 = possibleChildren[i1]
        p2 = possibleChildren[i2]

        newKid = []
        #uniform distribution state mixing
        for r in range(len(p1)):
            next1 = np.random.randint(0, 2)
            if next1 == 0:
                newKid.append(p1[r])
            else:
                newKid.append(p2[r])

        newPop.append(newKid)

    allBoards = newPop

