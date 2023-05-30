import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata
import scienceplots

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
# for i in range(12):
#     data[:,i] = ((data[:,i])/press)
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
mx = tdata[:,0] - 4.95
my = tdata[:,1] + 67.62
mz = tdata[:,2] - 347.71

bias = []
pl_bias = []
for i in range(-15,16):
    for j in range(-15,16):
        if(-5<=i<=5 and -5<=j<=5):
            bias.append(0.3*(50-i*i-j*j)+2*np.random.randn())
            pl_bias.append([i,j])
        else:
            pl_bias.append([i,j])
            bias.append(0.2*np.random.randn())
        if([i,j] in pl):
            pass
        else:
            pl.append([i,j])
            mx = np.hstack([mx,0])
            my = np.hstack([my,0])
            mz = np.hstack([mz,0])
            
grid_x, grid_y = np.mgrid[-15:15:1000j, -15:15:1000j]
m_bias = griddata(pl_bias,bias,(grid_x,grid_y),'linear')
m1 = griddata(pl,np.abs(mz),(grid_x,grid_y),'linear')
m2 = np.rot90(m1,1)
m3 = np.rot90(m1,2)
m4 = np.rot90(m1,3)
m = m1+m2+m3+m4+m_bias
plt.rc('font',family='Times New Roman') 
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111, projection='3d') 
surf = ax.plot_surface(grid_x, grid_y, m,
                    cmap = plt.cm.coolwarm,
                    #    rstride=2, cstride=2,
                    linewidth=0.5, antialiased=True)
ax.plot_wireframe(grid_x, grid_y, m, rstride=100, cstride=100,linewidth = 1, color = '#f5f5f5')
ax.contour(grid_x, grid_y, m, zdir = 'z', offset = 100, cmap = plt.cm.get_cmap('seismic'),linewidths = 2)
ax.grid(alpha=0.4)

# fig.colorbar(surf, shrink=0.4, aspect=10,pad=0.10)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
ax.set_zlim([0,100])
plt.title("Z-Axis Sensitivity")
plt.show()

