# -*- coding: utf-8 -*- #
 
# ------------------------------------------------------------------
# File Name:        calibration.py
# Author:           罗翊杰(1951578@tongji.edu.cn)
# Version:          0.1
# Created:          2023/3/9
# Description:      标定控件
# History:
#       <author>        <version>       <time>      <desc>
#       ultralyj         0.1          2023/3/9      创建控件
# ------------------------------------------------------------------


import csv
import time

import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont, QPainter
from PyQt5.QtWidgets import (QButtonGroup, QComboBox, QFileDialog, QGroupBox,
                             QHBoxLayout, QLabel, QPlainTextEdit, QPushButton,
                             QRadioButton, QVBoxLayout, QWidget)

import pointList
from cnc import cnc
from press import press
from skin import skin


class WorkThread(QThread):
    """标定工作子线程，向测试台发出位置信息，并收集压力计与皮肤的数据（50Hz）

    Args:
        QThread : Qt线程
        
    """
    # 定义与主线程交流的信号
    positon = pyqtSignal(float,float,float,float)   # 定位信号，控制测试台移动
    calibrated = pyqtSignal(int,float)              # 标定完成信号，单点单深度单次标定完成后发出
    pressZero = pyqtSignal(bool)                    # 压力计归零信号，按压前发出
    finished = pyqtSignal(bool)                     # 标定完成信号，所有标定任务完成后发出
    
    def __init__(self):
        super(WorkThread,self).__init__()
        self.working = False
        # 标定左边，以home为参考原点
        self.p = [0.0,0.0,0.0]
        # 标定参考原点
        self.home = [0.0,0.0,0.0]
        # 标定设置，由主线程输入
        self.setting = {
            'path':None,            # 数据存储路径
            'strategy':None,        # 按压点分布策略    
            'PressPiority':None,    # 按压顺序策略，深度优先or平面优先
            'MaxDepth':1.2,         # 最大按压深度
            'DepthStep':0.2,        # 按压深度步长
            'stackTime':100          # 单次按压收集样本数
        }
        # 数据缓冲区
        self.stackTemp = [] 
        # 数据收集完成标志
        self.stackIsFull = False
    def run(self):
        """线程运行主函数
        """
        # 开始标定
        self.working = True
        # 打开/创建csv文件吗，写入header
        self.f = open(self.setting['path'],'w',encoding='utf8',newline='')
        self.writer = csv.writer(self.f)
        headers = ['time','x','y','d','press']
        for i in range(4):
            headers.append('skin%d_x'%(i))
            headers.append('skin%d_y'%(i))
            headers.append('skin%d_z'%(i))
        self.writer.writerow(headers)
        # 获取点阵列
        points = self.selectStrategy(self.setting['strategy'])
        # 获取深度序列
        depths = np.arange(start=self.setting['DepthStep'],stop=self.setting['MaxDepth']+self.setting['DepthStep'],step=self.setting['DepthStep'])
        # 平面优先
        if(self.setting['PressPiority'] == 0):
            for d in depths:
                for p in points:
                    self.calibration(p[0],p[1],d,points.index(p))
        # 深度优先
        if(self.setting['PressPiority'] == 1):
            for p in points:
                for d in depths:
                    self.calibration(p[0],p[1],d,points.index(p))
        # 关闭csv文件
        self.f.close()
        # 发送标定完成信号
        self.finished.emit(True)
        
    def calibration(self,x,y,d,ip):
        """单点单次标定操作

        Args:
            x (float): 标定点x坐标
            y (float): 标定点y坐标
            d (float): 按压深度
            ip (int): 标定点在点序列的序号
        """
        print(d,[x,y])
        # 控制测试台做出按压动作
        self.excutePress(x,y,d)
        # 等待运行稳定
        time.sleep(0.5)
        # 清空缓冲区
        self.resetStack()
        # 等待数据收集    
        while(self.stackIsFull == False):
            time.sleep(0.1)
        # 写入csv
        self.flushCsv(x,y,d)
        # 发送单点标定信号
        self.calibrated.emit(ip,d)
        
    def stackData(self,timeStamp,skin,press):
        """缓存样本数据（主线程调用）

        Args:
            timeStamp (int): 时间戳
            skin (list): 皮肤样本数据
            press (float): 压力计数据
        """
        if(not self.stackIsFull):
            # 缓存区未满时追加缓存数据
            allData = {
                'time':timeStamp,
                'skin':skin,
                'press':press
            }
            self.stackTemp.append(allData)
            # 判断缓存区是否满数据
            if(len(self.stackTemp)>=self.setting['stackTime']):
                self.stackIsFull = True
                
    def excutePress(self,x,y,deep):
        """执行按压操作

        Args:
            x (float): 标定点x坐标
            y (float): 标定点y坐标
            deep (int): 按压深度
        """
        # 抬高压头
        self.setPosition(self.p[0],self.p[1],2,200)
        # 移动到预定位置
        self.setPosition(x,y,2,200)
         # 清零压力计
        self.pressZero.emit(True)
        # 缓慢压下
        self.setPosition(x,y,-deep,50)
        
    def resetStack(self):
        """清空缓冲区
        """
        self.stackTemp = []
        self.stackIsFull = False
    def setPosition(self,x:float,y:float,z:float,f:float=100):
        """设置测试台位置，发送信号到主线程控制测试台

        Args:
            x (float): 标定点x坐标
            y (float): 标定点y坐标
            z (float): 标定点z坐标
            f (float, optional): 进给率. Defaults to 100.
        """
        # 发送信号到主线程
        self.positon.emit(self.home[0]+x,self.home[1]-y,self.home[2]+z,f)
        # 计算移动距离，结合进给率计算移动事件
        dist = np.sqrt((self.p[0]-x)*(self.p[0]-x) + (self.p[1]-y)*(self.p[1]-y) + (self.p[2]-z)*(self.p[2]-z))
        time.sleep(dist/f*60.0+0.1)
        # 更新标定坐标
        self.p = [x,y,z]
    
    def setHome(self,x,y,z):
        """设置标定参考原点

        Args:
            x (float): 标定点x坐标
            y (float): 标定点y坐标
            z (float): 标定点z坐标
        """
        self.home[0]=x
        self.home[1]=y
        self.home[2]=z
    
    def selectStrategy(self,s):
        """选择标定点分布策略

        Args:
            s (int): 标定点分布策略代号

        Returns:
            list: [[x,y]...]标定点平面分布序列
        """
        if(s==0):
            return pointList.square_10_10(side=20,num=21)
        if(s==1):
            return pointList.square_10_10(side=20,num=11)
        if(s==2):
            return pointList.square_10_10(side=18,num=3)
        if(s==3):
            return pointList.single_sensor()
    
    def flushCsv(self,x,y,d):
        """写入数据到csv文件

        Args:
            x (float): 标定点x坐标
            y (float): 标定点y坐标
            deep (int): 按压深度
        """
        # 排列数据，生成对应csv的列表
        flushTemp = []
        for frame in self.stackTemp:
            fl = []
            fl.append(frame['time'])
            fl.append(x)
            fl.append(y)
            fl.append(d)
            fl.append(frame['press'])
            fl+=frame['skin'][:-1]
            flushTemp.append(fl)
        # 写入csv文件
        self.writer.writerows(flushTemp)
        # 立即写入，避免意外丢失数据
        self.f.flush()
        
    def flush(self):
        pass

