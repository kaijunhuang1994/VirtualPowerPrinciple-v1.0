from ..parser.inputdatabase import InputDatabase
import numpy as np
import Package.induction.induction3D as ind3D
# import Package.induction.induction_numpy as ind2D

class Sphere3D:

    def __init__(self):

        input_db = InputDatabase.from_file("input/theoryControlDict")
        self.__input_db = input_db

        # The radius of the cylinder
        assert isinstance(input_db["sphere3D"]["radius"], float)
        self.__radius = input_db["sphere3D"]["radius"]

        # The central coordinates of the cylinder
        assert isinstance(input_db["sphere3D"]["center"], list)
        self.__center = np.array(input_db["sphere3D"]["center"])


    def get_radius(self):

        return self.__radius

    def get_initial_center(self):

        return self.__center

    def get_input_db(self):

        return self.__input_db    


class MovingSphere3D(Sphere3D):

    def __init__(self, time):

        super(MovingSphere3D, self).__init__()

        # current time
        self.__time = time

        # Motion of the boundary
        input_db = self.get_input_db()

        assert isinstance(input_db["model"]["motion"], str)
        self.__motion = input_db["model"]["motion"]

        if(self.__motion == "stationary"):
            self.__current_center = self.get_initial_center()
        else:
            quit()


    def get_current_time(self):

        return self.__time

    def get_motion(self):

        return self.__motion

    def get_current_center(self):

        return self.__current_center

    # Nornmal vector
    def get_normal_vector(self, x0, y0, z0):
        x = x0 - self.__current_center[0]
        y = y0 - self.__current_center[1]
        z = z0 - self.__current_center[2]
        R = self.get_radius()

        re_x = x/R
        re_y = y/R
        re_z = z/R

        re = np.array([re_x, re_y, re_z]).T

        return re
    
    # Acceleration of wall motion
    def get_acc(self, x0, y0, z0):

        if(self.__motion == "stationary"):
            acc_x = x0 - x0
            acc_y = y0 - y0
            acc_z = z0 - z0
        else:
            quit()

        return np.array([acc_x,acc_y,acc_z]).T


    # Velocity of wall motion
    def get_Vb(self, x0, y0, z0):

        if(self.__motion == "stationary"): 
            Vb_x = x0 - x0
            Vb_y = y0 - y0
            Vb_z = z0 - z0
        else:
            quit("No this model!!!")

        return np.array([Vb_x,Vb_y,Vb_z]).T


        

class VirtualMovingSphere3D(MovingSphere3D):

    def __init__(self, time):

        super(VirtualMovingSphere3D, self).__init__(time)

        # Virtual motion 
        input_db = self.get_input_db()

        assert isinstance(input_db["model"]["virtualmotion"], str)
        self.__virtualmotion = input_db["model"]["virtualmotion"]



    # Calculate virtual velocity potential 
    def get_virPhi(self, x0, y0, z0):

        x = x0 - self.get_current_center()[0]
        y = y0 - self.get_current_center()[1]
        z = z0 - self.get_current_center()[2]
        R = self.get_radius()

        if (self.__virtualmotion == "virX"):

            phi = - R*R*x/(x*x+y*y+z*z)

        elif (self.__virtualmotion == "virY"):
            
            phi = - R*R*y/(x*x+y*y+z*z)

        elif (self.__virtualmotion == "virZ"):
            
            phi = - R*R*z/(x*x+y*y+z*z)

        elif (self.__virtualmotion == "sourcePoint"):

            collocation_out_x = self.get_input_db()["model"]["sourcePoint"][0]
            collocation_out_y = self.get_input_db()["model"]["sourcePoint"][1]
            collocation_out_z = self.get_input_db()["model"]["sourcePoint"][2]

            collocation_out = np.array([collocation_out_x, collocation_out_y, collocation_out_z])
            collocation_center = self.get_current_center()

            a = np.sqrt((collocation_out[0] - collocation_center[0])**2 + (collocation_out[1] - collocation_center[1])**2 + (collocation_out[2] - collocation_center[2])**2)
            collocation_in = collocation_center + (collocation_out - collocation_center)*R*R/a/a

            point = np.array([x0,y0,z0])

            phi = (ind3D.phi_point_sigma(collocation_out,1,point) 
                   + ind3D.phi_point_sigma(collocation_in,1,point) 
                   + ind3D.phi_point_sigma(collocation_center,-1,point))

        else:
            quit("No this model!!!")

        return np.array([phi]).T

    # Calculate virtual velocity
    def get_virU(self, x0, y0, z0):

        x = x0 - self.get_current_center()[0]
        y = y0 - self.get_current_center()[1]
        z = z0 - self.get_current_center()[2]
        R = self.get_radius()


        if (self.__virtualmotion == "virX"):
            
            U = R*R*(x*x-y*y-z*z)/(x*x+y*y+z*z)/(x*x+y*y+z*z)
            V = R*R*2*x*y/(x*x+y*y+z*z)/(x*x+y*y+z*z)  
            W = R*R*2*x*z/(x*x+y*y+z*z)/(x*x+y*y+z*z)

        elif (self.__virtualmotion == "virY"):
            
            U = R*R*2*y*x/(x*x+y*y+z*z)/(x*x+y*y+z*z)
            V = R*R*(y*y-x*x-z*z)/(x*x+y*y+z*z)/(x*x+y*y+z*z)
            W = R*R*2*y*z/(x*x+y*y+z*z)/(x*x+y*y+z*z)

        elif (self.__virtualmotion == "virZ"):
            
            U = R*R*2*z*x/(x*x+y*y+z*z)/(x*x+y*y+z*z)
            V = R*R*2*z*y/(x*x+y*y+z*z)/(x*x+y*y+z*z)
            W = R*R*(z*z-x*x-y*y)/(x*x+y*y+z*z)/(x*x+y*y+z*z)

        elif (self.__virtualmotion == "sourcePoint"):

            collocation_out_x = self.get_input_db()["model"]["sourcePoint"][0]
            collocation_out_y = self.get_input_db()["model"]["sourcePoint"][1]
            collocation_out_z = self.get_input_db()["model"]["sourcePoint"][2]

            collocation_out = np.array([collocation_out_x, collocation_out_y, collocation_out_z])
            collocation_center = self.get_current_center()

            a = np.sqrt((collocation_out[0] - collocation_center[0])**2 + (collocation_out[1] - collocation_center[1])**2 + (collocation_out[2] - collocation_center[2])**2)
            collocation_in = collocation_center + (collocation_out - collocation_center)*R*R/a/a

            point = np.array([x0,y0,z0])

            re_vel = (ind3D.velocity_point_sigma(collocation_out,1,point)
                      + ind3D.velocity_point_sigma(collocation_in,1,point) 
                      + ind3D.velocity_point_sigma(collocation_center,-1,point))

            U = re_vel[0]
            V = re_vel[1]
            W = re_vel[2]
        

        else:
            quit("No this model!!!")

        vel = np.array([U,V,W]).T

        return vel
