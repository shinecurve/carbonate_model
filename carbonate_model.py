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

import argparse
import sys
import json
import numpy as np
import pandas as pd


# 版本信息
def model_info():
    version_info = "Version: 0.1"
    author_info = "Author: Wang Yang Jun"
    description = "simulation of sedimentation in shallow marine depositional systems"
    print(version_info)
    print(author_info)
    print(description)


# 变量


# 保存文件输入的参数，静态变量(全局共享)
class Params(object):
    model_name = ""
    start_time = 0
    end_time = 0
    time_step = 0

    x_length = 0
    y_length = 0
    grid_spacing = 0

    initial_bathmetry_type = ""
    initial_bathmetry_file = ""
    init_sealevel = 0

    reef = ""
    lagoon = ""
    oolite = ""
    shale = ""

    sealevel_type = ""
    sealevel_file = ""
    sealevel_components = ""
    sealevel_amp = 0
    sealevel_period = 0

    subsidence_rate = 0

    @staticmethod
    def list():
        print(Params.model_name)


# 从json总读入参数
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
        Params.initial_bathmetry_type = json_file["initial_conditions"]["initial_bathmetry_type"]
        Params.initial_bathmetry_file = json_file["initial_conditions"]["initial_bathmetry_file"]
        Params.init_sealevel = json_file["initial_conditions"]["init_sealevel"]
        # lithlogoy
        Params.reef = json_file["lithlogoy"]["reef"]
        Params.lagoon = json_file["lithlogoy"]["lagoon"]
        Params.oolite = json_file["lithlogoy"]["oolite"]
        Params.shale = json_file["lithlogoy"]["shale"]
        # sealevel_conditions
        Params.sealevel_type = json_file["sealevel_conditions"]["sealevel_type"]
        Params.sealevel_file = json_file["sealevel_conditions"]["sealevel_file"]
        Params.sealevel_components = json_file["sealevel_conditions"]["sealevel_components"]
        Params.sealevel_amp = json_file["sealevel_conditions"]["sealevel_amp"]
        Params.sealevel_period = json_file["sealevel_conditions"]["sealevel_period"]
        # sediment
        Params.subsidence_rate = json_file["sediment"]["subsidence_rate"]


# 从文件读入初始地形
def initialise_bathmetry(file_path):
    column_names = ['X', 'Y', 'Z']
    df = pd.read_csv(file_path, delimiter=",", header=None,
                     names=column_names,
                     dtype={'X': int, 'Y': int, 'Z': float})
    # df转为numpy数组
    for i in range(X):
        for j in range(Y):
            bathmetry[i, j] = df[(df.X == (i + 1)) & (df.Y == (j + 1))].Z


if __name__ == '__main__':

    # 传递参数
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
    X = Params.x_length
    Y = Params.y_length

    loopX = 0
    loopY = 0

    # 初始地形

    bathmetry = np.zeros((int(X), int(Y)))

    new_surface = np.zeros((int(X), int(Y)))

    old_surface = np.zeros((int(X), int(Y)))

    strat = np.zeros((int(X), int(Y)))

    water_depth = np.zeros((int(X), int(Y)))

    # 读入初始地形到bathmetry[]
    initialise_bathmetry(Params.initial_bathmetry_file)

    print(bathmetry)


    # 双重循环遍历数组
    '''
    for x in bathmetry:
        for y in x:
            print(y, end=" ")
    '''

    print(bathmetry.shape)




