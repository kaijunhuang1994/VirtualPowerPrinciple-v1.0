import numpy as np

def phi_point_sigma(collocation,sigma,point):
        
    PI = 3.1415926536
    
    r = np.sqrt(((point[0] - collocation[0]))**2+((point[1] - collocation[1]))**2 
                  +((point[2] - collocation[2]))**2)

    phi = sigma/(2*PI)*np.log(r)

    return phi

def velocity_point_sigma(collocation,sigma,point):
        
    PI = 3.1415926536
    
    r = np.sqrt(((point[0] - collocation[0]))**2+((point[1] - collocation[1]))**2
               +((point[2] - collocation[2]))**2)

    d = 0.001

    velocity_u = sigma/(2*PI*r)*(point[0] - collocation[0])/r*(1-np.exp(-1.0*(r/d)**3))
    velocity_v = sigma/(2*PI*r)*(point[1] - collocation[1])/r*(1-np.exp(-1.0*(r/d)**3))
    velocity_w = sigma/(2*PI*r)*(point[2] - collocation[2])/r*(1-np.exp(-1.0*(r/d)**3))
    
    velocity = np.array([velocity_u, velocity_v, velocity_w]) 

    return velocity