import numpy as np
from scipy.interpolate import griddata
data = np.loadtxt(open("normB_z0.011.csv","r"),delimiter=",") 
xy = data[:,0:2]
B = data[:,3]*1e4
# Import libraries
from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt
 
grid_x, grid_y = np.mgrid[-0.015:0.015:1000j, -0.015:0.015:1000j]
Bn = griddata(xy,B,(grid_x,grid_y),'linear'); 
print(Bn)
# Creating figure
plt.rcParams['font.sans-serif'] = 'Times New Roman'
fig = plt.figure(figsize=(10, 7))
ax = plt.axes(projection="3d")
 
# Creating plot
ax.plot_surface(grid_x, grid_y, Bn,cmap = plt.get_cmap('rainbow'))
plt.title("simple 3D scatter plot")
ax.set_zlim(3e3, 6e3)
ax.set_zlabel('B(G)')
# show plot
plt.show()
