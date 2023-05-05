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
   # the average char frequencies of all 5 dictionarys
   freq = []

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
      self.greys = "." #initialize with character to bugfix empty object error
      self.patt = "....."
      self.indi = ["", "", "", "", ""]
      self.possibilities = []
      self.heuristic = []
      self.freq = [8.92, 1.39, 3.44, 4.15, 13.97, 1.24, 1.71, 2.96, 7.43, 0.34, 0.49, 4.89, 2.85, \
                   7.52, 6.72, 2.24, 0.51, 6.32, 6.62, 6.77, 4.09, 1.31, 0.84, 0.16, 0.67, 0.56]

   def setUpHeuristic(self):
      #initialize table of character frequencies
      # taken from https://www.sttmedia.com/characterfrequency-english
      freq = self.freq
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

   ''' Returns 1 if the word argument has repeating letters, else returns 0.
       Used to increase information recovered from first 2 guesses.
       Parameter:
               word = the word being checked for repeating letters.
   '''
   def repeating(self, word):
      #terate word and check each char, no need to check last one
      for j in range(len(word) - 1):
         check = ".*(" + word[j] + ".*" + word[j] + ").*"
         if re.search(check, word):
            return 1

      return 0


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

      # helps me to see the word without being blocked by colour
      currentWord = helper.letter_indices_to_word(letter_indexes, self.letters)
      print("guess is " + currentWord)

      #reinitialize global variables and return a random value with no repeating characters
      if guess_counter == 0:
         self.initCheatCodes()
         result = self.dictionary[np.random.randint(0, len(self.dictionary))]
         while self.repeating(result) == 1:
            result = self.dictionary[np.random.randint(0, len(self.dictionary))]
         return result

      pattern = self.patt
      n = 0
      tempGrey = ""

      # Loops the characters of the most recent guess and determines
      # possible actions given the current letter states.
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
               #if in yellows list, only not allowed in this position
               if re.search("[%s]" % currentWord[n], self.yellows):
                  self.indi[n] += currentWord[n]
               elif not re.search("[%s]" % currentWord[n], self.greys):
                  if re.search("[%s]" % currentWord[n], currentWord[n + 1:]):
                     st = currentWord[n + 1:]
                     check = st.index(currentWord[n]) + len(currentWord[:n + 1])
                     print(check)
                     if letter_states[check] == 1:
                        tempGrey += currentWord[n]
                  elif not re.search("[%s]" % currentWord[n], pattern):
                     self.greys += currentWord[n]
                  else:
                     tempGrey += currentWord[n]
               # add to unallowed characters for this char position
               elif not re.search("[%s]" % currentWord[n], self.greys + self.yellows + currentWord[n+1:]):
                  tempGrey += currentWord[n]
               else:
                  self.indi[n] += currentWord[n]

            # yellow value
            else:
               # add an extra if it's already in the word (bugfix identical letters)
               if re.search("[%s]" % currentWord[n], pattern + self.yellows):
                  self.yellows += currentWord[n]
               # this character is not in this position
               self.indi[n] += currentWord[n]
               # this character is in the word
               self.yellows += currentWord[n]
         n += 1
      #end while loop of prevGuess iteration

      # add the grey letters that are in the word to each unknown character positions
      if tempGrey != "":
         for e in range(len(self.indi)):
            if pattern[e] == ".":
               if not re.search("[%s]" % tempGrey, self.indi[e]):
                  self.indi[e] += tempGrey

      ''' helpful print functions
      print(pattern)
      print("word contains: " + self.yellows)
      print("word does not contain: " + self.greys)
      for i in range(self.word_length):
         print("unallowed in location %d: " % i + self.indi[i])
      '''
      possible_solutions = []
      #iterates the whole dictionary after guess 1 to create initial possible_solution list
      if guess_counter == 1:
         self.possibilities = self.iterMethod(self.dictionary, pattern, possible_solutions)
         #sets up the initial heuristics table
         self.setUpHeuristic()
      #on all remaining guesses, iterate the possible_solutions list
      else:
         self.possibilities = self.iterMethod(self.possibilities, pattern, possible_solutions)

      # adjust global variables with new data
      self.yellows = ""
      self.patt = pattern

      # calculate expected heuristic value
      h = 0.0
      for i in range(self.word_length):
         if self.patt[i] == ".":
            h += 3.77
         else:
            index = helper.word_to_letter_indices(self.patt[i], self.letters)
            h += self.freq[index[0]]

      ''' FIND AVERAGE HEURSTIC VALUE OF ALL POSSIBLE SOLUTIONS THEN AVERAGE THAT WITH THE EXPECTED HEURISTIC VALUE'''
      totAv = 0
      for i in range(len(self.possibilities)):
         totAv += self.heuristic[i]

      h = (totAv + h) / (len(self.possibilities) + 1)

      print("expected heuristic value is: %f" % h)

      resultIndex = np.abs(np.asarray(self.heuristic) - h).argmin()
      result = self.possibilities[resultIndex]
      # ensure second guess does not contain repeating letters
      if guess_counter == 0:
         infinite_check = 0
         while self.repeating(result) == 1:
            resultIndex = np.abs(np.asarray(self.heuristic) - (h + 1)).argmin()
            result = self.possibilities[resultIndex]

            infinite_check += 1
            #in case first list contains only words with repeating letters
            if infinite_check == len(self.possibilities):
               break

      return result