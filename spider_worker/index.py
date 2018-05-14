#coding:utf-8
import re
import sys

if not sys.version.startswith('3'):
    reload(sys)
    sys.setdefaultencoding('utf-8')
import requests
import json
from bs4 import BeautifulSoup
import socket
from spider_worker.model import *
from config import Config
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
def get_proxies():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.connect(('127.0.0.1', 1087))
        res = True
    except Exception as e:
        res = False
    finally:
        s.close()
    if res:
        return {"http": "http://127.0.0.1:1087"}
    else:
        return None
def get_html(url,retry=0):
    proxies = get_proxies()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
    }
    try:
        r = requests.get(url=url, headers=headers,timeout=10,proxies=proxies)
    except Exception as e:

        retry += 1
        if retry < Config.max_request_retry:
            get_html(url,retry=retry)
        else:
            print(e)
        #todo logging
            return False
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
            'presale_num': re.sub("\s", "", house.find('p',class_='black333 f16 line40').string),
            'url': house.a['href']
        })
    return result
def parser_html_xiaoshan(source_html):
    soup = BeautifulSoup(source_html,"html.parser")
    houses = soup.find("table",attrs={"style": "margin-top: 5px;"})
    presales = houses.find_all(name="tr")
    result = []
    for house in presales[1:]:
        house_info = house.find_all('td')
        result.append({
            'name': house_info[0].a['title'],
            'presale_num': house_info[1].get_text().strip("\n"),
            'url': house_info[0].a['href']
        })
    return result
def parser_html_yuhang(source_html):
    soup = BeautifulSoup(source_html,"html.parser")
    houses = soup.find("div",attrs={"style": "display:block;"}).find_next_sibling("div")
    presales = houses.find_all("div",attrs={"class": "tb_bg"})
    result = []
    for house in presales[0:5]:
        house_info1 = house.a.table.tbody.find_all('td')
        house_info2 = house.a.find_next_sibling("table")['onclick']
        pattern = re.compile('\(\'(.*)\'\)')
        url = pattern.search(house_info2).group(1).replace("presell","property")
        url = re.sub(r"(_\d+)\.htm","_info.htm",url)
        result.append({
            'name': house_info1[1].string.strip(),
            'presale_num': house_info1[3].string.strip(),
            'url': url
        })
    return result
NUMBER_MAP = {
    'numberdor': '.',
    'numberone': '1',
    'numbertwo': '2',
    'numberthree': '3',
    'numberfour': '4',
    'numberfive': '5',
    'numbersix': '6',
    'numberseven': '7',
    'numbereight': '8',
    'numbernine': '9',
    'numberzero': '0',
}
def parser_room_info(source_info):
    spans = [NUMBER_MAP[(span['class'][0])]for span in source_info.div.find_all("span")]
    if spans:
        return float(''.join(spans))
    return 0
def save_item(house):
    url = Config.tmsf_url + house['url']
    detail_html = get_html(url)
    if detail_html:
        soup = BeautifulSoup(detail_html,"html.parser")
        wuye_tag = soup.find("strong",text="物业类型：")
        wuye_info = re.sub("\s","",wuye_tag.next_sibling.next_sibling.get_text())
        if wuye_info.find("住宅")> -1 and not session.query(HouseDetail).filter(HouseDetail.presale_num==house['presale_num']).first():
            save_db(house)
    else:
        return False
def save_db(house):
    #房源不存在则插入
    if not session.query(Houses).filter(Houses.name == house['name']).first():
        Houses(name=house['name'],url = house['url']).save()
        print(house)
    #找到预售号ID
    house_price_uri = house['url'].replace("info","price")
    url = Config.tmsf_url + house_price_uri
    price_detail = get_html(url)
    if price_detail:
        soup = BeautifulSoup(price_detail,"html.parser")
        presellid = soup.find("a",text=house['presale_num']).get('id').split("_")[-1]
        #通过预售证id爬取所有房源信息
        print("{} page 1 start".format(house['name']))
        house_price_uri2 = house_price_uri + '?isopen=&presellid={}&buildingid=&area=&allprice=&housestate=&housetype=&page='.format(presellid)
        url2 = Config.tmsf_url + house_price_uri2
        first_page_detail = get_html(url2)
        soup = BeautifulSoup(first_page_detail,"html.parser")
        house_info_table = soup.find("table", attrs={'style': 'font-size:12px;'})
        if not house_info_table:
            #todo logging not found
            return False
        for room in house_info_table.find_all("tr"):
            room_info = room.find_all("td")
            room = HouseDetail()
            room.presale_num = house['presale_num']
            room.building_num = room_info[0].get_text().strip("\n")
            room.room_num = room_info[1].get_text().strip("\n")
            room.floor_area = parser_room_info(room_info[2])
            room.use_area = parser_room_info(room_info[3])
            room.used_precent = parser_room_info(room_info[4])
            room.unit_price = parser_room_info(room_info[5])
            room.decorate_price = parser_room_info(room_info[6])
            room.total_price = parser_room_info(room_info[7])
            room.house = session.query(Houses).filter(Houses.name == house['name']).first().id
            room.save()
        # 找到总页数
        total_page_tag = soup.find("div", attrs={'class': 'spagenext'})
        pattern = re.compile('1/(\d+)')
        match = pattern.search(total_page_tag.span.string)
        total_page = int(match.group(1))
        for page in range(2,total_page+1):
            print("{} page {} start".format(house['name'],page))
            house_price_uri3 = house_price_uri + '?isopen=&presellid={}&buildingid=&area=&allprice=&housestate=&housetype=&page={}'.format(
                presellid,page)
            url3 = Config.tmsf_url + house_price_uri3
            page_detail = get_html(url3)
            soup = BeautifulSoup(page_detail, "html.parser")
            house_info_table = soup.find("table", attrs={'style': 'font-size:12px;'})
            if not house_info_table:
                # todo logging not found
                return False
            for room in house_info_table.find_all("tr"):
                room_info = room.find_all("td")
                room = HouseDetail()
                room.presale_num = house['presale_num']
                room.building_num = room_info[0].get_text().strip("\n")
                room.room_num = room_info[1].get_text().strip("\n")
                room.floor_area = parser_room_info(room_info[2])
                room.use_area = parser_room_info(room_info[3])
                room.used_precent = parser_room_info(room_info[4])
                room.unit_price = parser_room_info(room_info[5])
                room.decorate_price = parser_room_info(room_info[6])
                room.total_price = parser_room_info(room_info[7])
                room.house = session.query(Houses).filter(Houses.name == house['name']).first().id
                room.save()

if __name__ == '__main__':
    html_text = get_html("http://www.tmsf.com/index.jsp")
    if html_text:
        houses = parser_html(html_text)
        if houses:
            for house in houses:
                save_item(house)
    html_text = get_html("http://www.tmsf.com/xsweb/")
    if html_text:
        houses = parser_html_xiaoshan(html_text)
        if houses:
            for house in houses:
                save_item(house)
    html_text = get_html("http://www.tmsf.com/newhouse/OpenReport_show_330184.htm")
    if html_text:
        houses = parser_html_yuhang(html_text)
        if houses:
            for house in houses:
                save_item(house)

