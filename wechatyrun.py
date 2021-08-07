import os
import asyncio
import paddlehub as hub
import cv2
import time
from PIL import Image
import math
from scipy.spatial import distance as dist
import numpy as np
import moviepy.editor as mpy
import time

from wechaty import (
    Contact,
    FileBox,
    Message,
    Wechaty,
    ScanStatus,
)

os.environ['WECHATY_PUPPET'] = 'wechaty-puppet-service'
os.environ['WECHATY_PUPPET_SERVICE_TOKEN'] = 'puppet_padlocal_9af8540f48cf470b926fc3d39863522a'

def transform_video_to_image(video_file_path, img_path,background):
    '''
        切割视频
    '''
    video_capture = cv2.VideoCapture(video_file_path)
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    count = 0
    while(True):
        ret, frame = video_capture.read() 
        if ret:
            if background==False:
                cv2.imwrite(img_path + '%d.jpg' % count, frame)
                #im = Image.open("/home/ubuntu/wechaty/pencil_picture/mp4_img/"+str(count)+".jpg")
                #im = im.rotate(90)
                #im.save("/home/ubuntu/wechaty/pencil_picture/mp4_img/"+str(count)+".jpg")
            else :
                cv2.imwrite(img_path + '%d.jpg' % count, frame)
                im = Image.open(img_path + '%d.jpg' % count)
                x_s = 500
                y_s = 500
                out = im.resize((x_s, y_s), Image.ANTIALIAS) 
                out.save(img_path + '%d.jpg' % count)
            count += 1
        else:
            break
    video_capture.release()
    return fps,count
def angle(v1,v2):
    '''
        计算夹角
    '''
    TheNorm = np.linalg.norm(v1)*np.linalg.norm(v2)
    rho = np.rad2deg(np.arcsin(np.cross(v1, v2)/TheNorm))
    theta = np.rad2deg(np.arccos(np.dot(v1,v2)/TheNorm))
    if rho < 0:
        return (-theta)
    else:
        return theta
def aspect_ratio(eye):
    '''
        计算纵横比
    '''
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
	# 计算距离，水平的
    C = dist.euclidean(eye[0], eye[3])
	# ear值
    ear = (A + B) / (2.0 * C)
    return ear
def mouth(count):
    '''
        画嘴巴
    '''
    ang_all=[]
    for i in range(count):
        img_path="C:/Users/G/Desktop/wechaty/pencil_picture/mp4_img/"+str(i)+".jpg"
        face_landmark = hub.Module(name="face_landmark_localization")
        if i==0:
            result = face_landmark.keypoint_detection(images=[cv2.imread(img_path)])[0]['data'][0]
        else:
            try:
                result = face_landmark.keypoint_detection(images=[cv2.imread(img_path)])[0]['data'][0]
            except:
                pass
        left_eye=aspect_ratio(result[36:42])
        right_eye=aspect_ratio(result[42:48])
        mouthlist=[result[60]]+[result[61]]+[result[63]]+[result[64]]+[result[65]]+[result[67]]
        mouth=aspect_ratio(mouthlist)
        img=cv2.imread('C:/Users/G/Desktop/wechaty/girl.jpg')
        mouth_img=round(mouth*3)+3
        if mouth_img>12 :mouth_img=12
        if mouth_img<3 :mouth_img=3
        cv2.ellipse(img,(495,460),(12,mouth_img),0,0,180,0,4)
        cv2.imwrite("C:/Users/G/Desktop/wechaty/pencil_picture/trans/"+str(i)+".jpg",img)
        ang1 = -angle([round(result[27][0])-round(result[32][0]), -(round(result[27][1])-round(result[32][1]))],[0,1])
        ang_all.append(round(ang1,3))
    return ang_all
def rotate(ang_all,count):
    '''
        防抖处理+旋转照片
    '''
    ang_all_b=[]
    for i in range(count):
        if i==0 :ang_all_b.append(round((ang_all[0]+ang_all[1]+ang_all[2])/3))
        if i==1 :ang_all_b.append(round((ang_all[0]+ang_all[1]+ang_all[2]+ang_all[3])/4))
        if (2<=i) and (i<=count-3): ang_all_b.append(round((ang_all[i-2]+ang_all[i-1]+ang_all[i]+ang_all[i+1]+ang_all[i+2])/5))
        if i==count-2:ang_all_b.append(round((ang_all[count-4]+ang_all[count-3]+ang_all[count-2]+ang_all[count-1])/4))
        if i==count-1:ang_all_b.append(round((ang_all[count-3]+ang_all[count-2]+ang_all[count-1])/3))
    for i in range(count):
        im = Image.open("C:/Users/G/Desktop/wechaty/pencil_picture/trans/"+str(i)+".jpg")
        im = im.rotate(ang_all_b[i])
        im.save("C:/Users/G/Desktop/wechaty/pencil_picture/trans/"+str(i)+".jpg")
        img=cv2.imread("C:/Users/G/Desktop/wechaty/pencil_picture/trans/"+str(i)+".jpg")
        cv2.imwrite("C:/Users/G/Desktop/wechaty/pencil_picture/trans/"+str(i)+".jpg", img[130:630, 250:750])
