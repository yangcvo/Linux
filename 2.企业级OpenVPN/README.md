##Pritunl企业级版本OpenVPN搭建部署

## 系统功能概述

OpenVPN是Linux下的一款开源VPN，提供了良好的性能和友好的用户GUI，
目前OpenVPN能在 Solaris、Linux、OpenBSD、FreeBSD、NetBSD、Mac OS X与Microsoft Windows以及Android和iOS上运行，并包含了许多安全性的功能。

## 部署环境

| 主机   |   角色   |   操作系统 |   软件版本  |    备注  |
| ------ | ----- | ----- | ------- | ------ |
| hz01-prod-ops-openvpn(172.16.2.96)  | server  |  Centos 7.3(x86-64)|  pritunl-1.24.1025.78-1.el7.centos.x86_64 + openvpn-2.4.3-1.el7.x86_64 + mongodb-server-2.6.12-4.el7.x86_64 |  主节点|

## 安装

- 安装epel仓库，有的话直接跳过

```
# wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
# rpm -ivh epel-release-latest-7.noarch.rpm
```

- 建立pritunl仓库文件(私有仓库已经有了,可跳过) 

```
# cat /etc/yum.repos.d/pritunl.repo
[pritunl]
name=Pritunl Repository
baseurl=https://repo.pritunl.com/stable/yum/centos/7/
gpgcheck=0
enabled=1
```

- 安装pritunl

```
# yum install pritunl mongodb-server
# systemctl start mongod pritunl
# systemctl enable mongod pritunl
```

- 获取setup key

```
# pritunl setup-key
f40fd5c985aa4806847525d8bba8727f
```

> 将key输入对话框

