---
title: Linux实用的一些命令
date: 2014-07-21 16:12:23
tags:
- Linux note
categories: Linux
---

#学习Linux 实用命令


最近把之前学的慢慢整理出来，很多都是很实用的，而且一时想不起来的，就记录在这里了，不需要去查询资料，这样可以方便下次复习把不经常用的在看一遍。



### 1. linux 下不解压查看tar.gz包中的文件列表

``` bash
第一种方法：gunzip <a.tar.gz |tar tvf -
第二种方法：gzip  -dc a.tar.gz | tar tvf -
```


###2. cp/rm/mv等命令强制覆盖无需输入yes实现方法

在linux中使用cp/rm/mv命令覆盖文件操作时总是提示输入yes或no，很是麻烦，一两个的也就算了，没什么，但有时会遇到大量文件的复制时，就麻烦了

一、使用unalias cp命令 解除对cp的别名（仅本次终端连接会话临时取消），我们先输入alias命令，查看系统内部已经设置的别名

```bash
[root@localhost ~]# alias   
alias cp='cp -i'  
alias l.='ls -d .* --color=tty'  
alias ll='ls -l --color=tty'  
alias ls='ls --color=tty'  
alias mv='mv -i'  
alias rm='rm -i'  
alias which='alias | /usr/bin/which --tty-only --read-alias --show-dot --show-tilde' 
```
输入unalias cp命令，取消cp命令的别名

```bash
[root@localhost ~]# unalias cp   
[root@localhost ~]# cp filename new/filename 
```
使用unalias cp命令后，即可使用cp filename new/filename就不会提示输入yes或no了，是不是很方便

二、直接输入\cp命令，作用也是取消cp的别名

```bash
[root@localhost ~]# \cp filename new/filename   
[root@localhost ~]# 
```
是不是比上一个方法更省事
三、使用管道的方式，自动输入yes

```bash
[root@localhost ~]# yes | cp filename new/filename   
cp: overwrite `new/filename'? [root@localhost ~]#
自己替我们输入了yes
```

### 3. Linux服务器查看网络丢包 命令：`mtr`
这个之前在学习中有搞过网络方面，一个非常实用的命令就记录下来。`mtr`

```bash
mtr -n -c 20 -r -i 0.5 公网IP地址
```

```bash
[root@LAN_tomcat_A1 ~]# mtr -n -c 20 -r -i 0.5 115.239.210.27
HOST: LAN_tomcat_A1               Loss%   Snt   Last   Avg  Best  Wrst StDev
  1. 202.107.202.82                0.0%    20    0.3   0.3   0.2   0.4   0.0
  2. 202.107.202.81                0.0%    20   25.0  23.3   3.5 104.8  31.2
  3. 61.164.7.120                 45.0%    20    4.4  10.5   4.2  35.4  10.4
  4. 61.164.31.218                 0.0%    20    6.6   6.0   2.9  18.7   3.7
  5. ???                          100.0    20    0.0   0.0   0.0   0.0   0.0
  6. 115.239.209.30                0.0%    20    4.9   4.9   3.9   5.6   0.3
  7. ???                          100.0    20    0.0   0.0   0.0   0.0   0.0
  8. ???                          100.0    20    0.0   0.0   0.0   0.0   0.0
  9. 115.239.210.27                0.0%    20    4.8   4.4   3.3   5.0   0.5
```
这里我也对mtr详细讲解下：
其中-c的说明是：–report-cycles COUNT

```bash
第三列:是显示的每个对应IP的丢包率
第四列:显示的最近一次的返回时延
第五列:是平均值 这个应该是发送ping包的平均时延
第六列:是最好或者说时延最短的
第七列:是最差或者说时延最常的
第八列:是标准偏差
接下来接着说相关参数：

mtr -s 用来指定ping数据包的大小
mtr -n no-dns不对IP地址做域名解析
mtr -a 来设置发送数据包的IP地址 这个对一个主机由多个IP地址是有用的
mtr -i 使用这个参数来设置ICMP返回之间的要求默认是1秒
mtr -4 IPv4
mtr -6 IPv6
mtr -h 提供帮助命令
mtr -v 显示mtr的版本信息
mtr -r 已报告模式显示
```


### 4. 查看文件是否有被修改过 命令：`stat`

```bash
[root@update]# stat system.sh
  File: "system.sh"
  Size: 2739           	Blocks: 8          IO Block: 4096   普通文件
Device: fc02h/64514d   	Inode: 524302      Links: 1
Access: (0755/-rwxr-xr-x)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2016-08-10 17:23:44.946958555 +0800
Modify: 2016-05-25 16:58:32.624000645 +0800
Change: 2016-05-25 16:58:32.624000645 +0800
```

### 5.文件锁定root权限也不能删除文件 命令：`chattr`

```bash
chattr  lsattr
+a  只能追加内容
+i  不能被修改

chattr +i a.txt 

rm -rf a.txt
-bash: a.txt: 权限不够

lsattr 命令是查看赋予了什么文件属性。
----ia-------e- ./system.sh
```


