#!/usr/bin/python
# -*- coding:utf8 -*-

from device import *
import csv


def random_allocation(dict_id2tx, dict_id2rx, rb_num):
    for rx_id in dict_id2rx:
        rb_id = int(rb_num * random.random())
        dict_id2rx[rx_id].set_allocated_rb(rb_id)
        tx_id = dict_id2rx[rx_id].get_tx_id()
        dict_id2tx[tx_id].set_allocated_rb(rb_id)
        print "节点：", rx_id, " 颜色：", rb_id


def graph_allocation(dict_id2tx, dict_id2rx, rb_num):
    dict_rx_id2node = {}
    list_nodes = []

    # 节点构建
    for rx_id in dict_id2rx:
        tx_id = dict_id2rx[rx_id].get_tx_id()
        temp_node = Node(dict_id2tx[tx_id], dict_id2rx[rx_id])
        temp_node.set_candidate_color(rb_num)
        dict_rx_id2node[rx_id] = temp_node
        list_nodes.append(temp_node)

    # 边构建
    for rx_id1 in dict_rx_id2node:
        for rx_id2 in dict_rx_id2node:
            if rx_id1 < rx_id2:
                node1 = dict_rx_id2node[rx_id1]
                node2 = dict_rx_id2node[rx_id2]
                inter_radius1 = node1.inter_radius
                inter_radius2 = node2.inter_radius
                d_tx12rx2 = get_distance(node1.tx_x_point, node1.tx_y_point, node2.rx_x_point, node2.rx_y_point)
                d_rx12tx2 = get_distance(node1.rx_x_point, node1.rx_y_point, node2.tx_x_point, node2.tx_y_point)
                if node1.tx_id == 0 and node2.tx_id == 0:
                    temp_weight = 1000  # 无穷干扰 两个车辆都是蜂窝用户
                elif d_tx12rx2 > inter_radius1 and d_rx12tx2 > inter_radius2:
                    temp_weight = 0  # 无干扰
                elif d_tx12rx2 < inter_radius1 and d_rx12tx2 < inter_radius2:
                    temp_weight = 100  # 强干扰
                else:
                    temp_weight = 10  # 中等干扰
                node1.dict_rx_id2weight[rx_id2] = temp_weight
                node2.dict_rx_id2weight[rx_id1] = temp_weight

    # 着色
    for color in range(rb_num):  # 选择一种颜色
        color_list_nodes = []
        while len(color_list_nodes) < 3:  # 最多允许3个节点共享一个RB
            interested_list_nodes = []
            for node in list_nodes:
                if node.interested_color == color:
                    interested_list_nodes.append(node)
                    node.compute_inter_value(dict_rx_id2node, color)  # 计算节点的干扰度
            interested_list_nodes = sorted(interested_list_nodes, key=lambda e: e.inter_value, reverse=False)  # 按照干扰度排序
            if len(interested_list_nodes) > 0:
                color_node = interested_list_nodes[0]
            else:
                break
            color_node.set_color(color)
            color_list_nodes.append(color_node)
            dict_id2rx[color_node.rx_id].set_allocated_rb(color)
            dict_id2tx[color_node.tx_id].set_allocated_rb(color)
            print "节点：", color_node.rx_id, " 颜色：", color_node.color
            color_node.delete_candidate_color()
            # 如果是着色节点是蜂窝用户，其他蜂窝用户都不能再着此颜色
            if color_node.tx_id == 0:
                for node in list_nodes:
                    if node.tx_id == 0:
                        node.update_candidate_color(color)
        # 将color从所有节点的候选颜色集中删除
        for node in list_nodes:
            node.update_candidate_color(color)


