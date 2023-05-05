from eightpuzzle import eightpuzzle
import time

# A class called 'node'
class node:
    # __init__ is a reserved identifier, used to indicate a constructor for the class
    def __init__(self, s, parent=None, g=0, h=0, action=None):
        self.s = s              #state
        self.parent = parent    #Reference to parent
        self.g = g              #Path cost g(n)
        self.f = g + h          #A* Evaluation function
        self.action = action    #action taken to get from parent state to this nodes state

def sameRow(j, i):
    if (j < 3 & i < 3):
        return 1
    if (j > 2 & j < 6 & i > 2 & i < 6):
        return 1
    if (j > 5 & i > 5):
        return 1
    return 0

def sameCol(j, i):
    if (j % 3 == i % 3):
        return 1
    else:
        return 0

# computes and returns the number of misplaced tiles
# added to the number of required steps for each tile
def heuristic(s, goal):
    h = 0
    j = 0
    k = 0
    for i in range(len(s)):
        if s[i] != goal[i]:
            j = i
            k = s[i]

            if (sameRow(k,j) == 1):
                j = max(k,goal[i]) - min(k,goal[i])
            else:
                if ((max(6,goal[i]) - min(6,goal[i])) > 4):
                     j = max(k,goal[i]) - min(k,goal[i]) + 2
                else:
                    j = max(k, goal[i]) - min(k, goal[i])
            h += 1 + j
    return h

#initializes a timer before the search is performed
start_time = time.time()

puzzle = eightpuzzle(mode='medium')

#retrieve the initial puzzle state
init_state = puzzle.reset()

#puzzle.show(s=init_state)

#retreive the goal state for comparison
goal_state = puzzle.goal()

#initialize root node of the A* search strtucture
root_node = node(s=init_state, parent=None, g=0, h=heuristic(s=init_state, goal=goal_state))

#add root node to the fringe (open list)
fringe = [root_node]

mini = root_node

solution_node = None

#Retrieves current state from the list (index=0)
#and analyzes the current state, expanding all nodes
#which correspond to available actions of the current nodes state
#ie. performs the A* search
while len(fringe) > 0:
    current_node = fringe.pop(0)
    current_state = current_node.s
    if current_state == goal_state:
        solution_node = current_node
        break
    else:
        available_actions = puzzle.actions(s=current_state)
        for a in available_actions:
            next_state = puzzle.step(s=current_state, a=a)
            new_node = node(s=next_state, parent=current_node, g=current_node.g+1,
                            h=heuristic(s=next_state, goal=goal_state), action=a)
            if mini.f > new_node.f:
                mini = new_node
                fringe.insert(0, new_node)
            else :
                fringe.append(new_node)

        fringe.sort(key=lambda x: x.f)

# Determines whether solution is found
#if found, path is traced back to root in 'action_sequence' variable
if solution_node is None:
    print("Solution NOT found!!!")
else:
    elapsed_time = time.time() - start_time
    print("Elapsed time: %.8f seconds" % elapsed_time)
    action_sequence = []
    next_node = solution_node
    while True:
        if next_node == root_node:
            break
        action_sequence.append(next_node.action)
        next_node = next_node.parent
    action_sequence.reverse()

    print("Number of moves: %d" % solution_node.g)
    puzzle.show(s=init_state, a=action_sequence)




