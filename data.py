#!/usr/bin/python
# -*- coding:utf8 -*-

import csv


class Data(object):
    def __init__(self, time_index, index, tx_device_id, rx_device_id, highway, suburban, urban,
                 t_reverse, t_forward, t_convoy, i_reverse, i_forward, i_convoy,
                 target_distance, inter_distance, target_power, inter_power, weight):
        self.__time_index = time_index  # 时间戳
        self.__index = index
        self.__tx_id = tx_device_id
        self.__rx_id = rx_device_id
        self.__highway = highway
        self.__suburban = suburban
        self.__urban = urban
        self.__t_reverse = t_reverse
        self.__t_forward = t_forward
        self.__t_convoy = t_convoy
        self.__i_reverse = i_reverse
        self.__i_forward = i_forward
        self.__i_convoy = i_convoy
        self.__target_distance = target_distance
        self.__inter_distance = inter_distance
        self.__target_power = target_power
        self.__inter_power = inter_power

        self.__weight = weight

        self.__inter_class = 0  # 干扰级别 0-0.1(1) 0.1-1(2) >1(3)

        if weight > 1:
            self.__inter_class = 3
        elif weight < 0.2:
            self.__inter_class = 1
        else:
            self.__inter_class = 2

    def print2csv(self):
        # 带有列名和行号
        file_name1 = "data_" + str(self.__time_index) + ".csv"
        with open(file_name1, "ab") as csv_file1:
            writer = csv.writer(csv_file1)
            if self.__index == 1:
                writer.writerow(["index", "tx_id", "rx_id", "highway", "suburban", "urban",
                                 "t_reverse", "t_forward", "t_convoy", "i_reverse", "i_forward", "i_convoy",
                                 "target_distance", "inter_distance",
                                 "target_power", "inter_power", "weight", "inter_class"])
            writer.writerow([self.__index, self.__tx_id, self.__rx_id,
                             self.__highway, self.__suburban, self.__urban,
                             self.__t_reverse, self.__t_forward, self.__t_convoy,
                             self.__i_reverse, self.__i_forward, self.__i_convoy,
                             self.__target_distance, self.__inter_distance,
                             self.__target_power, self.__inter_power, self.__weight, self.__inter_class])
        csv_file1.close()

        # 纯数据 无列名和行号
        file_name2 = "data_pure_" + str(self.__time_index) + ".csv"
        with open(file_name2, "ab") as csv_file2:
            writer = csv.writer(csv_file2)
            writer.writerow([self.__highway, self.__suburban, self.__urban,
                             self.__t_reverse, self.__t_forward, self.__t_convoy,
                             self.__i_reverse, self.__i_forward, self.__i_convoy,
                             self.__target_distance, self.__inter_distance,
                             self.__target_power, self.__inter_power, self.__weight, self.__inter_class])
        csv_file2.close()