def combine_image_to_video(comb_path, output_file_path, fps, is_print=False):
    '''
        合并图像到视频
    '''
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    file_items = os.listdir(comb_path)
    file_len = len(file_items)
    if file_len > 0 :
        temp_img = cv2.imread(os.path.join(comb_path, file_items[0]))
        img_height, img_width = temp_img.shape[0], temp_img.shape[1]
        
        out = cv2.VideoWriter(output_file_path, fourcc, fps, (img_width, img_height))

        for i in range(file_len):
            pic_name = os.path.join(comb_path, str(i)+".jpg")
            if is_print:
                print(i+1,'/', file_len, ' ', pic_name)
            img = cv2.imread(pic_name)
            out.write(img)
        out.release()



def background2pencil(count):
    '''
        背景处理
    '''
    for i in range(count):
        file_path="C:/Users/G/Desktop/wechaty/pencil_picture/mp4_img_bg/"+str(i)+".jpg"
        L = np.asarray(Image.open(file_path).convert('L')).astype('float')     #取得图像灰度

        depth = 10.                                     # (0-100)
        grad = np.gradient(L)                           # 取图像灰度的梯度值
        grad_x, grad_y = grad                           # 分别取横纵图像梯度值
        grad_x = grad_x*depth/100.
        grad_y = grad_y*depth/100.
        A = np.sqrt(grad_x**2 + grad_y**2 + 1.)
        uni_x = grad_x/A
        uni_y = grad_y/A
        uni_z = 1./A

        el = np.pi/2.2                              # 光源的俯视角度，弧度值
        az = np.pi/4                               # 光源的方位角度，弧度值
        dx = np.cos(el)*np.cos(az)              # 光源对x轴的影响
        dy = np.cos(el)*np.sin(az)              # 光源对y轴的影响
        dz = np.sin(el)                             # 光源对z轴的影响

        gd = 255*(dx*uni_x + dy*uni_y + dz*uni_z)        # 光源归一化
        gd = gd.clip(0,255)                               #避免数据越界，将生成的灰度值裁剪至0-255之间

        im = Image.fromarray(gd.astype('uint8'))         # 重构图像
        im.save(file_path)         # 保存图像
        img=cv2.imread(file_path)
        cv2.imwrite(file_path,img)

