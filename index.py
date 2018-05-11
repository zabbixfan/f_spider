#coding:utf-8
import sys,re
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
    r = requests.get(get_token_url,timeout=10)
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
def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
    }
    r = requests.get(url=url, headers=headers)
    if r.status_code == 200:
        content = r.content
        return content
    else:
        return False

def parser_html(source_html):
    soup = BeautifulSoup(source_html,"html.parser")
    houses = soup.find(name="dd", attrs={"style": "padding-bottom:10px;padding-left: 11px;"})
    presales = houses.find_all(name="li")
    result = []
    for house in presales[0:10]:
        result.append({
            'name': re.sub("\s", "", house.find('div',class_='secfyzs_wenzi').string).split('[')[0],
            'presaleid': re.sub("\s", "", house.find('p',class_='black333 f16 line40').string),
            'url': house.a['href']
        })
    return result

def save_item(house):
    url = Config.tmsf_url + house['url']
    detail_html = get_html(url)
    if detail_html:
        soup = BeautifulSoup(detail_html,"html.parser")
        wuye_tag = soup.find("strong",text="物业类型：")
        wuye_info = re.sub("\s","",wuye_tag.next_sibling.next_sibling.get_text())
        if wuye_info.find("")
    else:
        return False

if __name__ == '__main__':
    html_text = get_html("http://www.tmsf.com/index.jsp")
    if html_text:
        houses = parser_html(html_text)
        if houses:
            for house in houses:
                save_item(house)