class graphCalibration(QWidget):
    """标定示意图绘制，表示标定点在电子皮肤上的位置分布

    Args:
        QWidget : Qt控件
    """
    def __init__(self):
        """初始化控件
        """
        super().__init__()
        # 设置固定尺寸，便于绘制
        self.setFixedSize(480, 400)
        # 设置points分布策略
        self.method = 0
        self.points = None
            
    def paintEvent(self,event):
        """重写Qt调用的绘图事件

        Args:
            event: 事件
        """
        painter = QPainter(self)
        # 自定义绘图
        self.draw( painter)
        
    def draw(self, qp:QPainter):
        """自定义绘图函数

        Args:
            qp (QPainter): Qt绘图句柄
        """
        # 绘制电子皮肤的背景，灰色代表电子皮肤
        qp.fillRect(0,0,420,360,QColor(250,250,250) )
        qp.fillRect(60,30,300,300,QColor(50,50,50,70))
        # 遍历标定点，绿色代表为标定，由黄变红表示按压深度逐渐增加
        if (self.points is not None):
            for p in self.points:
                if(p[2]!=0):
                    qp.setPen( QColor.fromHsl(50-p[2]*40,200,120,alpha=200) )
                    qp.setBrush(QBrush(QColor.fromHsl(50-p[2]*40,200,200,alpha=200)))
                    qp.drawEllipse(110+p[0]*10,80+p[1]*10,8,8) 
                else:
                    qp.setPen( QColor(0, 224, 159, 150) )
                    qp.setBrush(QBrush(QColor(55,254,200,150)))
                    qp.drawEllipse(110+p[0]*10,80+p[1]*10,8,8) 
                
    def updateStrategy(self,s:int):
        """更新标定点分布策略

        Args:
            s (int): 标定点策略序号
        """
        if(s == 0):
            self.points = pointList.square_10_10(20,21)
            for p in self.points:
                p.append(0)
        if(s == 1):
            self.points = pointList.square_10_10(20,11)
            for p in self.points:
                p.append(0)
        if(s == 2):
            self.points = pointList.square_10_10(18,3)
            for p in self.points:
                p.append(0)
        if(s == 3):
            self.points = pointList.single_sensor()
            for p in self.points:
                p.append(0)
    def updatePoint(self,ip:int, d:float):
        """更新点信息，外部调用

        Args:
            ip (int): 标定点序号
            d (float): 按压深度
        """
        self.points[ip][2] = d
        
