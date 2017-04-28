# -*- coding:utf-8 -*-
import time
import sys
import copy
import json
from random import choice, shuffle
from math import log, sqrt
import string


from PyQt4.QtCore import *
from PyQt4.QtGui import *
from othello import Othello
from copy import deepcopy

UI_WIDTH = 800
UI_HEIGHT = UI_WIDTH * 0.72
BOARD_WIDTH = UI_WIDTH * 0.53
BOARD_BORDER = BOARD_WIDTH * 0.07925
BOARD_L = BOARD_WIDTH * 0.1052

REC_BUFFER_SIZE = 8192

class Game(QMainWindow):
    def __init__(self,host="localhost",port=9999,nickname="wa"):
        super(Game, self).__init__()
        #常量
        self.BLACK = 'images/black.png'
        self.WHITE = 'images/white.png'
        self.ME ="me"
        self.YOU = "you"
        self.ADMIN = "admin"
        #是否正在进行游戏
        self.nickname = nickname
        self.opponent = {
            'nickname':'',
            'client_id':'',
            'role':'',
        }
        self.host = str(host)
        self.port = int(port)
        self.playing = False
        # 设置标题、图标等
        self.setWindowTitle('黑白棋')
        self.setWindowIcon(QIcon('images/icon.jpg'))
        # 创建布局
        self.createGrid()
        # 创建菜单
        self.createMenu()
        #导入样式表
        self.createStyleQss()
        # 初始化类
        self.initGame()
        # 网络连接，并且为网络连接单独建立一个线程


    def initGame(self):
        self.statusBar().showMessage("准备就绪")
        self.setTurnImage(self.BLACK)
        self.displayScores(2,2)


        self.playing = False

    def restartGame(self):
        #重新开始游戏，初始化 Game、Othello、Board、Controller
        self.initGame()
        self.othello.initOthello()
        self.board.initBoard(self.othello)

    def createStyleQss(self):
        file = open('style.css','r')
        style = file.read()
        qApp.setStyleSheet(style)
        file.close()



    def createGrid(self):
        def btn_restart_game():
            if self.playing:
                self.packAndSend({
                    'to':self.opponent['client_id'],
                    'action':'restart',
                    'value': 'apply'
                })
            else:
                QMessageBox.information(self,'系统消息',"没有加入任何游戏")
                self.restartGame()
        def btn_leave_game():
            if self.playing:
                self.packAndSend({
                    'to':self.opponent['client_id'],
                    'action':'leave',
                    'value': ''
                })
                self.restartGame()
            else:
                QMessageBox.information(self,'系统消息',"没有加入任何游戏")
        #设置主窗口的大小与位置
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry( (screen.width() - UI_WIDTH)/2 ,( screen.height() - UI_HEIGHT )/2,UI_WIDTH,UI_HEIGHT)
        self.setFixedSize(UI_WIDTH,UI_HEIGHT)
        #创建布局
        main = QWidget(self)
        main.setObjectName('main')
        self.setCentralWidget(main)
        self.othello = Othello()
        self.board = Board(main,self.othello)

        #创建应该下子的图片标志，初始化为黑子
        pic = QLabel(self)
        pic.setGeometry(UI_WIDTH*0.212,UI_HEIGHT*0.12,50,50)
        pic.setObjectName('label_for_turn_image')

        #创建功能按钮
        buttons = QWidget(self)
        buttons.setGeometry(UI_WIDTH*0.77,UI_HEIGHT*0.4,UI_WIDTH*0.2,UI_HEIGHT*0.12)
        buttons.setObjectName('buttons')
        grid = QGridLayout()
        buttons.setLayout(grid)
        #创建分数显示屏,包括黑棋得分，黑棋昵称，白棋得分，白棋昵称
        self.score_black = QLabel(self)
        self.score_black.setObjectName('score_black')
        self.score_black.setGeometry(UI_WIDTH*0.08,UI_HEIGHT*0.25,100,60)
        self.nickname_black = QLabel("<p style='text-align:center'>黑棋</p>",self)
        self.nickname_black.setObjectName('nickname_black')
        self.nickname_black.setGeometry(UI_WIDTH*0.03,UI_HEIGHT*0.36,120,60)

        self.score_white = QLabel(self)
        self.score_white.setObjectName('score_white')
        self.score_white.setGeometry(UI_WIDTH*0.08,UI_HEIGHT*0.57,100,60)
        self.nickname_white = QLabel("<p style='text-align:center'>白棋</p>",self)
        self.nickname_white.setObjectName('nickname_white')
        self.nickname_white.setGeometry(UI_WIDTH*0.03,UI_HEIGHT*0.68,120,60)
        self.move_record =  QTextEdit("当前下子情况",self)
        self.move_record.setReadOnly(True)
        #显示走棋的位置
        self.move_record =  QTextEdit("下子情况",self)
        self.move_record.setObjectName("move_record")
        self.move_record.setReadOnly(True)
        self.move_record.setGeometry(UI_WIDTH*0.765,UI_HEIGHT*0.24,UI_WIDTH*0.215,UI_HEIGHT*0.15)

        #创建输入框
        chat = QWidget(self)
        chat.setObjectName('chat')
        chat.setGeometry(UI_WIDTH*0.755,UI_HEIGHT*0.54,UI_WIDTH*0.235,UI_HEIGHT*0.45)
        grid = QGridLayout()
        chat.setLayout(grid)
        
        
    def createMenu(self):
        def quitGame():
            #退出信号槽函数
            reply = QMessageBox.question(self,'问题','想要退出吗',QMessageBox.Yes,QMessageBox.No)
            if reply == QMessageBox.Yes:
                qApp.quit()

        def aboutUs():
            QMessageBox.about(self,'关于作者',str(self))

        menubar = self.menuBar()
        #主菜单
        main_menu = menubar.addMenu('&主菜单')
        main_menu.addAction(QAction(QIcon('images/icon.jpg'),'退出',
                                 self, statusTip="退出黑白棋游戏", triggered=quitGame))
        #关于菜单
        about_menu = menubar.addMenu('&关于')
        about_menu.addAction(QAction(QIcon('images/icon.jpg'),'作者',
                                 self, statusTip="作者信息", triggered=aboutUs))

    def setTurnImage(self,turn_image=None):
        if turn_image:
            pic_l = 30
            pic = self.findChild(QLabel,'label_for_turn_image')
            pic.setPixmap(QPixmap(turn_image).scaled(pic_l,pic_l))
        else:
            game_othello.setWhoFirst()
            QMessageBox.information(self,"提示","已选择" + ("黑棋" if game_othello.isBlack() else "白棋") + "优先")
            if game_othello.isBlack():
                self.setTurnImage(self.BLACK)
            else:
                self.setTurnImage(self.WHITE)

    def displayScores(self,black=0,white=0):
        #显示分数
        if not ( black and white):
            n = game_othello.N
            black = white = 0
            for x in range(n):
                for y in range(n):
                    if game_othello.isBlack(x,y):
                        black += 1
                    elif game_othello.isWhite(x,y):
                        white += 1
        self.score_white.setText(str('%02d' % white))
        self.score_black.setText(str('%02d' % black))
        return black,white

    def getBoard(self):
        #返回棋局
        return self.board

    def getOthello(self):
        #返回逻辑五子棋
        return self.othello

    def keyPressEvent(self,event):
        key = event.key()
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            self.chat()

    def isTurnMe(self):
        return (game_othello.isBlack() and self.opponent['role'] == "white" ) \
               or (game.othello.isWhite() and self.opponent['role'] == "black")

   

    


