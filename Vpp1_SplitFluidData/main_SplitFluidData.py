import tecplot 
from tecplot.exception import *
from tecplot.constant import *

import Package
from Package.solver.solvercontrol import SolverControl

import numpy as np
import pandas as pd
import os

from shutil import copy


tecplot.session.connect(port=7600)

# Read split control file
solver_control = SolverControl("input/splitControlDict")

# Create a folder named "_DataDir", which is used to store temporary data (The whole virtual power analysis data)
write_dir = solver_control.get_write_path() + "_DataDir/"
if not os.path.exists(write_dir):
    os.makedirs(write_dir)

# Create a folder named "Worksheet", which is used to store split data
worksheet_dir = write_dir + "Worksheet/"
if not os.path.exists(worksheet_dir):
    os.makedirs(worksheet_dir)

# Copy splitControlDict to Worksheet
copy("input/splitControlDict", worksheet_dir)

# Read openfoam case (controlDcit file)
dataset = tecplot.data.load_openfoam(
    solver_control.get_case_path(),
    frame=None,
    append=False,
    boundary_zone_construction=None,
    assign_strand_ids=True,
    add_zones_to_existing_strands=True,
    initial_plot_type=PlotType.Automatic,
    initial_plot_first_zone_only=False)


# Split the Tecplot data of each time step
num_zones = solver_control.get_num_zones()
for step,time in enumerate(dataset.solution_times):

    # Skip t = 0
    if step == 0:
        continue
    
    print("write tecplot data, time = ",time)

    # Create a list to save each step time's zone data
    zone_to_save = []

    for i in range(num_zones):
        zone_to_save.append(dataset.zone(step * num_zones + i))


    # The flow field data of each time step is saved in the "plt" format
    path = worksheet_dir + "fluid_plt/"
    if not os.path.exists(path):
        os.makedirs(path)
    
    write_name = path + "fluid_" + str(step) + ".plt"
    tecplot.data.save_tecplot_plt(
        write_name, 
        dataset=dataset,              
        zones=zone_to_save)
    


# Write the boundary data and the grid data of each time step
for step,time in enumerate(dataset.solution_times):

    # Skip t = 0
    if step == 0:
        continue
    
    print("write fluid data, time = ",time)

    fluid_x = dataset.zone(step * num_zones).values("X C").as_numpy_array()
    fluid_y = dataset.zone(step * num_zones).values("Y C").as_numpy_array()
    fluid_z = dataset.zone(step * num_zones).values("Z C").as_numpy_array()

    df = pd.DataFrame(np.array([fluid_x, fluid_y, fluid_z]).T, columns = ["X C", "Y C", "Z C"])

    path =  worksheet_dir + "fluid/"
    if not os.path.exists(path):
        os.makedirs(path)

    if(solver_control.get_write_format() == "h5"):
        
        filename = path + "fluid_" + str(step) + ".h5"
        df.to_hdf(filename, key = "data", mode = "w")

    elif(solver_control.get_write_format() == "csv"):

        filename = path + "fluid_" + str(step) + ".dat"
        df.to_csv(filename, index = False, encoding = "utf-8")

    else:
        quit("The format of the stored data is not supported")

    
    
    if(solver_control.whether_write_internal_boundary()):
        
        boundary_index, boundary_name = solver_control.get_internal_boundary()

        for i in range(len(boundary_index)):

            boundary_x = dataset.zone(step * num_zones + boundary_index[i]).values("X C").as_numpy_array()
            boundary_y = dataset.zone(step * num_zones + boundary_index[i]).values("Y C").as_numpy_array()
            boundary_z = dataset.zone(step * num_zones + boundary_index[i]).values("Z C").as_numpy_array()

            df = pd.DataFrame(np.array([boundary_x, boundary_y, boundary_z]).T, columns = ["X C", "Y C", "Z C"])

            path =  worksheet_dir + boundary_name[i] + "/"
            if not os.path.exists(path):
                os.makedirs(path)

            if(solver_control.get_write_format() == "h5"):
        
                filename = path + boundary_name[i] + "_" + str(step) + ".h5"
                df.to_hdf(filename, key = "data", mode = "w")

            elif(solver_control.get_write_format() == "csv"):

                filename = path + boundary_name[i] + "_" + str(step) + ".dat"
                df.to_csv(filename, index = False, encoding = "utf-8")

            else:
                quit("The format of the stored data is not supported")


    if(solver_control.whether_write_external_boundary()):
        
        boundary_index, boundary_name = solver_control.get_external_boundary()

        for i in range(len(boundary_index)):

            boundary_x = dataset.zone(step * num_zones + boundary_index[i]).values("X C").as_numpy_array()
            boundary_y = dataset.zone(step * num_zones + boundary_index[i]).values("Y C").as_numpy_array()
            boundary_z = dataset.zone(step * num_zones + boundary_index[i]).values("Z C").as_numpy_array()

            df = pd.DataFrame(np.array([boundary_x, boundary_y, boundary_z]).T, columns = ["X C", "Y C", "Z C"])

            path =  worksheet_dir + boundary_name[i] + "/"
            if not os.path.exists(path):
                os.makedirs(path)

            if(solver_control.get_write_format() == "h5"):
        
                filename = path + boundary_name[i] + "_" + str(step) + ".h5"
                df.to_hdf(filename, key = "data", mode = "w")

            elif(solver_control.get_write_format() == "csv"):

                filename = path + boundary_name[i] + "_" + str(step) + ".dat"
                df.to_csv(filename, index = False, encoding = "utf-8")

            else:
                quit("The format of the stored data is not supported")



# Write the time list
filename = worksheet_dir + "time.dat"
with open(filename,'w') as f:
    for step,time in enumerate(dataset.solution_times):
        if time == 0:
            continue
        f.writelines([str(step), "    ", str(time), "\n"])
        
print("Data split succeeded")