class Node(object):
    def __init__(self, tx, rx):
        self.tx_id = tx.get_id()
        self.rx_id = rx.get_id()
        self.tx_x_point = tx.get_x_point()
        self.tx_y_point = tx.get_y_point()
        self.rx_x_point = rx.get_x_point()
        self.rx_y_point = rx.get_y_point()
        self.dict_rx_id2weight = {}
        self.inter_value = 0
        if tx.get_id() == 0:
            self.inter_radius = 100
        else:
            self.inter_radius = 10
        self.color = -1
        self.candidate_color = []  # 候选颜色集
        self.interested_color = -1  # 当前候选颜色

    def compute_inter_value(self, dict_rx_id2node, color):
        self.inter_value = 0
        for rx_id in self.dict_rx_id2weight:
            if dict_rx_id2node[rx_id].color == color:
                self.inter_value += self.dict_rx_id2weight[rx_id]

    def set_color(self, color):
        self.color = color

    def set_candidate_color(self, rb_num):
        self.candidate_color = [n for n in range(rb_num)]
        self.interested_color = self.candidate_color[0]

    def update_candidate_color(self, color):
        if color in self.candidate_color:
            self.candidate_color.remove(color)
        if len(self.candidate_color) > 0:
            self.interested_color = self.candidate_color[0]

    def delete_candidate_color(self):
        self.candidate_color = []
        self.interested_color = -1


def net_allocation(dict_id2tx, dict_id2rx, rb_num):
    # 建立空字典
    rx_id2tx_id2class = {}

    for rx_id in dict_id2rx:
        tx_id2class = {}

        # 读取csv至字典
        csv_file = open("class.csv", "r")
        reader = csv.reader(csv_file)
        for item in reader:
            if rx_id == int(item[2]):
                tx_id2class[int(item[1])] = int(item[3])
        csv_file.close()

        rx_id2tx_id2class[rx_id] = tx_id2class

    dict_rx_id2node = {}
    list_nodes = []

    # 节点构建
    for rx_id in dict_id2rx:
        tx_id = dict_id2rx[rx_id].get_tx_id()
        temp_node = Node(dict_id2tx[tx_id], dict_id2rx[rx_id])
        temp_node.set_candidate_color(rb_num)
        dict_rx_id2node[rx_id] = temp_node
        list_nodes.append(temp_node)

    # 边构建
    for rx_id1 in dict_rx_id2node:
        for rx_id2 in dict_rx_id2node:
            if rx_id1 < rx_id2:
                node1 = dict_rx_id2node[rx_id1]
                node2 = dict_rx_id2node[rx_id2]

                if node1.tx_id == 0 and node2.tx_id == 0:
                    temp_weight = 1000  # 无穷干扰 两个车辆都是蜂窝用户
                elif rx_id2tx_id2class[rx_id1][node2.tx_id] == 1 \
                        and rx_id2tx_id2class[rx_id2][node1.tx_id] == 1:
                    temp_weight = 0  # 无干扰
                elif rx_id2tx_id2class[rx_id1][node2.tx_id] == 3 \
                        and rx_id2tx_id2class[rx_id2][node1.tx_id] == 3:
                    temp_weight = 100  # 强干扰
                else:
                    temp_weight = 10  # 中等干扰
                node1.dict_rx_id2weight[rx_id2] = temp_weight
                node2.dict_rx_id2weight[rx_id1] = temp_weight

    # 着色
    for color in range(rb_num):  # 选择一种颜色
        color_list_nodes = []
        while len(color_list_nodes) < 3:  # 最多允许3个节点共享一个RB
            interested_list_nodes = []
            for node in list_nodes:
                if node.interested_color == color:
                    interested_list_nodes.append(node)
                    node.compute_inter_value(dict_rx_id2node, color)  # 计算节点的干扰度
            interested_list_nodes = sorted(interested_list_nodes, key=lambda e: e.inter_value, reverse=False)  # 按照干扰度排序
            if len(interested_list_nodes) > 0:
                color_node = interested_list_nodes[0]
            else:
                break
            color_node.set_color(color)
            color_list_nodes.append(color_node)
            dict_id2rx[color_node.rx_id].set_allocated_rb(color)
            dict_id2tx[color_node.tx_id].set_allocated_rb(color)
            print "节点：", color_node.rx_id, " 颜色：", color_node.color
            color_node.delete_candidate_color()
            # 如果是着色节点是蜂窝用户，其他蜂窝用户都不能再着此颜色
            if color_node.tx_id == 0:
                for node in list_nodes:
                    if node.tx_id == 0:
                        node.update_candidate_color(color)
        # 将color从所有节点的候选颜色集中删除
        for node in list_nodes:
            node.update_candidate_color(color)


