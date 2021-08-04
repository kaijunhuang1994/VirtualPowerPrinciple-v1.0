import os
import shutil


file_list = []
for name in os.listdir("input/"):
    if(os.path.isfile("input/" + name)):
        file_list.append(name)


split_dir = "../Vpp1_SplitFluidData/input/"
if not os.path.exists(split_dir):
    os.makedirs(split_dir)

calc_dir = "../Vpp2_CalcVirtualFlow/input/"
if not os.path.exists(calc_dir):
    os.makedirs(calc_dir)

visualization_dir = "../Vpp3_FlowVisualization/input/"
if not os.path.exists(visualization_dir):
    os.makedirs(visualization_dir)


for file_name in file_list:
    shutil.copyfile("input/" + file_name, split_dir + file_name)
    shutil.copyfile("input/" + file_name, calc_dir + file_name)
    shutil.copyfile("input/" + file_name, visualization_dir + file_name)