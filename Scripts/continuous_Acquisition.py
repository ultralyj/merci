# -*- coding: utf-8 -*- #
# env: 'mavis':conda

# ------------------------------------------------------------------
# File Name:        conn.py
# Author:           罗翊杰(1951578@tongji.edu.cn)
# Version:          0.1
# Created:          2023/5/18
# Description:      用于连续全速采集测力计与电子皮肤的脚本
# History:
#       <author>        <version>       <time>      <desc>
#       ultralyj         0.1          2023/5/13      创建脚本
# ------------------------------------------------------------------

import serial
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
import ctypes
import threading
import time
import time,csv

count = 0

"""注： 可以参考这篇博客https://blog.csdn.net/l835311324/article/details/86608850的示例2，
这个MyThread类继承了threading模块的Thread类，对其下面的run方法进行了重写"""

press_raw_data = None

    
class CollectThread(threading.Thread):
    """测力计采集线程
    """
    def __init__(self , threadName):
        super(CollectThread,self).__init__(name=threadName)
        # 串口句柄（串口在线程内创建）
        self.ser = None
        self.baudSelect = 9600
        self.portSelect = 'COM10'
        # 零位数值
        self.wz = 0
        self.working = True

        
    def run(self):
        """线程运行函数
        """
        # 打开测力计串口
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
                global press_raw_data 
                press_raw_data = res_tuple
            except Exception as e:
                # 如果出现无法读取的情况，停止循环测量
                print(e)
                self.working = False
        # 关闭串口
        self.ser.close()
    
    def flush(self):
        pass

if __name__ == "__main__":
    # 打开测力计线程
    CollectThread('press').start()
    # 打开电子皮肤串口
    ser=serial.Serial(port = 'COM12', 
                    baudrate = 115200,
                    parity= 'N',
                    xonxoff= 0,
                    timeout=1.0)
    time.sleep(0.5)
    # 准备写入csv文件
    path = str(time.time())+ '_conn.csv'
    f = open(path,'w',encoding='utf8',newline='')
    writer = csv.writer(f)
    # 持续更新csv文件
    while(1):
        frame = str(ser.readline(),'ascii')
        # 分割数据并转化为浮点数列表
        dataRaw = list(map(float, frame[:-1].split(',')))
        press_data_list = list(press_raw_data)
        frame_list = []
        frame_list.append(time.time())
        frame_list+=dataRaw
        frame_list+=press_data_list
        writer.writerow(frame_list)
        print(frame_list)
        f.flush()
    ser.close()