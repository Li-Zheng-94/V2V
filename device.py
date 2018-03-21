#!/usr/bin/python
# -*- coding:utf8 -*-

import random
import math

random.seed()  # 随机数种子


class Interface(object):
    def __init__(self, i_id):
        self.__id = i_id

    def get_id(self):
        return self.__id


class Highway(object):
    def __init__(self, start_x_point, start_y_point, end_x_point, end_y_point):
        self.__start_x_point = start_x_point
        self.__start_y_point = start_y_point
        self.__end_x_point = end_x_point
        self.__end_y_point = end_y_point

    def get_start_x_point(self):
        return self.__start_x_point

    def get_start_y_point(self):
        return self.__start_y_point

    def get_end_x_point(self):
        return self.__end_x_point

    def get_end_y_point(self):
        return self.__end_y_point


class Vehicle(Interface):
    def __init__(self, i_id):
        # 调用父类的构造函数
        Interface.__init__(self, i_id)

        # 随机生成车辆行进方向
        rand_num = random.random()
        if rand_num > 0.5:
            self.__direction = 1  # 正方向
        else:
            self.__direction = -1  # 负方向

        self.__x_point = -1
        self.__y_point = -1

    def set_location(self, x_point, y_point):
        self.__x_point = x_point
        self.__y_point = y_point

    def get_x_point(self):
        return self.__x_point

    def get_y_point(self):
        return self.__y_point

    def get_direction(self):
        return self.__direction


class V2IVehicle(Vehicle):
    def __init__(self, i_id):
        # 调用父类的构造函数
        Vehicle.__init__(self, i_id)
        self.__txID = 0
        self.__inter_txID2weight = {}  # 存储干扰权值的字典 键——干扰发射机ID 值——干扰权值

    def update_location(self, highway):
        # 随机生成车辆位置
        temp_x = random.random() * (highway.get_end_x_point() - highway.get_start_x_point())
        x_point = highway.get_start_x_point() + temp_x
        temp_y = random.random() * (highway.get_end_y_point() - highway.get_start_y_point())
        y_point = highway.get_start_y_point() + temp_y
        Vehicle.set_location(self, x_point, y_point)

    def work(self, dict_id2tx, dict_id2channel):
        target_tx = dict_id2tx[self.__txID]  # 目标发射机
        target_power = target_tx.get_power()  # dBm
        target_power = pow(10, (target_power - 30) / 10)  # W
        target_channel = dict_id2channel[self.get_id()]
        target_link_loss = target_channel.get_link_loss(self.__txID)  # dB
        target_gain = pow(10, -target_link_loss / 10)
        for tx_id in dict_id2tx:
            if tx_id != self.__txID:
                inter_tx = dict_id2tx[tx_id]  # 干扰发射机
                inter_power = inter_tx.get_power()  # dBm
                inter_power = pow(10, (inter_power - 30) / 10)  # W
                inter_channel = dict_id2channel[self.get_id()]
                inter_link_loss = inter_channel.get_link_loss(tx_id)  # dB
                inter_gain = pow(10, -inter_link_loss / 10)
                weight = (inter_power * inter_gain) / (target_power * target_gain)
                self.__inter_txID2weight[tx_id] = weight

    def get_tx_id(self):
        return self.__txID

    def get_weight(self, tx_id):
        return self.__inter_txID2weight[tx_id]


class V2VTxVehicle(Vehicle):
    def __init__(self, i_id):
        # 调用父类的构造函数
        Vehicle.__init__(self, i_id)
        self.__rxID = -1
        self.__power = 30  # 车辆发射功率 dBm

    def update_location(self, highway):
        # 随机生成车辆位置
        temp_x = random.random() * (highway.get_end_x_point() - highway.get_start_x_point())
        x_point = highway.get_start_x_point() + temp_x
        temp_y = random.random() * (highway.get_end_y_point() - highway.get_start_y_point())
        y_point = highway.get_start_y_point() + temp_y
        Vehicle.set_location(self, x_point, y_point)

    def set_rx_id(self, rx_id):
        self.__rxID = rx_id

    def get_power(self):
        return self.__power


