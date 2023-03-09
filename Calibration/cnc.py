# -*- coding: utf-8 -*- #
 
# ------------------------------------------------------------------
# File Name:        cnc.py
# Author:           罗翊杰(1951578@tongji.edu.cn)
# Version:          0.1
# Created:          2023/3/8
# Description:      测试台控件
# History:
#       <author>        <version>       <time>      <desc>
#       ultralyj         0.1          2023/3/8      创建控件
# ------------------------------------------------------------------

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QButtonGroup, QGridLayout, QGroupBox, QHBoxLayout,
                             QLabel, QPlainTextEdit, QPushButton, QRadioButton,
                             QVBoxLayout, QWidget)

from usartConfig import usartConfig


class cnc(QWidget):
    """测试台控件
    """
    OnActivate = pyqtSignal(bool)
    def __init__(self, uart:usartConfig):
        """初始化控件

        Args:
            uart (usartConfig): 串口控件
        """
        super().__init__()
        # 载入串口控件
        self.uart = uart
        # 压头坐标与进给率
        self.probe = {
            'x':0.0,
            'y':0.0,
            'z':0.0,
            'step':0,
            'feed':0
        }
        # 设置字体
        self.smallFont = QFont()
        self.smallFont.setFamily("微软雅黑")  
        self.smallFont.setPointSize(9)
        self.gloabalFont = QFont()
        self.gloabalFont.setFamily("微软雅黑")  
        self.gloabalFont.setPointSize(10)
        # 设置控件布局
        self.setLayout(self.layout())
        # 设置控件交互功能
        self.connect()
        # 设置控件宽度
        self.setFixedWidth(400)

    def layout(self):
        """设置控件布局

        Returns:
            QBoxLayout: Qt控件对象
        """
        # 左侧：X-Y平面手动操控按钮
        self.buttonUp = QPushButton('↑')
        self.buttonDown = QPushButton('↓')
        self.buttonLeft = QPushButton('←')
        self.buttonRight = QPushButton('→')
        self.buttonStop = QPushButton('X')  # 急停
        # 布局，打包
        gridDirection = QGridLayout()
        gridDirection.addWidget(self.buttonUp,1,2)
        gridDirection.addWidget(self.buttonDown,3,2)
        gridDirection.addWidget(self.buttonLeft,2,1)
        gridDirection.addWidget(self.buttonRight,2,3)
        gridDirection.addWidget(self.buttonStop,2,2)
        groupManual = QGroupBox()
        groupManual.setTitle('X-Y')
        groupManual.setFont(self.smallFont)
        groupManual.setLayout(gridDirection)
        groupManual.setFixedWidth(200)
        
        # 右侧：Z轴手动操控按钮
        self.buttonLift = QPushButton('↑')
        self.buttonDescend = QPushButton('↓')
        # 布局，打包
        gridZaxis = QGridLayout()
        gridZaxis.addWidget(self.buttonLift,1,1)
        gridZaxis.addWidget(self.buttonDescend,2,1)
        groupZ = QGroupBox()
        groupZ.setTitle('Z')
        groupZ.setFont(self.smallFont)
        groupZ.setLayout(gridZaxis)
        groupZ.setFixedWidth(100)
        
        # 第一行：手动操控按钮组布局
        hboxManual= QHBoxLayout()
        hboxManual.addWidget(groupManual)
        hboxManual.addWidget(groupZ)
        
        # 第二行：步长选择按钮组
        labelStep = QLabel('step')
        self.btnStepn1 = QRadioButton('0.1')
        self.btnStep1 = QRadioButton('1')
        self.btnStep10 = QRadioButton('10')
        self.btnStep1.setChecked(True)
        # 打包按钮组
        self.groupButtonStep= QButtonGroup()
        self.groupButtonStep.addButton(self.btnStepn1,0)
        self.groupButtonStep.addButton(self.btnStep1,1)
        self.groupButtonStep.addButton(self.btnStep10,2)
        # 按钮组布局
        hboxStep = QHBoxLayout()
        hboxStep.addWidget(labelStep)
        hboxStep.addWidget(self.btnStepn1)
        hboxStep.addWidget(self.btnStep1)
        hboxStep.addWidget(self.btnStep10)
        hboxStep.addStretch(1)

        # 第三行：进给率选择按钮组
        labelFeed = QLabel('feed')
        self.btnf10 = QRadioButton('10')
        self.btnf100 = QRadioButton('100')
        self.btnf500 = QRadioButton('500')
        self.btnf500.setChecked(True)
        # 打包按钮组
        self.groupButtonFeed= QButtonGroup()
        self.groupButtonFeed.addButton(self.btnf10,0)
        self.groupButtonFeed.addButton(self.btnf100,1)
        self.groupButtonFeed.addButton(self.btnf500,2)
        # 按钮组布局
        hboxf = QHBoxLayout()
        hboxf.addWidget(labelFeed)
        hboxf.addWidget(self.btnf10)
        hboxf.addWidget(self.btnf100)
        hboxf.addWidget(self.btnf500)
        hboxf.addStretch(1)
        
        # 第四，五行：数值设置
        labelXp = QLabel('x:')
        labelYp = QLabel('y:')
        labelZp = QLabel('z:')
        self.lineXp = QPlainTextEdit('0.00')
        self.lineXp.setFixedHeight(46)
        self.lineYp = QPlainTextEdit('0.00')
        self.lineYp.setFixedHeight(46)
        self.lineZp = QPlainTextEdit('0.00')
        self.lineZp.setFixedHeight(46)
        self.lineZp.setFixedWidth(125)
        self.buttonSetPositon = QPushButton('定位')
        self.buttonSetPositon.setFixedWidth(125)
        # 布局
        hboxPosition1 = QHBoxLayout()
        hboxPosition1.addWidget(labelXp)
        hboxPosition1.addWidget(self.lineXp)
        hboxPosition1.addWidget(labelYp)
        hboxPosition1.addWidget(self.lineYp)
        hboxPosition2 = QHBoxLayout()
        hboxPosition2.addWidget(labelZp)
        hboxPosition2.addWidget(self.lineZp)
        hboxPosition2.addStretch(1)
        hboxPosition2.addWidget(self.buttonSetPositon)
        
        # 控件组合，并打包
        vboxCnc = QVBoxLayout()
        vboxCnc.addLayout(hboxManual)
        vboxCnc.addLayout(hboxStep)
        vboxCnc.addLayout(hboxf)
        vboxCnc.addLayout(hboxPosition1)
        vboxCnc.addLayout(hboxPosition2)
        groupManual = QGroupBox()
        groupManual.setTitle('测试台手动控制')
        groupManual.setFont(self.smallFont)
        groupManual.setLayout(vboxCnc)

        # 输出控件
        vboxCncAll = QVBoxLayout()
        vboxCncAll.addWidget(groupManual)
        return vboxCncAll

    def connect(self):
        """设置控件交互相关功能
        """
        # 设置默认步长与进给率
        self.probe['feed']=500.0
        self.probe['step']=1
        # 设置手动操作按钮组点击响应
        self.buttonUp.clicked[bool].connect(lambda: self.manualEvent('UP'))
        self.buttonDown.clicked[bool].connect(lambda: self.manualEvent('DW'))
        self.buttonLeft.clicked[bool].connect(lambda: self.manualEvent('LF'))
        self.buttonRight.clicked[bool].connect(lambda: self.manualEvent('RT'))
        self.buttonLift.clicked[bool].connect(lambda: self.manualEvent('LT'))
        self.buttonDescend.clicked[bool].connect(lambda: self.manualEvent('DS'))
        self.buttonStop.clicked[bool].connect(lambda: self.manualEvent('STOP'))
        self.buttonSetPositon.clicked[bool].connect(lambda: self.manualEvent('SET'))
        # 设置步长，进给率选择响应
        self.groupButtonStep.buttonClicked[int].connect(lambda: self.stepEvent())
        self.groupButtonFeed.buttonClicked[int].connect(lambda: self.feedEvent())
        # 串口连接信号响应
        self.uart.status.connect(self.uartStateChanged)
        # 默认关闭控件
        self.setDisabled(True)
        
    def uartStateChanged(self,act:str):
        """串口状态改变信号响应函数

        Args:
            act (str): 串口状态 'ON' or 'OFF'
        """
        if(act == 'OFF'):
            self.setDisabled(True)
            self.OnActivate.emit(False)
        if(act == 'ON'):
            self.setEnabled(True)
            self.OnActivate.emit(True)
            
    def manualEvent(self, act:str):
        """控制台按键回调函数

        Args:
            act (str): 按键代号
        """
        # 控制测试台对应串口必须开启
        if(self.uart.ser.isOpen() == True):
            if(act == 'UP'):
                # 根据步长改变当前坐标
                self.probe['y'] += self.probe['step']
                # 发送G-Code到测试台
                self.send(bytes("G01 y%.1f f%.f\r\n" % (self.probe['y'],self.probe['feed']),'ascii'))
            if(act == 'DW'):
                self.probe['y'] -= self.probe['step']
                self.send(bytes("G01 y%.1f f%.f\r\n" % (self.probe['y'],self.probe['feed']),'ascii'))
            if(act == 'LF'):
                self.probe['x'] -= self.probe['step']
                self.send(bytes("G01 x%.1f f%.f\r\n" % (self.probe['x'],self.probe['feed']),'ascii'))
            if(act == 'RT'):
                self.probe['x'] += self.probe['step']
                self.send(bytes("G01 x%.1f f%.f\r\n" % (self.probe['x'],self.probe['feed']),'ascii'))
            if(act == 'LT'):
                self.probe['z'] += self.probe['step']
                self.send(bytes("G01 z%.1f f%.f\r\n" % (self.probe['z'],self.probe['feed']),'ascii'))
            if(act == 'DS'):
                self.probe['z'] -= self.probe['step']
                self.send(bytes("G01 z%.1f f%.f\r\n" % (self.probe['z'],self.probe['feed']),'ascii'))
            if(act == 'STOP'):
                # GRBL急停命令
                self.send(b'!')
            if(act == 'SET'):
                # 获取文本框的xyz坐标
                x = float(self.lineXp.toPlainText())
                y = float(self.lineYp.toPlainText())
                z = float(self.lineZp.toPlainText())
                # 发送信息到测试台
                if(abs(x)<300 and abs(y)<300 and abs(z)<100):
                    self.probe['x'] = x
                    self.probe['y'] = y
                    self.probe['z'] = z
                    self.send(bytes("G01 x %.1f y%.1f z%.1f f%.f\r\n" % 
                                    (self.probe['x'],self.probe['y'],self.probe['z'],self.probe['feed']),'ascii'))
            # 更新文本框内信息
            self.updateProbeLines()
    
    def stepEvent(self):
        """步长改变事件，设置新的步长
        """
        id = self.groupButtonStep.checkedId()
        if(id == 0):
            self.probe['step'] = 0.1
        if(id == 1):
            self.probe['step'] = 1
        if(id == 2):
            self.probe['step'] = 10
    
    def feedEvent(self):
        """进给率改变事件，设置新的进给率
        """
        id = self.groupButtonFeed.checkedId()
        if(id == 0):
            self.probe['feed'] = 10
        if(id == 1):
            self.probe['feed'] = 100
        if(id == 2):
            self.probe['feed'] = 500
                    
    def send(self, cmd:bytes):
        """串口发送GRBL,G-Code命令

        Args:
            cmd (bytes): 命令
        """
        if(not(self.uart is None)):
            self.uart.send(cmd)
    
    def updateProbeLines(self):
        """更新文本框内信息
        """
        self.lineXp.setPlainText('%03.01f'%(self.probe['x']))
        self.lineYp.setPlainText('%03.01f'%(self.probe['y']))
        self.lineZp.setPlainText('%02.01f'%(self.probe['z']))
    
    def setPosition(self,x:float,y:float,z:float,f:float):
        """设置坐标

        Args:
            x (float): 测试台x坐标
            y (float): 测试台y坐标
            z (float): 测试台z坐标
            f (float): 进给率
        """
        if(abs(x)<300 and abs(y)<300 and abs(z)<100):
            # 更新进给率选择
            if(f==10):
                self.btnf10.setChecked(True)
            if(f==100):
                self.btnf100.setChecked(True)
            if(f==500):
                self.btnf500.setChecked(True)
            # 同步末端坐标
            self.probe['feed'] = f
            self.probe['x'] = x
            self.probe['y'] = y
            self.probe['z'] = z
            # 更新文本框内容
            self.lineXp.setPlainText('%03.01f'%(self.probe['x']))
            self.lineYp.setPlainText('%03.01f'%(self.probe['y']))
            self.lineZp.setPlainText('%02.01f'%(self.probe['z']))
            # 发送G-Code
            self.send(bytes("G01 x %.1f y%.1f z%.1f f%.f\r\n" % 
                (self.probe['x'],self.probe['y'],self.probe['z'],self.probe['feed']),'ascii'))