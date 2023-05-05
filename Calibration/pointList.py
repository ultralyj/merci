import numpy as np
def square_10_10(side = 20, num = 21):
    p = []
    l = np.linspace(start=0, stop=side, num=num)
    for i in l:
        for j in l:
            p.append([i,j])
    return p

def single_sensor():
    p = []
    l = [0,1,2,3,4,5,6,-6,-5,-4,-3,-2,-1]
    for i in l:
        for j in l:
            p.append([i,j])
    return p
