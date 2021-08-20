from Package.vector.vector import Vector
import tecplot 
from tecplot.exception import *
from tecplot.constant import *

from Package.solvercontrol.splitcontrol import SplitControl
from Package.solvercontrol.theorycontrol import TheoryControl

import numpy as np
import pandas as pd
import os

tecplot.session.connect(port=7600)

# Read control file
split_control = SplitControl("input/splitControlDict")
theory_control = TheoryControl("input/theoryControlDict")

# Create a folder named "result", which is used to store flow visualization data
result_dir = split_control.get_write_path() + "_DataDir/Result/"
if not os.path.exists(result_dir):
    os.makedirs(result_dir)

# Path to read the data output from the previous step
read_dir = split_control.get_write_path() + "_DataDir/"

# Read the list of the time
solution_time = np.loadtxt(read_dir + "Worksheet/" + "time.dat")
step_list = solution_time[:,0]
time_list = solution_time[:,1]

# Split the Tecplot data of each time step
num_zones = split_control.get_num_zones()

# Viscosity coefficient
mu = 1.0/150
print("The Reynolds number is ", 1/mu)

Pressure_data =pd.DataFrame(columns=['time','Pressure','dU_Square','vir_lamb','vir_friction','Pressure_prediction'])


for step, time in zip(step_list, time_list):

    tecplot.new_layout()

    print("time = ", time)

    path = read_dir + "Worksheet/fluid_plt/fluid_" + str(int(step)) + ".plt"

    dataset = tecplot.data.load_tecplot(
        path,
        frame=None,
        read_data_option=ReadDataOption.Append,
        reset_style=None,
        initial_plot_first_zone_only=None,
        initial_plot_type=None,
        zones=None,
        variables=None,
        collapse=None,
        skip=None,
        assign_strand_ids=True,
        add_zones_to_existing_strands=None,
        include_text=None,
        include_geom=None,
        include_custom_labels=None,
        include_data=None)


    # Pressure data
    point =  theory_control.get_source_point()
    result = tecplot.data.query.probe_at_position(point[0], point[1], point[2])
    if result is None:
        print('probe failed.')
    else:
        data, cell, zone = result

    Element_ID = dataset.zone(0).values('Element UserID')[:]
    position_index = np.where(Element_ID == cell[1] + 1)

    pressure_CFD = dataset.zone(0).values('pressure')[position_index[0]]
    print('Pressure_CFD = ', pressure_CFD)

    U_CFD = dataset.zone(0).values('U')[position_index[0]]
    V_CFD = dataset.zone(0).values('V')[position_index[0]]
    W_CFD = dataset.zone(0).values('W')[position_index[0]]

    dU_Square = 0.5 - (U_CFD * U_CFD + V_CFD * V_CFD + W_CFD * W_CFD) / 2
    # dU_Square = 0.0266141 + 0.516767 - (U_CFD * U_CFD + V_CFD * V_CFD + W_CFD * W_CFD) / 2

    print(U_CFD, V_CFD, W_CFD)
    print((U_CFD * U_CFD + V_CFD * V_CFD + W_CFD * W_CFD) / 2)
    print("index = ", position_index[0])

    # Draw virtual flow field
    tecplot.data.operate.execute_equation(
        "{vir_U} = 0 \n {vir_V} = 0 \n {vir_W} = 0", 
        zones=None, 
        i_range=None, 
        j_range=None,
        k_range=None, 
        value_location=ValueLocation.CellCentered, 
        variable_data_type=None,
        ignore_divide_by_zero=None)

    if(split_control.get_write_format() == "h5"):

        filename =  read_dir + "Worksheet2/fluid/fluid_" + str(int(step)) + ".h5"
        df = pd.read_hdf(filename, key = "data")

    elif(split_control.get_write_format() == "csv"):

        filename =  read_dir + "Worksheet2/fluid/fluid_" + str(int(step)) + ".dat"
        df = pd.read_csv(filename)

 
    vir_U, vir_V, vir_W = df["vir_U"].values, df["vir_V"].values, df["vir_W"].values
    virU = Vector(vir_U, vir_V, vir_W)

    dataset.zone(0).values("vir_U")[:] = np.copy(vir_U)
    dataset.zone(0).values("vir_V")[:] = np.copy(vir_V)
    dataset.zone(0).values("vir_W")[:] = np.copy(vir_W)

    # Calculate weighted lamb vector
    tecplot.data.operate.execute_equation(
        "{vir_lamb} = 0", 
        zones=None, 
        i_range=None, 
        j_range=None,
        k_range=None, 
        value_location=ValueLocation.CellCentered, 
        variable_data_type=None,
        ignore_divide_by_zero=None)

    velocity_x = dataset.zone(0).values("U").as_numpy_array()
    velocity_y = dataset.zone(0).values("V").as_numpy_array()
    velocity_z = dataset.zone(0).values("W").as_numpy_array()
    velocity = Vector(velocity_x, velocity_y, velocity_z)

    vorticity_x = dataset.zone(0).values("X vorticity").as_numpy_array()
    vorticity_y = dataset.zone(0).values("Y vorticity").as_numpy_array()
    vorticity_z = dataset.zone(0).values("Z vorticity").as_numpy_array()
    vorticity = Vector(vorticity_x, vorticity_y, vorticity_z)

    lamb = vorticity.times(velocity)
    vir_lamb = lamb.dot(virU)

    dataset.zone(0).values("vir_lamb")[:] = np.copy(vir_lamb)

    tecplot.macro.execute_extended_command('CFDAnalyzer4', '''
        Integrate [{index}]
        VariableOption='Scalar'
        XOrigin=0 YOrigin=0 ZOrigin=0
        ScalarVar={scalar_var}
        Absolute='F' 
        ExcludeBlanked='F'
        XVariable=1 YVariable=2 ZVariable=3
        IntegrateOver='Cells'
        IntegrateBy='Zones'
        PlotResults='F'
        PlotAs='Result'
    '''.format(scalar_var=dataset.variable("vir_lamb").index + 1, index = 0 + 1))

    frame = tecplot.active_frame()
    vir_lamb_integral = float(frame.aux_data['CFDA.INTEGRATION_TOTAL'])
    print("vir_lamb_integral = ", vir_lamb_integral)

    # Calculate weighted friction
    tecplot.data.operate.execute_equation(
        "{vir_friction} = 0", 
        zones=None, 
        i_range=None, 
        j_range=None,
        k_range=None, 
        value_location=ValueLocation.CellCentered, 
        variable_data_type=None,
        ignore_divide_by_zero=None)

    if(split_control.get_write_format() == "h5"):
        
        filename =  read_dir + "Worksheet2/cylinder/cylinder_" + str(int(step)) + ".h5"
        df = pd.read_hdf(filename, key = "data")

    elif(split_control.get_write_format() == "csv"):
        
        filename =  read_dir + "Worksheet2/cylinder/cylinder_" + str(int(step)) + ".dat"
        df = pd.read_csv(filename)

    normal_x, normal_y, normal_z = df["normal_x"].values, df["normal_y"].values, df["normal_z"].values
    normal = Vector(normal_x, normal_y, normal_z)

    vorticity_x = dataset.zone(5).values("X vorticity").as_numpy_array()
    vorticity_y = dataset.zone(5).values("Y vorticity").as_numpy_array()
    vorticity_z = dataset.zone(5).values("Z vorticity").as_numpy_array()
    vorticity = Vector(vorticity_x, vorticity_y, vorticity_z)

    vir_U, vir_V, vir_W = df["virU_x"].values, df["virU_y"].values, df["virU_z"].values
    virU = Vector(vir_U, vir_V, vir_W)

    friction = normal.times(vorticity)
    vir_friction = friction.dot(virU) * mu * (-1)

    ### 修正奇点

    ###

    dataset.zone(5).values("vir_friction")[:] = np.copy(vir_friction)

    tecplot.macro.execute_extended_command('CFDAnalyzer4', '''
        Integrate [{index}]
        VariableOption='Scalar'
        XOrigin=0 YOrigin=0 ZOrigin=0
        ScalarVar={scalar_var}
        Absolute='F' 
        ExcludeBlanked='F'
        XVariable=1 YVariable=2 ZVariable=3
        IntegrateOver='Cells'
        IntegrateBy='Zones'
        PlotResults='F'
        PlotAs='Result'
    '''.format(scalar_var=dataset.variable("vir_friction").index + 1, index = 5 + 1))

    frame = tecplot.active_frame()
    vir_friction_integral = float(frame.aux_data['CFDA.INTEGRATION_TOTAL'])
    print("vir_friction_integral =", vir_friction_integral)
    print("dU_Square = ", dU_Square)

    Pressure_prediction = vir_lamb_integral + vir_friction_integral + dU_Square
    print("Pressure_prediction = ", Pressure_prediction)


    new_line = pd.DataFrame([[time, pressure_CFD, dU_Square, vir_lamb_integral, vir_friction_integral, Pressure_prediction]], 
                            columns=['time','Pressure','dU_Square','vir_lamb','vir_friction','Pressure_prediction'])

    pressure_data = Pressure_data.append(new_line, ignore_index=True)
    
    write_dir = result_dir + "fluid_vir/"
    if not os.path.exists(write_dir):
        os.makedirs(write_dir)

    write_name = write_dir + "fluid_vir_" + str(int(step)) + ".plt"
    tecplot.data.save_tecplot_plt(
        write_name, 
        dataset=dataset) 

    break

pressure_data.to_excel(result_dir + "pressure.xlsx",index=False) 