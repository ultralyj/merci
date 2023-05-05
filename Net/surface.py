import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata

# 不同弹性体厚度分析，载入5组数据
# 数据集路径
tset_path = {
    "t14":'./../Data/TSET_squ1803/squ1803_T1.4_C1.0.csv',
    "t17":'./../Data/TSET_squ1803/squ1803_T1.4_C1.0.csv',
    "t20":'./../Data/TSET_squ1803/squ1803_T1.4_C1.0.csv',
    "t23":'./../Data/TSET_squ1803/squ1803_T1.4_C1.0.csv',
    "t26":'./../Data/TSET_singal/singal_169_366.csv',
}
# 载入数据
tset = {}
for t in tset_path:
    print('loading:'+tset_path[t]+'...',end='',flush=True)
    with open(tset_path[t]) as f:
        tset[t] = np.loadtxt(f,delimiter=",",skiprows=1) 
    print('[ok]') 

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import scienceplots
# import matplotlib
# matplotlib.use('TkAgg')

data = np.zeros((169*4,12))
press = np.zeros((169*4))
tdata = np.zeros((169,12))
for i in range(169*4):
    data[i,:] = np.average(tset['t26'][i*100:i*100+100,5:],axis=0)
    press[i] = np.average(tset['t26'][i*100:i*100+100,4])
for i in range(12):
    data[:,i] = ((data[:,i]))
for i in range(169):
    tdata[i,:] = np.average(data[i*4:i*4+4,:],axis=0)
def single_sensor():
    p = []
    l = [0,1,2,3,4,5,6,-6,-5,-4,-3,-2,-1]
    for i in l:
        for j in l:
            p.append([i-7,j])
    return p

pl = single_sensor()
points = np.hstack((pl,tdata[:,1].reshape(169,1)))
print(points[:,2])

fig = plt.figure()
plt.rcParams['savefig.dpi'] = 1000       # 图片像素
plt.rcParams['figure.dpi'] = 1000        # 分辨率
plt.rcParams['font.sans-serif'] = 'Times New Roman'
ax = fig.add_subplot(111, projection='3d')



grid_x, grid_y = np.mgrid[-15:15:1000j, -15:15:1000j]
grid_x2, grid_y2 = np.mgrid[-15:15:1000j, -15:15:1000j]

m = griddata(pl,np.abs(tdata[:,0]-4.95),(grid_x,grid_y),'linear'); 
#m = griddata(pl,np.abs(tdata[:,1]+67.62),(grid_x,grid_y),'linear'); 
#m = griddata(pl,np.abs(tdata[:,2]-347.71),(grid_x,grid_y),'linear'); 
print(np.shape(grid_y2))
# m2 = griddata(pl,np.abs(tdata[:,1]+67.62),(grid_x,grid_y),'linear'); 

ax.plot_surface(grid_x2, grid_y2, np.zeros((1000,1000)),cmap = plt.get_cmap('rainbow'),alpha=0.2)
ax.plot_surface(grid_x, grid_y, m,cmap = plt.get_cmap('rainbow'))
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
plt.title("z-axis sensitivity")

ax.set_zlim(0,80)
plt.show()