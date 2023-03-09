# -*- coding: utf-8 -*- #
 
# ------------------------------------------------------------------
# File Name:        press.py
# Author:           罗翊杰(1951578@tongji.edu.cn)
# Version:          0.1
# Created:          2023/3/8
# Description:      压力计控件
# History:
#       <author>        <version>       <time>      <desc>
#       ultralyj         0.1          2023/3/8      创建控件
# ------------------------------------------------------------------

import ctypes

import modbus_tk.defines as cst
import serial
from modbus_tk import modbus_rtu
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QVBoxLayout,QWidget)

from usartConfig import usartConfig


class MeasureThread(QThread):
    """压力计测量线程
    """
    # 测量完成信号
    measurement = pyqtSignal(float,float)
    def __init__(self):
        """初始化线程
        """
        super(MeasureThread,self).__init__()
        # 串口句柄（串口在线程内创建）
        self.ser = None
        self.baudSelect = 9600
        self.portSelect = 'COM0'
        # 零位数值
        self.wz = 0
        self.working = True
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
        # 创建ModBus RTU主机
        master = modbus_rtu.RtuMaster(self.ser)
        master.set_timeout(1.0)
        master.set_verbose(True)
        # 初始化，设置第一次标志位，进入循环测量
        first = True
        self.working = True
        while(self.working == True):
            try:
                # 读取压力计数值
                res_tuple = master.execute(1, cst.READ_HOLDING_REGISTERS, 0, 10)  
                # 获得压力的原始值
                w = ctypes.c_int16(res_tuple[7]).value
                # 选用首次测量的数值为0点
                if(first):
                    self.wz = w
                    first = False    
                # 发送测量信号到主线程
                self.measurement.emit(w,self.wz)
            except Exception as e:
                # 如果出现无法读取的情况，停止循环测量
                print(e)
                self.working = False
        # 关闭串口
        self.ser.close()
    
    def flush(self):
        pass
            
class press(QWidget):
    """压力计控件
    """
    OnActivate = pyqtSignal(bool)
    def __init__(self, uart:usartConfig):
        """初始化控件

        Args:
            uart (usartConfig): 串口控件
        """
        super().__init__()
        self.uart = uart
        self.uart.ThreadOutside = True
        # 压力原始值与零位原始值
        self.w = 0.0
        self.wp = 0.0       
        # 设置串口波特率为9600（压力计只支持9600）
        self.uart.setBaudRate(9600)
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
        # 第一行：实时压力显示
        labelData = QLabel('压力: ')
        self.textData = QLabel('0.00N')
        hboxData = QHBoxLayout()
        hboxData.addWidget(labelData)
        hboxData.addWidget(self.textData)
        hboxData.addStretch(1)
        
        # 第二行：校准零位
        labelCali = QLabel('校准零位: ')
        self.textCali = QLabel('0000')
        self.buttonZero = QPushButton('归零')
        self.buttonZero.setDisabled(True)
        hboxCalibration = QHBoxLayout()
        hboxCalibration.addWidget(labelCali)
        hboxCalibration.addWidget(self.textCali)
        hboxCalibration.addWidget(self.buttonZero)
        
        # 布局组合
        vboxPressAll = QVBoxLayout()
        vboxPressAll.addLayout(hboxData)
        vboxPressAll.addLayout(hboxCalibration)
        
        # 返回布局
        return vboxPressAll
    
    def connect(self):
        """设置控件交互相关功能
        """
        self.uart.status.connect(self.uartStateChanged)
        self.press = MeasureThread()
        self.press.measurement.connect(self.updateMeasurement)
        self.buttonZero.clicked[bool].connect(self.updateZero)
        
    def uartStateChanged(self,act):
        """串口状态改变信号响应函数

        Args:
            act (str): 串口状态 'ON' or 'OFF'
        """
        if(act == 'OFF'):
            self.buttonZero.setDisabled(True)
            self.press.working = False
            self.press.quit()
            self.press.wait()
            self.OnActivate.emit(False)
        if(act == 'ON'):
            self.buttonZero.setEnabled(True)
            self.press.baudSelect = self.uart.baudSelect
            self.press.portSelect = self.uart.portSelect
            self.press.start()
            self.OnActivate.emit(True)
            
    def updateMeasurement(self,w,wz):
        """更新测量数据，将原始值转化为压力

        Args:
            w (int): 原始压力数据
            wz (int): 零位
        """
        # 将原始值转化为压力
        self.wp = (w-wz)/133.763
        self.w = w
        # 更新显示
        self.textCali.setText('%.01f'%(wz))
        self.textData.setText('%.02f'%(self.wp))
    
    def updateZero(self):
        """校准零位
        """
        self.press.wz = self.w
