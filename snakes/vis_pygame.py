__author__ = "Lech Szymanski"
__organization__ = "COSC343/AIML402, University of Otago"
__email__ = "lech.szymanski@otago.ac.nz"
__date__ = "August 2022"

import pygame
import numpy as np
import sys

class visualiser:

   def __init__(self, speed, resolution=(720,480), playerStrings=None):
      pygame.init()

      #self.gridSize = gridSize
      self.playerStrings = playerStrings

      self.width, self.height = resolution
      self.WHITE = (255, 255, 255)
      self.BLACK = 0, 0, 0
      self.YELLOW = (255, 170, 25)
      self.DYELLOW = (255, 147, 0)
      self.MAGENTA = 255, 64, 255
      self.DMAGENTA = (225, 64, 225)
      self.GREEN = 155,225,0
      self.RED = 255,0,0


      if speed == "normal":
         self.frameTurns = 160
      elif speed == "fast":
         self.frameTurns = 16
      elif speed == "slow":
         self.frameTurns = 640

      self.screen = pygame.display.set_mode(resolution)



      #max_size=8
      #unit_size=4

      self.font = pygame.font.Font("arial.ttf", 14)

   def __del__(self):
      pygame.display.quit()
      pygame.quit()

   def show(self, map, turn=0, game=None, titleStr = None):
       if titleStr is None:
           caption = ''
       else:
           caption = titleStr + ', '

       if game is not None:
           if isinstance(game, str):
               caption += 'Game %s ' % game
           else:
               caption += 'Game %d' % game
               if turn > 0:
                   caption += ", "

       if turn > 0:
           caption += 'Turn %d' % (turn)

       pygame.display.set_caption(caption)

       fSize = np.min([self.width, self.height])
       margin = (self.width - fSize) / 2

       gridSize = np.shape(map)[0]
       unit = int(fSize / gridSize)
       if unit < 1:
           unit = 1

       for event in pygame.event.get():
           if event.type == pygame.QUIT: sys.exit()

       self.screen.fill(self.WHITE)

       if self.playerStrings is not None:
           label = self.font.render(self.playerStrings[0], 1, self.DYELLOW)
           self.screen.blit(label, (10, 10))

           if len(self.playerStrings) > 1:
               label = self.font.render(self.playerStrings[1], 1, self.DMAGENTA)
               self.screen.blit(label, (margin + (gridSize * unit) + 10, 10))

       for y in range(gridSize):
           for x in range(gridSize):

               if map[y,x,2]==1:
                   c = self.RED
               elif np.abs(map[y,x,0])==1:
                   c = self.YELLOW
               elif np.abs(map[y,x,0])==2:
                   c = self.DYELLOW
               elif np.abs(map[y,x,1])==1:
                   c = self.MAGENTA
               elif np.abs(map[y,x,1])==2:
                   c = self.DMAGENTA
               else:
                   c = self.GREEN

               pygame.draw.rect(self.screen, c,
                                (margin + (x * unit), y * unit, unit, unit))

       collisions1 = np.argwhere(map[:,:,0]<0)
       collisions2 = np.argwhere(map[:,:,1]<0)

       collisions = np.concatenate((collisions1,collisions2),axis=0)

       if len(collisions) == 0:
           pygame.display.flip()
           pygame.time.delay(self.frameTurns)
           return

       N = 8
       for k in range(N):
           if k % 4 == 0:
               i1 = 0
               c1 = self.YELLOW
               h1 = self.DYELLOW
               i2 = 1
               c2 = self.MAGENTA
               h2 = self.DMAGENTA
           else:
               i1 = 1
               c1 = self.MAGENTA
               h1 = self.DMAGENTA
               i2 = 0
               c2 = self.YELLOW
               h2 = self.DYELLOW

           for y,x in collisions:
               if k%2==1:
                   c=self.WHITE
               else:
                   if map[y,x,i1] == -2:
                       c = h1
                   elif map[y,x,i1] == -1:
                       c = c1
                   elif map[y,x,i2] == -2:
                       c = h2
                   elif map[y,x,i2] == -1:
                       c = c2

               pygame.draw.rect(self.screen, c,
                                (margin + (x * unit), y * unit, unit, unit))

           pygame.display.flip()

           pygame.time.delay(int(self.frameTurns/(N+1)))

       for y, x in collisions:

           if map[y, x, 2] == 1:
               c = self.RED
           elif map[y, x, 0] == 1:
               c = self.YELLOW
           elif map[y, x, 0] == 2:
               c = self.DYELLOW
           elif map[y, x, 1] == 1:
               c = self.MAGENTA
           elif map[y, x, 1] == 2:
               c = self.DMAGENTA
           else:
               c = self.GREEN

           pygame.draw.rect(self.screen, c,
                            (margin + (x * unit), y * unit, unit, unit))

       pygame.display.flip()

       pygame.time.delay(int(self.frameTurns / (N+1)))

   #def show(self, creature_state, food_array,wall_array,game=None,turn=0,titleStr=None):
   def show2(self, map, food, heads1, heads2, turn=0, game=None, titleStr = None,collisions = [],delay=True):
      if titleStr is None:
          caption = ''
      else:
          caption = titleStr + ', '

      gameEnd = False
      if game is not None:
         if isinstance(game,str):
            caption += 'Game %s ' % game
         else:
             caption += 'Game %d' % game
             if turn>0:
                caption += ", "

      if turn>0:
          caption += 'Turn %d' % (turn)

      pygame.display.set_caption(caption)

      fSize = np.min([self.width, self.height])
      margin = (self.width-fSize)/2

      gridSize = np.shape(map)[0]
      unit = int(fSize / gridSize)
      if unit < 1:
         unit = 1
      #I = np.where(creature_state[:,2]==1)[0]
      #nCreatures2 = int(np.sum(creature_state[I,3]))
      #nCreatures1 = len(I)-nCreatures2



      for event in pygame.event.get():
         if event.type == pygame.QUIT: sys.exit()

      self.screen.fill(self.WHITE)

      # render text
      if self.playerStrings is not None:
          label = self.font.render( self.playerStrings[0], 1, self.DYELLOW)
          self.screen.blit(label, (10, 10))
          #label = self.font.render( "Creatures: %d" % nCreatures1, 1, (33, 79, 255))
          #self.screen.blit(label, (10, 30))

          if len(self.playerStrings)>1:
             label = self.font.render(self.playerStrings[1], 1, self.DMAGENTA)
             self.screen.blit(label, (margin + (gridSize * unit)+10, 10))
             #label = self.font.render( "Creatures: %d" % nCreatures2, 1, (230, 42, 55))
             #self.screen.blit(label, (self.left_frame + (self.gridSize * self.unit)+10, 30))

      #for i in range(gridSize + 1):
      #   pygame.draw.line(self.screen, self.BLACK, [self.left_frame, i * unit],
      #                    [self.left_frame + (gridSize * unit), i * unit])
      #   pygame.draw.line(self.screen, self.BLACK, [self.left_frame + (i * unit), 0],
      #                    [self.left_frame + (i * unit), gridSize * unit])
      #fy,fx = food
      yellows = []
      magentas = []

      N = 8

      for k in range(N):

          for y in range(gridSize):
             for x in range(gridSize):

                if (y,x) in food:
                   c = self.RED
                elif map[y,x] > 0:
                   c = self.YELLOW
                elif map[y,x] < 0:
                   c = self.MAGENTA
                else:
                   c = self.GREEN

                #if hy1 == y and hx1 == x:  # head player 1
                #   c = self.DYELLOW

                #if len(heads) > 1 and hy2 == y and hx2 == x:
                #   c = self.DMAGENTA

                pygame.draw.rect(self.screen, c,
                                    (margin + (x * unit), y * unit, unit, unit))

          if k%4==0:
              h1 = heads1
              c1 = self.DYELLOW
              h2 = heads2
              c2 = self.DMAGENTA
          elif k%2==0:
              h1 = heads2
              c1 = self.DMAGENTA
              h2 = heads1
              c2 = self.DYELLOW


          for y,x in h1:
             pygame.draw.rect(self.screen, c1,
                              (margin + (x * unit), y * unit, unit, unit))

          for y,x in h2:
             pygame.draw.rect(self.screen, c2,
                              (margin + (x * unit), y * unit, unit, unit))

          if k%2==1:
              for y,x in collisions:
                  pygame.draw.rect(self.screen, self.WHITE,
                                   (margin + (x * unit), y * unit, unit, unit))

          pygame.display.flip()

          if len(collisions)==0:
              if delay:
                  pygame.time.delay(self.frameTurns)
              break

          pygame.time.delay(int(self.frameTurns/(N)))



      #if len(collisions)>0:

      #   snakes = yellows + magentas

      #   if len(collisions)==1 or (len(collisions)==2 and not (hx1==hx2 and hy1==hy2)):
      #      for k in range(12):
      #         for y,x in collisions+snakes:
      #            if k%2==0:

      #               if k%4==0 and hy1 == y and hx1 == x:  # head player 1
      #                  c = self.DYELLOW
      #               elif k%4 == 0 and len(heads) > 1 and hy2 == y and hx2 == x:
      #                  c = self.DMAGENTA
      #               elif map[y, x] > 0:
      #                  c = self.YELLOW
      #               elif map[y, x] < 0:
      #                  c = self.MAGENTA
      #               else:
      #                  c = self.GREEN
      #            else:
      #               c = self.WHITE

      #            pygame.draw.rect(self.screen, c,
      #                       (margin + (x * unit), y * unit, unit, unit))

      #         pygame.display.flip()
      #         pygame.time.delay(int(self.frameTurns/2))
      #   else:
      #      for k in range(12):
      #        for y, x in snakes:
      #           if k % 2 == 0:
      #              if map[y, x] > 0:
      #                  c = self.YELLOW
      #              else:
      #                  c = self.MAGENTA
      #           else:
      #               c = self.WHITE#

      #           pygame.draw.rect(self.screen, c,
      #                          (margin + (x * unit), y * unit, unit, unit))

      #        if k % 4 == 0:
      #          y,x = hy1,hx1
      #          c = self.DYELLOW
      #        elif k % 2 == 0:
      #          y,x = hy2,hx2
      #          c = self.DMAGENTA
      #        else:
      #           c = self.WHITE

      #        pygame.draw.rect(self.screen, c,
      #                          (margin + (x * unit), y * unit, unit, unit))



       #       pygame.display.flip()
       #       pygame.time.delay(int(self.frameTurns / 2))
      #self.prev_creature_state = np.copy(creature_state)
