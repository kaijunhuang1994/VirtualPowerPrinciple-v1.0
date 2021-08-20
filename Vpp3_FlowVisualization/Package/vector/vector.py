import numpy as np

class Vector:

    def __init__(self, x, y, z):

        self.__x = x
        self.__y = y
        self.__z = z

    def x(self):

        return self.__x

    def y(self):
        
        return self.__y

    def z(self):
        
        return self.__z


    def dot(self, A):
               
        result = A.x() * self.x() + A.y() * self.y() + A.z() * self.z()

        return result

    
    def times(self, A):
        
        result_x = self.y() * A.z() - self.z() * A.y()
        result_y = - self.x() * A.z() + self.z() * A.x()
        result_z = self.x() * A.y() - self.y() * A.x()

        return Vector(result_x, result_y, result_z)

    def write(self):

        print("Vector = (", self.x(), ",", self.y(), ",", self.z(), ")")