![](https://github.com/yangcvo/Linux/blob/master/2.企业级OpenVPN/15300102876978.jpg)

> 将key输入到web界面的图中,保存继续,会出现登录界面,默认登录用户名和密码都是 pritunl/pritunl

![](https://github.com/yangcvo/Linux/blob/master/2.企业级OpenVPN/15300103448209.jpg)

> 登录后，如下页面自行设置新的用户/密码(公网IP为vpn自己识别到的IP)

![](https://github.com/yangcvo/Linux/blob/master/2.企业级OpenVPN/15300104758732.jpg)

> 添加组织

![](https://github.com/yangcvo/Linux/blob/master/2.企业级OpenVPN/15300107035239.jpg)


> 添加用户,将用户关联到组织,设置用户密码(Pin就是后面客户端连接时的密码，Name就是用户名) 

![](https://github.com/yangcvo/Linux/blob/master/2.企业级OpenVPN/15300109030250.jpg)


> 添加服务


![image](https://github.com/jinyuchen724/linux-base/raw/master/7.openvpn/vpn6.png)

> 配置servers dns及端口

![](https://github.com/yangcvo/Linux/blob/master/2.企业级OpenVPN/15300111916134.jpg)

> 将服务与组织关联 

![](https://github.com/yangcvo/Linux/blob/master/2.企业级OpenVPN/15300112494267.jpg)

![](https://github.com/yangcvo/Linux/blob/master/2.企业级OpenVPN/15300095932941.jpg)

> 开启服务

![](https://github.com/yangcvo/Linux/blob/master/2.企业级OpenVPN/15300112869837.jpg)


> 查看服务启动状态和公网路由端口映射。

![](https://github.com/yangcvo/Linux/blob/master/2.企业级OpenVPN/15300655409059.jpg)

![](https://github.com/yangcvo/Linux/blob/master/2.企业级OpenVPN/15300645262321.jpg)



## 系统管理

> 基本的概念是组织 --> 用户 --> server 

![image](https://github.com/jinyuchen724/linux-base/raw/master/7.openvpn/vpn10.png)

上图是后台vpn server 状态图 


## 安装openvpn客户端

- 下载用户配置文件(.ovpn文件)

![image](https://github.com/jinyuchen724/linux-base/raw/master/7.openvpn/vpn11.png)

### Two-Step Authentication Key

![](https://github.com/yangcvo/Linux/blob/master/2.企业级OpenVPN/15300114385944.jpg)

![](https://github.com/yangcvo/Linux/blob/master/2.企业级OpenVPN/15300114706850.jpg)

![](https://github.com/yangcvo/Linux/blob/master/2.企业级OpenVPN/15300117055016.jpg)


- linux客户端

> 安装openvpn客户端

```
# yum install openvpn
```

> 设置配置文件(将管理员提供的用户配置文件导入)

```
# cat /etc/2.企业级OpenVPN/client.conf
  #{
  # "sync_secret": "XfefBn17cDzosXmsM6m5GehT1K9MtasU",
  # "organization_id": "59b7826c35ef2311e76401aa",
  # "user": "ops",
  # "organization": "\u8fd0\u7ef4\u90e8",
  # "sync_hash": "bd03539789340051ab1261085c19380d",
  # "server_id": "59b783e435ef2311e7640688",
  # "user_id": "59b7827035ef2311e76401c3",
  # "server": "\u8fd0\u7ef4\u90e8",
  # "version": 1,
  # "sync_hosts": [
  #  "https://101.68.67.180"
  # ],
  # "sync_token": "OHSWaoLWxzG2NgC3OTnuEy427E3VMauD",
  # "password_mode": "pin"
  #}
  setenv UV_ID 8a3bab99b6d54b0aa70f26969c5aba99
  setenv UV_NAME summer-forest-3987
  client
  dev tun
  dev-type tun
  remote 101.68.67.180 11081 tcp-client
  nobind
  persist-tun
  cipher AES-256-CBC
  auth SHA1
  verb 2
  mute 3
  push-peer-info
  ping 10
  ping-restart 60
  hand-window 70
  server-poll-timeout 4
  reneg-sec 2592000
  sndbuf 100000
  rcvbuf 100000
  remote-cert-tls server
  comp-lzo no
  auth-user-pass
  key-direction 1
  <ca>
  -----BEGIN CERTIFICATE-----
  MIIFcTCCA1mgAwIBAgIIbqeMCl/8D2swDQYJKoZIhvcNAQELBQAwRjEhMB8GA1UE
  CgwYNTliNzgyNmMzNWVmMjMxMWU3NjQwMWFhMSEwHwYDVQQDDBg1OWI3ODI2YzM1
  ZWYyMzExZTc2NDAxYjkwHhcNMTcwOTEyMDY0NTA0WhcNMjcwOTEyMDY0NTA0WjBG
  MSEwHwYDVQQKDBg1OWI3ODI2YzM1ZWYyMzExZTc2NDAxYWExITAfBgNVBAMMGDU5
  Yjc4MjZjMzVlZjIzMTFlNzY0MDFiOTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCC
  AgoCggIBAL5xU3qSfJrb857nZzdCATHTvZ3H2UpISS352Rol6DhnpfE+Q7q5Dt64
  vBEd3+saxNWGWjTpfCXy+1jQJbt0mUDrjv3IzyrI/IR3/uJSRs0ZXvYiZrsCDRCN
  iU1ysgt7wzYkT0KPnq8om1veS5F1m5+wcxmNjvFlNXrYoWhOExDkVZHcjxKHi2QB
  4LVuHK+vMEY6pgfhp4BjCi3LiApP2VzEDHsdD5pT15/g0hLHxs3rI5PxhpE+pOnk
  xnvc+A/y0CFyK+RoJOQ8dtdXoL1/eo7Fx3/QzcFp4hcaqwGkm2Xqb39y0ZdJihYN
  ujq2PnJo5zgM3VwOTEBwg0u33enAuvWyTKYvyWD9nZOmSw0egVlG3SmLC+sHJpPM
  bmfaVzs5Sn57Ku+fnijHSX33d2GIbGX/zlm8ZazeFoS7xMsGbQnwXOtuelX09Icy
  alGnZCH/GcA+Pz6wfq5jwuecnFv1wmvuQ9ihu86s3/IGMSvDAyQmuAiwQMEOfATg
  WL4RkFSgY98FN0x7csYXDy9+DcIU2Lswgg9UrppDhjQHaG4hd4t2VFsc3IvyNZsA
  OsPAZZ+vgBLkC/WvynzbeV/6kWzw54P+gAV+Mp2SgIbXZS4GvZ8h/fm0GCuefgBF
  VhwqwGF8Q90i4WBlw4UiSuX2Bxi86Y1WyPFQzrIWagvlCvExvv4LAgMBAAGjYzBh
  MA4GA1UdDwEB/wQEAwIBBjAPBgNVHRMBAf8EBTADAQH/MB0GA1UdDgQWBBSJKHih
  afvbx9WBP1NMjj3Ug7EjaDAfBgNVHSMEGDAWgBSJKHihafvbx9WBP1NMjj3Ug7Ej
  aDANBgkqhkiG9w0BAQsFAAOCAgEAeOhB+BxUOkB9umLR7jOgr65vPhf0RVXPDf3b
  2F78LEFg9BAMFkAVNDat7oNx7IVVUC5LWnNMnnITN57g0W8auPGRupB9c5oe/44k
  WfEeoui/F1HZEJG6AfBHZ6ayvtFXtkkfZRHBlT4w1rFUi9Bnn6j01GeBd1kBdxgU
  1PkstLi2f1WsPgSVXJGlC3cFDrHRr9yt4gLzOD/DBUR12zy159tk96Zouj2JCbb5
  IayVKiloC1zkg50qOFTzfrpF1zFbeS3XBOzsHjsMv++4ThVdc/A/sQsctSj17GnA
  5xq3d4i72cxHdAvJxqgVvJZDD0y8zQF7QS2l2VSLYVVip4dkHgd6snsrh9640dil
  fxNWkqr7s8zn5USwRr3FUMetvRVuS6vFlmsUH4JWuWxz/n6gTYe89uw7aBNgbpte
  A4BAFly7mUBPUedaLkzwqH1BJIBZfsaGPfSPWZ+W3N3zMiskvyvnrcgxA3TVDISH
  O0Dli5kzwCmC5QqtK0eOUlMzjkitM9RoWdgKuSOEmFBefl95/k6/sNxJE6kvgC7J
  8dueKDF+2e9AdC2yLSjdpnjXEjoVvLrLB+XwwDbElmBGUrdRxGvHmRMdh/LXAC32
  GagXEr1oBxKki6wFFY+qDVVX7M2y31AOA4rYcdo6v68hg36CLHiOO+n2sW3limcZ
  ChCR7mM=
  -----END CERTIFICATE-----
  </ca>
  <tls-auth>
  #
  # 2048 bit OpenVPN static key
  #
  -----BEGIN OpenVPN Static key V1-----
  9401356ed42b3b023f2d2a4c261c4d77
  53d9a355b687ecb7ac89dc3bd0147101
  102620fdb007e32b841236a47d480b64
  365c4adf8627900a71978bd6629908a4
  99154242ce4b24bd3616bb9dc317b9c8
  ee597376ddbe098cd4392b441866a698
  adab95361700c9e885ce0effa20467cf
  469c6438ee9ed26bdf13df548e915366
  15630ba1b1a2d85ae8bf81e787c92caf
  fe1a1b0a65cc1b0eb34fee9fba582e12
  48a76c309e072962cf60ac3b6da00221
  30f25c207620092de3c8b35c384e58b8
  4f08a99b3bda7166d95eb67db05a9db6
  be5e7588b881bb219ac97de6b818a828
  280f50c062a824136bf2d533d6d8ea8b
  e98207c9daaf74ed19e9ff326da73fdc
  -----END OpenVPN Static key V1-----
  </tls-auth>
  <cert>
  -----BEGIN CERTIFICATE-----
  MIIFgTCCA2mgAwIBAgIJAPVpaeQQa/qQMA0GCSqGSIb3DQEBCwUAMEYxITAfBgNV
  BAoMGDU5Yjc4MjZjMzVlZjIzMTFlNzY0MDFhYTEhMB8GA1UEAwwYNTliNzgyNmMz
  NWVmMjMxMWU3NjQwMWI5MB4XDTE3MDkxMjA2NDUxNFoXDTI3MDkxMjA2NDUxNFow
  RjEhMB8GA1UECgwYNTliNzgyNmMzNWVmMjMxMWU3NjQwMWFhMSEwHwYDVQQDDBg1
  OWI3ODI3MDM1ZWYyMzExZTc2NDAxYzMwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAw
  ggIKAoICAQCYZJIDp41htt+Ydhb0FUuCZT052X8VJ3cqLx52SaxiI1VYymEcQw/z
  XT71GqlJNJmV89OsYSTI6wHnr4B2H527ZkGcKRx+VnSmF4X68ce3HKtW+KE276BG
  huBJ5VJM28DE/xNwzPPx8HPg6s6DdqGDVGri/GDo2XQu+BAR7esgk+6anSieh1Gc
  oGMEYANvyRO6b/9+Mz1jL7d5VjDbKNDbOAddYLbVydrrgO+WHWzgKglaD05y9GgQ
  ub8lLLNMAvxJLPlc6ZbF8mQj4Pvid0bDIi2nRTq70ohchxlBA+2PEnmqNTH+nkmg
  D9t9sy7ALeGhMdFB/nPo86/7Ou/24xnfUWyzxKOKqMoI5PP/l4p5XuviRWeWub9D
  W3pGX+bjXUTfJtePKk9/Tl/IajJufGTRwToCEA4bgbMAQqrQDEMOmlLM7fYvM1wz
  m8QmLL2aTk5gDctrydatGuJsfqylMwuvoRDDm3rL/1hfX4TyLc4u1LlwoswErZrK
  KFABfjNTaTK3pIBN2XcVFgW5R6ZSh3A/IfOEhcXdgPXzGhjk0pu6aasG+tyI9r5G
  DnKb7cAvowltfiX2Tv+wb11JJsjWPE9Osb5J7OcJoptHTcprGKDuCtwmx/dtnoKe
  8AfRV+H4/uWsD4OCWZFfGp+YxccIth9vrS2tJayL3+v8F1gqG65+wwIDAQABo3Iw
  cDAOBgNVHQ8BAf8EBAMCBaAwCQYDVR0TBAIwADATBgNVHSUEDDAKBggrBgEFBQcD
  AjAdBgNVHQ4EFgQUdjBHY8otuH7qLMSDuD34ZcgIFw0wHwYDVR0jBBgwFoAUiSh4
  oWn728fVgT9TTI491IOxI2gwDQYJKoZIhvcNAQELBQADggIBABYi0Bl7FWLxvKC8
  dwSz16NLUkowzTwM2oqT4NVVaVtSaUakIhpDcKIp0Kuwsz7AyaoBjbSof5TIX9Ve
  DKgut+N7voUEQ43N++d1/+ycSFaZ4pyX2ASZtHHOHDcQPY7R6G27BCv9xo4XB/46
  o9F6fyPaLhBiSRXrd40J2SlbtRSR0E/LHVpLQ7s27H6aZ6SZu7K0M3tyHPv7/LC+
  +LutYrI4FlseVyMxghdXttmUuc7SHpPxbykEu4/4UnrJ0AWgl2WO80Jqkb3+nnCZ
  03NXrhbAFFqUfOQaHaGwrtFYuMUVj7e7fn2C4uiOAQ5nqkGmFSfyJUFRAae6kBAe
  4OPJvFQKjzuvoAylCDlnig86OK/n2hFd6n7HuUVeRGRMgZeQCmBLEZJPFsHx/8Lk
  /t64iO3BiNXqjSxPuppKe30VGQzkD3pqteUCz9BVLMmZ9AjJhYKy1OQwJW+4C84W
  6m8PQGm+8SB0Oi2F1L5P8cdA9AVrmrdmreYHxcAk4HOiI40LZpu93gRR1J8/a3JG
  SKp77IloBcmbMexD2BYKfezxsn0YDOSaGZUdy2nzg3K1sxLTBUElyfLpoMhD97q6
  1hHSV8JxScUMw6LKli+XxIPSkspV6s/wdcKN60oxpupgkeLl+/pc0wNpZr7eRdfd
  cBtaQSUkxiK6XBITXwMIhkzC84v3
  -----END CERTIFICATE-----
  </cert>
  <key>
  -----BEGIN PRIVATE KEY-----
  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
  j+xYr/jDnX+aMy/HPgB6gKHmuorRY6c=
  -----END PRIVATE KEY-----
  </key>
```

> 启动openvpn客户端(需要输入密码)

 ```
 # systemctl enable openvpn@client.service
 # systemctl start openvpn@client.service
 ```

> 保存密码,自动启动配置(可以自启动，自动拨号连接) 

```
# cat /etc/2.企业级OpenVPN/client.conf 
auth-user-pass 
变更为
auth-user-pass /etc/2.企业级OpenVPN/pass.txt
```

- 将用户名和密码写入文件

```
# cat /etc/2.企业级OpenVPN/pass.txt
ops
123456
```

注意: 第一行是用户名 第二行是密码 


- windows客户端

> 安装openvpn包

https://github.com/jinyuchen724/linux-base/blob/master/7.openvpn/03-openvpn-install-2.3.10-I601-x86_64.exe

设置配置文件(保存密码,自动启动配置,与linux方式一致)将刚下载的用户配置文件内容放入openvpn安装目录下的config目录下(文件.ovpn后缀)

启动openvpn,连接即可(无需输入账号密码)

- mac客户端

> 安装Tunnelblick 

![image](https://github.com/jinyuchen724/linux-base/raw/master/7.openvpn/vpn12.png)

点击“我没有配置文件” 

![image](https://github.com/jinyuchen724/linux-base/raw/master/7.openvpn/vpn13.png)

点击"新建配置样本,并且进行编辑",关闭所有弹出的对话框。在桌面出现一个配置样例：

![image](https://github.com/jinyuchen724/linux-base/raw/master/7.openvpn/vpn14.png)

设置配置文件(保存密码,自动启动配置,与linux方式一致)将刚下载的用户配置文件内容放入openvpn安装目录下的config目录下(文件.ovpn后缀),

>第一次导入.ovpn后缀，会提示让你输入账号和密码：记得密码不要永久记录，因为需要Google二次认证的。
先输入密码+五位数随机的动态认证。

[Client configuration for PINs and two-step authentication](https://docs.pritunl.com/docs/two-step-authentication)
![](https://github.com/yangcvo/Linux/blob/master/2.企业级OpenVPN/15300656751587.jpg)

如果登录不上，那么删除原来的client.ovpn。
启动openvpn,连接即可。



