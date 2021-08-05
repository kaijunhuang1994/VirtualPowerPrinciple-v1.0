import numpy as np

def phi_sigma(left,right,sigma,point):
    
    PI = 3.1415926536

    x0 = (left[0] + right[0])/2
    y0 = (left[1] + right[1])/2

    vtm = np.sqrt((right[0] - left[0])**2+(right[1] - left[1])**2)
    vtx = (right[0] - left[0])/vtm
    vty = (right[1] - left[1])/vtm
    vnx = -vty
    vny = vtx

    # 建立当地坐标系
    x1 = - vtm/2
    x2 = vtm/2

    x = (point[0] - x0) * vtx + (point[1] - y0) * vty
    y = (point[0] - x0) * vnx + (point[1] - y0) * vny

    # 计算速度势
    th1 = np.arctan2(y, x - x1)
    th2 = np.arctan2(y, x - x2)
    r1 = np.sqrt((x-x1)*(x-x1)+y*y)
    r2 = np.sqrt((x-x2)*(x-x2)+y*y)

    
    phi = sigma/(4*PI)*((x-x1)*np.log(r1*r1)-(x-x2)*np.log(r2*r2)+2*y*(th2-th1))
  
    return phi 

def phi_mu(left,right,mu,point):
    
    PI = 3.1415926536

    x0 = (left[0] + right[0])/2
    y0 = (left[1] + right[1])/2
    vtm = np.sqrt((right[0] - left[0])**2+(right[1] - left[1])**2)
    vtx = (right[0] - left[0])/vtm
    vty = (right[1] - left[1])/vtm
    vnx = -vty
    vny = vtx

    # 建立当地坐标系
    x1 = - vtm/2
    x2 = vtm/2

    x = (point[0] - x0) * vtx + (point[1] - y0) * vty
    y = (point[0] - x0) * vnx + (point[1] - y0) * vny

    th1 = np.arctan2(y, x - x1)
    th2 = np.arctan2(y, x - x2)

    phi = - 1.0 * mu/(2*PI)*(th2-th1)

    return phi

def velocity_sigma(left,right,sigma,point):
    
    PI = 3.1415926536

    x0 = (left[0] + right[0])/2
    y0 = (left[1] + right[1])/2

    vtm = np.sqrt((right[0] - left[0])**2+(right[1] - left[1])**2)
    vtx = (right[0] - left[0])/vtm
    vty = (right[1] - left[1])/vtm
    vnx = -vty
    vny = vtx

    # 建立当地坐标系
    x1 = - vtm/2
    x2 = vtm/2

    x = (point[0] - x0) * vtx + (point[1] - y0) * vty
    y = (point[0] - x0) * vnx + (point[1] - y0) * vny

    # 计算速度势
    th1 = np.arctan2(y, x - x1)
    th2 = np.arctan2(y, x - x2)
    r1=np.sqrt((x-x1)*(x-x1)+y*y)
    r2=np.sqrt((x-x2)*(x-x2)+y*y)

    velocity_u = sigma/(2 * PI) * np.log(r1/r2)
    velocity_v = 1.0 * sigma/(2 * PI)*(th2 - th1)
    
    velocity = np.array([velocity_u * vtx +  velocity_v * vnx, velocity_u * vty + velocity_v * vny]) 

    return velocity

def velocity_gamma(collocation,gamma,point):
    
    PI = 3.1415926536
    
    r = np.sqrt(((point[0] - collocation[0]))**2+((point[1] - collocation[1]))**2)

    d=0.001

    # velocity_u = - gamma/(2*PI)*((point[1] - collocation[1]))/(r*r)*(1-np.exp(-1.0*np.pow((r/d),3)))
    # velocity_v = gamma/(2*PI)*((point[0] - collocation[0]))/(r*r)*(1-np.exp(-1.0*np.pow((r/d),3)))

    velocity_u = - gamma/(2*PI)*((point[1] - collocation[1]))/(r*r)*(1-np.exp(-1.0*(r/d)**3))
    velocity_v = gamma/(2*PI)*((point[0] - collocation[0]))/(r*r)*(1-np.exp(-1.0*(r/d)**3))
    
    velocity = np.array([velocity_u, velocity_v]) 

    return velocity

def velocity_mu(left,right,mu,point):

    velocity = velocity_gamma(left,mu,point) + velocity_gamma(right,-mu,point)

    return velocity

###############################################################################################

def phi_point_sigma(collocation,sigma,point):
        
    PI = 3.1415926536
    
    r = np.sqrt(((point[0] - collocation[0]))**2+((point[1] - collocation[1]))**2)

    phi = sigma/(2*PI)*np.log(r)

    return phi

def velocity_point_sigma(collocation,sigma,point):
        
    PI = 3.1415926536
    
    r = np.sqrt(((point[0] - collocation[0]))**2+((point[1] - collocation[1]))**2)

    d = 0.001

    velocity_u = sigma/(2*PI*r)*(point[0] - collocation[0])/r*(1-np.exp(-1.0*(r/d)**3))
    velocity_v = sigma/(2*PI*r)*(point[1] - collocation[1])/r*(1-np.exp(-1.0*(r/d)**3))
    
    velocity = np.array([velocity_u, velocity_v]) 

    return velocity