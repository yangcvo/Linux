---
title: centos6和centos7细节变化和配置
date: 2016-07-24 15:20:18
tags:
- - Linux note 
categories: Linux
---


### (1)桌面系统

```bash
[CentOS6] GNOME 2.x
[CentOS7] GNOME 3.x（GNOME Shell）
```

### (2)文件系统

```bash
[CentOS6] ext4
[CentOS7] xfs
```

### (3)内核版本

```bash
[CentOS6] 2.6.x-x
[CentOS7] 3.10.x-x
```


### (4)默认数据库

```bash
[CentOS6] MySQL
[CentOS7] MariaDB
```

### (5)文件结构

```bash
[CentOS6] /bin, /sbin, /lib, and /lib64在/下
[CentOS7] /bin, /sbin, /lib, and /lib64移到/usr下
```

### (6)主机名

```bash
[CentOS6] /etc/sysconfig/network
[CentOS7] /etc/hostname
```
### (7)时间同步

```bash
[CentOS6]
$ ntp
$ ntpq -p

[CentOS7]
$ chrony
$ chronyc sources
```
### (8)修改时间

```bash
[CentOS6]
$ vim /etc/sysconfig/clock
   ZONE="Asia/Tokyo"
   UTC=fales
$ sudo ln -s /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

[CentOS7]
$ timedatectl set-timezone Asia/Tokyo
$ timedatectl status
```

###(9)修改地区

```bash
[CentOS6]
$ vim /etc/sysconfig/i18n
   LANG="ja_JP.utf8"
$ /etc/sysconfig/i18n
$ locale

[CentOS7]
$ localectl set-locale LANG=ja_JP.utf8
$ localectl status
```

### centos7 修改主机名

例如，要永久修改主机名，你可以修改静态主机名：

```bash
$ sudo hostnamectl --static set-hostname <host-name>
要同时修改所有三个主机名：静态、瞬态和灵活主机名：
$ sudo hostnamectl set-hostname <host-name>
```

注意，你不必重启机器以激活永久主机名修改。上面的命令会立即修改内核主机名。注销并重新登入后在命令行提示来观察新的静态主机名。

### Centos7故障

### `Centos7最小化服务器版本使用“ifconfig”命令提示没有`

查看网卡细节，输入以下命令：

- ip addr
找不到ifconfig，net-tools包提供了ifconfig命令。因此，让我们安装net-tools包来使用ifconfig命令。

- yum install net-tools
就可以实现了。

如果安装还是找不到的话 修复下：

```bash
修改vim /etc/profile
在最后面一行添加这一条命令 export PATH=/sbin:$PATH
修改用户主目录下面隐藏文件.bashrc
修改只对该用户有效
查看用户下面的隐藏的文件 修改.bashrc 修改以后 保存注销登陆。
用echo $PATH 查看
export PATH=/sbin:$PATH修改生效了。
```

### `CentOS7默认的防火墙不是iptables,而是firewalle.找不到iptables config文件`

CentOS 7.0默认使用的是firewall作为防火墙，这里改为iptables防火墙。
firewall：

```
systemctl start firewalld.service#启动firewall
systemctl stop firewalld.service#停止firewall
```
安装iptable iptable-service

```bash
#先检查是否安装了iptables service iptables status 
#安装iptables yum install -y iptables 
#升级iptables yum update iptables
#安装iptables-services yum install iptables-services
```
设置现有规则：

```
#查看iptables现有规则
iptables -L -n
#先允许所有,不然有可能会杯具
iptables -P INPUT ACCEPT
#清空所有默认规则
iptables -F
#清空所有自定义规则
iptables -X
#所有计数器归0
iptables -Z
#允许来自于lo接口的数据包(本地访问)
iptables -A INPUT -i lo -j ACCEPT
#开放22端口
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
#开放21端口(FTP)
iptables -A INPUT -p tcp --dport 21 -j ACCEPT
#开放80端口(HTTP)
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
#开放443端口(HTTPS)
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
#允许ping
iptables -A INPUT -p icmp --icmp-type 8 -j ACCEPT
#允许接受本机请求之后的返回数据 RELATED,是为FTP设置的
iptables -A INPUT -m state --state  RELATED,ESTABLISHED -j ACCEPT
#其他入站一律丢弃
iptables -P INPUT DROP
#所有出站一律绿灯
iptables -P OUTPUT ACCEPT
#所有转发一律丢弃
iptables -P FORWARD DROP

```

其他规则：

```bash
#如果要添加内网ip信任（接受其所有TCP请求） iptables -A INPUT -p tcp -s 45.96.174.68 -j ACCEPT 
#过滤所有非以上规则的请求 iptables -P INPUT DROP 
#要封停一个IP，使用下面这条命令： iptables -I INPUT -s ***.***.***.*** -j DROP 
#要解封一个IP，使用下面这条命令: iptables -D INPUT -s ***.***.***.*** -j DROP
```
保存规则设定

