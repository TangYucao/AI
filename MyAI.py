# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action
import numpy as np
from enum import Enum, unique
class MyAI( AI ):
	@unique
	class myAction (Enum):
		LEAVE = 0
		UNCOVER = 1
		FLAG = 2
		UNFLAG = 3
	class myBoard ():
		'''
		unknown =-1 
		unknown but safe=-2
		FLAG bomb =-3
		covered(not bomb)>= 0. if>=1 then mine is in surrounding 
		'''
		# NOBOOM = 0
		UNCOVER = -1
		UNCOVERSAFE = -2
		FLAGBOMB = -3
	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		self.rowDimension = colDimension
		self.colDimension = rowDimension
		self.moveCount = 0
		# print( "totalMines:"+str(totalMines))
		# print ("startX:"+str(startX))
		# print ("startY:"+str(startY))
		# print ("rowDimension:"+str(self.rowDimension))
		# print ("colDimension:"+str(self.colDimension))

		self.visited = np.zeros((self.rowDimension, self.colDimension))#0 not visited 1 visited
		self.board = np.full((self.rowDimension, self.colDimension), self.myBoard.UNCOVER)
		self.totalMines=totalMines;
		self.lastX=startX;
		self.lastY=startY;
		self.visited[self.lastX][self.lastY]=1;
		self.lastAction=self.myAction.UNCOVER
		# self.visited[startX][startY]=1
		self.debug=True
		# print(self.visited[startX][startX])
		pass
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################
		
	
	def getAction(self, number: int) -> "Action Object":
		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		# print("last action:",self.lastAction,"pos:%d,%d"%(self.lastX+1,self.lastY+1))
		if number==-1 or self.lastAction==self.myAction.FLAG:#if last step is FLAG mine
			self.updateboardboomb(self.lastX,self.lastY)
			# print("debug:FLAG Number is:"+str(number))
			# self.printBoardInfo(False) 

		if number!=-1:

			FLAGnum=self.countSurroundingTarget(self.lastX,self.lastY,self.myBoard.FLAGBOMB)

			self.board[self.lastX][self.lastY]=number-FLAGnum
			if number-FLAGnum==0:
				self.updateboard(self.visited,self.lastX,self.lastY,self.board,number-FLAGnum)

		for i in range(self.rowDimension):#uncover safe space.
			for j in range(self.colDimension):
				# print("%d:%d",i,j)		
				if self.visited[i][j]==0  and  (self.board[i][j]==self.myBoard.UNCOVERSAFE or self.totalMines==0):
					self.visited[i][j]=1; 
					self.lastX=i;
					self.lastY=j;
					self.lastAction=self.myAction.UNCOVER
					return Action(AI.Action.UNCOVER,i,j)
		# self.printBoardInfo(False) #DEBUG
		#---------------code above uncovered all available space.
		#deal with concave, like: 
		#B ? ?
		#B 2 B 
		#B B B
		targetX,targetY=self.dealwithconcave();
		if targetX>=0:
			self.visited[targetX][targetY]=1;
			self.lastX=targetX;
			self.lastY=targetY;
			self.board[targetX][targetY]=self.myBoard.FLAGBOMB
			# print("targetX:%d,targetY:%d,board value:%d"%(targetX,targetY,self.board[targetX][targetY]))
			self.lastAction=self.myAction.FLAG
			self.totalMines=self.totalMines-1
			return Action(AI.Action.FLAG,targetX,targetY)
		# -----------------todo: Assumtion: if this one is the boomb.
		backboard =self.board.copy()
		backvisited=self.visited.copy()
		# self.printBoardInfo(False) #DEBUG

		toFLAGplaces=[]
		for i in range(self.rowDimension):#uncover safe space.
			for j in range(self.colDimension):
				if self.visited[i][j]==0:
					if(self.countSurroundingTarget(i,j,self.myBoard.UNCOVER)==8):continue;#in the middle
					if (i==0 or i==self.rowDimension-1) and (j==0 or j==self.colDimension-1):#in the cornor
						if self.countSurroundingTarget(i,j,self.myBoard.UNCOVER)==3:continue;
					if (i==0 or i==self.rowDimension-1 or j==0 or j==self.colDimension-1):#on the side
						if self.countSurroundingTarget(i,j,self.myBoard.UNCOVER)==5:continue;
					if self.assume(i,j,self.myBoard.FLAGBOMB)==True:#assume there is a boomb.
						toFLAGplaces.append([i,j])
						self.board=backboard.copy()
						self.visited=backvisited.copy()
					else:#we can uncover the place!
						self.board=backboard.copy()
						self.visited=backvisited.copy()
						self.visited[i][j]=1; 
						self.lastX=i;
						self.lastY=j;
						self.lastAction=self.myAction.UNCOVER
						return Action(AI.Action.UNCOVER,i,j)
		# self.printBoardInfo(False) #DEBUG
		#----------------------todo:if only one place can be flagged as boomb,then flag it.
		if len(toFLAGplaces)==1:
			# print("toFLAGplaces Size:",len(toFLAGplaces))
			i=toFLAGplaces[0][0]
			j=toFLAGplaces[0][1]
			# print(i+1," ",j+1)

			self.visited[i][j]=1;
			self.lastX=i;
			self.lastY=j;
			self.board[i][j]=self.myBoard.FLAGBOMB
			self.lastAction=self.myAction.FLAG
			self.totalMines=self.totalMines-1
			return Action(AI.Action.FLAG,i,j)
		#todo:-------------------- calculate toFLAGplaces' probability and flag the 
		# self.printBoardInfo(False) #DEBUG
		if len(toFLAGplaces)>=2:
			map=[]
			i=0
			for (x,y) in toFLAGplaces:
				# print(x+1," ",y+1)
				map.append(self.calculateProbability(x,y))
				# print([x+1,y+1]," probability:",map[i])
				i+=1
			maxindex=np.argmax(map);#get the biggest probability, flag that pos!
			i=toFLAGplaces[maxindex][0]
			j=toFLAGplaces[maxindex][1]
			self.visited[i][j]=1;
			self.lastX=i;
			self.lastY=j;
			# print(i+1," ",j+1)
			# self.printBoardInfo(False) #DEBUG
			self.board[i][j]=self.myBoard.FLAGBOMB
			self.lastAction=self.myAction.FLAG
			self.totalMines=self.totalMines-1

			return Action(AI.Action.FLAG,i,j)


		return Action(AI.Action.LEAVE)
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################
	def updateboard(self,visited,i,j,board,number):
		# for l in range(j,0):#left
			# if board[][j]:
		if number==0:
			if i>0 and self.board[i-1][j]==self.myBoard.UNCOVER:
				self.board[i-1][j]=self.myBoard.UNCOVERSAFE;
			if j>0 and self.board[i][j-1]==self.myBoard.UNCOVER:
				self.board[i][j-1]=self.myBoard.UNCOVERSAFE;
			if i<self.rowDimension-1 and self.board[i+1][j]==self.myBoard.UNCOVER:
				self.board[i+1][j]=self.myBoard.UNCOVERSAFE;
			if j<self.colDimension-1 and self.board[i][j+1]==self.myBoard.UNCOVER:
				self.board[i][j+1]=self.myBoard.UNCOVERSAFE;
			if i>0 and j>0 and self.board[i-1][j-1]==self.myBoard.UNCOVER:	
				self.board[i-1][j-1]=self.myBoard.UNCOVERSAFE;
			if i>0 and j<self.colDimension-1 and self.board[i-1][j+1]==self.myBoard.UNCOVER:	
				self.board[i-1][j+1]=self.myBoard.UNCOVERSAFE;
			if i<self.rowDimension-1 and j>0 and self.board[i+1][j-1]==self.myBoard.UNCOVER:	
				self.board[i+1][j-1]=self.myBoard.UNCOVERSAFE;
			if i<self.rowDimension-1 and j<self.colDimension-1 and self.board[i+1][j+1]==self.myBoard.UNCOVER:	
				self.board[i+1][j+1]=self.myBoard.UNCOVERSAFE;
		# return visited,board
	def updateboardboomb(self,i,j):
		# for l in range(j,0):#left
			# if board[][j]:
		newzeroboard=[]
		if i>0 and self.board[i-1][j]>0: 
			self.board[i-1][j]-=1 
			if self.board[i-1][j]==0:
				newzeroboard.append([i-1,j])
		if i>0 and j>0 and self.board[i-1][j-1]>0: 
			self.board[i-1][j-1]-=1
			if self.board[i-1][j-1]==0:
				newzeroboard.append([i-1,j-1])
		if j>0 and self.board[i][j-1]>0: 
			self.board[i][j-1]-=1
			if self.board[i][j-1]==0:
				newzeroboard.append([i,j-1])
		if j<self.colDimension-1 and self.board[i][j+1]>0: 
			self.board[i][j+1]-=1
			if self.board[i][j+1]==0:
				newzeroboard.append([i,j+1])
		if i>0 and j<self.colDimension-1 and self.board[i-1][j+1]>0:
			self.board[i-1][j+1]-=1
			if self.board[i-1][j+1]==0:
				newzeroboard.append([i-1,j+1])
		if i<self.rowDimension-1:
			if self.board[i+1][j]>0: 
				self.board[i+1][j]-=1
				if self.board[i+1][j]==0:
					newzeroboard.append([i+1,j])
		if i<self.rowDimension-1 and j>0 and self.board[i+1][j-1]>0: 
			self.board[i+1][j-1]-=1
			if self.board[i+1][j-1]==0:
				newzeroboard.append([i+1,j-1])
		if i<self.rowDimension-1 and j<self.colDimension-1 and self.board[i+1][j+1]>0: 
			self.board[i+1][j+1]-=1
			if self.board[i+1][j+1]==0:
				newzeroboard.append([i+1,j+1])
		for p in newzeroboard:
			[m,n]=p
			self.updateboard(self.visited,m,n,self.board,0)


	def printBoardInfo(self,boolvisited) -> None:
		""" Print board for debugging """ 
		board_as_string = ""
		print("-----------myBoard---------")
		for r in range(self.rowDimension - 1, -1, -1):
			print(str(r+1).ljust(2) + '|', end=" ")
			for c in range(self.colDimension):
				if self.board[c][r]==self.myBoard.FLAGBOMB:
					print("B ",end=" ")
				if self.board[c][r]==self.myBoard.UNCOVER:
					print("? ",end=" ")
				if self.board[c][r]==self.myBoard.UNCOVERSAFE:
					print("-2",end=" ")
				if self.board[c][r]>=0:
					print(str(self.board[c][r])+" ",end=" ")
			if (r != 0):
				print('\n', end=" ")

		column_label = "     "
		column_border = "   "
		for c in range(1, self.colDimension+1):
			column_border += "---"
			column_label += str(c).ljust(3)
		print(board_as_string)
		print(column_border)
		print(column_label)

		if boolvisited:
			board_as_string = ""
			print("-----------myVisited---------")
			for r in range(self.rowDimension - 1, -1, -1):
				print(str(r+1).ljust(2) + '|', end=" ")
				for c in range(self.colDimension):
					if self.visited[c][r]==1:
						print("1 ",end=" ")
					if self.visited[c][r]==0:
						print("0 ",end=" ")
				if (r != 0):
					print('\n', end=" ")

			column_label = "     "
			column_border = "   "
			for c in range(1, self.colDimension+1):
				column_border += "---"
				column_label += str(c).ljust(3)
			print(board_as_string)
			print(column_border)
			print(column_label)
	def dealwithconcave(self):
		for i in range(self.rowDimension):
			for j in range(self.colDimension):
				if self.countSurroundingTarget(i,j,self.myBoard.UNCOVER)==self.board[i][j]:#find unknown
					if i>0 and self.board[i-1][j]==self.myBoard.UNCOVER:
						return i-1,j
					if j>0 and self.board[i][j-1]==self.myBoard.UNCOVER:
						return i,j-1
					if i<self.rowDimension-1 and self.board[i+1][j]==self.myBoard.UNCOVER:
						return i+1,j
					if j<self.colDimension-1 and self.board[i][j+1]==self.myBoard.UNCOVER:
						return i,j+1
					if i>0 and j>0 and self.board[i-1][j-1]==self.myBoard.UNCOVER:
						return i-1,j-1
					if i>0 and j<self.colDimension-1 and self.board[i-1][j+1]==self.myBoard.UNCOVER:	
						return i-1,j+1
					if i<self.rowDimension-1 and j>0 and self.board[i+1][j-1]==self.myBoard.UNCOVER:	
						return i+1,j-1
					if i<self.rowDimension-1 and j<self.colDimension-1 and self.board[i+1][j+1]==self.myBoard.UNCOVER:	
						return i+1,j+1



		return -1,-1
	def countSurroundingTarget(self,i,j,target):
		res=0
		if i>0 and self.board[i-1][j]==target:
			res+=1

		if j>0 and self.board[i][j-1]==target:
			res+=1

		if i<self.rowDimension-1 and self.board[i+1][j]==target:
			res+=1
		if j<self.colDimension-1 and self.board[i][j+1]==target:
			res+=1
		if i>0 and j>0 and self.board[i-1][j-1]==target:	
			res+=1
		if i>0 and j<self.colDimension-1 and self.board[i-1][j+1]==target:	
			res+=1
		if i<self.rowDimension-1 and j>0 and self.board[i+1][j-1]==target:	
			res+=1
		if i<self.rowDimension-1 and j<self.colDimension-1 and self.board[i+1][j+1]==target:	
			res+=1
		return res;
	def assume(self,i,j,target):
		self.visited[i][j]=1;#like we set that to boomb.
		self.board[i][j]=self.myBoard.FLAGBOMB
		self.updateboardboomb(i,j)
		for i in range(self.rowDimension):
			for j in range(self.colDimension):
				if self.visited[i][j]==1 and  self.board[i][j]>=1:
					if self.countSurroundingTarget(i,j,self.myBoard.UNCOVER)<self.board[i][j]:
						# print("debug:assume ",i+1," ",j+1," ",self.countSurroundingTarget(i,j,self.myBoard.UNCOVER),"!=",self.board[i][j])
						return False;
		return True;
	def calculateProbability(self,i,j):
		surroundingNumsPos=[]
		if i>0 and self.board[i-1][j]>0:
			surroundingNumsPos.append([i-1,j])
		if j>0 and self.board[i][j-1]>0:
			surroundingNumsPos.append([i,j-1])
		if i<self.rowDimension-1 and self.board[i+1][j]>0:
			surroundingNumsPos.append([i+1,j])
		if j<self.colDimension-1 and self.board[i][j+1]>0:
			surroundingNumsPos.append([i,j+1])
		if i>0 and j>0 and self.board[i-1][j-1]>0:	
			surroundingNumsPos.append([i-1,j-1])
		if i>0 and j<self.colDimension-1 and self.board[i-1][j+1]>0:	
			surroundingNumsPos.append([i-1,j+1])
		if i<self.rowDimension-1 and j>0 and self.board[i+1][j-1]>0:	
			surroundingNumsPos.append([i+1,j-1])
		if i<self.rowDimension-1 and j<self.colDimension-1 and self.board[i+1][j+1]>0:	
			surroundingNumsPos.append([i+1,j+1])
		probs=[]
		tmp=1
		#todo:calculate P(boomb)=P(A||B||C)=1-P(!A!B!C)=1-P(!A)P(!B)P(!C)
		for pos in surroundingNumsPos:
			priorprobability=self.board[pos[0]][pos[1]]/self.countSurroundingTarget(pos[0],pos[1],self.myBoard.UNCOVER)
			probs.append(priorprobability)
			tmp=tmp*(1-priorprobability)

		# return max(probs)# simply make biggest probability as its probability
		return 1-tmp
