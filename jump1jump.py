#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 29 12:53:53 2017

@author: kevin
"""
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image
import time
import os
import string
import random

class J1J:
    def __init__(self,**kwargs):
        self.save_screenshot = kwargs['save_screenshot']
        if self.save_screenshot:       
            self.screen_dir = "screen"
            self.screen_name = lambda: ''.join(random.sample(string.ascii_letters+string.digits,15))
            if not os.path.isdir(self.screen_dir):
                os.mkdir(self.screen_dir)
                        
        self.fig = plt.figure()        
        self.update = True 
        self.click_count = 0
        self.cor = []
        
    def __call__(self):
        self.pull_screenshot()
        self.img = np.array(Image.open('1.png'))
        self.im = plt.imshow(self.img, animated=True)
        self.fig.canvas.mpl_connect('button_press_event', self.onClick)
        ani = animation.FuncAnimation(self.fig, self.updatefig, interval=50, blit=True)
        plt.show()
            
    def pull_screenshot(self):
        os.system('adb shell screencap -p /sdcard/1.png')
        os.system('adb pull /sdcard/1.png . >{}'.format(os.devnull))
        if self.save_screenshot:
            os.system("cp 1.png {}".format(os.path.join(self.screen_dir,'{}.png'.format(self.screen_name()))))
    
    def jump(self,distance):
        x,y = random.randint(300,350),random.randint(400,430)
        press_time = int(distance * 1.36)
        cmd = f'adb shell input swipe {x} {y} {x} {y} {press_time}'
        print(cmd)
        os.system(cmd)
    
    def update_data(self):
        return np.array(Image.open('1.png'))
        
    def updatefig(self,*args):
        if self.update:
            time.sleep(round(random.random()*1.5 +2,2))
            self.pull_screenshot()
            self.im.set_array(self.update_data())
            self.update = False
        return self.im,
    
    def onClick(self,event):      
        ix, iy = event.xdata, event.ydata
        self.cor.append((ix, iy))    
        self.click_count += 1
        if self.click_count > 1:
            self.click_count = 0
            
            position = np.array([self.cor.pop(),self.cor.pop()])    
            distance = np.sqrt(np.power(position[0] - position[1],2).sum())
            print('distance = ', distance)
            self.jump(distance)
            self.update = True
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Save ScreenShot')
    parser.add_argument('--save_screenshot','--save',action='store_false', help='Save ScreenShot')
    args = parser.parse_args()
    args_dict = vars(args)
    J = J1J(**args_dict)
    J()