```bash
#保存上述规则
service iptables save
```
centos设置iptables配置规则脚本：

```
#!/bin/sh iptables -P INPUT ACCEPT 
iptables -F 
iptables -X 
iptables -Z 
iptables -A 
INPUT -i lo -j ACCEPT 
iptables -A INPUT -p tcp --dport 22 -j ACCEPT 
iptables -A INPUT -p tcp --dport 21 -j ACCEPT 
iptables -A INPUT -p tcp --dport 80 -j ACCEPT 
iptables -A INPUT -p tcp --dport 443 -j ACCEPT 
iptables -A INPUT -p icmp --icmp-type 8 -j ACCEPT 
iptables -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT iptables -P INPUT DROP iptables -P OUTPUT ACCEPT 
iptables -P FORWARD DROP service iptables save systemctl restart iptables.service
```

### `解决Centos7.1各种yum报错Error这里我更换源`


第一种方法：
执行yum list就开始报错：

1.`Error: Cannot retrieve metalink for repository: epel. Please verify its path and try again`

在网上查了查，解决办法是编辑`/etc/yum.repos.d/epel.repo`，把基础的恢复，镜像的地址注释掉

```
#baseurl
mirrorlist
```
改成

```
baseurl
#mirrorlist
```


这里如果还是不行，可以使用我这里贴出的源码文件。

```bash
# CentOS-Base.repo
#
# The mirror system uses the connecting IP address of the client and the
# update status of each mirror to pick mirrors that are updated to and
# geographically close to the client.  You should use this for CentOS updates
# unless you are manually picking other mirrors.
#
# If the mirrorlist= does not work for you, as a fall back you can try the
# remarked out baseurl= line instead.
#
#

[base]
name=CentOS-$releasever - Base - mirrors.aliyun.com
failovermethod=priority
baseurl=http://mirrors.aliyun.com/centos/$releasever/os/$basearch/
        http://mirrors.aliyuncs.com/centos/$releasever/os/$basearch/
#mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=os
gpgcheck=1
gpgkey=http://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-7

#released updates
[updates]
name=CentOS-$releasever - Updates - mirrors.aliyun.com
failovermethod=priority
baseurl=http://mirrors.aliyun.com/centos/$releasever/updates/$basearch/
        http://mirrors.aliyuncs.com/centos/$releasever/updates/$basearch/
#mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=updates
gpgcheck=1
gpgkey=http://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-7

#additional packages that may be useful
[extras]
name=CentOS-$releasever - Extras - mirrors.aliyun.com
failovermethod=priority
baseurl=http://mirrors.aliyun.com/centos/$releasever/extras/$basearch/
        http://mirrors.aliyuncs.com/centos/$releasever/extras/$basearch/
#mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=extras
gpgcheck=1
gpgkey=http://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-7

#additional packages that extend functionality of existing packages
[centosplus]
name=CentOS-$releasever - Plus - mirrors.aliyun.com
failovermethod=priority
baseurl=http://mirrors.aliyun.com/centos/$releasever/centosplus/$basearch/
        http://mirrors.aliyuncs.com/centos/$releasever/centosplus/$basearch/
#mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=centosplus
gpgcheck=1
enabled=0
gpgkey=http://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-7

#contrib - packages by Centos Users
[contrib]
name=CentOS-$releasever - Contrib - mirrors.aliyun.com
failovermethod=priority
baseurl=http://mirrors.aliyun.com/centos/$releasever/contrib/$basearch/
        http://mirrors.aliyuncs.com/centos/$releasever/contrib/$basearch/
#mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=contrib
gpgcheck=1
enabled=0
gpgkey=http://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-7
```

第二套yum源文件：

```bash
[base]
name=CentOS-$releasever - Base
mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=os&infra=$infra
#baseurl=http://mirror.centos.org/centos/$releasever/os/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7

#released updates 
[updates]
name=CentOS-$releasever - Updates
mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=updates&infra=$infra
#baseurl=http://mirror.centos.org/centos/$releasever/updates/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7

#additional packages that may be useful
[extras]
name=CentOS-$releasever - Extras
mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=extras&infra=$infra
#baseurl=http://mirror.centos.org/centos/$releasever/extras/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7

#additional packages that extend functionality of existing packages
[centosplus]
name=CentOS-$releasever - Plus
mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=centosplus&infra=$infra
#baseurl=http://mirror.centos.org/centos/$releasever/centosplus/$basearch/
gpgcheck=1
enabled=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
```
这里我弄成文件了，直接导入试试下就可以了。

下载：

[CentOS-Base.repo1](http://oak0aohum.bkt.clouddn.com/CentOS-Base.repo)

[CentOS-Base.repo2](http://oak0aohum.bkt.clouddn.com/Centos7-CentOS-Base.repo)

