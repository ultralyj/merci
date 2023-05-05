# -*- coding: utf-8 -*- #
 
# ------------------------------------------------------------------
# File Name:        main.py
# Author:           罗翊杰(1951578@tongji.edu.cn)
# Version:          0.1
# Created:          2023/3/8
# Description:      Mevis Calibration Unity 
#                   基于PyQt5的一体式磁触觉电子皮肤标定框架
# History:
#       <author>        <version>       <time>      <desc>
#       ultralyj         0.1          2023/3/8      创建控件
# ------------------------------------------------------------------


import sys
import time

# 引用pyqt5界面库                             
from PyQt5.QtGui import QFont, QIcon
# 引用pyqt5控件库
from PyQt5.QtWidgets import (QAction, QApplication, QDesktopWidget,
                             QFileDialog, QGroupBox, QHBoxLayout, QLabel,
                             QMainWindow, QMessageBox, QToolTip, QVBoxLayout,
                             QWidget)
from pyqt_led import Led

from calibration import calibration
from cnc import cnc
from press import press
from skin import skin
#上位机类
from usartConfig import usartConfig


class MevisCalibration(QMainWindow):
    """上位机主窗口
    """
    def __init__(self):
        """
        @brief 构造函数
        """
        super().__init__()
        # 实例化串口控件对象
        self.uartCnc = usartConfig()
        self.uartPress = usartConfig()
        self.uartSkin = usartConfig()
        # 实例化测试台，压力计，电子皮肤控件
        self.hcnc = cnc(self.uartCnc)
        self.hpress = press(self.uartPress)
        self.hskin = skin(self.uartSkin)
        # 实例化标定控件
        self.hcalibration = calibration()
        # 设置窗口
        self.setWindow()
        # 设置窗口布局
        self.setCentralWidget(self.layout())
        # 设置基本操作
        self.setActions()
        self.setMenuBar()
        # 默认端口号（仅供调试）
        # self.uartCnc.setPort('COM11')
        # self.uartPress.setPort('COM10')
        # self.uartSkin.setPort('COM12')
        self.show()
        
    def setActions(self):
        """载入基本操作（打开，保存...）
        """
        self.exitAction = QAction('退出', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.close)
    
    def setMenuBar(self):
        """载入菜单栏
        """
        self.statusBar()
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&文件 ')

        editMenu = menubar.addMenu('&编辑 ')

        helpMenu = menubar.addMenu('&帮助 ')
        helpMenu.addAction(self.exitAction)

    def layout(self):
        """设置主页布局

        Returns:
            QBoxLayout: Qt Layout
        """
        ## 测试台布局（左侧）
        vboxLeft = QVBoxLayout()
        vboxLeft.addWidget(self.uartCnc)
        vboxLeft.addStretch(1)  
        vboxLeft.addWidget(self.hcnc)
        groupMachine = QGroupBox()
        groupMachine.setTitle('测试台')
        groupMachine.setLayout(vboxLeft)
        # 压力计布局（中间上）
        vboxPress = QVBoxLayout()
        vboxPress.addWidget(self.uartPress)
        vboxPress.addWidget(self.hpress)
        groupPress = QGroupBox()
        groupPress.setTitle('压力计')
        groupPress.setLayout(vboxPress)
        # 电子皮肤串口布局（中间下）
        vboxSkin = QVBoxLayout()
        vboxSkin.addWidget(self.uartSkin)
        # vboxSkin.addWidget(self.hskin)
        groupSkin = QGroupBox()
        groupSkin.setTitle('电子皮肤')
        groupSkin.setLayout(vboxSkin)
        # 设备检查指示灯，3灯亮起激活标定面板
        labelMachine = QLabel('测试台')
        labelPress = QLabel('压力计')
        labelSkin = QLabel('电子皮肤')
        self.ledMachine = Led(self,on_color=Led.green, off_color=Led.red, shape=Led.rectangle)
        self.ledPress = Led(self,on_color=Led.green, off_color=Led.red, shape=Led.rectangle)
        self.ledSkin = Led(self,on_color=Led.green, off_color=Led.red, shape=Led.rectangle)
        self.ledMachine.setFixedSize(30,40) 
        self.ledPress.setFixedSize(30,40) 
        self.ledSkin.setFixedSize(30,40)        
        self.hcnc.OnActivate.connect(self.machineActivateCallback)
        self.hpress.OnActivate.connect(self.pressActivateCallback)
        self.hskin.OnActivate.connect(self.skinActivateCallback)
        hboxFushin = QHBoxLayout()
        hboxFushin.addWidget(self.ledMachine)
        hboxFushin.addWidget(labelMachine)
        hboxFushin.addWidget(self.ledPress)
        hboxFushin.addWidget(labelPress)
        hboxFushin.addWidget(self.ledSkin)
        hboxFushin.addWidget(labelSkin)
        # 中间布局组合
        vboxMid = QVBoxLayout()
        vboxMid.addWidget(groupPress)
        vboxMid.addWidget(groupSkin)
        vboxMid.addStretch(1)
        vboxMid.addLayout(hboxFushin)
        vboxMid.addStretch(1) 
        
        #右侧布局
        vboxRight = QVBoxLayout()
        vboxRight.addWidget(self.hcalibration)     
        # 左中右布局排列  
        hboxMain = QHBoxLayout()
        hboxMain.addWidget(groupMachine)
        hboxMain.addLayout(vboxMid)
        hboxMain.addLayout(vboxRight)
        hboxMain.addStretch(1)
        mainWiget = QWidget()
        mainWiget.setLayout(hboxMain)
        return mainWiget

    def setWindow(self):
        """初始化窗口，包括设置字体，窗口
        """
        # 1.设置字体
        self.gloabalFont = QFont()
        self.gloabalFont.setFamily("微软雅黑")  # 括号里可以设置成自己想要的其它字体
        self.gloabalFont.setPointSize(10)
        self.smallFont = QFont()
        self.smallFont.setFamily("微软雅黑")  # 括号里可以设置成自己想要的其它字体
        self.smallFont.setPointSize(9)

        QToolTip.setFont(self.gloabalFont)
        self.setFont(self.gloabalFont)

        # 设置窗口的位置和大小
        self.setFixedSize(1400,1000)

        # 设置窗口的标题
        self.setWindowTitle('Mevis Calibration Unity')

        # 设置窗口的图标，引用当前目录下的web.png图片
        self.setWindowIcon(QIcon('mt.png'))

        # 移到中心
        qr = self.frameGeometry()
        # 获得屏幕中心点
        cp = QDesktopWidget().availableGeometry().center()
        # 显示到屏幕中心
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def closeEvent(self, event):

        reply = QMessageBox.question(self, '关闭提示',
                                     "确定要退出吗?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def machineActivateCallback(self, state):
        """ 测试台激活回调函数

        Args:
            state (_type_): led状态
        """
        # 
        if(state):
            self.ledMachine.turn_on()
            self.checkDemarcate()
        else:
            self.ledMachine.turn_off()

    def pressActivateCallback(self, state):
        """ 压力计激活回调函数

        Args:
            state (_type_): led状态
        """
        if(state):
            self.ledPress.turn_on()
            self.checkDemarcate()
        else:
            self.ledPress.turn_off()
    
    def skinActivateCallback(self, state):
        """皮肤激活回调函数

        Args:
            state (_type_): led状态
        """
        if(state):
            self.ledSkin.turn_on()
            self.checkDemarcate()
        else:
            self.ledSkin.turn_off() 
    
    def checkDemarcate(self):
        """当测试台，压力计，皮肤全部连接，激活标定仪表界面
        """
        if(self.ledSkin.is_on() and 
           self.ledMachine.is_on() and
           self.ledPress.is_on()):
            time.sleep(1)
            self.hcalibration.activate(self.hcnc,self.hpress,self.hskin)
            
if __name__ == '__main__':
    # 创建应用程序和对象
    app = QApplication(sys.argv)
    ex = MevisCalibration()
    sys.exit(app.exec_())
