# -*- coding: utf-8 -*-
import threading
import time
import sys
import os
import webbrowser
import win32api
import win32con
import codecs
import time 
from socket import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from keda_tingxie.sub_instruction import * # 语音听写模块引入
from gene_voice.speak_word import *        # 语音合成模块引入
from UNIT.baidu_chat import *              # UNIT语音平台引入
from bilibili.bilibili_search import *     # B站视频模块引入
from QQ_chat.qq_program import *           # QQ聊天相关程序调用
from visual_scene.yolo_detect_obj import * # yolo实时检测引入
from visual_scene.image_detect import *    # 百度平台通用物体和场景识别引入



global windows，browser

browser = webdriver.Chrome(ChromeDriverManager().install())
browser.maximize_window()

##################################################################################################################################################################
#
#                                                                                 前端处理函数
# 
##################################################################################################################################################################
def put_on_screen(word, item): # 在html页面上上显示字符串
    browser.find_element_by_css_selector('input[name=%s]'%(item)).send_keys(Keys.CONTROL+'a')
    browser.find_element_by_css_selector('input[name=%s]'%(item)).send_keys(Keys.DELETE)
    browser.find_element_by_css_selector('input[name=%s]'%(item)).send_keys(word)

def get_user_instruction(): # 获取用户说的话，并在html页面上上显示
    instruction=get_instruction()
    put_on_screen(instruction,"_user")   
    return instruction 

def get_siri_answer(word): # 获取Siri说的话，并在html页面上上显示
    i_wanna_speak(word)
    put_on_screen(word,"_siri")

def round_wait(): # 轮询，直到收到非空指令
    instruction=""
    while instruction=="":
        instruction=get_user_instruction()
    return instruction

##################################################################################################################################################################
#
#                                                                                 B站爬虫处理函数
# 
##################################################################################################################################################################


def bilibili_init(): # 运行B站视频分支总函数
    get_siri_answer("已打开，请问您想看什么？")  
    content=get_user_instruction()
    bilibili_html_proc(content)
    get_siri_answer("您还要看其他的嘛？")  
    while 1:
        content=get_user_instruction()
        while content=="":
            get_siri_answer("不好意思，没听清") 
            content=get_user_instruction()
        if "不" in content:
            break
        else:
            get_siri_answer("好的，请问您接下来想看什么？")  
            content=get_user_instruction()
            bilibili_html_proc(content)   
            get_siri_answer("您还要看其他的嘛？")  

def bilibili_html_proc(content): # 生成html页面进行信息搜集
    while content=="":
        get_siri_answer("不好意思，没听清")
        content=get_user_instruction()
    spraw(content)
    get_siri_answer("正在为您搜索，请稍后")
    get_siri_answer("请问您想看最新，最多播放还是最多弹幕")
    catigory=get_user_instruction()
    while 1:
        if ("最新" in catigory) or("时间" in catigory) :
            gene_html("time")
            break
        elif ("播放" in catigory)or("多" in catigory):
            gene_html("view")
            break
        elif ("弹幕" in catigory) or ("评论" in catigory):
            gene_html("comment")
            break
        else:
            get_siri_answer("噢吼，没听清，请再说一遍")
            catigory=get_user_instruction()
    
    browser.execute_script('window.open()')
    windows = browser.window_handles
    browser.switch_to.window(windows[-1])
    browser.get(bili_show)
    while 1:
        i_wanna_speak("请问您想看哪个视频")
        video_name=get_instruction()  
        bilibili_start_proc(video_name)
        i_wanna_speak("还想看其他的吗？")
        continue_order=get_instruction()
        while continue_order=='':
            i_wanna_speak("不好意思，没听清")
            continue_order=get_instruction()
        if "不" in continue_order:
            break
    # round_wait()
    browser.close()
    browser.switch_to.window(windows[0])
    get_siri_answer("%s相关视频播放结束"%(content))

def bilibili_start_proc(video_name): #在html页面生成后进行视频选择
    global windows
    while video_name=='':
        i_wanna_speak("不好意思，没听清")
        video_name=get_instruction()
    bili_open_video(video_name)
    video_stop=get_instruction()  
    while '关闭' not in video_stop:
        video_stop=get_instruction()
    browser.close()
    windows = browser.window_handles
    browser.switch_to.window(windows[-1])

def bili_open_video(video_name): # 打开单个视频的具体操作
    global windows
    video_link=open_video(video_name)
    browser.execute_script('window.open()')
    windows = browser.window_handles
    browser.switch_to.window(windows[-1])
    browser.get(video_link)
    time.sleep(5)
    windll.user32.SetCursorPos(512,384)
    #按下鼠标再释放
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0,0,0)#press mouse
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0,0,0)#release mouse


##################################################################################################################################################################
#
#                                                                                 QQ聊天处理函数
# 
##################################################################################################################################################################

def QQ_chat_init(): # QQ聊天窗口初始化函数
    get_siri_answer("请稍等，正在为您打开QQ。")
    QQ(qq="请输入QQ账号", pwd="请输入QQ密码")
    get_siri_answer("请问您想和谁聊天？")
    friend_name=get_user_instruction()
    try:
        QQ_chat_proc(friend_name)
    except:
        get_siri_answer("窗口打开失败，正在重启")
        QQ_chat_proc(friend_name)
    while True:
        get_siri_answer("您还要继续聊天嘛？")
        instruction=get_user_instruction()
        if "不" in instruction:
            break
        else:
            get_siri_answer("请问您想和谁聊天？")
            friend_name=get_user_instruction()
            try:
                QQ_chat_proc(friend_name)
            except:
                get_siri_answer("窗口打开失败，正在重启")
                QQ_chat_proc(friend_name)

