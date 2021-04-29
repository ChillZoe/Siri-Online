# 说明：将固定文本发送给百度平台实现UNIT的交流

import requests
import json

# 需要的库requests、json（import 进来就好了）
baidu_server = 'https://aip.baidubce.com/oauth/2.0/token?'  #获取token的server
grant_type = 'client_credentials'
client_id = 'SFIGS9UYbYcHU1pwnFWcuhkM' #API KEY
client_secret = 'SqeF4q4GYnT7k9GEKQ6yosSFhL8lLpzb' #Secret KEY   这里可以自己去百度注册，这里是我的API KEY 和 Secret KEY

#合成请求token的url
url = baidu_server+'grant_type='+grant_type+'&client_id='+client_id+'&client_secret='+client_secret

#获取token
res = requests.get(url).text
data = json.loads(res)  #将json格式转换为字典格式
token = data['access_token']

mode_dict={
"weather":'1090427',
"couplet":'1090435',
"joke":'1090436',
"chat":'1090428',
"poem":'1090440',
"calculator":'1090439'
}
access_token = token
url = 'https://aip.baidubce.com/rpc/2.0/unit/service/chat?access_token=' + access_token    #不用动
session_id=''
def clever_chatter(mode,sentence): # 根据不同模式采取不同回复方式
    q = sentence   #需要发送给UNIT服务器的内容放到这里即可
    global session_id
    if (mode!="chat" and mode!="weather"): 
        post_data = "{\"log_id\":\"UNITTEST_10000\",\"bot_id\":\"%s\",\"version\":\"2.0\",\"service_id\":\"S50173\",\"session_id\":\"\",\"request\":{\"query\":\"%s\",\"user_id\":\"88888\",\"query_info\":{\"type\":\"TEXT\",\"source\":\"KEYBOARD\"}}}}"%(mode_dict[mode],q)
    elif session_id=='':
        post_data = "{\"log_id\":\"UNITTEST_10000\",\"bot_id\":\"%s\",\"version\":\"2.0\",\"service_id\":\"S50173\",\"session_id\":\"\",\"request\":{\"query\":\"%s\",\"user_id\":\"88888\",\"query_info\":{\"type\":\"TEXT\",\"source\":\"KEYBOARD\"}}}}"%(mode_dict[mode],q)
    else:
        post_data = "{\"log_id\":\"UNITTEST_10000\",\"bot_id\":\"%s\",\"version\":\"2.0\",\"service_id\":\"S50173\",\"session_id\":\"%s\",\"request\":{\"query\":\"%s\",\"user_id\":\"88888\",\"query_info\":{\"type\":\"TEXT\",\"source\":\"KEYBOARD\"}}}}"%(mode_dict[mode],session_id,q)
    #post_data中主要修改的是：service_id（提前准备好的机器人id）、type(TEXT为常规的文本型，EVENT为一组K-V（json），且其中必须包含一个名为『event_name』的key，其他自便)、source（"ASR","KEYBOARD"。ASR为语音输入，KEYBOARD为键盘文本输入。针对ASR输入，UNIT平台内置了纠错机制，会尝试解决语音输入中的一些常见错误）
    #print('post_data:',post_data)
    headers = {'content-type': 'application/x-www-form-urlencoded'}  
    response = requests.post(url, data=post_data.encode('utf-8'), headers=headers)
    #post_data.encode('utf-8')，需要先将post_data编码为‘utf-8’格式，否则会出错
    if response:
        content=response.json()
        try:
            session_id=content["result"]["session_id"]
        except:
            return "啊偶，我不知道您在说什么"
        words_list=[]
        for item in content['result']['response_list']:
            if item['origin']!=mode_dict[mode]:
                continue
            if 'action_list' in item:
                for action_item in item['action_list']:
                    words_list.append(action_item['say'])
        while '我不知道应该怎么答复您。' in words_list and len(words_list)!=1:
            words_list.remove('我不知道应该怎么答复您。')
        print(words_list)
        return words_list[0]