def paste(count,neck):
    '''
        图片抠图+合并图层
    '''
    for i in range(count):
        img=cv2.imread("C:/Users/G/Desktop/wechaty/pencil_picture/trans/"+str(i)+".jpg")
        rows,cols,channels = img.shape

        #转换hsv
        hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        if neck==True :
            lower_blue=np.array([0,0,200])
            upper_blue=np.array([165,225,255])
        else :
            lower_blue=np.array([0,0,196])
            upper_blue=np.array([110,225,255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        #腐蚀膨胀
        erode=cv2.erode(mask,None,iterations=1)
        dilate=cv2.dilate(erode,None,iterations=1)
        mask=dilate

        # 加载图像
        if neck==False:
            img2 = cv2.imread("C:/Users/G/Desktop/wechaty/pencil_picture/trans/"+str(i)+".jpg")
            img1 = cv2.imread("C:/Users/G/Desktop/wechaty/pencil_picture/mp4_img_bg/"+str(i)+".jpg")
        if neck==True:
            img2 = cv2.imread("C:/Users/G/Desktop/wechaty/pencil_picture/trans/"+str(i)+".jpg")
            img1 = cv2.imread("C:/Users/G/Desktop/wechaty/neck.jpg")
        rows,cols,channels = img2.shape
        roi = img1[0:rows, 0:cols ] 

        mask_inv = cv2.bitwise_not(mask)
        img1_bg = cv2.bitwise_and(roi,roi,mask = mask) 
        img2_fg = cv2.bitwise_and(img2,img2,mask = mask_inv)
        dst = cv2.add(img1_bg,img2_fg)
        img1[0:rows, 0:cols ] = dst
        cv2.imwrite("C:/Users/G/Desktop/wechaty/pencil_picture/trans/"+str(i)+".jpg",img1)


def mainpencil(input_video,background_video):
    fps,count = transform_video_to_image(input_video, 'C:/Users/G/Desktop/wechaty/pencil_picture/mp4_img/',False)
    fps_bg,count_bg = transform_video_to_image(background_video, 'C:/Users/G/Desktop/wechaty/pencil_picture/mp4_img_bg/',True)
    background2pencil(count_bg)
    background2pencil(count_bg)
    ang_all=mouth(count)
    rotate(ang_all,count)
    paste(count,True)
    paste(count,False)
    combine_image_to_video('C:/Users/G/Desktop/wechaty/pencil_picture/trans/', 'C:/Users/G/Desktop/wechaty/pencil_picture/mp4_analysis.mp4' ,fps)
    os.system("C:/dev/app/ffmpeg/bin/ffmpeg -i "+input_video+" -vn C:/Users/G/Desktop/wechaty/pencil_picture/output/video.mp3")
    os.system("C:/dev/app/ffmpeg/bin/ffmpeg -i C:/Users/G/Desktop/wechaty/pencil_picture/mp4_analysis.mp4 -i C:/Users/G/Desktop/wechaty/pencil_picture/output/video.mp3 -c:v libx264 -crf 28 -strict -2 -ac 1 -c copy C:/Users/G/Desktop/wechaty/pencil_picture/output/video_output2.mp4")
    os.system("C:/dev/app/ffmpeg/bin/ffmpeg -i C:/Users/G/Desktop/wechaty/pencil_picture/output/video_output2.mp4 -b 1M C:/Users/G/Desktop/wechaty/pencil_picture/output/video_output.mp4")
async def on_message(msg: Message):
    if msg.text() == '收货':
        file_box_3 = FileBox.from_file('C:/Users/G/Desktop/wechaty/pencil_picture/output/video_output.mp4')
        await msg.say(file_box_3)
        os.system(r"del /q C:/Users/G/Desktop/wechaty/pencil_picture/output/*")
        #await msg.say('这是自动回复: dong dong dong')
    if msg.text() == 'hi' or msg.text() == '你好':
        await msg.say('这是自动回复: 机器人目前的功能是\n- 收到"ding", 自动回复"dong dong dong"\n- 收到"图片", 自动回复一张图片\n- 收到"视频"，自动生成铅笔画虚拟形象视频')
    if msg.text() == '图片':
        url = 'https://ai.bdstatic.com/file/403BC03612CC4AF1B05FB26A19D99BAF'
        # 构建一个FileBox
        file_box_1 = FileBox.from_url(url=url, name='xx.jpg')
        await msg.say(file_box_1)
    # 如果收到的message是一个视频
    if msg.type() == Message.Type.MESSAGE_TYPE_VIDEO:
        # 将Message转换为FileBox
        file_box_2 = await msg.to_file_box()
        video_name = file_box_2.name
        img_path = video_name
        await file_box_2.to_file(file_path=video_name)
        background_video = 'C:/Users/G/Desktop/wechaty/background.mp4'
        # 防止程序退出
        '''
        try:
            video_new_path=main(video_name,background_video)
        except:
            await msg.say('很抱歉，出错了。可以换一个视频试试哦:)')
        else:
            file_box_3 = FileBox.from_file(video_new_path)
            await msg.say(file_box_3)
        '''
        video_path='C:/Users/G/Desktop/wechaty/' + video_name
        mainpencil(video_path,background_video)
        #print(video_new_path)
        await msg.say("视频已制作完成，请回复“收货”来取视频吧！")
        os.system(r"del /q C:\Users\G\Desktop\wechaty\pencil_picture\trans\*")
        os.system(r"del /q C:\Users\G\Desktop\wechaty\pencil_picture\mp4_img\*")
        #os.system(r"del /q C:/Users/G/Desktop/wechaty/pencil_picture/output/*")
        os.system(r"del /q C:\Users\G\Desktop\wechaty\pencil_picture\mp4_analysis.mp4")
        os.system(r"del /q C:\Users\G\Desktop\wechaty\\"+video_name)
        file_box_3 = FileBox.from_file('C:/Users/G/Desktop/wechaty/pencil_picture/output/video_output.mp4')
        await msg.say(file_box_3)
        file_box_3 = FileBox.from_file('C:/Users/G/Desktop/wechaty/pencil_picture/output/video_output.mp4')
        await msg.say(file_box_3)
async def on_scan(
        qrcode: str,
        status: ScanStatus,
        _data,
):
    print('Status: ' + str(status))
    print('View QR Code Online: https://wechaty.js.org/qrcode/' + qrcode)


async def on_login(user: Contact):
    print(user)


async def main():
    # 确保我们在环境变量中设置了WECHATY_PUPPET_SERVICE_TOKEN
    if 'WECHATY_PUPPET_SERVICE_TOKEN' not in os.environ:
        print('''
            Error: WECHATY_PUPPET_SERVICE_TOKEN is not found in the environment variables
            You need a TOKEN to run the Python Wechaty. Please goto our README for details
            https://github.com/wechaty/python-wechaty-getting-started/#wechaty_puppet_service_token
        ''')

    bot = Wechaty()

    bot.on('scan', on_scan)
    bot.on('login', on_login)
    bot.on('message', on_message)

    await bot.start()

    print('[Python Wechaty] Ding Dong Bot started.')


asyncio.run(main())
