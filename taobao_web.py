# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import time
import datetime
import hashlib
import re
from urllib import parse
import json
import sys
from bs4 import BeautifulSoup, Tag
import random

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


User_Agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

appKey = '12574478'


requests_session = requests.session()


def get_sign_val(d):
    print(user_cookie, d)
    _m_h5_tk = re.findall(r"_tb_token_=([^;]*)", user_cookie)[0]
    t = str(int(time.time() * 1000))
    token = _m_h5_tk.split('_')[0]
    str_sign = '&'.join([token, t, appKey, str(d)])
    sign = hashlib.md5(str_sign.encode('utf-8')).hexdigest()
    return sign, t


def build_order(buyNow):
    flag = False
    sign, t = get_sign_val(buyNow)
    params = {'jsv': '2.5.1', 'appKey': appKey, 't': t,
              'sign': sign, 'api': 'mtop.trade.order.build.h5', 'v': '4.0',
              'type': 'originaljson', 'ttid': '#t#ip##_h5_2019', 'isSec': '1', 'ecode': '1', 'AntiFlood': 'true',
              'AntiCreep': 'true', 'H5Request': 'true', 'dataType': 'jsonp'}
    # &smToken=as&sm=e

    url = 'https://h5api.m.taobao.com/h5/mtop.trade.order.build.h5/4.0/?' + \
        parse.urlencode(params)
    headers = {
        "Accept": 'application/json',
        "Origin": 'https://main.m.taobao.com',
        "User-Agent": User_Agent,
        "Content-type": 'application/x-www-form-urlencoded',
        "Cookie": user_cookie,
    }
    data = requests_session.post(url, headers=headers, data={'data': buyNow})
    print(data.content)
    data = data.json()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print("%s order.build %s " % (now, data.get('ret')))
    if "SUCCESS" not in data.get('ret')[0]:
        fail_sys_sleep(data)
        return flag, data

    item_info = [x[1] for x in data.get('data').get(
        'data').items() if "itemInfo_" in x[0]]
    is_disabled = item_info[0].get('fields').get('disabled')
    if is_disabled == 'false':
        flag = True

    return flag, data


def get_buy_cart(good_id):
    exParams = {
        "mergeCombo": True,
        "version": '1.1.1',
        "globalSell": 1,
    }
    data = json.dumps({"isPage": True, "extStatus": 0,
                       "netType": 0, "exParams": json.dumps(exParams)})
    sign, t = get_sign_val(data)
    params = {'jsv': '2.5.1', 'appKey': appKey, 't': t,
              'sign': sign, 'api': 'mtop.trade.query.bag', 'v': '5.0',
              'type': 'jsonp', 'ttid': 'h5', 'isSec': '0', 'ecode': '1', 'AntiFlood': 'true',
              'AntiCreep': 'true', 'H5Request': 'true', 'dataType': 'jsonp', 'callback': 'mtopjsonp2', 'data': data}

    url = 'https://h5api.m.taobao.com/h5/mtop.trade.query.bag/5.0/?' + \
        parse.urlencode(params)
    headers = {
        "Accept": 'application/json',
        "Origin": 'https://main.m.taobao.com',
        "User-Agent": User_Agent,
        "Content-type": 'application/x-www-form-urlencoded',
        "Cookie": user_cookie,
    }
    jsonp = requests_session.get(url, headers=headers).text
    response = jsonp[jsonp.index("(") + 1: jsonp.rindex(")")]
    data = json.loads(response)
    print("%s query.bag %s " % (datetime.datetime.now().strftime(
        '%Y-%m-%d %H:%M:%S.%f'), data.get('ret')))
    settlement = ''
    canCheck = False
    if "SUCCESS" not in data.get('ret')[0]:
        fail_sys_sleep(data)
        flag = False
    else:
        flag = True
        item_like = ['item_']
        for x in data.get('data').get('data').items():
            for y in item_like:
                if y in x[0]:
                    if good_id == x[1]['fields']['itemId']:
                        settlement = x[1]['fields']['settlement']
                        canCheck = x[1]['fields']['canCheck']
                        break

    buy_now = {"buyNow": False, "buyParam": settlement,
               "spm": "a21202.12579950.settlement-bar.0"}
    return flag, canCheck, json.dumps(buy_now)


