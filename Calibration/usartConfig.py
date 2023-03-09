# -*- coding: utf-8 -*- #
 
# ------------------------------------------------------------------
# File Name:        usartConfig.py
# Author:           罗翊杰(1951578@tongji.edu.cn)
# Version:          0.1
# Created:          2023/3/9
# Description:      串口配置控件
# History:
#       <author>        <version>       <time>      <desc>
#       ultralyj         0.1          2023/3/9      创建控件
# ------------------------------------------------------------------

import serial
import serial.tools.list_ports
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QComboBox, QGroupBox, QHBoxLayout, QLabel,
                             QPushButton, QVBoxLayout, QWidget)


def getSerialList():
    """_summary_

    Returns:
        _type_: _description_
    """
    port_list = list(serial.tools.list_ports.comports())
    serialList = []
    if len(port_list) != 0:
        for i in range(0, len(port_list)):
            serialList.append(port_list[i].device)
    return serialList

class usartConfig(QWidget):
    """串口配置控件
    """
    status = pyqtSignal(str)  # 串口打开状态控件
    # 串口配置控件
    def __init__(self):
        """_summary_
        """
        super().__init__()
        # 设置外置线程标志位（默认为否，即控件内管理串口收发）
        self.ThreadOutside = False
        # 创建串口句柄
        self.ser = None
        # 获取串口列表
        self.portChoiceList = getSerialList()
        # 波特率列表
        self.baudChoiceList = ['4800','9600','14400', '19200', '38400','115200','460800']
        # 设置字体
        self.smallFont = QFont()
        self.smallFont.setFamily("微软雅黑")  
        self.smallFont.setPointSize(9)
        self.gloabalFont = QFont()
        self.gloabalFont.setFamily("微软雅黑") 
        self.gloabalFont.setPointSize(10)
        # 设置波特率选择与串口选择
        self.baudSelect = 115200
        self.portSelect = 'COM0'
        # 设置控件宽度
        self.setFixedWidth(400)
        # 设置控件布局
        self.setLayout(self.layout())
        # 设置控件信号连接与交互响应
        self.connect()

    def layout(self):
        """设置控件布局

        Returns:
            QBoxLayout: Qt控件对象
        """
        
        # 第一行：端口选择
        self.comboBoxPort = QComboBox()
        self.comboBoxPort.setFont(QFont(self.smallFont))
        labelPort = QLabel("端口")
        labelPort.setFont(self.gloabalFont)
        hboxPort = QHBoxLayout()
        hboxPort.addWidget(labelPort)
        hboxPort.addWidget(self.comboBoxPort)

        # 第二行：波特率选择
        self.comboBoxBaud = QComboBox()
        self.comboBoxBaud.setFont(QFont(self.smallFont))
        labelBaud = QLabel("波特率")
        labelBaud.setFont(self.gloabalFont)
        hboxBaud = QHBoxLayout()
        hboxBaud.addWidget(labelBaud)
        hboxBaud.addWidget(self.comboBoxBaud)

        # 第三行：串口开关按键
        self.portOpenButton = QPushButton("打开串口")
        self.portOpenButton.setFont(self.gloabalFont)
        self.portCloseButton = QPushButton("关闭串口")
        self.portCloseButton.setFont(self.gloabalFont)
        self.portCloseButton.setDisabled(True)
        hboxPortKey = QHBoxLayout()
        hboxPortKey.addWidget(self.portOpenButton)
        hboxPortKey.addWidget(self.portCloseButton)

        # 布局组合
        vboxPort = QVBoxLayout()
        vboxPort.addLayout(hboxPort)
        vboxPort.addLayout(hboxBaud)
        vboxPort.addLayout(hboxPortKey)

        # 打包成串口配置组件
        groupBoxPort = QGroupBox()
        groupBoxPort.setTitle('串口配置')
        groupBoxPort.setFont(self.smallFont)
        groupBoxPort.setLayout(vboxPort)

        # 输出布局
        vboxPortAll = QVBoxLayout()
        vboxPortAll.addWidget(groupBoxPort)
        
        return vboxPortAll
    
    def connect(self):
        """设置控件交互相关功能
        """
        # 填充串口列表并设置选框回调函数
        if len(self.portChoiceList) > 0:
            self.comboBoxPort.addItems(self.portChoiceList)
            self.comboBoxPort.setCurrentIndex(0)
            self.portSelect = self.portChoiceList[self.comboBoxPort.currentIndex()]
        self.comboBoxPort.currentIndexChanged.connect(
            lambda: self.comboEvent(self.comboBoxPort))

        # 填充波特率列表并设置选框回调函数
        self.comboBoxBaud.addItems(self.baudChoiceList)
        self.comboBoxBaud.setCurrentIndex(self.baudChoiceList.index(str(self.baudSelect)))
        self.comboBoxBaud.currentIndexChanged.connect(lambda: self.comboEvent(self.comboBoxBaud))
        
        # 开启/关闭按钮回调函数
        self.portOpenButton.clicked[bool].connect(lambda: self.statusEvent('ON'))
        self.portCloseButton.clicked[bool].connect(lambda: self.statusEvent('OFF'))

    def comboEvent(self, combobox):
        """选框回调函数

        Args:
            combobox: 选框实例对象
        """
        self.updatePortList()
        if combobox == self.comboBoxBaud:
            self.baudSelect = int(
                self.baudChoiceList[self.comboBoxBaud.currentIndex()])
        if combobox == self.comboBoxPort:
            self.portSelect = self.portChoiceList[self.comboBoxPort.currentIndex()]
    
    def setBaudRate(self,baud:int):
        """设置波特率

        Args:
            baud (int): 波特率
        """
        self.baudSelect = baud
        self.comboBoxBaud.setCurrentIndex(self.baudChoiceList.index(str(baud)))
    
    def setPort(self,port:str):
        """设置端口

        Args:
            port (str): 端口
        """
        self.portSelect = port
        self.comboBoxPort.setCurrentIndex(self.portChoiceList.index(port))

    def statusEvent(self, act: str):
        """状态变化响应函数

        Args:
            act (str): 开启/关闭状态
        """
        if(act == 'ON'):
            if(self.ThreadOutside):
                # 外置线程串口，只需要发送消息到控件外部即可
                self.portOpenButton.setDisabled(True)
                self.portCloseButton.setEnabled(True)
                self.status.emit('ON')
            else:
                # 开启串口
                self.open(self.portSelect, self.baudSelect)
                self.portOpenButton.setDisabled(True)
                self.portCloseButton.setEnabled(True)
        if(act == 'OFF'):
            if(self.ThreadOutside):
                self.portCloseButton.setDisabled(True)
                self.portOpenButton.setEnabled(True)
                self.status.emit('OFF')
            else:
                if self.ser.is_open == True:
                    # 关闭串口
                    self.ser.close()
                    self.portCloseButton.setDisabled(True)
                    self.portOpenButton.setEnabled(True)
                    self.status.emit('OFF')
                    
    def updatePortList(self):
        """更新串口列表
        """
        if self.portChoiceList != getSerialList():
            self.portChoiceList = getSerialList()     
    
    def open(self, port: str, baud: int):
        """打开串口

        Args:
            port (str): 端口
            baud (int): 波特率
        """
        
        if(self.ser is None):
            # 若串口没有打开，则新建串口
            self.ser = serial.Serial(
                port = port, 
                baudrate = baud,
                parity= 'N',
                xonxoff= 0,
                timeout=1.0)
            if(self.ser.isOpen() == True):
                print("open serial:",self.ser.port,'successfully')
                self.status.emit('ON')
            else:
                print("failed")

    def send(self, buffer:bytes):
        """发送数据

        Args:
            sendBuffer (bytes): 发送的字节数据
        """
        if(self.ser.isOpen()):
            self.ser.write(buffer)

