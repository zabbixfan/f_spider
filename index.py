#coding:utf-8
import sys
print(sys.version)
if not sys.version.startswith('3'):
    reload(sys)
    sys.setdefaultencoding('utf-8')
import requests
import json
from config import Config
from bs4 import BeautifulSoup
from model import *
corp_id = Config.corp_id
corp_secret = Config.corp_secret
agent_id = Config.agent_id


# 获取token函数，文本里记录的token失效时调用
def get_access_token():
    get_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s' % (corp_id, corp_secret)
    r = requests.get(get_token_url)
    request_json = r.json()
    this_access_token = request_json['access_token']
    r.close()
    return this_access_token


def send_message(message):
    access_token = get_access_token()
    to_user = '@all'
    send_message_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s' % access_token
    message_params = {
        "touser": to_user,
        "msgtype": "text",
        "agentid": agent_id,
        "text": {
            "content": message
        },
        "safe": 0
    }
    r = requests.post(send_message_url, data=json.dumps(message_params))
    print(json.dumps(r.json(), indent=4))


# send_message("中国你好")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
}
r = requests.get(url="http://www.hzfc.gov.cn/yszmore.php",headers=headers)
content = r.content
soup = BeautifulSoup(content,"html.parser")
contents = soup.find(name="div",attrs={"class":"policy"})
if contents:
    for li_body in contents.find_all_next("li"):
        if li_body.a:
            if not session.query(User).filter(User.href==li_body.a['href']).first():
                User(href=li_body.a['href'],content=li_body.a.string).save()
                send_message("新预售证 {}".format(li_body.a.string))
else:
    print(content)