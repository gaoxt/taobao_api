# !/usr/bin/env python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import datetime
import time


def buy(times):
    flag = True

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    if 'cart' in browser.current_url:
        browser.refresh()
        print('%s refresh' % now)
    else:
        browser.get("https://cart.taobao.com/cart.htm")
        print('%s reload' % now)
    if now > times:
        browser.find_element_by_id("J_SelectAll1").click()
        j_go = browser.find_element_by_id("J_Go")
        while True:
            if 'submit-btn-disabled' not in j_go.get_attribute('class'):
                j_go.click()
                break
            print('%s j_go' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))

        try:
            WebDriverWait(browser, 2, 0.1).until(EC.element_to_be_clickable((By.LINK_TEXT, "提交订单"))).click()
            now1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            print('%s 抢购成功' % now1)
            flag = False
        except Exception as e:
            print("%s 重新下单" % now)

    return flag


def login():
    # 打开淘宝登录页，并进行扫码登录
    browser.get("https://www.taobao.com")
    time.sleep(1)
    if browser.find_element_by_link_text("亲，请登录"):
        browser.find_element_by_link_text("亲，请登录").click()
        print(browser.find_element_by_id("J_QRCodeImg").text)
        print("请在15秒内完成扫码")
        time.sleep(5)
    time.sleep(1)
    now = datetime.datetime.now()
    print('%s login success' % now.strftime('%Y-%m-%d %H:%M:%S'))


if __name__ == "__main__":

    # times = '2019-06-01 10:00:00.000000'
    times = '2019-06-02 10:00:00.000000'
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    browser = webdriver.Chrome()
    browser.maximize_window()


    login()
    flag = True
    while True:
        if flag == False:
            break
        flag = buy(times)
        time.sleep(0.01)
