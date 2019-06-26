#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This file is part of Carbonate_Model.

Carbonate_Model is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Carbonate_Model is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Carbonate_Model.  If not, see <https://www.gnu.org/licenses/>.

@license : GPL-3.0
@author  : Wang Yang Jun
@contact : wyj1988@me.com
@file    : carbonate_model.py
@date    : 04-22-2019 14:01
"""

import random
import argparse
import sys
import json
import numpy as np
import pandas as pd
import h5py


# 版本信息
def model_info():
    version_info = "Version: 0.1"
    author_info = "Author: Wang Yang Jun"
    description = "simulation of sedimentation in shallow marine depositional systems"
    print(version_info)
    print(author_info)
    print(description)


# 获取变量名字符串
class varname():
    def __getattr__(self, attr):
        return attr


# 读入参数
class Params(object):
    model_name = ""
    start_time = 0
    end_time = 0
    time_step = 0

    x_length = 0
    y_length = 0
    grid_spacing = 0

    initial_bathymetry_type = ""
    initial_bathymetry_file = ""
    init_sealevel = 0

    reef = ""
    lagoon = ""
    oolite = ""
    shale = ""

    sealevel_type = ""
    sealevel_init = 0
    sealevel_file = ""
    sealevel_components = ""
    sealevel_amp = 0
    sealevel_period = 0

    distribute_type = ""
    profile_type = ""

    subsidence_rate = 0

    @staticmethod
    def list():
        print(Params.model_name)


# 预定义参数
chrons_max = 2000
RADIUS_SCALING_FACTOR = 2.0


# 从json读入外部参数
def read_params(file_path):
    with open(file_path) as f:
        json_file = json.load(f)
        # main
        Params.model_name = json_file["main"]["model_name"]
        Params.start_time = json_file["main"]["start_time"]
        Params.end_time = json_file["main"]["end_time"]
        Params.time_step = json_file["main"]["time_step"]
        # grid
        Params.x_length = json_file["grid"]["x_length"]
        Params.y_length = json_file["grid"]["y_length"]
        Params.grid_spacing = json_file["grid"]["grid_spacing"]
        # initial_conditions
        Params.initial_bathymetry_type = json_file["initial_conditions"]["initial_bathymetry_type"]
        Params.initial_bathymetry_file = json_file["initial_conditions"]["initial_bathymetry_file"]
        Params.init_sealevel = json_file["initial_conditions"]["init_sealevel"]
        # lithology
        Params.reef = json_file["lithology"]["reef"]
        Params.lagoon = json_file["lithology"]["lagoon"]
        Params.oolite = json_file["lithology"]["oolite"]
        Params.shale = json_file["lithology"]["shale"]
        # sealevel_conditions
        Params.sealevel_type = json_file["sealevel_conditions"]["sealevel_type"]
        Params.sealevel_init = json_file["sealevel_conditions"]["sealevel_init"]
        Params.sealevel_file = json_file["sealevel_conditions"]["sealevel_file"]
        Params.sealevel_components = json_file["sealevel_conditions"]["sealevel_components"]
        Params.sealevel_amp = json_file["sealevel_conditions"]["sealevel_amp"]
        Params.sealevel_period = json_file["sealevel_conditions"]["sealevel_period"]
        # carbonates_type
        Params.distribute_type = json_file["carbonates_type"]["distribute_type"]
        Params.profile_type = json_file["carbonates_type"]["profile_type"]
        # sediment
        Params.subsidence_rate = json_file["sediment"]["subsidence_rate"]


# 从文件读入初始地形
def initialise_bathymetry(file_path):
    column_names = ['X', 'Y', 'Z']
    df = pd.read_csv(file_path, delimiter=",", header=None,
                     names=column_names,
                     dtype={'X': int, 'Y': int, 'Z': float})
    df_x_max = df['X'].max() + 1
    df_y_max = df['Y'].max() + 1
    global bathymetry
    bathymetry = np.zeros([df_x_max, df_y_max])
    for row in df.itertuples(index=True, name='Z'):
        bathymetry[getattr(row, "X"), getattr(row, "Y")] = getattr(row, "Z")


# 写入文件
def make_hdf5_file(file_path, *variables):
    file = h5py.File(file_path, "w")
    for variable in variables:
        name = varname()
        file.create_dataset(name.variable, data=variable)
    file.close()


# 数组初始化
def initialise_arrays():
    global bathymetry
    bathymetry = np.zeros((int(x_max), int(y_max)))
    global new_bathymetry
    new_bathymetry = np.zeros((int(x_max), int(y_max)))
    global new_surface
    new_surface = np.zeros((int(x_max), int(y_max)))
    global old_surface
    old_surface = np.zeros((int(x_max), int(y_max)))
    global strat
    strat = np.zeros((int(x_max), int(y_max), int(chrons_max)))
    global water_depth
    water_depth = np.zeros((int(x_max), int(y_max)))
    global mosaic_radius
    mosaic_radius = np.zeros(int(chrons_max))


# 初始化sed_type
def init_sed_type():
    global sed_type
    sed_type = np.zeros((int(x_max), int(y_max)))


def make_2d_list(rows, cols):
    ll = []
    for row in range(rows):
        ll += [[0] * cols]
    return ll


# 半径的指数分布程序
def init_exponential_area_array():
    loop = -1
    marker = 0
    radius = 1
    global mosaic_thick_distrib
    mosaic_thick_distrib = make_2d_list(0, 2)

    while True:
        frequency = 333.0 * np.exp(-0.666 * radius)
        while loop < marker + int(frequency + 0.5):
            mosaic_radius[loop] = radius * RADIUS_SCALING_FACTOR
            loop += 1
        if frequency + 0.5 > 1:
            marker = loop + 1
        radius += 1
        if radius < 20.0:
            break

    mosaic_radii_count = marker

    for loop in range(0, 9999, 1):
        element = int(random.random() * mosaic_radii_count)
        radius = mosaic_radius[element]
        mosaic_thick_distrib.append([element, radius])

    mosaic_thick_distrib = np.array(mosaic_thick_distrib)


# 主程序
if __name__ == '__main__':

    # 主程序传递参数
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', action='store', dest='json_path',
                        help='specify the path of params file.')
    parser.add_argument('-v', action='store_true', dest='version', help='version information')
    args = parser.parse_args()
    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(0)
    if args.version:
        model_info()
        sys.exit(0)
    if args.json_path:
        json_path = ''.join(map(str, args.json_path))

    print('The files {0!s} will be read into model.'.format(json_path))

    # 读参数
    read_params(json_path)

    # 列出参数
    Params.list()

    # 初始化
    # 网格数
    x_max = Params.x_length + 1
    y_max = Params.y_length + 1

    loopX = 0
    loopY = 0

    sealevel = Params.sealevel_init

    # 数组初始化
    initialise_arrays()

    # 读入初始地形到bathymetry[]，并赋值给其他数组
    initialise_bathymetry(Params.initial_bathymetry_file)
    new_surface = old_surface = strat = bathymetry.copy()

    # 初始化sed_type
    init_sed_type()

    init_exponential_area_array()
    # 定义总周期
    chrons_total = (Params.end_time - Params.start_time) / Params.time_step
    chron = 1
    emt = 0

    print(bathymetry)
    print(bathymetry.shape)
    print(chrons_total)

    [rows, cols] = bathymetry.shape
    print(rows, cols)
    for i in range(1, rows, 1):
        for j in range(1, cols, 1):
            new_bathymetry[i, j] = bathymetry[i, j] + 1

    print(new_bathymetry)


    print(mosaic_thick_distrib)
    make_hdf5_file("mosaic_thick_distrib.hdf5", mosaic_thick_distrib)
