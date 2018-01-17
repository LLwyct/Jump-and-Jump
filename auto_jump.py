#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
author: 787552171
date: 2018/01/17/15:57
tip: 目前只适用于1920*1080像素
'''

import re
import os
import json
import time
import random
from PIL import Image

# 从adb获取手机屏幕分辨率
def getScreenSize():
    screen_size = os.popen('adb shell wm size').read()
    if not screen_size:
        print('请安装adb及配置')
        exit()
    m = re.search(r'(\d+)x(\d+)', screen_size)
    if m:
        return '%sx%s' %(m.group(2), m.group(1))

# 初始化
def init():
    # 获取分辨率
    screen_size = getScreenSize()
    config_path = 'config/%s/config.json' %screen_size
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            print('loading config with %s size...' %screen_size)
            return json.loads(f.read())
    else:
        with open('config/defult.json', 'r') as f:
            print('loading default config...')
            return json.loads(f.read())

# 获取截图
def get_screenshot():
    os.system('adb shell screencap -p /sdcard/auto.png')
    os.system('adb pull /sdcard/auto.png .')

# 根据图片和配置文件找到棋子棋盘坐标
def find_piece_board(img, config):
    # 获取图片宽和高
    width, height = img.size
    # 扫描y的起始坐标
    scan_start_y = 0
    # 棋子的最大y坐标
    piece_y_max = 0
    # 加载图像
    img_pixel = img.load()
    # 扫描
    for i in range(height//3, height*2//3, 50):
        first_pixel = img_pixel[0,i]
        for j in range(0, width):
            pixel = img_pixel[j, i]
            if first_pixel[:-1] != pixel[:-1]:
                scan_start_y = i - 50
                break
        if scan_start_y !=0:
            break

    left = 0
    right = 0
    for i in range(scan_start_y, height*2//3):
        flag = True
        for j in range(width//8, width*7//8):
            pixel = img_pixel[j, i]
            if (50<pixel[0]<60) and(53<pixel[1]<63)and(95<pixel[2]<110):
                if flag:
                    left = j
                    flag = False
                right = j
                piece_y_max = max(piece_y_max, i)
    piece_x = (left + right)//2
    piece_y = piece_y_max - config['piece_base_height_1_2']
    # print('-',piece_x, piece_y)


    # =====================================================
    next_top_pos = []
    # print('--',scan_start_y,height*2//3)
    for i in range(scan_start_y, height*2//3):
        first_pixel = img_pixel[0, i]
        flag = False
        for j in range(width//8, width*7//8):
            pixel = img_pixel[j, i]
            if (pixel[0]-3<first_pixel[0]<pixel[0]+3) and (pixel[1]-3<first_pixel[1]<pixel[1]+3) and (pixel[2]-3<first_pixel[2]<pixel[2]+3):
                pass
            else:
                next_top_pos.append(i + 5)
                next_top_pos.append(j)
                flag = True
                break
        if flag:
            break

    next_top_piexl = img_pixel[next_top_pos[1], next_top_pos[0]]
    # print('---',next_top_pos[0], next_top_pos[1])
    # print(next_top_piexl)
    for i in range(piece_y_max + 100, next_top_pos[0], -1):
        pixel = img_pixel[next_top_pos[1], i]
        print('here',next_top_pos[1], i, pixel)
        if (pixel[0]-2<next_top_piexl[0]<pixel[0]+2) and (pixel[1]-2<next_top_piexl[1]<pixel[1]+2) and (pixel[2]-2<next_top_piexl[2]<pixel[2]+2):
            return piece_x, piece_y, next_top_pos[1], (next_top_pos[0] + i)//2


def jump(distance, press_ratio):
    print(distance)
    sx = random.randint(100, 300)
    sy = random.randint(200, 400)
    ex = random.randint(100, 500)
    ey = random.randint(300, 400)
    os.system('adb shell input swipe %s %s %s %s %s' %(sx,sy,ex,ey,int(distance*press_ratio)))


def run():

    '''检查配置和环境'''
    config = init()
    '''主循环'''
    while True:
        # 获取截图
        get_screenshot()
        # 生成图片对象
        img = Image.open('auto.png')
        # 获得坐标
        piece_x, piece_y, board_x, board_y = find_piece_board(img, config)
        # 计算距离
        distance = ((piece_x-board_x)**2 + (piece_y-board_y)**2)**0.5
        # 跳跃
        if distance < 180:
            '''当距离足够近时，可能会出现像素分析上的偏差，在这里需要手动操作'''
            time.sleep(10)
            continue
        jump(distance, config['press_ratio'])
        # 随机间隔
        time.sleep(random.randint(2,4))


if __name__ == '__main__':
    run()