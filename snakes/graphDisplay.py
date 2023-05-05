import numpy as np
import matplotlib.pyplot as plt

fitnesses = []
generations = []
currGen = 0

with open("fitnesses.txt", "r") as file:
    for number in file:
        currGen += 1
        generations.append(currGen)
        fitnesses.append(float(number))

plt.scatter(generations, fitnesses, marker='x', color='red', label="Scatter")

plt.xlabel('Generation Number')
plt.ylabel('Average Fitness')

plt.legend()

fitnesses = np.array(fitnesses)
generations = np.array(generations)

a, b, c, d = np.polyfit(generations, fitnesses, 3)

p, q = np.polyfit(generations, fitnesses, 1)

#plot the 3rd degree polynomial model
#plt.plot(generations, (a * generations ** 3) + (b * generations ** 2)
#         + (c * generations) + d, color='blue', linewidth=4)

# plot the linear polynomial
plt.plot(generations, (p * generations) + q, color='green', linewidth =4)

plt.show()