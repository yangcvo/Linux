---
title: DNS服务器主从复制搭建
date: 2016-01-28 11:33:07
tags:
- DNS
categories: Linux
---

## DNS 服务器主从复制搭建

最近部署测试环境和灰度发布环境，之前已经整改过一次，因为需要扩容添加，所以这次操作就把实现的过程记录下来了。 

### 实现环境：

centos 6.7 x86_64

* 主DNS服务器：192.168.1.173
* 从DNS服务器：192.168.1.174


### 实验步骤

1、关闭网络防火墙及SElinux（主从DNS服务器上都要有此操作）

``` bash 
[root@LAN_redis2 ~]# /etc/init.d/iptables stop
[root@LAN_redis2 ~]# /etc/init.d/iptables status
iptables: Firewall is not running.
```
（注意：此步骤不容忽略，否则会吃大亏，比如我在此就耗费大半天的时间）

``` bash 
[root@LAN_redis2 ~]# setenforce 0
[root@LAN_redis2 ~]# getenforce 
Permissive（或是disable也可以）
```
### 主DNS服务器的安装及配置

2、 安装DNS服务器

``` bash
[root@LAN_redis1 ~]# yum install bind bind-libs bind-utils -y
[root@LAN_redis1 ~]# yum list all | grep ^bind
bind.x86_64                                 32:9.8.2-0.47.rc1.el6       @base
bind-libs.x86_64                            32:9.8.2-0.47.rc1.el6       @base
bind-utils.x86_64                           32:9.8.2-0.47.rc1.el6       @base
bind-chroot.x86_64                          32:9.8.2-0.47.rc1.el6       base
bind-devel.i686                             32:9.8.2-0.47.rc1.el6       base
bind-devel.x86_64                           32:9.8.2-0.47.rc1.el6       base
bind-dyndb-ldap.x86_64                      2.3-8.el6                   base
bind-libs.i686                              32:9.8.2-0.47.rc1.el6       base
bind-sdb.x86_64                             32:9.8.2-0.47.rc1.el6       base
```
3、修改配置文件/etc/named.conf

``` bash
[root@LAN_redis1 ~]# cp /etc/named.conf /etc/named.conf.bak (备份原始配置文件)
[root@LAN_redis1 ~]# vim /etc/named.conf
```
对主配置文件进行编辑修改，也可以自己编写,这里是我设置的 

