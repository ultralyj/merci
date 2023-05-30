from tensorflow import keras
import numpy as np
import csv
from sklearn.preprocessing import MinMaxScaler

model = None
# 创建 MinMaxScaler 对象
scaler = MinMaxScaler()

magnetic = None
position = None
def init():
    global model
    global magnetic
    global position
    model = keras.models.load_model('position_model')
    data = []
    with open('../../Calibration/data/squ2011_88.csv','rt') as f:
        csv_reader = csv.reader(f)
        isHeader = True                 # 判断帧头
        for row in csv_reader:          # 将csv 文件中的数据保存到data中
            if isHeader:
                isHeader = False
                continue
            frame = {
                'time':row[0],
                'xyd':row[1:4],
                'press':row[4],
                'mag4':row[5:17]
                }
            data.append(frame)           # 将字典加入到data数组中
    print("read csv file successfully")
    length = len(data)
    # 获取磁场数据，触点水平位置数据和压力数据
    magnetic = []
    position = []
    press = []
    for i,frame in enumerate(data):
        if(float(frame['press'])>0.05):
            press.append(float(frame['press']))
            magnetic.append(list(map(float, frame['mag4'])))
            position.append(list(map(float, frame['xyd'][:2])))
    press = np.array(press)
    magnetic = np.array(magnetic)
    position = np.array(position)
    normalized_magnetic = scaler.fit_transform(magnetic)
def predict(mag:list):
    mag = np.array(mag)
    nmag = scaler.transform([mag])
    return model.predict(nmag).tolist()

if __name__ == "__main__":
    init()
    
    mag = magnetic[478]
    print(mag)
    
    print(predict(mag))
    print(position[478])
    