class V2VRxVehicle(Vehicle):
    def __init__(self, i_id):
        # 调用父类的构造函数
        Vehicle.__init__(self, i_id)
        self.__txID = -1
        self.__inter_txID2weight = {}  # 存储干扰权值的字典 键——干扰发射机ID 值——干扰权值

    def update_location(self, highway, v2v_tx_vehicle):
        temp_x = (random.random() - 0.5) * 500  # 设 V2V 之间最大间距500m
        temp_y = (random.random() - 0.5) * 500
        if highway.get_end_x_point() - highway.get_start_x_point():
            x_point = v2v_tx_vehicle.get_x_point() + temp_x
            y_point = v2v_tx_vehicle.get_y_point()
        else:
            x_point = v2v_tx_vehicle.get_x_point()
            y_point = v2v_tx_vehicle.get_y_point() + temp_y
        Vehicle.set_location(self, x_point, y_point)

        self.__txID = v2v_tx_vehicle.get_id()
        v2v_tx_vehicle.set_rx_id(self.get_id())

    def work(self, dict_id2tx, dict_id2channel):
        target_tx = dict_id2tx[self.__txID]  # 目标发射机
        target_power = target_tx.get_power()  # dBm
        target_power = pow(10, (target_power - 30) / 10)  # W
        target_channel = dict_id2channel[self.get_id()]
        target_link_loss = target_channel.get_link_loss(self.__txID)  # dB
        target_gain = pow(10, -target_link_loss / 10)
        for tx_id in dict_id2tx:
            if tx_id != self.__txID:
                inter_tx = dict_id2tx[tx_id]  # 干扰发射机
                inter_power = inter_tx.get_power()  # dBm
                inter_power = pow(10, (inter_power - 30) / 10)  # W
                inter_channel = dict_id2channel[self.get_id()]
                inter_link_loss = inter_channel.get_link_loss(tx_id)  # dB
                inter_gain = pow(10, -inter_link_loss / 10)
                weight = (inter_power * inter_gain) / (target_power * target_gain)
                self.__inter_txID2weight[tx_id] = weight

    def get_tx_id(self):
        return self.__txID

    def get_weight(self, tx_id):
        return self.__inter_txID2weight[tx_id]


class RSU(Interface):
    def __init__(self, i_id):
        # 调用父类的构造函数
        Interface.__init__(self, i_id)
        self.__power = 40  # 发射功率 dBm
        self.__x_point = 0
        self.__y_point = 0
        self.__direction = 0  # 路边单元静止 没有行进方向

    def get_x_point(self):
        return self.__x_point

    def get_y_point(self):
        return self.__y_point

    def get_direction(self):
        return self.__direction

    def get_power(self):
        return self.__power


class Channel(object):
    def __init__(self, rx_id):
        self.__rx_id = rx_id
        self.__link_loss = {}  # 存储链路损耗的字典 键——发射机id值 值——链路损耗
        self.__id2direction = {}  # 存储行进方向的字典 键——发射机id值 值——方向
        self.__id2distance = {}  # 存储距离的字典 键——发射机id值 值——距离

    def update_link_loss(self, tx_device, rx_device):
        distance = get_distance(tx_device.get_x_point(), tx_device.get_y_point(),
                                rx_device.get_x_point(), rx_device.get_y_point())
        self.__id2distance[tx_device.get_id()] = distance
        if tx_device.get_direction() == 0:  # 发射机是路边单元
            if rx_device.get_direction() * rx_device.get_x_point() > 0:
                direction = 1  # 车辆行驶方向与车辆坐标同号，车辆相对于路边单元反向行驶
                self.__id2direction[tx_device.get_id()] = "reverse"
            else:
                direction = -1
                self.__id2direction[tx_device.get_id()] = "forward"
        else:  # 发射机是车辆
            if tx_device.get_direction() * rx_device.get_direction() > 0:
                direction = 0  # 发射机和接收机同向行驶
                self.__id2direction[tx_device.get_id()] = "convoy"
            elif (rx_device.get_x_point() - tx_device.get_x_point()) * rx_device.get_direction() > 0:
                direction = 1
                self.__id2direction[tx_device.get_id()] = "reverse"
            else:
                direction = -1
                self.__id2direction[tx_device.get_id()] = "forward"

        link_loss = 63.3 + 10 * math.log10(distance / 10) + random.uniform(0, 3.1) + direction * 3.3
        self.__link_loss[tx_device.get_id()] = link_loss

    def get_rx_id(self):
        return self.__rx_id

    def get_link_loss(self, tx_id):
        return self.__link_loss[tx_id]

    def get_direction(self, tx_id):
        return self.__id2direction[tx_id]

    def get_distance(self, tx_id):
        return self.__id2distance[tx_id]


def get_distance(x1, y1, x2, y2):
    return pow(pow((x1 - x2), 2) + pow((y1 - y2), 2), 0.5)