``` bash
options {
        listen-on port 53 { any; };
        listen-on-v6 port 53 { ::1; };
        directory       "/var/named";
        dump-file       "/var/named/data/cache_dump.db";
        statistics-file "/var/named/data/named_stats.txt";
        memstatistics-file "/var/named/data/named_mem_stats.txt";
        allow-query     { any; };
        recursion yes;

//      dnssec-enable yes;
//      dnssec-validation yes;

        /* Path to ISC DLV key */
        pid-file "/var/run/named/named.pid";

//      bindkeys-file "/etc/named.iscdlv.key";

//      managed-keys-directory "/var/named/dynamic";
};

logging {
        channel default_debug {
                file "data/named.run";
                severity dynamic;
        };
};

zone "." IN {
        type hint;
        file "named.ca";
};

include "/etc/named.rfc1912.zones";
#include "/etc/named.root.key";

```
![](http://7xrthw.com1.z0.glb.clouddn.com/dns-name.conf.png)


#### named.conf文件说明：

``` bash
上面的named.conf文件包括三部分：key,controls,logging，options,zone。



在options中：
directory    "/var/named"    :定义bind的工作目录为/var/named，配置文件中所有使用的相对路径，指的都是在这里配置的目录下。  
pid-file "/var/run/named/named.pid";   把bind程序运行的pid写入文件named.pid
transfer-format many-answers:使用更加有效的域传输格式many-answers。
allow-query { any; }:允许所有用户查询dns


logging:设置日志服务器和日志信息的发送地。
options:控制服务器的全局配置选项和为其它语句设置默认值
zone:定义一个域,比如正解析域和反解析域。
logging是定义日志的，不需要深究，主要是options和zone。


在zone中：
这里定义了两个zone，一个是正解析zone qbtop.com，一个是反解析zone 81.19.23.in-addr.arpa。
他们的参数基本相同：
type master:定义dns服务器为主dns。
file "qbtop.com.zone":定义此zone的文件名。
allow-transfer { 23.19.81.194; }:允许向从dns 23.19.81.194传输dns数据。
唯一不同的是zone名称的定义，正解析zone名称的定义是受权的域名，可以是顶级域名，也可以是二级域名，或多级。反解析zone名称定义规定前部分ip倒着写。如ip 192.168.1.2,名称定义为1.168.192.in-addr.arpa。

正解析qbtop.com.zone
```
### 编辑头文件配置
``` bash
[root@LAN_redis1 etc]# vim named.rfc1912.zones
```
``` bash
zone "1.0.0.127.in-addr.arpa" IN {
        type master;
        file "named.loopback";
        allow-update { none; };
};

zone "0.in-addr.arpa" IN {
        type master;
        file "named.empty";
        allow-update { none; };
};

zone "prod.intranet" IN {
        type master;
        file "prod.intranet.zone";
         allow-transfer { 192.168.1.174; };
};

zone "1.168.192.in-addr.arpa" IN {
        type master;
        file "192.168.1.zone";
        allow-transfer { 192.168.1.174; };
};
```

4、新建正反向解析文件并修改权限及属组

``` bash
[root@LAN_redis1 named]# vim prod.intranet.zone   (正向解析配置文件)
```

``` bssh
$TTL    1200
@               IN      SOA     ns1.prod.intranet.      admin.prod.intranet.   (  //设置SOA标记、域名、域管理邮箱
                                                        2015120101             //更新序列号，用于标记地址数据库的变化 
                                                        1H                //刷新时间，从域名服务器更新该地址数据库文件的间隔时间
                                                        10M              //重试延时，从域名服务器更新地址数据库失败以后，等待多长时间再次尝试  
                                                        7D              //失效时间，超过该时间仍无法更新地址数据库，则不再尝试
                                                        1D            //设置无效地址解析记录（该数据库中不存在的地址）的默认缓存时间
)
                  IN     NS      ns1.prod.intranet.
                  IN     NS      ns2.prod.intranet.
                  IN     MX  10  mail.prod.intranet.
ns1.prod.intranet.       IN      A       192.168.1.173
ns2.prod.intranet.       IN      A       192.168.1.174
mysql.prod.intranet.     IN      A       192.168.1.171
mysql-2.prod.intranet.   IN      A       192.168.1.170
sentinel.prod.intranet.  IN      A       192.168.1.175
redis1.prod.intranet.    IN      A       192.168.1.173
redis2.prod.intranet.    IN      A       192.168.1.174
```
![](http://7xrthw.com1.z0.glb.clouddn.com/dns-prod.test.zone.png)


### DNS正反解析：

* 正向解析就是将我们知道的域名解析成IP地址，而反向解析就是把正向解析掉了个方向，就是通过IP地址解析域名

* 反向域名解析与通常的正向域名解析相反，提供IP地址到域名的对应，反向域名格式如：X.X.X.in-addr.arpa。目前很多网络服务提供商要求访问的IP地址具有反向域名解析的结果，否则不提供服务。

> 通俗易懂的讲：
> 
> 正向解析：通过域名查找ip；
> 
> 反向解析：通过ip查找域名；


```bash 
vim /var/named/192.168.1.zone     (逆向解析配置文件)
```

``` bash

$TTL    1200
@               IN      SOA     ns1.prod.intranet.      admin.prod.intranet.   (
                                                        2015120101
                                                        1H
                                                        10M
                                                        7D
                                                        1D
)
                  IN     NS      ns1.prod.intranet.
                  IN     NS      ns2.prod.intranet.
                  IN     MX  10  mail.prod.intranet.
173       IN    PTR       ns1.prod.intranet.
174       IN    PTR       ns2.prod.intranet.
170       IN    PTR       mysql.prod.intranet.
171       IN    PTR       mysql-2.prod.intranet.
172       IN    PTR       sentinel.prod.intranet.
173       IN    PTR       redis1.prod.intranet.
174       IN    PTR       redis2.prod.intranet.
175       IN    PTR       tomcatA1.prod.intranet.
176       IN    PTR       tomcatB1.prod.intranet.
```

修改文件的属主属组和访问权限

``` bash

[root@LAN_redis1 named]# chgrp -v named prod.intranet.zone
"prod.intranet.zone" 的所属组已更改为named
[root@LAN_redis1 named]# chgrp -v named 192.168.1.zone
"192.168.1.zone" 的所属组已更改为named

[root@LAN_redis1 named]# chmod  o=  192.168.1.zone
[root@LAN_redis1 named]# chmod  o=  prod.intranet.zone
[root@LAN_redis1 named]# ll prod.intranet.zone 192.168.1.zone
-rw-r-----. 1 root named 1700 6月  30 16:25 192.168.1.zone
-rw-r-----. 1 root named 1922 6月  30 16:26 prod.intranet.zone
```
5、检查主配置文件和区域配置文件语法是否有错误

``` bash
[root@LAN_redis1 ~]# named-checkconf /etc/named.conf
[root@LAN_redis1 ~]# named-checkzone "prod.intranet" /var/named/prod.intranet.zone
[root@LAN_redis1 ~]#  named-checkzone "1.168.192.in-addr.arpa" /var/named/192.168.1.zone
ok
```
6、启动named的服务和进程：

刚刚开始弄启动失败了。
启动失败：

``` bash
[root@LAN_redis1 ~]# service named start
启动 named：                                               [失败]

然后定位查看原因：
[root@LAN_redis1 ~]# tail /var/log/messages
Jun 30 17:03:18 LAN_redis1 named[17582]: corporation.  Support and training for BIND 9 are
Jun 30 17:03:18 LAN_redis1 named[17582]: available at https://www.isc.org/support
Jun 30 17:03:18 LAN_redis1 named[17582]: ----------------------------------------------------
Jun 30 17:03:18 LAN_redis1 named[17582]: adjusted limit on open files from 65535 to 1048576
Jun 30 17:03:18 LAN_redis1 named[17582]: found 2 CPUs, using 2 worker threads
Jun 30 17:03:18 LAN_redis1 named[17582]: using up to 4096 sockets
Jun 30 17:03:18 LAN_redis1 named[17582]: loading configuration from '/etc/named.conf'
Jun 30 17:03:18 LAN_redis1 named[17582]: none:0: open: /etc/named.conf: permission denied
Jun 30 17:03:18 LAN_redis1 named[17582]: loading configuration: permission denied
Jun 30 17:03:18 LAN_redis1 named[17582]: exiting (due to fatal error)


日志上面说没有权限访问 '/etc/named.conf'

查看下
[root@LAN_redis1 ~]# ll /etc/named*
-rwxr-x--x. 1 root root  1019 6月  30 14:36 /etc/named.conf
-rw-r-----. 1 root named  984 11月 20 2015 /etc/named.conf.bak
-rw-r-----. 1 root root  1019 6月  30 16:38 /etc/named.conf.bak.2016
-rw-r--r--. 1 root named 2389 5月  11 07:07 /etc/named.iscdlv.key
-rw-r-----. 1 root named 1171 6月  30 15:28 /etc/named.rfc1912.zones
-rw-r--r--. 1 root named  487 7月  19 2010 /etc/named.root.key

然后修改属性和权限
[root@LAN_redis1 ~]# chown -R root:named /etc/named
[root@LAN_redis1 ~]# service named start
启动 named：                                               [确定]

就可以了。
```

### 二、在上述前提下搭建备用从DNS服务器

> 在另一台服务器上安装bind，安装方法和上述一致
> 
> 编辑主配置文件/etc/named.conf，和上述一致
>
>  编辑主配置文件中定义的头文件/etc/named.rfc1912.zones 
> 
> 

``` bash
zone "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.ip6.arpa" IN {
        type master;
        file "named.loopback";
        allow-update { none; };
};

zone "1.0.0.127.in-addr.arpa" IN {
        type master;
        file "named.loopback";
        allow-update { none; };
};

zone "0.in-addr.arpa" IN {
        type slave;
        file "named.empty";
        allow-update { none; };
};
zone "prod.intranet" IN {
        type slave;
        file "slaves/prod.intranet.zone";       // 正向解析，定义服务器类型，主服务器地址以及正向解析的配置文件名
        masters { 192.168.1.173; };
};

zone "1.168.192.in-addr.arpa" IN {
        type slave;
        file "slaves/192.168.1.zone";
        masters { 192.168.1.173; };  // 逆向解析
};

```
> 注意：不需要配置指定文件salaves/prod.intranet.zone和slaves/192.168.1.zone,因为这是一个从服务器，所以它的所有条目都是同步主服务器里面的。从服务器的条目存放文件存放在slaves目录的是一种安全机制。
> 
> 
测试主配置文件和区域配置文件：

``` bash
[root@LAN_redis2 slaves]# named-checkconf /etc/named.conf
```
### 启动从DNS服务器上的named服务

``` bash
[root@LAN_redis2 slaves]# service named start
启动 named：                                               [确定]
[root@LAN_redis2 slaves]#  chkconfig named on  （将named服务设为开机自启动）
[root@LAN_redis2 ~]# chkconfig --list named
named          	0:关闭	1:关闭	2:启用	3:启用 4:启用 5:启用 6:关闭
[root@LAN_redis2 ~]# cd /var/named/slaves/
[root@LAN_redis2 slaves]# ll
总用量 8
-rw-r--r--. 1 named named 1105 6月  30 17:46 192.168.1.zone
-rw-r--r--. 1 named named  947 6月  30 17:46 prod.intranet.zone
```
### 查看同步结果

``` bash
[root@LAN_redis2 slaves]# cat 192.168.1.zone
$ORIGIN .
$TTL 1200	; 20 minutes
1.168.192.in-addr.arpa	IN SOA	ns1.prod.intranet. admin.prod.intranet. (
				2016030101 ; serial
				3600       ; refresh (1 hour)
				600        ; retry (10 minutes)
				604800     ; expire (1 week)
				86400      ; minimum (1 day)
				)
			NS	ns1.prod.intranet.
			NS	ns2.prod.intranet.
$ORIGIN 1.168.192.in-addr.arpa.
170			PTR	mysql.prod.intranet.
171			PTR	mysql-2.prod.intranet.
172			PTR	sentinel.prod.intranet.
173			PTR	ns1.prod.intranet.
			PTR	redis1.prod.intranet.
174			PTR	ns2.prod.intranet.
			PTR	redis2.prod.intranet.

root@LAN_redis2 slaves]# cat prod.intranet.zone
$ORIGIN .
$TTL 1200	; 20 minutes
prod.intranet		IN SOA	ns1.prod.intranet. admin.prod.intranet. (
				2016030101 ; serial
				3600       ; refresh (1 hour)
				600        ; retry (10 minutes)
				604800     ; expire (1 week)
				86400      ; minimum (1 day)
				)
			NS	ns1.prod.intranet.
			NS	ns2.prod.intranet.
$ORIGIN prod.intranet.
10001			A	192.168.1.181
10002			A	192.168.1.181
10003			A	192.168.1.181
10004			A	192.168.1.181
10005			A	192.168.1.181
10006			A	192.168.1.181
10007			A	192.168.1.181
10008			A	192.168.1.181
10009			A	192.168.1.181
10010			A	192.168.1.181
10011			A	192.168.1.181
```

此时，看的以上两个文件已经自动从主服务器上同步到从服务器上，表明实验成功。

以后每次，主服务器上更新正反向解析文件的话，从服务器上的解析文件会自动与之同步。
可以看到，在主服务器更新的数据、序列号，在从服务器上都自动更新过来了，表明验证成功。


### 其他服务器测试：

我先到D1：192.168.1.178

添加新的DNS：

```bash
[root@tomcat_D1 ~]# vim  /etc/resolv.conf

#namserver 233.5.5.5  注释掉阿里云的DNS 
nameserver 192.168.1.173
nameserver 192.168.1.174
```
保存退出，测试是否可以ping外网是否可以解析设置好的内网域名。

``` bash
[root@tomcat_D1 ~]# ping www.baidu.com
ping: unknown host www.baidu.com

[root@tomcat_D1 ~]# ping 10002.prod.intranet.
ping: unknown host 10002.prod.intranet.
```

>都是提示这个错误。
>
>无法解析，后面我看我做的负载均衡反向代理域名都正常的。
>
>后来定位是什么原因导致的，可是DNS上面主从正常的。
>
>回到主从：

``` bash
[root@LAN_redis1 named]# nslookup 10001.prod.intranet
Server:		127.0.0.1
Address:	127.0.0.1#53

Name:	10001.prod.intranet
Address: 192.168.1.181

[root@LAN_redis1 named]#
[root@LAN_redis1 named]# nslookup 10002.prod.intranet
Server:		127.0.0.1
Address:	127.0.0.1#53

Name:	10002.prod.intranet
Address: 192.168.1.181

[root@LAN_redis2 slaves]# nslookup 192.168.1.175
Server:		127.0.0.1
Address:	127.0.0.1#53

175.1.168.192.in-addr.arpa	name = tomcatA1.prod.intranet.

```
>这里解析正常的，很奇怪。
>逆解析也正常。

### 问题解决：
后来我看了很久，发现原来是我DNS 防火墙开启了，可是没有把DNS 端口53没有开放。

``` bash
-A INPUT -p tcp -m state --state NEW -m tcp --dport 53 -j ACCEPT
-A INPUT -p udp -m state --state NEW -m udp --dport 53 -j ACCEPT
```

添加了防火墙规则已经可以了。

```
[root@tomcat_D1 ~]# ping 10001.prod.intranet.
PING 10001.prod.intranet (192.168.1.181) 56(84) bytes of data.
64 bytes from 10003.prod.intranet (192.168.1.181): icmp_seq=1 ttl=64 time=0.843 ms
```



