# 铅笔画下的虚拟形象
在看到B站一些UP主，都是用虚拟AI合成的形象与观众互动，所以我也想用飞桨来自制一个属于自己的虚拟形象，也让大家可以在微信中，生成自己的虚拟形象。

此项目分为两个版本，AI Studio测试版本和Wechaty版本。此项目采用人脸检测模型([face_landmark_localization](https://www.paddlepaddle.org.cn/hubdetail?name=face_landmark_localization))来实现。Github项目地址([https://github.com/zengzhuoqi/paddle-virtual-figures-in-penclings](https://github.com/zengzhuoqi/paddle-virtual-figures-in-penclings))

先看成品（因为GIF大于1M，没法上传，所以只截取一帧的画面进行展示）

自拍视频太丑了，笑脸比我帅:)

![](https://ai-studio-static-online.cdn.bcebos.com/4a5d66d3bd0a46e38df621c689f10883463a11c5b1844e059fa0f924e0b47e1d)


## 实现方式
首先将原视频拆分成一帧帧画面，然后再进行处理。
头部旋转：为了让头部可以模仿原视频进行旋转，我采用了人脸检测模型，通过求鼻子的两个特征点的向量与竖直方向向量的角度，从而实现旋转头部。遗憾的是，因为人脸检测模型精度不高，通过EAR公式，无法准确地判断眼睛是否闭眼，所以没有对眼睛进行处理。

合成：通过super松的[铅笔素描画](https://aistudio.baidu.com/aistudio/projectdetail/1468432)的代码，形成背景。然后除去脖子和头部图片的白色背景，合并多图层，形成一帧画面，最后将每一帧画面按照原视频的帧率进行合成，并加上原视频的声音，就形成了视频版的虚拟形象，也可以通过moviepy进行转GIF图片（因为GIF图片太大，无法在微信保存为表情，所以在wechaty版本上只采用视频的形式）

## 请大家给一颗星星:heart_eyes::heart_eyes:
