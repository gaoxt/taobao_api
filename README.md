# description
淘宝抢购脚本仅供交流学习使用

登陆逻辑使用了selenium，刷新购物车和下单调用了手机淘宝taobao_api，自动付款也使用了selenium，能自动模拟触摸输入密码付款，接口签名sign生成方法参考get_sign_val。


| 作用       | 主要的接口地址(https://h5api.m.taobao.com/h5/) |
| ---------- | ---------------------------------------------- |
| 购物车列表 | mtop.trade.query.bag/5.0/?                     |
| 订单确认页 | mtop.trade.order.build.h5/4.0/?                |
| 创建订单页 | mtop.trade.order.create.h5/4.0/?               |


```c
├── taobao.py         #第一版，通过selenium扫码下单，兼容性强。 
├── taobao_web.py     #第二版，通过selenium扫码，调用接口下单。
└── taobao_api.py     #第三版，增加调启支付宝支付、二维码下载到本地服务器扫码。
```

# using
```c
python3 taobao_api.py 2019-11-05 10:00:00 good_id password user_cookie
```


## 同步阿里云时间服务器
0.1秒的重要性。
```c
#一次性设置
sudo sntp -sS ntp.aliyun.com
#永久设置
sudo systemsetup -setnetworktimeserver ntp.aliyun.com
sudo systemsetup -setusingnetworktime on
```



# 一些坑
 * 尝试过阿里、腾讯的ECS，好像被taobao通过whois信息给识别了，看来只能本地跑了。
 * 签名算法好像时不时会变，果然个人的力量没有团队的力量强。