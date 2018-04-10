#!/usr/bin/python
# -*- coding:utf8 -*-

import time
import matlab.engine
from data import Data
from RBAllocation import *
import os

slot_num = 20  # 循环次数

for slot in range(slot_num):
    print "循环次数：", slot
    time_index = int(time.time())

    dict_id2device = {}  # 车辆id-设备对象登记表
    dict_id2rx = {}  # 车辆id-接收机对象登记表
    dict_id2tx = {}  # 车辆id-发射机对象登记表
    dict_id2channel = {}  # 接收车辆id-信道对象登记表
    dict_data = {}  # 数据集

    rsu_num = 1
    V2I_vehicle_num = 10
    V2V_vehicle_num = 20
    RB_num = 10  # 可分配信道数

    highway = Highway(-1000, 0, 1000, 0)  # 生成高速公路对象，赋值起始位置

    for i in range(rsu_num):
        temp_rsu = RSU(i)  # 生成路边单元对象
        dict_id2device[temp_rsu.get_id()] = temp_rsu
        dict_id2tx[temp_rsu.get_id()] = temp_rsu

    # 生成车辆对象，存入车辆id-车辆对象登记表

    # 生成 V2I 车辆 下行链路
    for i in range(rsu_num, rsu_num + V2I_vehicle_num):
        temp_rx_vehicle = V2IVehicle(i)
        temp_rx_vehicle.update_location(highway)
        dict_id2device[temp_rx_vehicle.get_id()] = temp_rx_vehicle
        dict_id2rx[temp_rx_vehicle.get_id()] = temp_rx_vehicle

    for i in range(rsu_num + V2I_vehicle_num, rsu_num + V2I_vehicle_num + V2V_vehicle_num):
        # 生成 V2V Tx 车辆
        temp_tx_vehicle = V2VTxVehicle(i)
        temp_tx_vehicle.update_location(highway)
        dict_id2device[temp_tx_vehicle.get_id()] = temp_tx_vehicle
        dict_id2tx[temp_tx_vehicle.get_id()] = temp_tx_vehicle

        # 生成 V2V Rx 车辆
        temp_rx_vehicle = V2VRxVehicle(i + V2V_vehicle_num)
        temp_rx_vehicle.update_location(highway, temp_tx_vehicle)
        dict_id2device[temp_rx_vehicle.get_id()] = temp_rx_vehicle
        dict_id2rx[temp_rx_vehicle.get_id()] = temp_rx_vehicle

    # 生成信道 一个接收机对应一个信道对象
    for rx_id in dict_id2rx:  # 遍历所有的接收机
        temp_channel = Channel(rx_id)

        for tx_id in dict_id2tx:  # 遍历所有的发射机
            temp_channel.update_link_loss(dict_id2tx[tx_id], dict_id2rx[rx_id])

        dict_id2channel[temp_channel.get_rx_id()] = temp_channel

    # 计算干扰权值
    for rx_id in dict_id2rx:  # 遍历所有的接收机
        temp_rx = dict_id2rx[rx_id]
        temp_rx.work(dict_id2tx, dict_id2channel)

    # 统计数据集
    index = 1  # 为数据计数
    for rx_id in dict_id2rx:
        temp_rx = dict_id2rx[rx_id]
        temp_channel = dict_id2channel[rx_id]
        for tx_id in dict_id2tx:
            if tx_id != temp_rx.get_tx_id():
                # 场景
                is_highway = 1
                is_suburban = 0
                is_urban = 0
                # 行进方向
                t_is_reverse = 0
                t_is_forward = 0
                t_is_convoy = 0
                i_is_reverse = 0
                i_is_forward = 0
                i_is_convoy = 0
                i_direction = temp_channel.get_direction(tx_id)
                if i_direction == "reverse":
                    i_is_reverse = 1
                elif i_direction == "forward":
                    i_is_forward = 1
                else:
                    i_is_convoy = 1
                t_direction = temp_channel.get_direction(temp_rx.get_tx_id())
                if t_direction == "reverse":
                    t_is_reverse = 1
                elif t_direction == "forward":
                    t_is_forward = 1
                else:
                    t_is_convoy = 1
                # 距离
                target_distance = temp_channel.get_distance(temp_rx.get_tx_id())
                inter_distance = temp_channel.get_distance(tx_id)
                # 功率
                target_power = dict_id2tx[temp_rx.get_tx_id()].get_power()
                inter_power = dict_id2tx[tx_id].get_power()
                # 权值
                weight = temp_rx.get_weight(tx_id)

                # 统计出一组数据
                temp_data = Data(time_index, index, tx_id, rx_id, is_highway, is_suburban, is_urban,
                                 t_is_reverse, t_is_forward, t_is_convoy, i_is_reverse, i_is_forward, i_is_convoy,
                                 target_distance, inter_distance, target_power, inter_power, weight)
                dict_data[index] = temp_data
                index += 1

    # 输出数据集到csv文件
    os.remove("testData.csv")  # 删除上次循环的数据
    for index in dict_data:
        temp_data = dict_data[index]
        temp_data.print2csv()

    # 调用 matlab 引擎
    eng = matlab.engine.start_matlab()
    eng.test(nargout=0)

    ###########################################################################################
    # # 随机分配信道
    # random_allocation(dict_id2tx, dict_id2rx, RB_num)
    #
    # # 计算接收SINR
    # list_sinr = []
    # for rx_id in dict_id2rx:
    #     dict_id2rx[rx_id].comp_sinr(dict_id2tx, dict_id2channel)
    #     list_sinr.append(dict_id2rx[rx_id].get_sinr())
    #     print "接收用户：", rx_id, "SINR:", dict_id2rx[rx_id].get_sinr()
    #
    # # list_sinr.sort()
    # sum_sinr = 0
    # for sinr in list_sinr:
    #     # print sinr
    #     sum_sinr += sinr
    # print "总SINR：", sum_sinr
    ###########################################################################################

    ###########################################################################################
    # 神经网络分类图着色分配信道
    net_allocation(dict_id2tx, dict_id2rx, RB_num)

    # 计算接收SINR
    list_sinr = []
    for rx_id in dict_id2rx:
        dict_id2rx[rx_id].comp_sinr(dict_id2tx, dict_id2channel)
        list_sinr.append(dict_id2rx[rx_id].get_sinr())
        print "接收用户：", rx_id, "SINR:", dict_id2rx[rx_id].get_sinr()

        # 将用户接收 sinr 写入文件
        file_name = "net_sinr.csv"
        with open(file_name, "ab") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([dict_id2rx[rx_id].get_sinr()])
        csv_file.close()

        if dict_id2rx[rx_id].get_tx_id() == 0:
            # 将V2I用户接收 sinr 写入文件
            file_name = "net_V2I_sinr.csv"
            with open(file_name, "ab") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([dict_id2rx[rx_id].get_sinr()])
            csv_file.close()
        else:
            # 将V2V用户接收 sinr 写入文件
            file_name = "net_V2V_sinr.csv"
            with open(file_name, "ab") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([dict_id2rx[rx_id].get_sinr()])
            csv_file.close()

    sum_sinr = 0
    for sinr in list_sinr:
        # print sinr
        sum_sinr += sinr
    print "总SINR：", sum_sinr
    ###########################################################################################

    ###########################################################################################
    # 分类图着色分配信道
    graph_allocation(dict_id2tx, dict_id2rx, RB_num)

    # 计算接收SINR
    list_sinr = []
    for rx_id in dict_id2rx:
        dict_id2rx[rx_id].comp_sinr(dict_id2tx, dict_id2channel)
        list_sinr.append(dict_id2rx[rx_id].get_sinr())
        print "接收用户：", rx_id, "SINR:", dict_id2rx[rx_id].get_sinr()

        # 将用户接收 sinr 写入文件
        file_name = "graph_sinr.csv"
        with open(file_name, "ab") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([dict_id2rx[rx_id].get_sinr()])
        csv_file.close()

        if dict_id2rx[rx_id].get_tx_id() == 0:
            # 将V2I用户接收 sinr 写入文件
            file_name = "graph_V2I_sinr.csv"
            with open(file_name, "ab") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([dict_id2rx[rx_id].get_sinr()])
            csv_file.close()
        else:
            # 将V2V用户接收 sinr 写入文件
            file_name = "graph_V2V_sinr.csv"
            with open(file_name, "ab") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([dict_id2rx[rx_id].get_sinr()])
            csv_file.close()

    sum_sinr = 0
    for sinr in list_sinr:
        # print sinr
        sum_sinr += sinr
    print "总SINR：", sum_sinr
    ###########################################################################################

print("finish！")
