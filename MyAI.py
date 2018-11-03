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
		NOBOOM = 0
		UNCOVER = -1
		UNCOVERSAFE = -2
		FLAGBOMB = -3
	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		self.rowDimension = rowDimension
		self.colDimension = colDimension
		self.moveCount = 0
		# print( "totalMines:"+str(totalMines))
		# print ("startX:"+str(startX))
		# print ("startY:"+str(startY))
		self.visited = np.zeros((rowDimension, colDimension))#0 not visited 1 visited
		self.board = np.full((rowDimension, colDimension), self.myBoard.UNCOVER)

		self.lastX=startX;
		self.lastY=startY;
		self.lastAction=self.myAction.UNCOVER
		self.visited[startX][startY]=1
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
		print("last action:",self.lastAction,"pos:%d,%d"%(self.lastX+1,self.lastY+1))
		if number==-1 or self.lastAction==self.myAction.FLAG:#if last step is FLAG mine
			self.updateboardboob(self.lastX,self.lastY)
			# print("debug:FLAG Number is:"+str(number))
			self.printBoardInfo(False) 

		if number!=-1:
			FLAGnum=self.countSurroundingTarget(self.lastX,self.lastY,self.myBoard.FLAGBOMB)
			self.board[self.lastX][self.lastY]=number-FLAGnum
			if number-FLAGnum==0:
				self.updateboard(self.visited,self.lastX,self.lastY,self.board,number-FLAGnum)
		# self.printBoardInfo(False) 
		for i in range(self.rowDimension):
			for j in range(self.colDimension):
				# print("%d:%d",i,j)		
				if self.visited[i][j]==0  and  self.board[i][j]==self.myBoard.UNCOVERSAFE:
					self.visited[i][j]=1; 
					self.lastX=i;
					self.lastY=j;
					self.lastAction=self.myAction.UNCOVER
					return Action(AI.Action.UNCOVER,i,j)
		#---------------code above uncovered all available space.

		#deal with concave, like: 
		#1 ? 1
		#1 1 1
		targetX,targetY=self.dealwithconcave();
		if targetX>=0:
			self.visited[targetX][targetY]=1;
			self.lastX=targetX;
			self.lastY=targetY;
			self.board[targetX][targetY]=self.myBoard.FLAGBOMB
			# print("targetX:%d,targetY:%d,board value:%d"%(targetX,targetY,self.board[targetX][targetY]))
			self.lastAction=self.myAction.FLAG
			return Action(AI.Action.FLAG,targetX,targetY)
		# -----------------todo: deal with boarder problems where two 1 line together.
		'''
		0 0 1 ?
		1 1 1 ?
		? ? ? ?
		'''
		for i in range(self.rowDimension):
			for j in range(self.colDimension):
				# print("%d:%d",i,j)		
				if self.visited[i][j]==1  and self.board[i][j]==1:
					toflagX,toflagY=self.linear(i,j,4)#return next flag position.
					if toflagX==-1:
						continue
					# print("success!start point:%d,%d next flag:%d,%d"%(i+1,j+1,toflagX+1,toflagY+1))
					self.visited[toflagX][toflagY]=1;
					self.lastX=toflagX;
					self.lastY=toflagY;
					self.board[toflagX][toflagY]=self.myBoard.FLAGBOMB
					self.lastAction=self.myAction.FLAG
					return Action(AI.Action.FLAG,toflagX,toflagX)
		return Action(AI.Action.LEAVE)
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################
	def linear(self,i,j,count):
		'''
		1->1->1
		or
		1
		1
		1
		'''
		tmpj=j+1;
		while tmpj<self.colDimension:
			if self.board[i][tmpj]!=1:
				tmpj-=1
				break
			tmpj+=1
		if tmpj-j+1==count:
			if i<self.rowDimension-1 and self.board[i+1][j+1]==-1 :
				return i+1,j+1
			if i>0 and  self.board[i-1][j]==-1:
				return i-1,j+1
		tmpi=i+1;
		while tmpi<self.rowDimension :
			if self.board[tmpi][j]!=1:
				tmpi-=1
				break
			tmpi+=1
		if tmpi-i+1==count:
			if j<self.rowDimension-1 and self.board[i][j+1]==-1 :
				return i+1,j+1
			if j>0 and self.board[i][j-1]==-1:
				return i+1,j-1
		return -1,-1
	def updateboard(self,visited,i,j,board,number):
		# for l in range(j,0):#left
			# if board[][j]:
		if number==0:
			if i>0 and self.board[i-1][j]==-1:
				self.board[i-1][j]=self.myBoard.UNCOVERSAFE;
			if j>0 and self.board[i][j-1]==-1:
				self.board[i][j-1]=self.myBoard.UNCOVERSAFE;
			if i<self.rowDimension-1 and self.board[i+1][j]==-1:
				self.board[i+1][j]=self.myBoard.UNCOVERSAFE;
			if j<self.colDimension-1 and self.board[i][j+1]==-1:
				self.board[i][j+1]=self.myBoard.UNCOVERSAFE;
			if i>0 and j>0 and self.board[i-1][j-1]==-1:	
				self.board[i-1][j-1]=self.myBoard.UNCOVERSAFE;
			if i>0 and j<self.colDimension-1 and self.board[i-1][j+1]==-1:	
				self.board[i-1][j+1]=self.myBoard.UNCOVERSAFE;
			if i<self.rowDimension-1 and j>0 and self.board[i+1][j-1]==-1:	
				self.board[i+1][j-1]=self.myBoard.UNCOVERSAFE;
			if i<self.rowDimension-1 and j<self.colDimension-1 and self.board[i+1][j+1]==-1:	
				self.board[i+1][j+1]=self.myBoard.UNCOVERSAFE;
		# return visited,board
	def updateboardboob(self,i,j):
		# for l in range(j,0):#left
			# if board[][j]:
		newzeroboard=[]
		if i>0:
			if self.board[i-1][j]>0: 
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


