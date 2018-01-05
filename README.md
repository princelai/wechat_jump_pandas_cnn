# 用Pandas和tensorflow玩跳一跳
后知后觉，也凑个热闹，自己写个跳一跳辅助工具

## 使用方法
**手动版**

python jump1jump.py [--save]

可选参数--save用来把每一次的截屏保存起来，用来收集数据，一般不需要

这个版本是借鉴的[wangshub][1]的初代版本，自己进行了结构上的改进，但是并没有修改功能，
详细使用方法点链接查看

**自动版**

python jump1jump_auto.py [--save] [--score SCORE]

--score用于添加一个目标分数，超过目标分数进行乱跳

如果使用--score参数，需要安装tensorflow和keras，程序会加载目录下的Recognize_score.h5模型文件


**训练分数识别模型**

python train_score_model.py [--save] [--r RATIO]

添加--save参数会在训练后保存模型为Recognize_score.h5，不添加不会保存模型

--r参数是训练集的比例，默认75%的训练集

数据集为我自己裁剪然后分类的分数截图，在目录内的wechat_jump_score_train_datas.npz文件，
一共1226个样本，分为11类

## 思路

棋子的位置是用颜色来找到的，所以**如果未来微信改变棋子的颜色，那么该版本自动跳就会失效**

查找目标位置是利用它的颜色与底色的差异来区分

Pandas主要起到的作用就是指定颜色或差异颜色，然后用pandas把图片矩阵转换为mask矩阵，
之后dropna，最后求出columns或index的值


[1]:https://github.com/wangshub/wechat_jump_game
