__author__ = "Zac Seales - 6687905"
__organization__ = "COSC343/AIML402, University of Otago"
__email__ = "seaza886@student.otago.ac.nz"

import numpy as np
import re
import helper

class WordleAgent():
   """
       A class that encapsulates the code dictating the
       behaviour of the Wordle playing agent

       ...

       Attributes
       ----------
       dictionary : list
           a list of valid words for the game
       letter : list
           a list containing valid characters in the game
       word_length : int
           the number of letters per guess word
       num_guesses : int
           the max. number of guesses per game
       mode: str
           indicates whether the game is played in 'easy' or 'hard' mode

       Methods
       -------
       AgentFunction(percepts)
           Returns the next word guess given state of the game in percepts
   """

   # letters that must be in the next guess
   yellows = ""
   # letters that can not be in the next guess
   greys = ""
   # the regex pattern of the next guess
   patt = ""
   # the values not allowed for each character in the word
   # (indi[0] = unallowed letters for index[0] of the word)
   indi = []
   # the list of possible solutions
   possibilities = []
   # the heuristic values of each word in the possibilities list
   heuristic = []

   def __init__(self, dictionary, letters, word_length, num_guesses, mode):
      """
      :param dictionary: a list of valid words for the game
      :param letters: a list containing valid characters in the game
      :param word_length: the number of letters per guess word
      :param num_guesses: the max. number of guesses per game
      :param mode: indicates whether the game is played in 'easy' or 'hard' mode
      """
      self.dictionary = dictionary
      self.letters = letters
      self.word_length = word_length
      self.num_guesses = num_guesses
      self.mode = mode

   ''' Global variables to make life easier (these reset each new game)
   Parametere:
            yellows = letters that are in the answer somewhere
            greys = letters that are not in the answer
            patt = the regex pattern of the next guess
            indi = unknown characters for each individual string position
            possibilities = the list of possible_solutions
   '''
   def initCheatCodes(self):
      self.yellows = ""
      self.greys = ""
      self.patt = "....."
      self.indi = ["", "", "", "", ""]
      self.possibilities = []
      self.heuristic = []

   def setUpHeuristic(self):
      #initialize table of character frequencies
      # taken from https://www.sttmedia.com/characterfrequency-english
      freq = [8.34, 1.54, 2.73, 4.14, 12.60, 2.03, 1.92, 6.11, 6.71, 0.23, 0.87, 4.24, 2.53, \
              6.80, 7.70, 1.66, 0.09, 5.68, 6.11, 9.37, 2.85, 1.06, 2.34, 0.20, 2.04, 0.06]
      # loop solutions and calculate heuristic values for each
      for i in range(len(self.possibilities)):
         result = 0
         #convert each word to indices
         letterVals = helper.word_to_letter_indices(self.possibilities[i], self.letters)
         for j in range(self.word_length):
            result += freq[letterVals[j]]

         self.heuristic.append(result)

   ''' Iterates the entire dictionary parameter and returns a list of all possible_solutions
       given the specified regex pattern. Also compares global yellows and unallowed letters.
       Parameters:      
               dictionary = the list of all possible solutions.
               pattern = the regex pattern defining possible solutions
               possible_solutions = the list that will be returned after analysis
   '''
   def iterMethod(self, dictionary, pattern, possible_solutions):
      nextGuessIndex = 0
      tempH = []

      #finds all possible solutions from iterating dictionary
      while nextGuessIndex < len(dictionary):
         addIt = 0 # change to 1 if guess is added to possible_solutions lsit

         # make a guess and compare
         nextGuess = dictionary[nextGuessIndex]

         # if nextGuess matches pattern, do additional checks
         if re.match(pattern, nextGuess):
            #only analyze words that do not contain global unallowed letters
            if not re.search("[%s]" % self.greys, nextGuess):
               addCheck = 0
               # check each letter in the guess against unallowed letters for each position
               for e in range(self.word_length):
                  if re.search("[%s]" % nextGuess[e], self.indi[e]):
                     addCheck = 1
                     break
               #only continue analysis if previous checks passed
               if addCheck == 0:
                  # if no yellows, add the solution
                  if self.yellows == "":
                     addIt = 1
                  else:
                     #iterate all yellows
                     for i in range(len(self.yellows)):
                        temp = "[%s]" % self.yellows[i]
                        #alter regex if word contains 2 or more identical letters
                        if i < len(self.yellows) - 1:
                           if self.yellows[i] == self.yellows[i+1]:
                              temp = ".*(" + temp + ".*" + temp + ").*"
                              i += 1
                        if re.search(temp, nextGuess):
                           addCheck += 1
                     # add solution if all yellow checks passed
                     if addCheck == len(self.yellows):
                        addIt = 1
            #add solution to list of possibilities
            if addIt == 1:
               possible_solutions.append(nextGuess)
               #add heuristic if not first iteration
               if dictionary != self.dictionary:
                  tempH.append(self.heuristic[nextGuessIndex])

         nextGuessIndex += 1
      #end while loop (dictionary iteration loop)

      if dictionary != self.dictionary:
         self.heuristic = tempH     # save heuristics list
      # return new list
      return possible_solutions


   def AgentFunction(self, percepts):
      """Returns the next word guess given state of the game in percepts

      :param percepts: a tuple of three items: guess_counter, letter_indexes, and letter_states;
               guess_counter is an integer indicating which guess this is, starting with 0 for initial guess;
               letter_indexes is a list of indexes of letters from self.letters corresponding to
                           the previous guess, a list of -1's on guess 0;
               letter_states is a list of the same length as letter_indexes, providing feedback about the
                           previous guess (conveyed through letter indexes) with values of 0 (the corresponding
                           letter was not found in the solution), -1 (the correspond letter is found in the
                           solution, but not in that spot), 1 (the corresponding letter is found in the solution
                           in that spot).
      :return: string - a word from self.dictionary that is the next guess
      """

      # This is how you extract three different parts of percepts.
      guess_counter, letter_indexes, letter_states = percepts

      # Here's where you should put in your code

      currentWord = helper.letter_indices_to_word(letter_indexes, self.letters)
      #helps me to see the word without being blocked by colour
      print("guess is " + currentWord)

      #reinitialize global variables and return a random value
      if guess_counter == 0:
         self.initCheatCodes()
         return self.dictionary[np.random.randint(0, len(self.dictionary))]

      pattern = self.patt
      n = 0
      tempGrey = ""

      ''' Loops the characters of the most recent guess and determines 
          possible actions given the current letter states.
      '''
      while n < self.word_length:
         # only check unconfirmed results from previous pattern
         if pattern[n] == '.':

            #green value
            if letter_states[n] == 1:
               # add this letter to the regex pattern
               letter = currentWord[n]
               pattern = pattern[:n] + letter + pattern[n + 1:]

            #grey value
            elif letter_states[n] == 0:
               self.indi[n] += currentWord[n]
               #if not in lists already, add it to unallowed letters list
               if not re.findall("[%s]" % currentWord[n], self.greys + self.yellows + pattern + currentWord[n+1:]):
                  self.greys += currentWord[n]
               # add to unallowed characters for this char position
               elif not re.search("[%s]" % currentWord[n], self.greys + self.yellows + currentWord[n+1:]):
                  tempGrey += currentWord[n]

            # yellow value
            else:
               # this character is not in this position
               self.indi[n] += currentWord[n]
               # this character is in the word
               self.yellows += currentWord[n]
               # add an extra if it's already in the word (bugfix identical letters)
               if re.search("[%s]" % currentWord[n], pattern):
                  self.yellows += currentWord[n]

         n += 1
      #end while loop of prevGuess iteration

      # add the grey letters that are in the word to each unknown character positions
      if tempGrey != "":
         for e in range(len(self.indi)):
            if pattern[e] == ".":
               if re.match("[^%s]" % tempGrey, self.indi[e]):
                  self.indi[e] += tempGrey

      ''' helpful print functions'''
      print(pattern)
      print("word contains: " + self.yellows)
      print("word does not contain: " + self.greys)
      for i in range(self.word_length):
         print("unallowed in location %d: " % i + self.indi[i])

      possible_solutions = []
      #iterates the whole dictionary after guess 1 to create initial possible_solution list
      if guess_counter == 1:
         self.possibilities = self.iterMethod(self.dictionary, pattern, possible_solutions)
         #sets up the initial heuristics table
         self.setUpHeuristic()
         print(self.heuristic)
      #on all remaining guesses, iterate the possible_solutions list
      else:
         self.possibilities = self.iterMethod(self.possibilities, pattern, possible_solutions)
         print(self.heuristic)

      self.yellows = ""

      #adjust global variables with new data 
      self.patt = pattern

      print(self.possibilities)

      #error occur (empty list)
      if len(self.possibilities) < 1:
         return "err"

      #return random word from list of possible solutions
      return self.possibilities[self.heuristic.index(max(self.heuristic))]