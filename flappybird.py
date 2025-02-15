from itertools import cycle
from numpy.random import randint,choice
import sys

import random, sys, smbus, time
import pygame
from pygame.locals import *

FPS = 30
SCREENWIDTH  = 288
SCREENHEIGHT = 512
# amount by which base can maximum shift to left
PIPEGAPSIZE  = 160 # gap between upper and lower part of pipe
BASEY        = SCREENHEIGHT * 0.79
SCORE = 0

BACKGROUND = pygame.image.load('./background.png')

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'


class Bird(pygame.sprite.Sprite):

    def __init__(self,displayScreen):

        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load('./redbird.png')

        self.x = int(SCREENWIDTH * 0.2)
        self.y = SCREENHEIGHT*0.5
        
        self.rect = self.image.get_rect()
        self.height = self.rect.height
        self.screen = displayScreen
        
        self.playerVelY = -9
        self.playerMaxVelY = 10
       	self.playerMinVelY = -8
       	self.playerAccY = 1
       	self.playerFlapAcc = -9
       	self.playerFlapped = False

        self.display(self.x, self.y)

    def display(self,x,y):

        self.screen.blit(self.image, (x,y))
        self.rect.x, self.rect.y = x,y


    def move(self,input):

    	if input != None:
    		self.playerVelY = self.playerFlapAcc
    		self.playerFlapped = True

    	if self.playerVelY < self.playerMaxVelY and not self.playerFlapped:
    		self.playerVelY += self.playerAccY
    	if self.playerFlapped:
    		self.playerFlapped = False

    	self.y += min(self.playerVelY, SCREENHEIGHT - self.y - self.height)
    	self.y = max(self.y,0)
    	self.display(self.x,self.y)


class PipeBlock(pygame.sprite.Sprite):

	def __init__(self,image,upper):

		pygame.sprite.Sprite.__init__(self)

		if upper == False:
			self.image = pygame.image.load(image)
		else:
			self.image = pygame.transform.rotate(pygame.image.load(image),180)

		self.rect = self.image.get_rect()



class Pipe(pygame.sprite.Sprite):
	
	
	def __init__(self,screen,x):

		pygame.sprite.Sprite.__init__(self)

		self.screen = screen
		self.lowerBlock = PipeBlock('./pipe-red.png',False)
		self.upperBlock = PipeBlock('./pipe-red.png',True)
		

		self.pipeWidth = self.upperBlock.rect.width
		self.x = x
		

		heights = self.getHeight()
		self.upperY, self.lowerY = heights[0], heights[1]

		self.behindBird = 0
		self.display()


	def getHeight(self):

		# randVal = randint(1,10)
		randVal = choice([1,2,3,4,5,6,7,8,9], p =[0.04,0.04*2,0.04*3,0.04*4,0.04*5,0.04*4,0.04*3,0.04*2,0.04] )

		midYPos = 106 + 30*randVal

		upperPos = midYPos - (PIPEGAPSIZE/2)
		lowerPos = midYPos + (PIPEGAPSIZE/2)

		# print(upperPos)
		# print(lowerPos)
		# print('-------')
		return([upperPos,lowerPos])

	def display(self):

		self.screen.blit(self.lowerBlock.image, (self.x, self.lowerY))
		self.screen.blit(self.upperBlock.image, (self.x, self.upperY - self.upperBlock.rect.height))
		self.upperBlock.rect.x, self.upperBlock.rect.y = self.x, (self.upperY - self.upperBlock.rect.height)
		self.lowerBlock.rect.x, self.lowerBlock.rect.y = self.x, self.lowerY

	def move(self):

		self.x -= 3

		if self.x <= 0:
			self.x = SCREENWIDTH
			heights = self.getHeight()
			self.upperY, self.lowerY = heights[0], heights[1]
			self.behindBird = 0

		self.display()
		return([self.x+(self.pipeWidth/2), self.upperY, self.lowerY])










def game():

	

	pygame.init()

	FPSCLOCK = pygame.time.Clock()
	DISPLAY  = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
	pygame.display.set_caption('Flappy Bird')

	global SCORE,bus_data,X,Y

	bird = Bird(DISPLAY)
	pipe1 = Pipe(DISPLAY, SCREENWIDTH+100)
	pipe2 = Pipe(DISPLAY, SCREENWIDTH+100+(SCREENWIDTH/2))
    

	pipeGroup = pygame.sprite.Group()
	pipeGroup.add(pipe1.upperBlock)
	pipeGroup.add(pipe2.upperBlock)
	pipeGroup.add(pipe1.lowerBlock)
	pipeGroup.add(pipe2.lowerBlock)
	bus=smbus.SMBus(1)
	addr = 0x20
	direction = UP

	# birdGroup = pygame.sprite.Group()
	# birdGroup.add(bird1)
    
    ## I2C bus start
    

	moved = False
	pause =0

	while True:

		DISPLAY.blit(BACKGROUND,(0,0))

		# if (pipe1.x < pipe2.x and pipe1.behindBird==0) or (pipe2.x < pipe1.x and pipe2.behindBird==1):
		# 	input = (bird.y,pipe1.x, pipe1.upperY, pipe1.lowerY)
		# 	centerY = (pipe1.upperY + pipe1.lowerY)/2
		# elif (pipe1.x < pipe2.x and pipe1.behindBird==1) or (pipe2.x < pipe1.x and pipe2.behindBird==0):
		# 	input = (bird.y,pipe2.x, pipe2.upperY, pipe2.lowerY)
		# 	centerY = (pipe2.upperY + pipe2.lowerY)/2

		# print(input)

		t = pygame.sprite.spritecollideany(bird,pipeGroup)

		if t!=None or (bird.y== 512 - bird.height) or (bird.y == 0):
			print("GAME OVER")
			print("FINAL SCORE IS %d"%SCORE)
			return(SCORE)

        # Reads Qwiic Joystick
		try:
			bus_data = bus.read_i2c_block_data(addr, 0x03, 5)
		except Exception as e:
			print(e)
		X = (bus_data[0]<<8 | bus_data[1])>>6
		Y = (bus_data[2]<<8 | bus_data[3])>>6
		if X < 450:
			direction = UP
		elif 575 < X:
			direction = UP
		elif Y < 450:
			direction = UP
		elif 575 < Y:
			direction = UP
			

		
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYDOWN and (event.key == K_ESCAPE )):
				pygame.quit()
				sys.exit()
			if direction==UP or (event.type == KEYDOWN and (event.key == K_UP or event.key == K_RETURN)):
				bird.move("UP")
				moved = True
			if event.type == KEYDOWN and event.key == K_m :
				pause=1
		

		if moved == False:
			bird.move(None)
		else:
			moved = False


		
		pipe1Pos = pipe1.move()
		if pipe1Pos[0] <= int(SCREENWIDTH * 0.2) - int(bird.rect.width/2):
			if pipe1.behindBird == 0:
				pipe1.behindBird = 1
				SCORE += 1
				print("SCORE IS %d"%SCORE)

		pipe2Pos = pipe2.move()
		if pipe2Pos[0] <= int(SCREENWIDTH * 0.2) - int(bird.rect.width/2):
			if pipe2.behindBird == 0:
				pipe2.behindBird = 1
				SCORE += 1
				print("SCORE IS %d"%SCORE)
		
		

		if pause==0:
			pygame.display.update()

		FPSCLOCK.tick(FPS)
game()
