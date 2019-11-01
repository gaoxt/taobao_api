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

from pyzbar.pyzbar import decode
from PIL import Image
import qrcode

User_Agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

# 抢购前最好重新登录一遍避免过期
times = sys.argv[1]
good_id = sys.argv[2]
pwd = sys.argv[3]
user_cookie = ''
if len(sys.argv) >= 5 and sys.argv[4] != '':
    user_cookie = sys.argv[4]

appKey = '12574478'

# 二维码扫码
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-extensions')
options.add_argument("--no-sandbox")
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('w3c', False)
browser = webdriver.Chrome(options=options)
browser.get('https://login.taobao.com/member/login.jhtml')

if user_cookie == '':
    img = WebDriverWait(browser, 2, 0.1).until(
        EC.presence_of_element_located((By.XPATH, "//div[@id='J_QRCodeImg']/img"))).get_attribute('src')
    img_content = requests.get(img, timeout=5).content
    file_name = 'taobao_qrcode.png'
    fp = open(file_name, 'wb')
    fp.write(img_content)
    fp.close()

    barcode_url = ''
    barcodes = decode(Image.open(file_name))
    for barcode in barcodes:
        barcode_url = barcode.data.decode("utf-8")

    qr = qrcode.QRCode()
    qr.add_data(barcode_url)
    qr.print_ascii(invert=True)
    while True:
        if 'login.taobao.com' not in browser.current_url:
            print("%s : success %s " % (datetime.datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S.%f'), browser.current_url))
            browser.get(
                'https://main.m.taobao.com/cart/index.html?cartFrom=taobao_client&spm=a215s.7406091.toolbar.i2')
            break
        print("%s : %s" % (datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S.%f'), browser.current_url))
        time.sleep(2)

    user_cookie = ''
    for i in range(len(browser.get_cookies())):
        user_cookie += browser.get_cookies()[i].get('name') + \
            '=' + browser.get_cookies()[i].get('value') + ';'

print(user_cookie)
# options = webdriver.ChromeOptions()
# prefs = {"profile.managed_default_content_settings.images": 2, 'disk-cache-size': 10240}
# options.add_argument('--headless')
# options.add_argument('--disable-extensions')
# options.add_argument('--disable-gpu')
# options.add_argument("--disable-plugins")
# options.add_argument("--disable-images")
# options.add_argument("--no-sandbox")
# options.add_experimental_option('w3c', False)
# options.add_experimental_option("prefs", prefs)
# options.add_experimental_option('excludeSwitches', ['enable-automation'])
# browser = webdriver.Chrome(options=options)
# browser.get('https://maliprod.alipay.com/w/trade_pay.do')
requests_session = requests.session()


def alipay(url):
    flag = False
    browser.get(url)
    message = re.findall(
        '<div class="am-dialog-text".*?>(.*?)</div>', browser.page_source)
    if '#CCCCCC' in message:
        print('%s alipay %s' % (datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S.%f'), message[0]))
        return flag
    browser.find_element_by_xpath("//div[@class='am-section']/button").click()
    for p in pwd:
        # 0.1秒内随机
        time.sleep(random.randint(1, 200) / 1000)
        browser.find_element_by_id("spwd_unencrypt").send_keys(p)
    print("%s alipay done" %
          (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
    time.sleep(1)
    message = re.findall(
        '<div class="am-dialog-text".*?>(.*?)</div>', browser.page_source)
    if len(message) == 0:
        message = re.findall(
            '<div class="am-message[\w\W]*<p><span>([\w\W]*?)</span>', browser.page_source)
    if len(message) == 0:
        message = 'no message'

    print('%s alipay %s' % (datetime.datetime.now().strftime(
        '%Y-%m-%d %H:%M:%S.%f'), message[0]))
    return True


def get_sign_val(d):
    _m_h5_tk = re.findall(r"_m_h5_tk=([^;]*)", user_cookie)[0]
    t = str(int(time.time() * 1000))
    token = _m_h5_tk.split('_')[0]
    str_sign = '&'.join([token, t, appKey, str(d)])
    sign = hashlib.md5(str_sign.encode('utf-8')).hexdigest()
    return sign, t


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
    start_time = int(time.time() * 1000)
    jsonp = requests_session.get(url, headers=headers).text
    end_time = int(time.time() * 1000)
    response = jsonp[jsonp.index("(") + 1: jsonp.rindex(")")]
    data = json.loads(response)

    print("%s query.bag %s " % (datetime.datetime.now().strftime(
        '%Y-%m-%d %H:%M:%S.%f'), data.get('ret')))
    settlement = ''
    canCheck = False
    # aliyun_time = int(data.get('data').get('global').get('controlParas').get('time'))
    # halfway_time = end_time - aliyun_time
    # cpu_time = aliyun_time - start_time - halfway_time
    # print("start   :%s.%s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time / 1000)), str(start_time)[-3:]))
    # print("aliyun  :%s.%s " % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(aliyun_time / 1000)), str(aliyun_time)[-3:]))
    # print("end     :%s.%s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time / 1000)), str(end_time)[-3:]))
    # print("halfway :%s " % (halfway_time/1000))
    # print("cpu_time:%s " % (cpu_time/1000))
    # print("total   :%s " % ((end_time-start_time)/1000))
    # exit()
    flag = False
    if "SUCCESS" not in data.get('ret')[0]:
        fail_sys_sleep(data)
    else:
        item_like = ['item_']
        for x in data.get('data').get('data').items():
            for y in item_like:
                if y in x[0]:
                    if good_id == x[1]['fields']['itemId']:
                        flag = True
                        settlement = x[1]['fields']['settlement']
                        canCheck = x[1]['fields']['canCheck']
                        break

    buy_now = {"buyNow": False, "buyParam": settlement,
               "spm": "a21202.12579950.settlement-bar.0"}
    return flag, canCheck, json.dumps(buy_now)


# punish_url = 'https://h5api.m.taobao.com:443//h5/mtop.trade.order.build.h5/4.0/_____tmd_____/punish?x5secdata=5e0c8e1365474455070961b803bd560607b52cabf5960afff39b64ce58073f781bfb15e0f149ea97f57ae941e5007f71e00224e112fff7e0d9d151f880c6122aeb2bc16b1dbc91ea592f0222d32ec23f1976b91a091e5174a4153ee53f360b269783bbae415916f4e376d892cf8ccf5dfbfc572b0e4d94492bf2c09f80dc487327cae2b41822c1ba4a1874ce5949dc8cd67793aece688dba185bf8f92e389a27f81fff07998f8acfa877abb3f15d770daa6574f817e057f32f85e9086384ba384ff05e8880d08bb22a4955f34ba10716cd53a336f3444e515b0eaf868776b2368bb505aed8c8053301c2fdfd6ca072d78ee96f65385e9e8044603ac2da587c18a3b3e7b92e7a104a939356775160b15068c45899ff2343106c6c98685007b2048b06cf3207fb4622cadb23ac5d92e12dbfcc508cd27518b3557b9baec779a869b2c1397a425abb93dc6495a5ecbe704bef6a3cd44835da8eebba31e12701f0db320c17dc2b67e0ae13d3ede711bee620cee17e05e5c3b772c04cf90f894ea48083cab5c59b9014113fea064a853cf0cdb7e108b3d5af782ab33bb080840b54b4e4fdb669199653e9edf651264a0c972d3123cecd72a2c0fbe78d44e02dc747d4bfec2900ad20df5c2feda956ce3fbf30ae00e0af686564656d0ba1988f7909a75d9a678964b11679bf2531504047e854&x5step=2'
# options = webdriver.ChromeOptions()
# prefs = {"profile.managed_default_content_settings.images": 2}
# # options.add_argument('headless')
# # options.add_experimental_option("prefs", prefs)
# options.add_experimental_option('excludeSwitches', ['enable-automation'])
# browser = webdriver.Chrome(options=options)
# browser.get(punish_url)
# browser.execute_script("window.localStorage.setItem('_uab_collina','155935896307023857138966');")
# browser.execute_script("window.localStorage.setItem('_um_cn_umsvtn','TCE4883A61E74008B0B425307EC021C6A5427660787E2C4E9E1B454441F@@1560088278');")
# browser.execute_script("window.localStorage.setItem('_um_cn__umdata','G1AAFF6A38DFF674A937A686B3BF80664DA83A0');")
# browser.execute_script("window.localStorage.setItem('closeReturn','true');")
# browser.execute_script("window.localStorage.setItem('_umcost','1956');")
# browser.execute_script("window.localStorage.setItem('x5referer','https://main.m.taobao.com/order/index.html?buyNow=false&buyParam=589325148289_1_0_null_0_null_null_1298787624499_null_null_null_0_null_buyerCondition~0~~dpbUpgrade~null~~cartCreateTime~1559358443000_0_0_null_null_null_null_null_null_null_null_null,560663982182_1_4132339316807_null_0_null_null_1298071200825_null_null_null_0_null_buyerCondition~0~~dpbUpgrade~null~~cartCreateTime~1559325863000_0_0_null_null_null_null_null_null_null_null_null&spm=a21202.12579950.settlement-bar.0');")
# test = browser.execute_script("window.localStorage.getItem('x5referer');")
# browser.delete_all_cookies()
# cookie_json = {}
# for item in user_cookie.split(";"):
#     cookie_json[item.strip().split('=')[0]] = item.strip().split('=')[1]
#
# for item in cookie_json.items():
#     browser.add_cookie({'name': item[0], 'value': item[1]})
#
# browser.get(punish_url)
#
# print(browser.page_source)
# exit()

# def verify_action(punish_url):
# user_cookie = ''
# punish_url = "https://h5api.m.taobao.com:443//h5/mtop.trade.order.build.h5/4.0/_____tmd_____/punish?x5secdata=5e0c8e1365474455070961b803bd560607b52cabf5960afff39b64ce58073f781bfb15e0f149ea97f57ae941e5007f71e00224e112fff7e0d9d151f880c6122aeb2bc16b1dbc91ea592f0222d32ec23f1976b91a091e5174a4153ee53f360b269783bbae415916f4e376d892cf8ccf5de774c279781f0a38323d598028a5b64fbdd5c67c684bed5a02cc040080d6031a857e1e610dacc61de563a6b9aa773596f81fff07998f8acfa877abb3f15d770daa6574f817e057f32f85e9086384ba384ff05e8880d08bb22a4955f34ba10716cd53a336f3444e515b0eaf868776b2368bb505aed8c8053301c2fdfd6ca072d78ee96f65385e9e8044603ac2da587c18a3b3e7b92e7a104a939356775160b15068c45899ff2343106c6c98685007b2048b06cf3207fb4622cadb23ac5d92e12dbfcc508cd27518b3557b9baec779a869b2c1397a425abb93dc6495a5ecbe704bef6a3cd44835da8eebba31e12701f0db320c17dc2b67e0ae13d3ede711bee620cee17e05e5c3b772c04cf90f894ea48083cab5c59b9014113fea064a853cf0cdb7e108b3d5af782ab33bb080840b54b4e4fdb669199653e9edf651264a0c972d3123cecd72a2c0fbe78d44e02dc747d4bfec2900ad20df5c2feda956ce3fbf30ddefec7c193422c34f45883fab1d21575d9a678964b11679bf2531504047e854&x5step=2"
#
# verify_options = webdriver.ChromeOptions()
# verify_options.add_argument('--disable-extensions')
# verify_options.add_argument("--no-sandbox")
# verify_options.add_experimental_option('excludeSwitches', ['enable-automation'])
# verify_options.add_experimental_option('w3c', False)
# verify_browser = webdriver.Chrome(options=verify_options)
# verify_browser.get('https://login.taobao.com/member/login.jhtml')
#
# for item_cookie in user_cookie.split(';'):
#     item = item_cookie.split('=')
#     if len(item) == 2:
#         verify_browser.add_cookie({'name': item[0], 'value': item[1]})
#
# verify_browser.get(punish_url)
#
# exit()

# time.sleep(30)

#
# flag = True
#
# headers = {
#     "authority": 'h5api.m.taobao.com',
#     "upgrade-insecure-requests": '1',
#     "User-Agent": User_Agent,
#     "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
#     "accept-encoding": 'gzip, deflate, br',
#     "accept-language": 'zh-CN,zh;q=0.9',
#     "cookie": user_cookie,
# }
# html = requests.get(punish_url, headers=headers)
# soup = BeautifulSoup(html, 'html.parser')
# verify_data = {}
# for item in soup.form.children:
#     if not isinstance(item, Tag):
#         continue
#     if item.get('name') not in verify_data:
#         verify_data[item.get('name')] = item.get('value')
#
# params = {
#     'a': verify_data.get('nc_app_key'),
#     't': verify_data.get('nc_token'),
#     'n': '',
#     'p': '',
#     'scene': 'register',
#     'asyn': '0',
#     'lang': 'cn',
#     'v': '996',
#     'callback': '',
# }
# headers = {
#     "User-Agent": User_Agent,
# }
# analyze_url = 'https://cfall.aliyun.com/nocaptcha/analyze.jsonp?' + parse.urlencode(params)
#
# analyze = requests.get(analyze_url, headers=headers).json()
# verify_data['nc_session_id'] = analyze.get('result').get('csessionid')
# verify_data['nc_sig'] = analyze.get('result').get('value')
#
# headers = {
#     "authority": 'h5api.m.taobao.com',
#     "upgrade-insecure-requests": '1',
#     "User-Agent": User_Agent,
#     "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
#     "accept-encoding": 'gzip, deflate, br',
#     "accept-language": 'zh-CN,zh;q=0.9',
#     "cookie": user_cookie,
# }
# verify_url = soup.form.attrs.get('action') + '?' + parse.urlencode(verify_data)
# verify_response = requests.get(verify_url, headers=headers)
# print(verify_response.headers)
# print(verify_response.text)
# return flag


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
    print(json_data.text)
    json_data = json_data.json()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print("%s order.create %s " % (now, json_data.get('ret')))
    if "SUCCESS" in json_data.get('ret')[0]:
        flag = True
    else:
        fail_sys_sleep(json_data)
    return flag, json_data


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
    print(url, headers, buy_now)
    data = requests_session.post(url, headers=headers, data={'data': buyNow})
    print(data.text)
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


def fail_sys_sleep(data):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    if len(data.get('ret')) == 1:
        if "FAIL_SYS_TOKEN_EXOIRED" in data.get('ret')[0]:
            print("%s cookie timeout" % (now))
            exit()

        if "FAIL_SYS_TRAFFIC_LIMIT" in data.get('ret')[0]:
            print("%s need sleep", now)

        if "P-01415-14-15-004" in data.get('ret')[0]:
            time.sleep(2)
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


while True:
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    if now < times:
        print("%s waiting" % (now))
        time.sleep(0.1)

    buy_now = ''
    buy_cart_flag = False
    buy_cart_limit = 0
    while not buy_cart_flag:
        buy_cart_flag, canCheck, buy_now = get_buy_cart(good_id)
        if not buy_cart_flag:
            if buy_cart_limit >= 3:
                buy_cart_limit = 0
                time.sleep(5)
            else:
                time.sleep(2)
        buy_cart_limit += 1

    build_data = {}
    build_order_flag = False
    build_order_limit = 0
    while not build_order_flag:
        build_order_flag, build_data = build_order(buy_now)
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
                time.sleep(3)
            else:
                time.sleep(0.2)
        create_order_limit += 1

    if create_order_flag:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        print("%s Congratulations!" % now)

    pay_url = "https:" + create_order_data.get('data').get('nextUrl')
    flag = alipay(pay_url)
    break
