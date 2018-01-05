#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 13:08:36 2018

@author: kevin
"""

import numpy as np
import random
import argparse

from keras.models import Sequential
from keras.layers import Dense, Flatten
from keras.layers import Conv2D, MaxPooling2D


class train_score:
    def __init__(self,**kwargs):
        self.save = kwargs['save_model']
        self.train_ratio = kwargs['ratio']
    
    def __call__(self):
        self.load_datas()
        self.split_train_test()
        self.train_model()
        self.test_model()
        if self.save:
            self.save_model()
            
    def load_datas(self):
        datas = np.load('wechat_jump_score_train_datas.npz')
        self.X,self.Y = [datas[n] for n in datas.files]
    
    def split_train_test(self):
        all_index = range(self.X.shape[0])
        train_num = random.sample(all_index,int(len(all_index) * self.train_ratio))
        test_num = list(set(all_index) - set(train_num))
        self.train_x = self.X[train_num,:,:,:]
        self.train_y = self.Y[train_num,:]
        self.test_x = self.X[test_num,:,:,:]
        self.test_y = self.Y[test_num,:]
        
    def train_model(self):
        model = Sequential()
        model.add(Conv2D(16, (5, 5), activation='relu', input_shape=(100, 80, 3)))
        model.add(MaxPooling2D(pool_size=(3, 3)))
        model.add(Conv2D(32, (5, 5), activation='relu'))
        model.add(MaxPooling2D(pool_size=(3, 3)))
        model.add(Flatten())
        model.add(Dense(128, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(11, activation='softmax'))
        model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])
        model.fit(self.train_x, self.train_y,epochs=5,batch_size=64)
        print("\n\n\t\tModel Summary")
        print(model.summary())
        self.model = model
                
    def save_model(self):
        self.model.save('Recognize_score.h5')
    
    def test_model(self):
        test_score = self.model.evaluate(self.test_x, self.test_y, batch_size=64)
        print("\n\tTest Datas:\nloss\t{:.4f}\nacc\t{:.2%}".format(*test_score))
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Toy CNN model.')
    parser.add_argument('--save_model','--save',action='store_true', help='Save model.')
    parser.add_argument('--ratio','--r', action='store',type=float, default=0.75,help='train test ratio,default is 0.75.')
    args = parser.parse_args()
    args_dict = vars(args)
    T = train_score(**args_dict)
    T()