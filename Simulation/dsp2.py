import numpy as np
from scipy.interpolate import griddata
data = np.loadtxt(open("normB_z0.011.csv","r"),delimiter=",") 
x = data[:,0]
y = data[:,1]

B = data[:,3]
# Import libraries
from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt
 
# Creating figure
fig = plt.figure(figsize=(10, 7))
ax = plt.axes(projection="3d")
 
# Creating plot
ax.scatter(x,y,B, color="green")
plt.title("simple 3D scatter plot")
 
# show plot
plt.show()
