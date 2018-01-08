#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 18:11:51 2018

@author: kevin
"""

import argparse
import numpy as np
import pandas as pd
from PIL import Image
import time
import os
import string
import random


class J1J:
    def __init__(self, **kwargs):
        self.save_screenshot = kwargs['save_screenshot']
        if self.save_screenshot:
            self.screen_dir = "screen"
            self.screen_name = lambda: ''.join(random.sample(string.ascii_letters + string.digits, 15))
            if not os.path.isdir(self.screen_dir):
                os.mkdir(self.screen_dir)
        self.display_score = bool(kwargs['dest_score'])
        self.end_score = kwargs['dest_score']
        # 得分位置的x坐标
        self.score_position = [45, 125, 205, 285, 365]
        self.person_bottom_color = np.array([54, 60, 102])
        self.person_head_color = np.array([52, 53, 61])
        if self.display_score:
            from keras.models import load_model
            self.model = load_model('./Recognize_score.h5')

    def __call__(self):
        while True:
            self.pull_screenshot()
            self.read_img()
            if self.is_over():
                print('本局已结束，请手动开始游戏，然后再重新运行本脚本！')
                break
            if self.display_score:
                self.cur_score()
                if self.now_sc < self.end_score:
                    print('当前分数{}，还差{}分达到目标～'.format(self.now_sc, self.end_score - self.now_sc))
                    self.handle_pic()
                else:
                    print('达到预定分数，进入瞎JB跳模式^_^')
                    self.distance = random.randint(500, 1000)
            else:
                self.handle_pic()
            self.jump()

    def pull_screenshot(self):
        """
        截图后传回电脑
        """
        os.system('adb shell screencap -p /sdcard/ss.png')
        os.system('adb pull /sdcard/ss.png . >{}'.format(os.devnull))
        if self.save_screenshot:
            os.system("cp ss.png {}".format(os.path.join(self.screen_dir, '{}.png'.format(self.screen_name()))))

    def jump(self):
        """
        跳跃
        """
        # 随机产生触屏位置的x,y坐标
        x, y = random.randint(200, 650), random.randint(200, 630)
        press_time = int(self.distance * 1.365)
        cmd = f'adb shell input swipe {x} {y} {x} {y} {press_time}'
        os.system(cmd)
        # 随机等待1.8-3.4秒，防ban
        time.sleep(round(random.random() * 1.6 + 1.8, 3))

    def read_img(self):
        """
        读取图像，并转换为RGB模式
        """
        self.img = np.array(Image.open('ss.png').convert('RGB'))

    def is_over(self):
        """
        判断是否已结束游戏
        """
        return np.sqrt(np.square(self.img - np.array([50, 40, 30])).sum(axis=2)).mean().mean() < 90

    def cur_score(self):
        """
        加载模型，识别当前得分
        """
        single_score = []
        im_score = self.img[200:300, 70:450, :]
        for i, (x1, x2) in enumerate(zip(self.score_position[:-1], self.score_position[1:])):
            single_score.append(self.model.predict((im_score[:, x1:x2, :] / 255)[np.newaxis, :]).argmax())
        while single_score[-1] == 10:
            single_score.pop()
        self.now_sc = int(''.join([str(sc) if sc != 10 else str(0) for sc in single_score]))

    def handle_pic(self):
        """
        处理图片，找到棋子和目标点的坐标计算距离
        """
        img_partial1 = self.img[500:1500].astype(int)
        left_up_color = img_partial1[0, 0, :]

        person_bottom_diff = pd.DataFrame(np.sqrt(np.square(img_partial1 - self.person_bottom_color).sum(axis=2)))
        person_bottom_y = person_bottom_diff.where(person_bottom_diff < 10, np.nan).dropna(axis=0, how='all').index[-1]
        person_bottom_x = np.array(person_bottom_diff.where(person_bottom_diff < 10, np.nan).dropna(axis=1, how='all').columns).mean().astype(int)
        person_head_diff = pd.DataFrame(np.sqrt(np.square(img_partial1 - self.person_head_color).sum(axis=2)))
        person_head_y = person_head_diff.where(person_head_diff < 10, np.nan).dropna(axis=0, how='all').index[0]
        person_head_x = np.array(person_head_diff.where(person_head_diff < 10, np.nan).dropna(axis=1, how='all').columns).mean().astype(int)
        person_reset = img_partial1[person_head_y - 5:person_bottom_y, person_head_x - 33:person_bottom_x + 33, :]
        person_reset[:, :, :] = left_up_color
        img_partial2 = img_partial1[:person_bottom_y, :]

        dest_color = pd.DataFrame(np.sqrt(np.square(img_partial2 - left_up_color).sum(axis=2)))
        dest_color2 = dest_color.where(dest_color > 25, np.nan).dropna(axis=0, how='all')
        top_y = dest_color2.index[0]
        top_x = np.array(dest_color2.iloc[0].dropna().index).mean().astype(int)
        top_color = img_partial2[top_y, top_x]
        top_diff = pd.DataFrame(np.sqrt(np.square(img_partial2 - top_color).sum(axis=2)))
        top_diff2 = top_diff.where(top_diff < 5, np.nan)
        if top_x > person_bottom_x:
            # hor_x = top_diff2.dropna(axis=1,how='all').columns[-1]
            hor_y = top_diff2.dropna(axis=1, how='all').iloc[:, -1].dropna().index[0]
        else:
            # hor_x = top_diff2.dropna(axis=1,how='all').columns[0]
            hor_y = top_diff2.dropna(axis=1, how='all').iloc[:, 0].dropna().index[0]
        dest_point_x, dest_point_y = top_x, hor_y
        self.distance = np.sqrt(np.square(np.array([person_bottom_x, person_bottom_y]) - np.array([dest_point_x, dest_point_y])).sum())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Have a Fun!')
    parser.add_argument('--save_screenshot', '--save', action='store_true', help='Save ScreenShot')
    parser.add_argument('--dest_score', '--score', action='store', type=int, default=0, help='Set a destination score')
    args = parser.parse_args()
    args_dict = vars(args)
    J = J1J(**args_dict)
    J()
