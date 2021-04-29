from bs4 import BeautifulSoup
import requests
import numpy as np
from operator import itemgetter 
import urllib.request
from difflib import SequenceMatcher
import os

video_log=[]
ini_word="<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n<html xmlns=\"http://www.w3.org/1999/xhtml\">\n<head>\n<title></title>\n<meta http-equiv=\"Content-Type\" content=\"text/html;charset=utf-8\">\n<style type=\"text/css\">\n*{padding:0;margin:0;}\n.con{width:1000px;margin:0 auto;border:1px solid #ccc;padding:1px 0;}\n.con:after{clear:both;display:block;width:0;height:0;content:\"\"}\n.pic{width:180px;height:140px;float:left;border:1px solid #ccc}\n.pic img{width:178px;height:138px;}\n.cent{float:left;width:700px;margin-left:90px;}\n</style>\n</head>\n<body>"

def spraw(userSeach): # 爬虫爬取信息
    global video_log
    video_log=[]
    page=1
    viedoNum=0
    val=0
    mainUrl='https://search.bilibili.com/all?keyword='+userSeach
    mainSoup = BeautifulSoup(requests.get(mainUrl).text, "html.parser")
    pages=mainSoup.find('li',class_="page-item last")
    if(pages):
        pages=int(pages.text)
        if pages>2:
            pages=2
    else:
        pages=1
    while page<=pages:
        mainUrl='https://search.bilibili.com/all?keyword='+userSeach+'&page='+page.__str__()
        mainSoup = BeautifulSoup(requests.get(mainUrl).text, "html.parser")
        temp_list=[]
        for item in mainSoup.find_all('li',class_="video-item matrix"):
            try:
                viedoNum += 1
                print('第'+ viedoNum.__str__() + '个视频:')
                val=item.find('a',class_="img-anchor")
                print('视频标题:'+ val["title"])
                print('视频链接:'+'https:'+val["href"])
                print('视频简介:'+item.find('div',class_="des hide").text.strip())
                print('up主:'+ item.find('a',class_="up-name").text.strip())
                raw_num=item.find('span',title='观看').text.strip()
                print('视频观看量:'+ raw_num)
                if raw_num[-1]<"0"or raw_num[-1]>"9":
                    if raw_num[-1]=="万":
                        raw_num=float(raw_num.replace("万",""))
                        raw_num*=10000
                else:
                    raw_num=float(raw_num)
                comment_num=item.find('span',title='弹幕').text.strip()    
                print('弹幕量:'+ comment_num)
                if comment_num[-1]<"0"or comment_num[-1]>"9":
                    if comment_num[-1]=="万":
                        comment_num=float(comment_num.replace("万",""))
                        comment_num*=10000
                else:
                    comment_num=float(comment_num)
                print('上传时间:'+ item.find('span',title='上传时间').text.strip())
                subUrl=val["href"]
                subSoup = BeautifulSoup(requests.get('https:'+subUrl).text.strip(), "html.parser")
                print('视频图片:'+subSoup.find(itemprop="image")["content"])
                video_log.append({"title":val["title"],"link":'https:'+val["href"],"brief":item.find('div',class_="des hide").text.strip(),"auther":item.find('a',class_="up-name").text.strip(),"viewer":raw_num,"time":item.find('span',title='上传时间').text.strip(),"image":subSoup.find(itemprop="image")["content"],"comment":comment_num})
            except:
                continue
        page+=1

# 爬虫信息搜集
# 视频标题:2000元买一条超大日本须鲨，处理一下午，切开后看着这肉质就过瘾
# 视频链接:https://www.bilibili.com/video/BV1QZ4y1s7kp?from=search
# 视频简介:
# up主:小文哥吃吃吃
# 视频观看量:181.7万
# 弹幕量:6691
# 上传时间:2020-05-17

def gene_html(mode="time"): # 将搜集到的信息整理并生成html页面
    global ini_word
    if mode=="time":
        clean_list = sorted(video_log, key=itemgetter('time'),reverse=True)[:10] 
    if mode=="view":
        clean_list = sorted(video_log, key=itemgetter('viewer'),reverse=True)[:10] 
    if mode=="comment":
        clean_list = sorted(video_log, key=itemgetter('comment'),reverse=True)[:10]
    gene_content=""
    for item_message in clean_list:
        if item_message["viewer"]>10000:
            item_message["viewer"]=str(item_message["viewer"]/10000)+"万"
        else:
            item_message["viewer"]=str(item_message["viewer"])
        if item_message["comment"]>10000:
            item_message["comment"]=str(item_message["comment"]/10000)+"万"
        else:
            item_message["comment"]=str(item_message["comment"])        
        item_content="\n<div class=\"con\">\n\t<div class=\"pic\"><img src=\"%s\" alt=\"猫\"></div>\n\t<div class=\"cent\"><p>视频标题:%s</p><p>视频简介:%s</p><p>up主:%s</p><p>视频观看量:%s</p><p>弹幕量:%s</p><p>上传时间:%s</p></div>\n</div>"%(item_message["image"],item_message["title"],item_message["brief"],item_message["auther"],item_message["viewer"],item_message["comment"],item_message["time"])
        gene_content+=item_content
    ini_word+=gene_content
    input_file=ini_word+"\n</body>\n</html>"
    html_path="C:\\Users\\72453\\Desktop\\大三下课程\\应用软件设计\\应用软件小作业\\bilibili-video-master\\front_page\\info_collect.html"
    if os.path.exists(html_path):
        os.remove(html_path)
    html_file = open(html_path, "w",encoding="utf-8")
    html_file.write(input_file)

def similarity(a, b): # 比较序列，模糊查找
    return SequenceMatcher(None, a, b).ratio()

def open_video(video_name): # 根据查找结果打开视频
    simi_list=[]
    for item in video_log:
        simi_list.append(similarity(item["title"],video_name))
    max_index = simi_list.index(max(simi_list))
    return video_log[max_index]["link"]
