# encoding:utf-8
import base64
import requests
import urllib.request
import urllib.parse
import json
import sys
import os
import cv2
import threading
import win32gui
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from keda_tingxie.sub_instruction import *
from tts_ws_python3_demo.speak_word import *
'''
通用物体和场景识别
'''


# 需要的库requests、json（import 进来就好了）
baidu_server = 'https://aip.baidubce.com/oauth/2.0/token?'  #获取token的server
grant_type = 'client_credentials'
client_id = 'GVLBWfijYyDRsqLPlooDcRol' #API KEY
client_secret = 'kEQagxQjrgptu3OlRxNzWQnkfunS8Gdi' #Secret KEY   这里可以自己去百度注册，这里是我的API KEY 和 Secret KEY

#合成请求token的url
url = baidu_server+'grant_type='+grant_type+'&client_id='+client_id+'&client_secret='+client_secret
res = requests.get(url).text
data = json.loads(res)  #将json格式转换为字典格式
# print(data)
access_token = data['access_token']

def get_img_message(frame): # 将收到的图片转换为二进制文件并发送给百度服务器，并返回检测结果
    frame=np.array(cv2.imencode('.png', frame)[1]).tobytes()
    img = base64.b64encode(frame)
    params = {"image":img,}
    params = urllib.parse.urlencode(params)
    header={'Content-Type':'application/x-www-form-urlencoded'}
    request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general"
    request_url = request_url + "?access_token=" + access_token
    request = requests.post(url=request_url, data=params, headers=header)
    content = request.text
    content = json.loads(content)
    # print(content[0])
    if "result" in content:
        if len(content["result"])>=3:
            i_wanna_speak("图中的物体最有可能是%s，还有可能是%s，也有可能是%s"%(content["result"][0]["keyword"],content["result"][1]["keyword"],content["result"][2]["keyword"]))
        elif len(content["result"])==2:
            i_wanna_speak("图中的物体最有可能是%s，还有可能是%s"%(content["result"][0]["keyword"],content["result"][1]["keyword"]))
        elif len(content["result"])==1:
            i_wanna_speak("图中的物体有应该是%s"%(content["result"][0]["keyword"]))
    else:
        i_wanna_speak("不好意思，我没看出来是什么，再拍一张照片吧")


global signal
signal=0
def round_instruction(): # 轮询函数接收语音指令，收到“关闭”时关掉检测程序
    global signal
    signal=0
    instruction=""
    while 1:
        instruction=get_instruction()
        if ("好" in instruction)or ("拍" in instruction):
            signal=2
        if "关闭" in instruction:
            signal=1
            break

def img_detect(): # 进行图像检测
    global signal
    cap = cv2.VideoCapture(1)
    t1 = threading.Thread(target=round_instruction)
    t1.start()
    while cv2.waitKey(1) < 0:
        ret, frame = cap.read()
        frame=cv2.resize(frame,(2000,1000))
        cv2.resizeWindow("Detect Image", 2000, 1000)
        cv2.imshow("Detect Image", frame)
        win32gui.FindWindow(None,"Detect Image")
        if signal == 2:
            get_img_message(frame)
            signal=0
        if signal == 1:
            cv2.destroyAllWindows()
            cv2.waitKey(1)
            cv2.waitKey(1)
            cv2.waitKey(1)
            cv2.waitKey(1)
            break
    return 