import json
import os.path
import time
import requests
import re

ERROR = ("ERROR_FAULT_CODE", "ERROR_NOT_CODE", "ERROR_UNKNOW")
SUCCESS = ("SUCCESS")
root_path = os.path.split(os.path.realpath(__file__))[0]
headers = {
    'User-Agent':
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A366 MicroMessenger/6.7.3(0x16070321) NetType/WIFI Language/zh_CN',
}


def query(id):
    url = "https://api.m.sm.cn/rest?method=kuaidi.getdata&sc=express_cainiao&q=" + id + "&bucket=&callback=jsonp1"
    r = requests.get(url, headers=headers)
    result = re.search(r'jsonp1\((.*)\);', r.text, re.I)
    result = json.loads(result.group(1))
    if not result['data']["company"]:
        return "ERROR_FAULT_CODE", ""
    elif result['status'] == 1:
        return "SUCCESS", result["data"]
    elif result['status'] == 0:
        return "ERROR_NOT_CODE", ""
    else:
        return "ERROR_UNKNOW", ""


def sc_noti(key, description, full):
    text = '!-{description}-!快递状态变化'.format(description=description)

    desp = ''
    for i in full:
        desp = desp + '{time} **{state}**\n\n'.format(time=i.get('time'),
                                                      state=i.get('context'))
    print(text)

    if key =="test":
        return
    sc_url = 'https://sc.ftqq.com/' + key + '.send'
    requests.post(sc_url, data={'text': text, 'desp': desp})


def is_signed(state):
    flag = False
    if state == "已签收" or state == "\u5df2\u7b7e\u6536":
        flag = True
    if state == "单号错误":
        flag = True
    if state == "不支持":
        flag = True
    return flag


def send(phoneid):
    with open(root_path + "/data/" + phoneid + "_data.json",
              encoding="utf8") as a:
        data = json.loads(a.read())

    with open(root_path + "/config/" + phoneid + "_config.json",
              encoding="utf8") as b:
        config = json.loads(b.read())

    data_n = {}

    for i in config.get("post_list"):
        id = i.get('id')
        description = i.get('description')

        if not id or not description:
            print('\nconfig.py文件错误！', i, '\n')
            return

        # 如果是一个新的数据
        if not data.get(id):
            data[id] = {}
            data[id]['last_time'] = '0'

        # 状态已经是已签收
        if is_signed(data.get(id).get('state', '0')):
            data_n[id] = data[id]
            continue

        print("-----------{time}-----------".format(
            time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        print("尝试读取{description}:{id}".format(description=description, id=id))
        try:
            status, result = query(id)
        except:
            print("请求接口错误\n")
            continue

        if status in ERROR:
            print('快递单号数据出错！', i, '\n')
            data[id]['last_time'] = ""
            data[id]['state'] = "单号错误"
            data[id]['description'] = description
            sc_noti(config.get("key"), description, "单号错误，请重新添加！")
        else:
            last_time = result.get('messages')[0].get('time')
            context = result.get('messages')[0].get('context')
            full = result.get('messages')

            if last_time != data.get(id).get('last_time'):
                data[id]['last_time'] = last_time
                data[id]['state'] = result.get('status')
                data[id]['description'] = description
                sc_noti(config.get("key"), description, full)
                print("更新数据为 : {context}\n".format(context=context))
            else:
                print("未更新数据")

        # 写入数据，舍弃旧数据
        data_n[id] = data[id]
        time.sleep(6)

    with open(root_path + "/data/" + phoneid + "_data.json","w",encoding="utf8") as a:
        a.write(json.dumps(data_n, ensure_ascii=False))


with open(root_path + "/phoneid.json", encoding="utf8") as a:
    ids = json.loads(a.read())
    for phoneid in ids.get("phoneid"):
        print("+ = + = + = + ={phoneid} + = + = + = + = + =\n".format(
            phoneid=phoneid))
        send(phoneid)