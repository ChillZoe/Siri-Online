import websocket
import requests
import hashlib
import base64
import hmac
import json
import os, sys
import re
from urllib.parse import urlencode
import logging
import time
from time import mktime
import ssl
import wave
from wsgiref.handlers import format_date_time
from datetime import datetime
from pyaudio import PyAudio,paInt16
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from get_audio import recording # 导入录音.py文件


input_filename = "input.wav"               # 麦克风采集的语音输入
input_filepath = ".\\audios"              # 输入文件的path
in_path = input_filepath + input_filename

type = sys.getfilesystemencoding()

path_pwd = os.path.split(os.path.realpath(__file__))[0]
os.chdir(path_pwd)

try:
    import thread
except ImportError:
    import _thread as thread

logging.basicConfig()

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识


global wsParam  # websocket参数
global sentence # 听写得到的句子
class Ws_Param(object):
    # 初始化
    def __init__(self, host):
        self.Host = host
        self.HttpProto = "HTTP/1.1"
        self.HttpMethod = "GET"
        self.RequestUri = "/v2/iat"
        self.APPID = "2d9076fa" # 在控制台-我的应用-语音听写（流式版）获取APPID
        self.Algorithm = "hmac-sha256"
        self.url = "wss://" + self.Host + self.RequestUri

        # 采集音频 录音
        recording(".\\audios\\input.wav")

        # 设置测试音频文件，流式听写一次最多支持60s，超过60s会引起超时等错误。
        self.AudioFile = r".\\audios\\input.wav"

        self.CommonArgs = {"app_id": self.APPID}
        self.BusinessArgs = {"domain":"iat", "language": "zh_cn","accent":"mandarin"}

    def create_url(self):
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        APIKey = 'd0812d26b756b0788f37ea285e01695d' # 在控制台-我的应用-语音听写（流式版）获取APIKey
        APISecret = 'NDkwMTcyZjQyOGYxNjVlMmQ1ZjY3ZDNm' # 在控制台-我的应用-语音听写（流式版）获取APISecret

        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
        signature_sha = hmac.new(APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        url = url + '?' + urlencode(v)
        return url

# 收到websocket消息的处理 这里我对json解析进行了一些更改 打印简短的一些信息
def on_message(ws, message):
    global sentence
    msg = json.loads(message) # 将json对象转换为python对象 json格式转换为字典格式
    try:
        code = msg["code"]
        sid = msg["sid"]

        if code != 0:
            errMsg = msg["message"]
            print("sid:%s call error:%s code is:%s\n" % (sid, errMsg, code))
        else:
            result = msg["data"]["result"]["ws"]
            # 以json格式显示 
            data_result = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': ')) 
            print("sid:%s call success!" % (sid))
            # print("result is:%s\n" % (data_result))
            for item in result:
                if item["cw"][0]["w"] != "。":
                    sentence+=item["cw"][0]["w"]
    except Exception as e:
        print("receive msg,but parse exception:", e)

# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)

# 收到websocket关闭的处理
def on_close(ws):
    print("### closed ###")

# 收到websocket连接建立的处理
def on_open(ws):
    def run(*args):
        frameSize = 1280  # 每一帧的音频大小
        intervel = 0.04  # 发送音频间隔(单位:s)
        status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧
        with open(wsParam.AudioFile, "rb") as fp:
            while True:
                buf = fp.read(frameSize)

                # 文件结束
                if not buf:
                    status = STATUS_LAST_FRAME
                # 第一帧处理
                # 发送第一帧音频，带business 参数
                # appid 必须带上，只需第一帧发送
                if status == STATUS_FIRST_FRAME:

                    d = {"common": wsParam.CommonArgs,
                         "business": wsParam.BusinessArgs,
                         "data": {"status": 0, "format": "audio/L16;rate=16000",
                                   "audio": str(base64.b64encode(buf),'utf-8'),
                                  "encoding": "raw"}}
                    d = json.dumps(d)
                    ws.send(d)
                    status = STATUS_CONTINUE_FRAME
                # 中间帧处理
                elif status == STATUS_CONTINUE_FRAME:
                    d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                                   "audio": str(base64.b64encode(buf),'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                # 最后一帧处理
                elif status == STATUS_LAST_FRAME:
                    d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf),'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                    time.sleep(1)
                    break
                # 模拟音频采样间隔
                time.sleep(intervel)
        ws.close()

    thread.start_new_thread(run, ())

def get_instruction(): # 简化的听写函数，供外部调用
    global sentence
    global wsParam
    sentence=""
    wsParam = Ws_Param("ws-api.xfyun.cn") #流式听写 域名
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    return sentence # 返回语