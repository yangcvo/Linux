---
title: LAMP一键安装包-Centos5/6下自动编译安装
date: 2014-12-07 18:43:45
tags:
- Linux note
categories: Linux
---

# LAMP一键安装包-CentOS 5/6下自动编译安装Apache,MySQL,PHP，phpmyadmin

适用环境：

系统支持：CentOS-5 (32bit/64bit)、CentOS-6 (32bit/64bit) 内存要求：≥256M

安装了什么:

```bash
1、Apache 2.2.22或Apache 2.4.2

2、MySQL 5.5.24

3、PHP 5.2.17或PHP 5.3.13

4、phpmyadmin 3.5.1

5、ZendOptimizer 3.3.9(可选，只适合PHP 5.2.17)

6、xcache 1.3.2(可选)

7、pure-ftpd-1.0.36（可选）
```

如何安装:


```bash
wget http://centos.googlecode.com/files/lamp0.4.tar.gz
tar xf lamp0.4.tar.gz && cd lamp0.4 && chmod +x lamp.sh && ./lamp.sh

如果下载失败可以试试这个：http://oak0aohum.bkt.clouddn.com/lamp0.4.tar.gz
```

安装其它


```bash
1、执行脚本pureftpd.sh安装pure-ftpd。

2、执行脚本zend.sh安装ZendOptimizer。

3、执行脚本xcache.sh安装xcache。 使用提示： LAMP脚本使用
```

```bash
lamp add(del,list)：创建（删除，列出）虚拟主机。
lamp ftp(add|del|list)：创建（删除，列出）ftp用户。
lamp uninstall：一键卸载lamp（卸载之前注意备份好数据！）。
```
程序目录


```bash
mysql目录:   /usr/local/mysql
mysql data目录：/usr/local/mysql/data
php目录:     /usr/local/php
apache目录： /usr/local/apache
```
进程管理


```bash
apache启动（停止｜重启｜重载配置文件）:service httpd start(stop|restart|reload)
mysql（停止｜重启｜重载配置文件）:service mysqld start(stop|restart|reload)
pureftpd（停止｜重启｜重载配置文件）:service pure-ftpd start(stop|restart|reload)
```

配置文件路径

```bash
apache:/etc/httpd/conf mysql:/etc/my.cnf php:/etc/php.ini /etc/php.d pure-ftpd:/etc/pure-ftpd.conf
```
####使用注意

1、mysql root密码存放在/root/my.cnf文件中，添加虚拟主机的时候需要调用。如果修改了root密码，请手动更新my.cnf文件。 更新记录

```bash
2012年6月17日：发布lamp0.4

1、增加自定义mysql data目录功能。

2、openvz的vps自动关闭innodb。

3、采用多核编译软件，提升编译速度。

4、增加自定义网站目录功能。 2012年5月29日：发布lamp0.3

1、使用pure-ftpd代替vsftpd 2012年5月23日：发布lamp0.2

1、增加apache-2.4.2安装 2、增加ssl模块 3、增加mpm选择 2012年2月14日：发布lamp0.1
```


