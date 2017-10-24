---
title: wkhtmltox源码安装实现HTML页面转成pdf效果
date: 2014-06-24 14:32:56
tags:
- Linux note
- wkhtmltox
---


wkhtmltopdf是一个将html页面转成pdf的工具。

wkhtmltox项目主页：http://wkhtmltopdf.org/  `支持html转pdf、image`



这段时间公司涉及到将html转成pdf/jpg的相关功能，我查了很多资料，网上大能找到的方法主要有以下两种：


## 系统环境：

系统最好CentOS release 6.5

网上google wkhtmltopdf发现，wkhtmltopdf官网的主机已经迁移到：[wkhtmltopdf官网](http://wkhtmltopdf.org/downloads.html)


`Ubuntu`的源无法更新。`wkhtmltopdf`有编译好的Linux版本，这里我把链接共享出来：
[wkhtmltopdf源码](http://wkhtmltopdf.org/downloads.html)中对应的版本，查看打包文件的URL，下载编译好的版本：这里下载源码包最好源码安装，所以直接用编译好的源码就没有报错了。 一开始发现编译安装很多报错，可能需要安装很多依赖,也用RPM安装过，也出现很多问题。好多坑


[官网下载](http://download.gna.org/wkhtmltopdf/obsolete/linux/) 这里官网下载的是外国链接下载会很慢，可以用下面直接服务器wget下载下来。

[百度云](http://pan.baidu.com/s/1pJl6jtL)  #这个是我下载好的可以直接在我百度云下载。也是在官网下载的。

运行命令：


```bash
wget http://download.gna.org/wkhtmltopdf/obsolete/linux/wkhtmltopdf-0.10.0_rc2-static-amd64.tar.bz2  -C  /opt/app/
```

然后解压缩下载到的文件：

```bash
tar jxvf wkhtmltopdf-0.10.0_rc2-static-amd64.tar.bz2
```

进行安装,安装完成后将可执行文件复制到 usr/bin 中

```bash
cp /opt/app/wkhtmltopdf-amd64 /usr/bin/wkhtmltopdf-amd64
```
或者做个软链接：

```bash
ln -s  /opt/app/wkhtmltopdf-amd64 /usr/bin/wkhtmltopdf-amd64
```

更改所有者为root用户,并增加可执行属性

```bash
sudo chown root:root /usr/bin/wkhtmltopdf-amd64
sudo chmod +x /usr/bin/wkhtmltopdf-amd64
```

测试一下，打印一个网页到你自己的指定目录/opt/：

```bash
wkhtmltopdf-amd64 www.qq.com /opt/app/qq.pdf
```

![](http://7xrthw.com1.z0.glb.clouddn.com/wkhtmltox.png)


如果显示成功输出了pdf 那么 wkhtmltopdf 就告安装完成。
安装OpenERP8.0 之后，使用打印功能，提示没有wkhtmltopdf，只能以html预览。

在`Ubuntu 12.04`安装wkhtmltopdf

```bash
sudo apt-get install wkhtmltopdf
```

提示OpenERP需要至少wkhtmltopdf 0.12.0，检查安装的wkhtmltopdf的版本

```bash
wkhtmltopdf -V
```




### 参考链接：


wkhtmltopdf官网: [wkhtmltopdf官网下载包](http://wkhtmltopdf.org/downloads.html)

wkhtmltopdf源码包：  [wkhtmltopdf源码下载](http://download.gna.org/wkhtmltopdf/obsolete/linux/)

mac配置wkhtmltopdf：[mac配置wkhtmltopdf](http://www.cnblogs.com/timelyxyz/archive/2012/12/24/2831523.html)

php-wkhtmltox-Github:[php-wkhtmltox](https://github.com/mreiferson/php-wkhtmltox)