class calibration(QWidget):
    """标定控件
    """
    def __init__(self):
        """控件初始化
        """
        super().__init__()
        # 控件获取测试台，压力计，电子皮肤3个子控件的实例
        self.cnc = None
        self.press = None
        self.skin = None
        # 创建工作子线程实例
        self.work = WorkThread()
        # 设置字体
        self.smallFont = QFont()
        self.smallFont.setFamily("微软雅黑") 
        self.smallFont.setPointSize(9)
        self.gloabalFont = QFont()
        self.gloabalFont.setFamily("微软雅黑")  
        self.gloabalFont.setPointSize(10)
        # 设置控件界面布局与宽度
        self.setLayout(self.layout())
        self.setFixedWidth(480)
        # 设置控件响应与信号连接
        self.connect()
       
    def layout(self):
        """设置控件布局

        Returns:
            QBoxLayout: Qt布局对象
        """
        # 第一行：标定点分布策略选择
        labelStrategy = QLabel('标点分布')
        self.comboxStrategy = QComboBox()
        self.comboxStrategy.setFont(QFont(self.smallFont))
        hboxStrategy = QHBoxLayout()
        hboxStrategy.addWidget(labelStrategy)
        hboxStrategy.addStretch(1)
        hboxStrategy.addWidget(self.comboxStrategy)
        
        # 第二行：按压优先级选择
        labelPressPriority = QLabel('按压策略')
        self.btnPressPriority1 = QRadioButton('平面优先')
        self.btnPressPriority2 = QRadioButton('深度优先')
        self.btnPressPriority1.setFont(self.smallFont)
        self.btnPressPriority2.setFont(self.smallFont)
        hboxPressPriority = QHBoxLayout()
        hboxPressPriority.addWidget(labelPressPriority)
        hboxPressPriority.addStretch(1)
        hboxPressPriority.addWidget(self.btnPressPriority1)
        hboxPressPriority.addWidget(self.btnPressPriority2)
        self.btnPressPriority1.setChecked(True)
        
        # 第三行：按压深度和步长
        labelDepth = QLabel('按压深度')
        self.lineDepth = QPlainTextEdit('1.2')
        labelDepthStep = QLabel('步长')
        self.lineDepthStep = QPlainTextEdit('0.2')
        self.lineDepth.setFixedHeight(46)
        self.lineDepthStep.setFixedHeight(46)
        hboxDepth = QHBoxLayout()
        hboxDepth.addWidget(labelDepth)
        hboxDepth.addWidget(self.lineDepth)
        hboxDepth.addWidget(labelDepthStep)
        hboxDepth.addWidget(self.lineDepthStep)
        
        # 第四行：标定信息输出
        self.labelMessage = QLabel('------------------------------------')
        hboxMessage = QHBoxLayout()
        hboxMessage.addWidget(self.labelMessage)
        
        # 第五行：设定存储路径
        self.linePath = QLabel('./')
        self.linePath.setFixedHeight(46)
        self.buttonSetPath = QPushButton('更改路径')
        self.buttonSetPath.setFixedWidth(120)
        hboxSetPath = QHBoxLayout()
        hboxSetPath.addWidget(self.linePath)
        hboxSetPath.addWidget(self.buttonSetPath)
        
        # 第六行：设定标定参考点，开始标定按钮
        self.buttonSetHome = QPushButton('设置起点')
        self.buttonStart = QPushButton('开始标定')
        hboxButtons = QHBoxLayout()
        hboxButtons.addStretch(1)
        hboxButtons.addWidget(self.buttonSetHome)
        hboxButtons.addWidget(self.buttonStart)
        
        # 前3行打包为标定配置
        vboxSetting = QVBoxLayout()
        vboxSetting.addLayout(hboxStrategy)
        vboxSetting.addLayout(hboxPressPriority)
        vboxSetting.addLayout(hboxDepth)
        self.groupSetting = QGroupBox()
        self.groupSetting.setTitle('标定配置')
        self.groupSetting.setFont(self.smallFont)
        self.groupSetting.setLayout(vboxSetting)
        
        # 456行打包为数据设置
        vboxData = QVBoxLayout()
        vboxData.addLayout(hboxMessage)
        vboxData.addLayout(hboxSetPath)
        vboxData.addLayout(hboxButtons)
        self.groupData = QGroupBox()
        self.groupData.setTitle('数据设置')
        self.groupData.setFont(self.smallFont)
        self.groupData.setLayout(vboxData)
        
        # 底部绘制示意图
        self.graph = graphCalibration()
        
        # 布局组合
        vboxAll = QVBoxLayout()
        vboxAll.addWidget(self.groupSetting)
        vboxAll.addWidget(self.groupData)
        vboxAll.addStretch(1)
        vboxAll.addWidget(self.graph)
        
        # 输出布局
        return vboxAll
    
    def connect(self):
        """设置控件交互相关功能
        """
        # 标定点分布策略填充与选择响应
        self.strategySelect = ['square_20_20(441P)','square_20_20(121P)','square_20_20(9P)','single_sensor(49P)']
        self.comboxStrategy.addItems(self.strategySelect)
        self.comboxStrategy.setCurrentIndex(0)
        self.comboxStrategy.currentIndexChanged.connect(self.onMethodChanged)
        
        # 将按压优先级策略ration打包为按键组，并添加响应
        self.groupButtonPressMethod= QButtonGroup()
        self.groupButtonPressMethod.addButton(self.btnPressPriority1,0)
        self.groupButtonPressMethod.addButton(self.btnPressPriority2,1)
        self.groupButtonPressMethod.buttonClicked[int].connect(self.onPressPriorityChanged)
        
        # 保存路径
        self.buttonSetPath.clicked[bool].connect(self.onPathSetting)
        self.file_name = ('./data/%s%d.csv'%('squ2021_',time.time()%1000),'CSV UTF-8 逗号分隔(*.csv)')
        self.linePath.setText(self.file_name[0])
        
        # 设置起点
        self.buttonSetHome.clicked[bool].connect(self.onHomeSetting)
        
        # 开始标定
        self.buttonStart.clicked[bool].connect(self.onStart)
        
        # 禁用所有面板，在标定条件满足前
        self.setDisabled(True)
        
        # 连接子线程信号槽
        self.work.positon.connect(self.setPosition)
        self.work.pressZero.connect(self.pressZero)
        self.work.calibrated.connect(self.onCalibrated)
        self.work.finished.connect(self.onFinished)
    
    def activate(self,cnc:cnc=None,press:press=None,skin:skin=None):
        """激活控件，外部窗口触发

        Args:
            cnc (cncConfig, optional): 测试台控件实例. Defaults to None.
            press (pressConfig, optional): 压力计控件实例. Defaults to None.
            skin (skinConfig, optional): 电子皮肤控件实例. Defaults to None.
        """
        # 控件实例填充
        self.cnc = cnc
        self.press = press
        self.skin = skin
        # 接入电子皮肤数据更新信号到控件响应函数
        self.skin.skin.measurement.connect(self.updateSkinData)
        # 设置标定参考点
        self.work.home = [self.cnc.probe['x'],self.cnc.probe['y'],self.cnc.probe['z']]
        # 激活标定控件
        self.setEnabled(True)
     
    def updateSkinData(self,data):
        """电子皮肤数据更新响应函数，工作子线程数据填充由电子皮肤数据更新驱动

        Args:
            data (list): 电子皮肤数据，4*[x,y,z]+求和校验
        """
        # 同步拉取当前压力计读数
        press = self.press.wp
        # 传输数据到工作线程
        if(self.work.working):
            self.work.stackData(time.time(),data,press)   
            
    def setPosition(self,x:float,y:float,z:float,f:float):
        """设置测试台位置，工作线程控制信号响应函数，传递到测试台控件

        Args:
            x (float): 测试台x坐标
            y (float): 测试台y坐标
            z (float): 测试台z坐标
            f (float): 进给率
        """
        # 传递到测试台控件
        self.cnc.setPosition(x,y,z,f)
    
    def pressZero(self):
        """工作线程压力计归零信号响应函数
        """
        self.press.press.wz = self.press.w
        
    def onMethodChanged(self):
        """标定点选择发送变化的回调函数
        """
        # 设置保存文件名并且重新绘制图像
        if(self.comboxStrategy.currentIndex()==0):
            self.file_name = ('./data/%s%d.csv'%('squ2021_',time.time()%1000),'CSV UTF-8 逗号分隔(*.csv)')
            self.linePath.setText(self.file_name[0])
            self.graph.updateStrategy(0)
            self.graph.update()
        if(self.comboxStrategy.currentIndex()==1):
            self.file_name = ('./data/%s%d.csv'%('squ2011_',time.time()%1000),'CSV UTF-8 逗号分隔(*.csv)')
            self.linePath.setText(self.file_name[0])
            self.graph.updateStrategy(1)
            self.graph.update()
        if(self.comboxStrategy.currentIndex()==2):
            self.file_name = ('./data/%s%d.csv'%('squ2003_',time.time()%1000),'CSV UTF-8 逗号分隔(*.csv)')
            self.linePath.setText(self.file_name[0])
            self.graph.updateStrategy(2)
            self.graph.update()
        if(self.comboxStrategy.currentIndex()==3):
            self.file_name = ('./data/%s%d.csv'%('singal_49_',time.time()%1000),'CSV UTF-8 逗号分隔(*.csv)')
            self.linePath.setText(self.file_name[0])
            self.graph.updateStrategy(3)
            self.graph.update()
            
    def onPressPriorityChanged(self):
        """按压策略变化的回调函数
        """
        id = self.groupButtonPressMethod.checkedId()
        if(id == 0):
            pass
        if(id == 1):
            pass
  
    def onPathSetting(self):
        """存储路径设置的回调函数
        """
        # 弹出保存对话框
        self.file_name = QFileDialog.getSaveFileName(None,"选择存储路径",".","CSV UTF-8 逗号分隔(*.csv)")
        # 省略部分路径以保证能够显示在控件上
        l = self.file_name[0].split('/')[-1]
        maxl = 14
        if(len(l)<=maxl):
            self.linePath.setText(self.file_name[0][:maxl-len(l)]+'...'+l)
        else:
            self.linePath.setText('...'+l[:maxl])
    
    def onHomeSetting(self):
        """标定参考点回调函数
        """
        self.work.setHome(self.cnc.probe['x'],self.cnc.probe['y'],self.cnc.probe['z'])
        
    def onStart(self):
        """标定开始回调函数
        """
        # 将标定设置同步到工作线程
        self.work.setting['path'] = self.file_name[0]
        self.work.setting['strategy'] = self.comboxStrategy.currentIndex()
        self.work.setting['PressPiority'] = self.groupButtonPressMethod.checkedId()
        self.work.setting['MaxDepth'] = float(self.lineDepth.toPlainText())
        self.work.setting['DepthStep'] = float(self.lineDepthStep.toPlainText())
        # 禁用测试台，压力计，电子皮肤以及他们的串口控制线程，避免误触影响标定
        self.cnc.setDisabled(True)
        self.press.setDisabled(True)
        self.skin.setDisabled(True)
        self.cnc.uart.setDisabled(True)
        self.press.uart.setDisabled(True)
        self.skin.uart.setDisabled(True)
        # 禁用标定设置
        self.groupData.setDisabled(True)
        self.groupSetting.setDisabled(True)
        # 开启工作线程
        self.work.start()
    
    def onCalibrated(self,ip:int,d:float):
        """单点单次标定完成的响应函数

        Args:
            ip (int): 标定点序列的序号
            d (float): 按压深度
        """
        # 显示当前已完成的标定点信息
        self.labelMessage.setText('Cali:(%.1f,%.1f) depth:%.1fmm'%(self.graph.points[ip][0],self.graph.points[ip][1],d))
        # 更新图像并重新绘制
        self.graph.updatePoint(ip,d)
        self.graph.update()
        
    def onFinished(self,f):
        """标定完成信号的响应函数

        """
        
        # 恢复禁用的控件
        self.cnc.setEnabled(True)
        self.press.setEnabled(True)
        self.skin.setEnabled(True)
        self.cnc.uart.setEnabled(True)
        self.press.uart.setEnabled(True)
        self.skin.uart.setEnabled(True)
        self.groupData.setEnabled(True)
        self.groupSetting.setEnabled(True)
        
        # 输出信息提示标定完成
        self.labelMessage.setText('标定完成')