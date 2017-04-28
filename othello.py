# -*- coding:utf-8 -*-
# Othello.py

#import standard packages
import os

class Othello():
    def __init__(self):
       
        self.N = 8
        self.WHITE = "0"
        self.BLACK = "1"
        self.EMPTY = "*"
        self.initOthello()

    def initOthello(self):
        self.who = self.BLACK
        self.board = []
        self.game_over = False

        for i in range(self.N):
            self.board.append(['*'] * self.N)
        self.board[3][3] = self.board[4][4] = self.WHITE
        self.board[4][3] = self.board[3][4] = self.BLACK

    def isOnBoard(self,x,y):
        return x > -1 and x < self.N and y > -1 and y < self.N

    def isEmpty(self,x,y):
        return self.board[x][y] == self.EMPTY

    def isBlack(self , x =-1 ,y= -1):
        if self.isOnBoard(x,y):
            return self.board[x][y] == self.BLACK
        return self.who == self.BLACK

    def isWhite(self ,x=-1,y=-1):
        if self.isOnBoard(x,y):
            return self.board[x][y] == self.WHITE
        return self.who == self.WHITE

    def opponent(self,role):
        if role == self.BLACK:
            return self.WHITE
        return self.BLACK

    def isValid(self,role,x,y):
        ready_for_reverse = []
        if (not self.isOnBoard(x,y)) or self.board[x][y] != self.EMPTY:
            return ready_for_reverse

        opponent = self.opponent(role)
        directions =[ [0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1] ]

        for _x , _y in directions:
            t_x , t_y  = x , y
            t_x += _x
            t_y += _y
            if not self.isOnBoard(t_x, t_y) or self.board[t_x][t_y] != opponent:
                continue

            t_x += _x
            t_y += _y
            if not self.isOnBoard(t_x,t_y):
                continue
            while self.board[t_x][t_y] == opponent:
                t_x += _x
                t_y += _y
                if not self.isOnBoard(t_x,t_y):
                    break
            if self.isOnBoard(t_x,t_y) and self.board[t_x][t_y] == role:
                while(t_x != x or t_y != y):
                    t_x -= _x
                    t_y -= _y
                    ready_for_reverse.append((t_x,t_y))
        return ready_for_reverse

    def availablePositions(self,role):
        
        pos = []
        for x in range(self.N):
            for y in range(self.N):
                reverse_pieces = self.isValid(role,x,y)
                if len(reverse_pieces) < 1:
                    continue
                pos.append((x,y))
        return pos
    
    def remain(self,role):
        available = []
        for x in range(self.N):
            for y in range(self.N):
                reverse = self.isValid(role, x, y)
                if len(reverse) < 1:
                    continue
                available.append(x * 8 + y);
        return available

    def setWhoTurn(self):
       
        role = self.opponent(self.who)
        pos = self.availablePositions(role)
        if len(pos) > 0 :
            self.who = role
        elif len(pos) == 0:
            self.game_over = True
        return pos

    def setWhoFirst(self,who = None):
     
        if who:
            self.who = who
        else:
            self.who = self.opponent(self.who)

    def placePiece(self,x,y):
        if self.game_over:
            print('game over')
        else:
            ready_for_reverse = self.isValid(self.who,x,y)
            if len(ready_for_reverse):
                self.board[x][y] = self.who
                for _x ,_y in ready_for_reverse:
                    self.board[_x][_y] = self.who
            return ready_for_reverse
    
    def exchange(self):
        self.who = self.opponent(self.who)
    
    def get_hashed_state(self):
        return ''.join([''.join(map(str,_))for _ in self.board])
    
    def get_cur_player(self):
        return self.who
    
    def getWinner(self):
        black_score = 0
        white_score = 0
        for i in range(0,8):
            for j in range(0,8):
                if self.board[i][j] == self.BLACK:
                    black_score += 1
                else:
                    white_score += 1
        if black_score > white_score:
            return self.BLACK
        elif black_score < white_score:
            return self.WHITE    