def create_order(build_data):
    flag = False
    item_like = ['item_', 'itemInfo_', 'service_yfx_',
                 'invoice_', 'promotion_', 'deliveryDate_']
    item_hit = ['anonymous_1', 'address_1', 'voucher_1',
                'confirmOrder_1', 'ncCheckCode_ncCheckCode1', 'submitOrder_1']

    params_data_children = {}
    for x in build_data.get('data').get('data').items():
        for y in item_hit:
            if y == x[0]:
                params_data_children[x[0]] = x[1]
                break

        for y in item_like:
            if y in x[0]:
                params_data_children[x[0]] = x[1]

    params_data = {
        "operator": None,
        "data": json.dumps(params_data_children),
        "linkage": json.dumps(build_data.get('data').get('linkage')),
        "hierarchy": json.dumps(build_data.get('data').get('hierarchy')),
        "lifecycle": None
    }
    data = json.dumps({"params": json.dumps(params_data)},
                      separators=(',', ':'), ensure_ascii=False)
    sign, t = get_sign_val(data)
    params3 = {'jsv': '2.5.1', 'appKey': appKey, 't': t,
               'sign': sign, 'v': '4.0', 'post': '1', 'type': 'originaljson', 'timeout': '15000',
               'api': 'mtop.trade.order.create.h5',
               'isSec': '1', 'ecode': '1', 'AntiFlood': 'true', 'dataType': 'jsonp', 'ttid': '#t#ip##_h5_2019'}

    url = 'https://h5api.m.taobao.com/h5/mtop.trade.order.create.h5/4.0/?' + \
        parse.urlencode(params3)
    headers = {
        "Accept": 'application/json',
        "Origin": 'https://main.m.taobao.com',
        "User-Agent": User_Agent,
        "Content-type": 'application/x-www-form-urlencoded',
        "Cookie": user_cookie,
    }
    json_data = requests_session.post(
        url, headers=headers, data={'data': data})
    print(json_data.content)
    json_data = json_data.json()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print("%s order.create %s " % (now, json_data.get('ret')))
    if "SUCCESS" in json_data.get('ret')[0]:
        flag = True
    else:
        fail_sys_sleep(json_data)
    return flag, json_data


def fail_sys_sleep(data):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    if len(data.get('ret')) == 1:
        if "FAIL_SYS_TOKEN_EXOIRED" in data.get('ret')[0]:
            print("%s cookie timeout" % (now))
            exit()

        if "FAIL_SYS_TRAFFIC_LIMIT" in data.get('ret')[0]:
            print("%s need sleep", now)

        if "P-01415-14-15-004" in data.get('ret')[0]:
            print("%s 系统繁忙，请稍候再试" % (now))

    # ['RGV587_ERROR::SM::亲,访问被拒绝了哦!请检查是否使用了代理软件或VPN哦~', 'FAIL_SYS_USER_VALIDATE::亲,访问被拒绝了哦!请检查是否使用了代理软件或VPN哦~']
    elif len(data.get('ret')) == 2:
        if "FAIL_SYS_USER_VALIDATE" in data.get('ret')[0] or "FAIL_SYS_USER_VALIDATE" in data.get('ret')[1]:
            print("%s need verify !!!" % (now))
            exit()
            # punish_url = data.get('data').get('url')
            # verify_flag = verify_action(punish_url)
            # now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            # print("%s verify %s " % (now, verify_flag))
    else:
        pass


# 二维码扫码
options = webdriver.ChromeOptions()
options.add_argument('--disable-extensions')
options.add_argument("--no-sandbox")
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('w3c', False)
browser = webdriver.Chrome(options=options)
browser.get('https://login.taobao.com/member/login.jhtml')

while True:
    if 'cart.taobao.com' not in browser.current_url:
        print("%s : success %s " % (datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S.%f'), browser.current_url))
        browser.get(
            'https://main.m.taobao.com/cart/index.html?cartFrom=taobao_client&spm=a215s.7406091.toolbar.i2')
        break
    print("%s : %s" % (datetime.datetime.now().strftime(
        '%Y-%m-%d %H:%M:%S.%f'), browser.current_url))
    time.sleep(3)

user_cookie = ''
for i in range(len(browser.get_cookies())):
    user_cookie += browser.get_cookies()[i].get('name') + \
        '=' + browser.get_cookies()[i].get('value') + ';'
print(user_cookie)

while True:
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    buy_cart_flag, canCheck, buy_now = get_buy_cart('580003475920')

    build_order_flag, build_data = build_order(buy_now)

    exit()
    build_data = {}
    build_order_flag = False
    build_order_limit = 0
    while not build_order_flag:

        if not build_order_flag:
            if build_order_limit >= 3:
                build_order_limit = 0
                time.sleep(0.5)
            else:
                time.sleep(0.2)
        build_order_limit += 1

    create_order_data = {}
    create_order_flag = False
    create_order_limit = 0
    while not create_order_flag:
        create_order_flag, create_order_data = create_order(build_data)
        if not create_order_flag:
            if create_order_limit >= 3:
                create_order_limit = 0
                time.sleep(0.5)
            else:
                time.sleep(0.2)
        create_order_limit += 1

    if create_order_flag:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        print("%s Congratulations!" % now)

    break
