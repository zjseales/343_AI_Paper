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
   prevIndex = 0
   letterPatterns = None
   yellows = ""
   greys = ""
   patt = ""
   indi = []

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
   
            prevIndex = initialize random first index
            yellows = letters that are in the answer somewhere
            greys = letters that are not in the answer
            patt = the regex pattern of the next guess
   '''
   def initCheatCodes(self):
      self.prevIndex = np.random.randint(0, len(self.dictionary))
      self.yellows = ""
      self.greys = ""
      self.patt = "....."
      self.indi = ["", "", "", "", ""]

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

      #reinitialize global variables and return the index state defined in the initCheatCodes method
      if guess_counter == 0:
         self.initCheatCodes()
         return self.dictionary[self.prevIndex]

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
               #if not in lists already, add it to unallowed letters list
               if not re.findall("[%s]" % currentWord[n], self.greys + self.yellows + pattern + currentWord[n+1:]):
                  self.greys += currentWord[n]
               # add to unallowed characters for this char position
               elif not re.findall("[%s]" % currentWord[n], self.indi[n] + self.greys + self.yellows):
                  tempGrey += currentWord[n]

            # yellow value
            else:
               self.indi[n] += currentWord[n]
               self.yellows += currentWord[n]
               if re.search("[%s]" % currentWord[n], pattern):
                  self.yellows += currentWord[n]

         n += 1
      #end while loop

      # add the grey letters to each unknown character positions
      if tempGrey != "":
         for e in range(len(self.indi)):
            if pattern[e] == ".":
               if re.match("[^%s]" % tempGrey, self.indi[e]):
                  self.indi[e] += tempGrey

      nextGuessIndex = self.prevIndex
      possible_solutions = []

      '''------------------ implement this once basics working, to tidy code
      #iterates the whole dictionary after guess 1
      if guess_counter == 1:
         iterMethod()
      #on all remaining guesses, iterate the already found possible_solutions list
      else:
         iterMethod()
      '''
      #finds first 50 possible solutions from iterating entire dictionary
      while len(possible_solutions) < 50:
         # ensures guessIndex is within range
         if nextGuessIndex >= len(self.dictionary):
            nextGuessIndex = nextGuessIndex - len(self.dictionary)

         # make a guess and compare
         nextGuess = self.dictionary[nextGuessIndex]
         ma = re.match(pattern, nextGuess)

         # adjust nextGuessIndex
         # iterate dictionary if first letter found
         if re.match("^[0-9]", pattern):
            nextGuessIndex += 1
         else:
            bigboi = 0
            for i in range(self.word_length):
               bigboi += pow(letter_indexes[i], (5-i))
            # change this to hash function
            nextGuessIndex += bigboi % 11423

         # break loop if next guess = first guess
         if len(possible_solutions) > 1:
            if possible_solutions[0] == nextGuess:
               break

         # if nextGuess matches pattern, do additional checks
         if ma:
            if not re.search("[" + self.greys + "]", nextGuess):
               addCheck = 0
               for e in range(self.word_length):
                  if re.search("[%s]" % nextGuess[e], self.indi[e]):
                     addCheck = 1
                     break

               if addCheck == 0:
                  #must contain yellows if yellow string is not empty
                  if self.yellows != "":
                     for i in range(len(self.yellows)):
                        if re.search("[%s]" % self.yellows[i], nextGuess):
                           addCheck += 1

                     if addCheck == len(self.yellows):
                        possible_solutions.append(nextGuess)

                  else:
                     possible_solutions.append(nextGuess)

      #end while loop (dictionary iteration loop)
      self.yellows = ""

      #adjust global variables with new data
      self.patt = pattern
      self.prevIndex = nextGuessIndex
      self.possible_solutions = possible_solutions

      print(possible_solutions)
      #print a random value from the list of possible solutions
      return self.possible_solutions[np.random.randint(0, len(possible_solutions))]