class Board(QWidget):
    def __init__(self,parent=None,othello = None):
        super(Board,self).__init__(parent)
        #设置常量
        self.setObjectName('board')

        self.BLACK = "images/black.png"
        self.WHITE = "images/white.png"
        self.READY = "images/available_pos.png"
        #初始化棋盘
        self.initBoard(othello)
        self.isWhoTurn = "black"

    def paintEvent(self,event):
        painter=QPainter(self)
        painter.drawPixmap(0,0,QPixmap("images/board.jpg").scaled(BOARD_WIDTH,BOARD_WIDTH))
        self.move(UI_WIDTH * 0.201 ,UI_HEIGHT * 0.1 )

    def initBoard(self,othello):
        #初始化棋盘
        n = othello.N
        for x in range(n):
            for y in range(n):
                if othello.isBlack(x,y):
                    self.placePieceImage(x, y, self.BLACK)
                elif othello.isWhite(x,y):
                    self.placePieceImage(x, y, self.WHITE)
                else:
                    label = self.getPiece(x, y)
                    if label:
                        label.hide()
        #记录上一次可以落子的位置
        self.last_available_pos = []

    def mousePressEvent(self,event):
#         if not game.playing:
#             QMessageBox.information(self,"警告","您未加入任何棋局，点击大厅可加入")
#             return
#         if not game.isTurnMe():
#             QMessageBox.information(self,"警告","等待对方走棋")
#             return

        _x = event.x()
        _y = event.y()
        x = round((_x - BOARD_BORDER - BOARD_L/2 )/BOARD_L )
        y = round((_y - BOARD_BORDER - BOARD_L/2)/BOARD_L )
        #下子
        if self.isWhoTurn == "black":
            self.placePiece(x,y)
        if self.isWhoTurn == "white":
            move = ai.get_action()
            if move[0] != -1:
                self.placePiece(move[0],move[1])

    def placePiece(self,x,y):
        #返回可以翻转的子
        ready_for_reverse = game_othello.placePiece(x, y)
        if ready_for_reverse and len(ready_for_reverse):
            
            #如果可以下子，则下子
            if game_othello.isBlack():
                self.placePieceImage(x, y, self.BLACK)
                for i,j in ready_for_reverse:
                    self.placePieceImage(i, j, self.BLACK)
                game.move_record.append("黑棋落子 %d %d"% (x+1,y+1))
                self.isWhoTurn = "white"
            else:
                self.placePieceImage(x, y, self.WHITE)
                for i,j in ready_for_reverse:
                    self.placePieceImage(i, j, self.WHITE)
                game.move_record.append("白棋落子 %d %d"% (x+1,y+1))
                self.isWhoTurn = "black"
            #显示分数，并且判断游戏是否结束
