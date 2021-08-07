# 铅笔画下的虚拟形象
在看到B站一些UP主，都是用虚拟AI合成的形象与观众互动，所以我也想用飞桨来自制一个属于自己的虚拟形象，也让大家可以在微信中，生成自己的虚拟形象。

此项目分为两个版本，AI Studio测试版本和Wechaty版本。此项目采用人脸检测模型([face_landmark_localization](https://www.paddlepaddle.org.cn/hubdetail?name=face_landmark_localization))来实现。AIStudio项目地址([https://aistudio.baidu.com/aistudio/projectdetail/2205727](https://aistudio.baidu.com/aistudio/projectdetail/2205727))

先看成品（因为GIF大于1M，没法上传，所以只截取一帧的画面进行展示）

自拍视频太丑了，笑脸比我帅:)

![](https://ai-studio-static-online.cdn.bcebos.com/4a5d66d3bd0a46e38df621c689f10883463a11c5b1844e059fa0f924e0b47e1d)


## 实现方式
首先将原视频拆分成一帧帧画面，然后再进行处理。
头部旋转：为了让头部可以模仿原视频进行旋转，我采用了人脸检测模型，通过求鼻子的两个特征点的向量与竖直方向向量的角度，从而实现旋转头部。遗憾的是，因为人脸检测模型精度不高，通过EAR公式，无法准确地判断眼睛是否闭眼，所以没有对眼睛进行处理。

合成：通过super松的[铅笔素描画](https://aistudio.baidu.com/aistudio/projectdetail/1468432)的代码，形成背景。然后除去脖子和头部图片的白色背景，合并多图层，形成一帧画面，最后将每一帧画面按照原视频的帧率进行合成，并加上原视频的声音，就形成了视频版的虚拟形象，也可以通过moviepy进行转GIF图片（因为GIF图片太大，无法在微信保存为表情，所以在wechaty版本上只采用视频的形式）

## Wechaty配置方式
我是使用Linux+Windows进行部署。

Linux上的代码
```Python
export WECHATY_LOG="verbose"
export WECHATY_PUPPET="wechaty-puppet-wechat"
export WECHATY_PUPPET_SERVER_PORT="8080" #按自己需要选择端口
export WECHATY_TOKEN=puppet_padlocal_******** #输入自己的Token
docker run -ti \
--name wechaty_puppet_service_token_gateway \
--rm \
-e WECHATY_LOG \
-e WECHATY_PUPPET \
-e WECHATY_PUPPET_SERVER_PORT \
-e WECHATY_TOKEN \
-p "$WECHATY_PUPPET_SERVER_PORT:$WECHATY_PUPPET_SERVER_PORT" \
wechaty/wechaty:latest
```
如果是在服务器上使用，记得开放**上行和下行端口**，不然无法进行连接。


然后下面的代码，在任意环境部署都可以。
### Windows

```Python
os.environ['WECHATY_PUPPET'] = 'wechaty-puppet-service'
os.environ['WECHATY_PUPPET_SERVICE_TOKEN'] = 'puppet_padlocal_********'
```

在```wechatyrun.py```中更改
### Linux
```
export WECHATY_PUPPET=wechaty-puppet-service
export WECHATY_PUPPET_SERVICE_TOKEN=puppet_padlocal_********
python wechatyrun.py
```

而且在```wechatyrun.py```中删除

```Python
os.environ['WECHATY_PUPPET'] = 'wechaty-puppet-service'
os.environ['WECHATY_PUPPET_SERVICE_TOKEN'] = 'puppet_padlocal_********'
```
### 提示（防踩坑）
因为python-wechaty可能有bug

#### 1、出现```The network is not good, the bot will try to restart after 60 seconds. ```报错

则安装不同版本的**wechaty-puppet-service**
```
pip install wechaty-puppet-service==0.8.1 #or
pip install wechaty-puppet-service==0.8.4 #选其中一个安装即可
```
#### 2、视频无法发送的bug

在wechatyrun.py中
```Python
        file_box_3 = FileBox.from_file('C:/Users/G/Desktop/wechaty/pencil_picture/output/video_output.mp4') #第267行
        await msg.say(file_box_3)
        file_box_3 = FileBox.from_file('C:/Users/G/Desktop/wechaty/pencil_picture/output/video_output.mp4')
        await msg.say(file_box_3)
```
一开始尝试直接发送视频时，是无法发送成功的。导致需要再次回复“收货”进行发送视频才能发送成功，我不知道是什么原因导致的。
```Python
    if msg.text() == '收货':
        file_box_3 = FileBox.from_file('C:/Users/G/Desktop/wechaty/pencil_picture/output/video_output.mp4') #第229行
        await msg.say(file_box_3)
        os.system(r"del /q C:/Users/G/Desktop/wechaty/pencil_picture/output/*")
```
而且是将视频的比特率降下来，才能用这样的方法发送成功。
```Python
    os.system("C:/dev/app/ffmpeg/bin/ffmpeg -i C:/Users/G/Desktop/wechaty/pencil_picture/output/video_output2.mp4 -b 1M C:/Users/G/Desktop/wechaty/pencil_picture/output/video_output.mp4") #第226行
```
#### 3、注意引号
```
export WECHATY_PUPPET_SERVICE_TOKEN=puppet_padlocal_********
```
在输入Token码的时候是**没有引号的**，但是其他参数是**有引号的**
## 请大家给一颗星星:heart_eyes::heart_eyes:
