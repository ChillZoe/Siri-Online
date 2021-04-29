#!/usr/bin/python
import win32clipboard as w
import time
import os
import time
import win32gui
import win32api
import win32con
import win32com.client
from win32process import *
import pymouse,pykeyboard
from pymouse import *
from pykeyboard import PyKeyboard
from ctypes import *
import sys
import pyperclip
import re



def send_message(class_name,receiver,msg,upper=1): # 在QQ对话框发送信息，upper参数决定发送信息的条数
    w.OpenClipboard()
    w.EmptyClipboard()
    w.SetClipboardData(win32con.CF_UNICODETEXT, msg)
    w.CloseClipboard()
    for i in range(upper):
        win32gui.EnumWindows(_window_enum_callback, ".*%s.*" %(receiver))
        print(i)
        qq = win32gui.FindWindow(None, receiver)
        print(qq)
        win32gui.SendMessage(qq, win32con.WM_PASTE, 0, 0)
        win32gui.SendMessage(qq, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)

def _window_enum_callback(hwnd, wildcard): # 定位并打开对话框
    '''
    Pass to win32gui.EnumWindows() to check all the opened windows
    把想要置顶的窗口放到最前面，并最大化
    '''
    if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
        win32gui.BringWindowToTop(hwnd)
        # 先发送一个alt事件，否则会报错导致后面的设置无效：pywintypes.error: (0, 'SetForegroundWindow', 'No error message is available')
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        # 设置为当前活动窗口
        win32gui.SetForegroundWindow(hwnd)
        # 最大化窗口
        win32gui.ShowWindow(hwnd, win32con.SW_NORMAL)


def open_window(friends): # 利用搜索功能打开QQ对话框
    handle = win32gui.FindWindow(None, "QQ")
    win32gui.ShowWindow(handle,win32con.SW_SHOW)
    loginid = win32gui.GetWindowPlacement(handle)
    windll.user32.SetCursorPos(loginid[4][0]+150,loginid[4][1]+122)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0,0,0)#press mouse
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0,0,0)#release mouse
    time.sleep(0.1)
    pyperclip.copy(friends)
    time.sleep(0.1)
    k = PyKeyboard()
    k.press_key(k.control_key)
    k.tap_key('v')
    k.release_key(k.control_key)
    time.sleep(1)
    win32api.keybd_event(13,0,0,0)
    win32api.keybd_event(13,0,win32con.KEYEVENTF_KEYUP,0)
    time.sleep(0.2)
    hWndList = [] 
    win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), hWndList) 
    for hwnd in hWndList:
        clsname = win32gui.GetClassName(hwnd)
        title = win32gui.GetWindowText(hwnd)
        if (clsname=='TXGuiFoundation') and title!="QQ"and title!=""and title!="TXMenuWindow" : #调整目标窗口到坐标(600,300),大小设置为(600,600)
            break
    hwnd=win32gui.FindWindow(None, title)
    win32gui.ShowWindow(hwnd,win32con.SW_SHOW)
    return clsname,title

def QQ(qq="",pwd=""): # qq=“输入账号” pwd=“输入密码”
    #运行QQ
    if win32gui.FindWindow(None, "QQ"):
        return
    os.system('"C:\Program Files (x86)\Tencent\QQ\Bin\QQScLauncher.exe"') # 运行QQ客户端
    time.sleep(5)
    #获取QQ的窗口句柄
    #参数1是类名,参数2是QQ软件的标题
    a = win32gui.FindWindow(None,"QQ")
    #获取QQ登录窗口的位置
    loginid = win32gui.GetWindowPlacement(a)


    #定义一个键盘对象
    k = PyKeyboard()

    #把鼠标放置到登陆框的输入处
    windll.user32.SetCursorPos(loginid[4][0]+192,loginid[4][1]+112)

    #按下鼠标再释放
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0,0,0)#press mouse
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0,0,0)#release mouse
    win32api.keybd_event(13,0,0,0)
    win32api.keybd_event(13,0,win32con.KEYEVENTF_KEYUP,0)

def close_chat(class_name,receiver): # 关闭QQ聊天窗口
    curwindow = win32gui.FindWindow(class_name, receiver)
    win32gui.PostMessage(curwindow,win32con.WM_CLOSE,0,0)