#             game_othello.exchange()
            b_score , w_score = game.displayScores()
            available_pos = game_othello.setWhoTurn()
            #判断游戏是否结束
            if not game_othello.game_over:
                if game_othello.isBlack():
                    game.setTurnImage(game.BLACK)
                else:
                    game.setTurnImage(game.WHITE)
                #游戏未结束，显示下一个可下子的地方
                for i,j in self.last_available_pos:
                    if not( i == x and j == y) :
                        self.getPiece(i,j).hide()
                for i,j in available_pos:
                    self.placePieceImage(i, j, self.READY)
                self.last_available_pos = available_pos
            else:
                for i,j in self.last_available_pos:
                    if not( i == x and j == y) :
                        self.getPiece(i,j).hide()
                win = "黑棋胜" if b_score > w_score else "白棋胜"
                if b_score == w_score:
                    win = "和局"
                game_over_info = "游戏结束\r\n" + win + "\r\n"
                QMessageBox.question(self,'警告',game_over_info,QMessageBox.Yes)
            if not len(available_pos):
                for i,j in self.last_available_pos:
                    if not( i == x and j == y) :
                        self.getPiece(i,j).hide()
                win = "黑棋胜" if b_score > w_score else "白棋胜"
                if b_score == w_score:
                    win = "和局"
                game_over_info = "游戏结束\r\n" + win + "\r\n"
                QMessageBox.question(self,'警告',game_over_info,QMessageBox.Yes)
                ai.writeStates()
        else:
            #不能下子，弹出提醒
            QMessageBox.question(self,'警告','这个地方不能下子哟哟哟',QMessageBox.Yes)
            
            print("不能下子",game_othello.who,x,y)
            if(game_othello.who == "0"):
                move = ai.get_action()
                if move[0] != -1:
                    self.placePiece(move[0],move[1])

    def placePieceImage(self, x, y, image):
        #下子，如果该标签存在，则替换图片，不存在，则新建
        label = self.getPiece(x, y)
        pixmap = QPixmap(image).scaled(BOARD_L,BOARD_L)
        if not label:
            label = QLabel(self)
            label.setGeometry( x*BOARD_L + BOARD_BORDER ,y*BOARD_L + BOARD_BORDER,BOARD_L,BOARD_L)
            label.setPixmap(pixmap)
            label.setObjectName('point_' + str(x) +'_' + str(y) )
            label.show()
        else:
            label.setPixmap(pixmap)
            label.show()
        return label

    def getPiece(self, x, y):
        #判断标签是否存在
        return self.findChild(QLabel , 'point_' + str(x) +'_' + str(y))  


