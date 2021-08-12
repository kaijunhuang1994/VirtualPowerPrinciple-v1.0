import Package
from Package.solvercontrol.splitcontrol import SplitControl
from Package.solvercontrol.theorycontrol import TheoryControl

import numpy as np
import pandas as pd
import os

def write_fluid_data():

    file_dir = worksheet_dir + "fluid"
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    

    df = pd.DataFrame(virtualflow.get_virU(fluid_x, fluid_y, fluid_z), columns = ["vir_U", "vir_V", "vir_W"])
    if(split_control.get_write_format() == "h5"):

        filename = worksheet_dir + "fluid/fluid_" + str(int(step)) + ".h5"
        df.to_hdf(filename, key = "data", mode = "w")

    elif(split_control.get_write_format() == "csv"):

        filename = worksheet_dir + "fluid/fluid_" + str(int(step)) + ".dat"
        df.to_csv(filename, index = False, encoding = "utf-8")

    else:
        quit("The format of the stored data is not supported")

def write_boundary_data():

    file_dir = worksheet_dir + boundary_name
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    df_array = np.concatenate((virtualflow.get_acc(boundary_x, boundary_y, boundary_z),
                               virtualflow.get_Vb(boundary_x, boundary_y, boundary_z),
                               virtualflow.get_virU(boundary_x, boundary_y, boundary_z),
                               virtualflow.get_virPhi(boundary_x, boundary_y, boundary_z),
                               virtualflow.get_normal_vector(boundary_x, boundary_y, boundary_z)), axis=1)
    
    df = pd.DataFrame(df_array, 
                      columns = ["acc_x", "acc_y", "acc_z", 
                                 "Vb_x", "Vb_y", "Vb_z",
                                 "virU_x", "virU_y", "virU_z",
                                 "virPhi",
                                 "normal_x", "normal_y", "normal_z"])


    if(split_control.get_write_format() == "h5"):

        filename = worksheet_dir + boundary_name + "/" + boundary_name + "_" + str(int(step)) + ".h5"
        df.to_hdf(filename, key = "data", mode = "w")

    elif(split_control.get_write_format() == "csv"):

        filename = worksheet_dir + boundary_name + "/" + boundary_name + "_" + str(int(step)) + ".dat"
        df.to_csv(filename, index = False, encoding = "utf-8")

    else:
        quit("The format of the stored data is not supported") 


# The main function
if __name__ == "__main__":

    # Read control file: split control, theory control
    split_control = SplitControl("input/splitControlDict")
    theory_control = TheoryControl("input/theoryControlDict")

    # Create a folder named "Worksheet2", which is used to store virtual flow data
    worksheet_dir = split_control.get_write_path() + "_DataDir/Worksheet2/"
    if not os.path.exists(worksheet_dir):
        os.makedirs(worksheet_dir)

    # Path to read the data output from the previous step
    read_dir = split_control.get_write_path() + "_DataDir/Worksheet/"

    

    # Read the list of the time
    solution_time = np.loadtxt(read_dir + "time.dat")

    step_list = solution_time[:,0]
    time_list = solution_time[:,1]

    for step, time in zip(step_list, time_list):

        # Build geometric model
        if(theory_control.get_geometry() == "cylinder2D"):

            from Package.geometry.cylinder2D import VirtualMovingCylinder2D
            virtualflow = VirtualMovingCylinder2D(time)

        elif(theory_control.get_geometry() == "sphere3D"):

            from Package.geometry.sphere3D import *
            virtualflow = VirtualMovingSphere3D()

        else:
            quit()

        # Read flow field coordinates
        if(split_control.get_write_format() == "h5"):

            filename = read_dir + "fluid/fluid_" + str(int(step)) + ".h5"
            df = pd.read_hdf(filename, key='data')

        elif(split_control.get_write_format() == "csv"):

            filename = read_dir + "fluid/fluid_" + str(int(step)) + ".dat"
            df = pd.read_csv(filename)
        
        fluid_x = df['X C'].values
        fluid_y = df['Y C'].values
        fluid_z = df['Z C'].values
   
        write_fluid_data()

        boundary_name = split_control.get_internal_boundary()[1][0]

        if(split_control.get_write_format() == "h5"):

            filename = read_dir + boundary_name + "/" + boundary_name + "_" + str(int(step)) + ".h5"
            df = pd.read_hdf(filename, key='data')

        elif(split_control.get_write_format() == "csv"):

            filename = read_dir + boundary_name + "/" + boundary_name + "_" + str(int(step)) + ".dat"
            df = pd.read_csv(filename)

        else:
            quit(("The format of the stored data is not supported"))

        boundary_x = df['X C'].values
        boundary_y = df['Y C'].values
        boundary_z = df['Z C'].values

        write_boundary_data()

    print("Virtual flow solved successfully")
