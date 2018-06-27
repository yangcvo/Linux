---
title: DNS服务器主从复制搭建
date: 2015-12-29 11:33:07
tags:
- DNS
categories: Linux
---

#### 一 、什么是DNS污染 
 
 就是客户端发起正常的一次DNS请求，得到的确是一个异常或者不真实的DNS信息。一般造成这样的情况，很有可能DNS信息在某个环节被通过某种方式篡改。   
 
 
 
####  二、有什么手段可以造成DNS污染
 
 主要的方式，可以归纳为如下两种： 
 
 

方式一、攻击者监测到DNS查询的请求报文时，伪装成DNS服务器向发出请求主机发送响应报文。因为DNS报文通常是无连接的UDP报文，没有确认机制，源主机不能识别出这个报文并非出自DNS服务器。攻击者并不需要丢弃真正DNS服务器发回来的响应报文，因为DNS的机制会导致源主机只接受最先到达的响应报文（甚至不管是谁发的）而忽略后继到达的其他报文。这样，源主机得到的就是攻击者伪造的域名解析结果。

条件：1、攻击者能截获客户的数据包。2、能最短时间接替返回消息

方式二、本地DNS服务器的缓存已受到污染，里面缓存的是错误的结果。DNS服务器通常将DNS查询的结果缓存在本地一段时间，这本意是为了减少重复DNS查询，从而降低DNS报文占用的网络带宽。可如果某次DNS查询的结果受到污染，则后继一段时间内向该DNS服务器查询的结果都会受到污染。

条件：1、本地DNS存在攻击漏洞 2、本地DNS成为被污染的对象


#### 三、如何测试DNS信息受到污染

 我们可以拿访问google 、facebook来演示：

```bash
root@imoocc.com:/opt# nslookup  www.google.com 8.8.8.8  #使用NDS8.8.8.8 解析 www.google.com

Server:8.8.8.8

Address:8.8.8.8#53

 

Non-authoritative answer:

Name:www.google.com

Address: 37.61.54.158

 

root@imoocc.com:/opt# nslookup -vc www.google.com 8.8.8.8   #同样，不过改使用TCP的方式解析

Server:8.8.8.8

Address:8.8.8.8#53

 

Non-authoritative answer:

Name:www.google.com

Address: 216.58.221.228

＃我们再同样查查脸书

root@imoocc.com:/opt# nslookup  www.facebook.com 8.8.8.8

Server:8.8.8.8

Address:8.8.8.8#53

 

Non-authoritative answer:

Name:www.facebook.com

Address: 37.61.54.158    #发现什么了？DNS受到了污染。

```

我们仔细来查查这个什么玩意地址37.61.54.158
![](http://oak0aohum.bkt.clouddn.com/DNS-test.png)



 下面是一个正常的Google地址返回，因该如下：

![](http://oak0aohum.bkt.clouddn.com/DNS-test2.png)






 