def QQ_chat_proc(friend_name): # QQ聊天具体进程管控函数
    while friend_name=="":
        friend_name=get_user_instruction()
        get_siri_answer("不好意思，没听清")
    class_name,window_title=open_window(friend_name)
    print(class_name,window_title)
    get_siri_answer("小主您要皮一把嘛？")
    answer=get_user_instruction()
    while answer=="":
        get_siri_answer("不好意思，没听清，请说“是，好，对或其他”")
        answer=get_user_instruction()
    if ("是" in answer) or ("好" in answer)or ("对" in answer):
        get_siri_answer("哈哈哈，可真有您的。")
        get_siri_answer("请输入您想说的话")
        chat_log=""
        while "不聊了" not in chat_log:
            chat_log=get_user_instruction()
            if "不聊了" in chat_log:
                time.sleep(3)
                break
            if chat_log!="":
                send_message(class_name,window_title,chat_log,100)
                get_siri_answer("发送了%s100遍"%(chat_log))
            else:
                get_siri_answer("不好意思，没听清")
        close_chat(class_name,window_title)
    else:
        get_siri_answer("好的，请输入您想说的话")
        chat_log=""
        while "不聊了" not in chat_log:
            chat_log=get_user_instruction()
            if "不聊了" in chat_log:
                
                break
            # chat_log="trail"
            if chat_log!="":
                send_message(class_name,window_title,chat_log)
                get_siri_answer("发送了%s给%s"%(chat_log,window_title))
            else:
                get_siri_answer("不好意思，没听清")
        close_chat(class_name,window_title)

##################################################################################################################################################################
#
#                                                                                 主程序运行函数
# 
##################################################################################################################################################################

def main():

    browser.get('front_page\index.html')   # Siri初始化
    browser.find_element_by_css_selector('input[name="_siri"]').send_keys("Waiting to begin...")
    get_siri_answer("再次见到您仿佛隔了一个世纪一样漫长，欢迎您回来")

    instruction=""

    while "再见"  not in instruction:         # 轮询函数，当指令中不包含“再见”时，提取指令中的关键词进行
        instruction=get_user_instruction()    # 并执行对应函数，当指令中包含“再见”时，退出程序并关闭窗口
        # instruction="b站"
        if instruction!="":
            get_siri_answer("请稍等")
            # UNIT对话模块
            if "天气" in instruction:                                  # 天气查询模块
                get_siri_answer(clever_chatter("weather",instruction))
                get_siri_answer("您还想让我为您做点什么？")
            elif ("聊天" in instruction)and ("你" in instruction):     # 聊天模块
                get_siri_answer("哈哈，小主您寂寞了吗，有我不比对象香？")
                instruction=get_user_instruction()
                while '不聊了' not in instruction:
                    get_siri_answer(clever_chatter("chat",instruction))
                    instruction=get_user_instruction()
                get_siri_answer("好哒，撒由那拉")
                get_siri_answer("您还想让我为您做点什么？")
            elif "对联" in instruction:                                 # 对对联模块
                get_siri_answer("得嘞，您给整个上联呗")
                instruction=get_user_instruction()
                get_siri_answer(clever_chatter("couplet",instruction))  
                get_siri_answer("您还想让我为您做点什么？")
            elif "笑话" in instruction:                                 # 讲笑话模块
                get_siri_answer(clever_chatter("joke",instruction))  
                get_siri_answer("您还想让我为您做点什么？")
            elif "数学" in instruction:                                 # 算题模块
                get_siri_answer("好呀，出题吧，我可是小天才纳兰珈")
                instruction=get_user_instruction()
                get_siri_answer(clever_chatter("calculator",instruction))  
                get_siri_answer("您还想让我为您做点什么？")
            elif "诗" in instruction:                                   # 作诗模块
                get_siri_answer("好的，给个主题呗")
                instruction=get_user_instruction()
                get_siri_answer(clever_chatter("poem",instruction))
                get_siri_answer("您还想让我为您做点什么？")    
            # B站爬取视频模块
            elif "b站" in instruction:
                bilibili_init()
                get_siri_answer("您还想让我为您做点什么？")
            # QQ对话模块
            elif "QQ" in instruction:
                QQ_chat_init()
                get_siri_answer("您还想让我为您做点什么？")    
            # 视频检测模块  
            elif "看" in instruction:
                get_siri_answer("好的，请问您想视频检测还是图像检测？")
                while True:
                    instruction=get_user_instruction()
                    if "视频" in instruction:
                        get_siri_answer("好的，即将为您打开yolo实时检测视频窗口")
                        video_detect()
                        get_siri_answer("您还想让我为您做点什么？")
                        break
                    elif "图像" in instruction:
                        get_siri_answer("好的，即将为您打开图像检测窗口")
                        img_detect()
                        get_siri_answer("您还想让我为您做点什么？")
                        break
                    else:
                        get_siri_answer("没听清，请您再说一遍")
            # 彩蛋模块
            elif "聪明" in instruction:                                
                get_siri_answer("嘻嘻，其实人家也没有你说的那么好啦") 
                get_siri_answer("您还想让我为您做点什么？")    
            # 退出模块            
            elif "再见" in instruction:
                continue
            # 若instruction为空，则调用提示语句，并请求重新发送命令
            else:
                get_siri_answer("啊偶，我不太理解呢，不过我能讲笑话，对对联，吟诗作对，陪您聊天，天气预报，算数学题，看图猜物，打开B站看视频，打开QQ侃大山，请问您需要我做点什么？")
        else:
            get_siri_answer("没听清，请您再说一遍")
    put_on_screen("再见，英俊潇洒的小主人，记得想我呦","_siri")
    get_siri_answer("再见，英俊潇洒的小主人，记得想我呦")
    browser.close()
if __name__ == '__main__':
    main()