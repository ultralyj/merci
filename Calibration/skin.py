# -*- coding: utf-8 -*- #
 
# ------------------------------------------------------------------
# File Name:        skin.py
# Author:           罗翊杰(1951578@tongji.edu.cn)
# Version:          0.1
# Created:          2023/3/8
# Description:      电子皮肤控件
# History:
#       <author>        <version>       <time>      <desc>
#       ultralyj         0.1          2023/3/8      创建控件
# ------------------------------------------------------------------

import serial
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from usartConfig import usartConfig


class SkinThread(QThread):
    """电子皮肤测量线程
    """
    measurement = pyqtSignal(list)
    def __init__(self):
        """初始化线程
        """
        super(SkinThread,self).__init__()
        # 串口句柄（串口在线程内创建）
        self.ser = None
        self.baudSelect = 115200
        self.portSelect = 'COM0'
        # 电子皮肤数据容器
        self.data = []
        self.working = False
    def run(self):
        """线程运行函数
        """
        # 打开串口
        self.ser=serial.Serial(self.portSelect,self.baudSelect,timeout=0.5)
        # 判断串口是否成功打开
        if self.ser.isOpen():                      
            print("open serial:",self.ser.port,'successfully')
        else:
            print("open serial failed")
        # 初始化，进入循环测量
        self.working = True
        while(self.working == True):
            try:
                 # 读取数据帧
                frame = str(self.ser.readline(),'ascii')
                # 分割数据并转化为浮点数列表
                dataRaw = list(map(float, frame[:-1].split(',')))
                # 数据求和校验
                if(len(dataRaw)==13 and abs(sum(dataRaw[:-1])-dataRaw[-1])<1.0):
                    self.data = dataRaw
                    self.measurement.emit(self.data)
            except Exception as e:
                # 如果出现无法读取的情况，停止循环测量
                print(e)
                self.working = False
        # 关闭串口
        self.ser.close()
        
    def flush(self):
        pass

            
class skin(QWidget):
    """电子皮肤控件
    """
    OnActivate = pyqtSignal(bool)
    def __init__(self,uart:usartConfig):
        """初始化控件

        Args:
            uart (usartConfig): 串口控件
        """
        super().__init__()
        self.uart = uart
        self.uart.ThreadOutside = True
        # 设置字体
        self.smallFont = QFont()
        self.smallFont.setFamily("微软雅黑") 
        self.smallFont.setPointSize(9)
        self.gloabalFont = QFont()
        self.gloabalFont.setFamily("微软雅黑")  
        self.gloabalFont.setPointSize(10)
        # 设置控件布局
        self.setLayout(self.layout())
        # 设置控件宽度
        self.setFixedWidth(400)
        # 设置控件信号连接与交互响应
        self.connect()
       
    def layout(self):
        """设置控件布局

        Returns:
            QBoxLayout: Qt控件对象
        """
        vboxSkinAll = QVBoxLayout()
        return vboxSkinAll
    
    def connect(self):
        """设置控件交互相关功能
        """
        # 实例化电子皮肤线程
        self.skin = SkinThread()
        self.uart.status.connect(self.uartStateChanged)
        
    def uartStateChanged(self,act):
        """串口状态改变信号响应函数

        Args:
            act (str): 串口状态 'ON' or 'OFF'
        """
        if(act == 'OFF'):
            # 退出读取线程
            self.skin.working = False
            self.skin.quit()
            self.skin.wait()
            self.OnActivate.emit(False)
        if(act == 'ON'):
            self.skin.baudSelect = self.uart.baudSelect
            self.skin.portSelect = self.uart.portSelect
            self.skin.start()
            self.OnActivate.emit(True)
  