class MCTS(object):
    def __init__(self,othello,play_turn,max_actions = 1000):
        self.othello = game_othello
        self.play_turn = play_turn
        self.player_cur = play_turn[0]
        self.max_actions = max_actions
        self.calculation_time = float(1)
        self.avaliable = game_othello.availablePositions("0")
        
        self.player = play_turn[0]
        self.confident = 1.414
        self.max_depth = 1
        self.plays = {}
        self.wins = {}
        self.readStates()
        self.writeStates()
    
    def writeStates(self):
        try:
            states = open("states.txt","w")
            wins = open("wins.txt","w")
            for key,count in self.plays.items():
                temp = (key[0],key[1],count)
                states.write("%s,%s,%d"%(key[0],key[1],count))
            for key,count in self.wins.items():
                wins.write("%s,%s,%d"%(key[0],key[1],count))
            states.close()
            wins.close()
        except IOError:
            pass
        
    
    def readStates(self):
        try:
            states = open('states.txt')
            wins = open('wins.txt')
            for each_line in states:
                try:
                    
                    player,state,count = each_line.split(",")
                    value = int(count)
                    self.plays[(player,state)] = value
                except ValueError:
                    pass
            for each_line_ in wins:
                try:
                    player,state,count=each_line_.split(",")
                    value = int(count)
                    self.wins[(player,state)] = value
                except ValueError:
                    pass
        except IOError:
            pass
        states.close()
        wins.close()
    def get_action(self):
        if len(self.othello.availablePositions(self.player)) == 1:
            return self.othello.availablePositions(self.player)[0]
        
        simulations = 0
        begin = time.time()
        self.othello = copy.deepcopy(game_othello)
        self.avaliable = self.othello.availablePositions("0")
        i = 0
        if len(self.avaliable)==1:
            return self.avaliable.pop()
        while time.time() - begin < self.calculation_time:
            self.run_simulation()
            simulations += 1
            i += 1
        move = self.run_simulation(get_one=True)
        return move   
    
    def get_player(self,players):
        p = players.pop(0)
        players.append(p)
        return p
            
    def run_simulation(self,get_one=False):
        othello = deepcopy(self.othello)
        play_turn = deepcopy(self.play_turn)
        plays = self.plays
        wins = self.wins
#         
#         player = self.get_player(play_turn)
#         self.othello.exchange()
        availables = othello.availablePositions(play_turn)
        player = self.player
        self.othello.exchange()
        visited_states = set()
        winner = -1
        expand = True
        move = [-1,-1]
        cur_key = (0,0)
        next_key = (player,othello.get_hashed_state())
        for t in range(1,self.max_actions + 1):
            availables = othello.availablePositions(player)
            cur_key = next_key
            if len(availables) <= 1:
                if len(availables) == 1:
                    move = availables.pop()
                    
                if len(availables) == 0:
                    winner = othello.getWinner()
                    break
            elif self.plays.get(cur_key):
                log_total,val = log(self.plays.get(cur_key)),0
                for item in availables:
                    temp_othello = copy.deepcopy(othello)
                    temp_othello.placePiece(item[0],item[1])
                    temp_othello.exchange()
                    tmp_key = (temp_othello.get_cur_player(),temp_othello.get_hashed_state())
                    if self.plays.get(tmp_key):
                        temp_val = ( self.wins[tmp_key]/self.plays[tmp_key]) + self.confident * sqrt(2*log_total/self.plays[tmp_key])
                    else:
                        temp_val = self.confident*sqrt(log_total)
                    del temp_othello
                    
                    if temp_val > val:
                        val = temp_val
                        move = item
                if  val == 0:
                    move = choice(availables)
             
            else:
                move = choice(availables)
            if get_one:
                return move    
            visited_states.add(cur_key)
            othello.placePiece(move[0],move[1])
            othello.exchange()
            availables = othello.availablePositions(othello.who)
            
            #游戏结束
            if not len(availables):
                if player == othello.getWinner():
                    winner = player
                break
            next_key = (othello.get_cur_player(),othello.get_hashed_state())
            if expand and cur_key not in self.plays:
                expand = False
                self.plays[cur_key] = 0
                self.wins[cur_key] = 0
        visited_states.add(cur_key)
        for state in visited_states:
            if state not in self.plays:continue
            self.plays[state] += 1
            #AI获胜过
            if winner == player:
                self.wins[state] += 1
                
            
                   

            
                
        
        
    
    def select_one_move(self):
        maxvalue = 0
        res = [-1,-1]
        self.avaliable = game_othello.availablePositions("0")
        for move in self.avaliable:
            tempvalue = move[0] * 8 + move[1]
            value1 = self.wins.get((self.player_cur,tempvalue),0)
            value2 = self.plays.get((self.player_cur,tempvalue),1)
            value = value1 / value2
            if value >= maxvalue:
                maxvalue = value
                res = move        
        return res      
    
        
class GetDataWorker(QThread):
    dataSignal = pyqtSignal(str)

    def __init__(self,client):
        super(GetDataWorker , self).__init__()
        self.client = client

    def run(self):
        while True:
            buf = self.client.recv(REC_BUFFER_SIZE)
            if len(buf):
                self.dataSignal.emit(buf.decode("utf8"))

def startGame():
    global game,game_othello,game_board,ai
    
    game = Game()
    game_board = game.getBoard()
    game_othello = game.getOthello()
    ai = MCTS(game_othello,["0","1"])
    game.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    startGame()
    sys.exit(app.exec_())
    
        
        
        
                        
