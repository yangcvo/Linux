---
title: yum一键安装与卸载LAMP环境
date: 2014-12-07 18:43:45
tags:
- LAMP
- Linux note
categories: Linux
---

### CentOS 可以通过 yum 安装:

```bash
yum -y install httpd php php-mysql  mysql-server
```

启动服务

```bash
service httpd status|start|stop|restart|reload
service mysqld status|start|stop|restart|reload
```

yum一键安装默认目录：

```bash
网站根目录 /var/www/html/


Apache主目录 /etc/httpd/
Apache主配置文件 /etc/httpd/conf/httpd.conf
Apache日志 /etc/httpd/logs/


PHP主目录 /etc/php.d/
PHP配置文件 /etc/php.ini
PHP模块位置 /usr/lib/php/ 或者 /usr/lib64/php/


MySQL配置文件 /etc/my.cnf


MySQL数据库文件 /var/lib/mysql/
运行 mysql_secure_installation 设置mysql根用户密码
```


由于目前使用的是lamp环境，目前为实验需要想把apache更换为litespeed web服务器。因为之前是通过yum安装的。

卸载前：

```bash
rpm -qa|grep http

rpm -qa|grep php

rpm -qa|grep mysql
```

查看目前安装的包后，通过

```bash
yum remove mysql-*
yum remove php-*
yum remove httpd
```
卸载安装的包。

