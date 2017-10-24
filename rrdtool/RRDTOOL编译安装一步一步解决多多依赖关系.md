---
title: rrdtool 编译安装一步一步解决多多依赖关系
date: 2014-11-24 18:13:30
tags:
- Linux note
categories: Linux
---


## RRDTOOL 编译安装一步一步解决多多依赖关系


在一些监控软件中需要借助rrdtool绘图，然后安装rrdtool这个画图工具的时候经常报错，下面就简单说明下安装步骤（Cenetos6.5 64bit）。 

#### 介绍

RRDTOOL 是一个基于时间片的日志和绘图工具，有了她你可以轻松的绘制各种基于时间的可视化数据，用于做统计和监控非常合适。著名的开源监控软件Ganglia 就是采用的RRDTOOL。
为什么要特别提到RRDTOOL的安装，因为我在安装RRDTOOL的过程中遇到了各种问题和困难。先说明一下我安装的环境是

CentOS5.7。
先说一下教训，尽量使用root权限或者具有sudo权限的账号安装RRDTOOL。

笔者一开始尝试着在一台不具备root权限的机器上安装，首先遇到的问题就是系统无法正确的识别到共享包，需要设置PKG_CONFIG_PATH和LD_LIBRARAY_PATH但是这还没有完，最后libX11-devel的安装彻底让我灰心，其依赖然我彻底失去了信心。但也许有更好的在非root权限账号安装的办法，希望大家分享;-)

#### 安装步骤：

>下载软件包：

去http://oss.oetiker.ch/rrdtool/pub/?M=D 下载最新的RRD版本，并且在http://oss.oetiker.ch/rrdtool/pub/libs/ 下载相应的依赖包，也许是作者本身意识到其依赖之多，所以在其下载站就提供了对应依赖的下载。这里如果失效的话，网页访问不了，下面我会把该对应的依赖包做成链接让大家下载。不需要再次去寻找依赖包。 =_=
我在这次安装中用到的包如下：   （全部都是最新版的  安装就不会报错，如果是低版本的 我安装都会报错，那时候低版本报错安装 安装了一4个小时。因为很多依赖包安装报错，很多依赖包中又要安装其他包。）
下面一次成功的 最新安装包：

* pkgconfig-0.18.tar.gz 
* zlib-1.2.8.tar.gz
* libpng-1.6.18.tar.gz
* freetype-2.6.tar.gz
* libxml2-2.6.3.tar.gz
* fontconfig-2.10.1.tar.gz
*  pixman-0.32.6.tar.gz
* cairo-1.14.2.tar.gz
*  glib-2.28.6.tar.bz2
* pango-1.30.1.tar.xz 
* rrdtool-1.4.7.tar.gz


这里我安装的目录统一 `/usr/local/rrdtool`   
操作系统：` Cenetos  6.5 `
因为直接安装rrdtool 会提示依赖错误。然后我们按提示依赖，都安装上，就可以了。

##### 这里我先安装

（1）

```bash
* pkg-config-0.18.tar.gz 
* 现在版本更新到0.18 最新版本了，我在这里用最新版本安装。
* # wget http://pkgconfig.freedesktop.org/releases/pkgconfig-0.18.tar.gz
* # tar zxvf pkgconfig-0.18.tar.gz
* # cd pkgconfig-0.18
* # ./configure --prefix=/usr/local/rrdtool/pkgconfig
* # make && make install  
* cd ..    
```

（2）

```bash
* 安装zlib-1.2.8.tar.gz
* # wget http://www.zlib.net/zlib-1.2.8.tar.gz
* #cd zlib-1.2.8
* # tar zxvf zlib-1.2.8.tar.gz  
* # ./configure -prefix=/usr/local/rrdtool/zlib 
* # make && make install 
* cd .. 
```

( 3 )
  
```bash
* 安装libpng-1.6.18.tar.gz
* wget ftp://ftp.simplesystems.org/pub/libpng/png/src/libpng16/libpng-1.6.18.tar.gz
* # cd libpng-1.6.18
*  # ./configure --prefix=/usr/local/rrdtool/libpng 
* # make && make install
* cd ..
```bash

( 4 )

```bash
* 安装freetype-2.6.tar.gz
*  # wget http://download.savannah.gnu.org/releases/freetype/freetype-2.6.tar.gz
* # tar zxvf freetype-2.6.tar.gz 
* # cd freetype-2.6
* 这里会提示有两个包不存在。 yum  安装下 就行。没安装也没事情。 bzip2:         no
* # make && make install 
```

( 5 )

```bash
* 安装libxml2-2.6.3.tar.gz
* # tar zxvf libxml2-2.6.3.tar.gz
* # cd libxml2-2.6.3
* # ./configure --prefix=/usr/local/rrdtool/libxml2 
* # make && make install
```

( 6 )

```bash
    * 安装fontconfig-2.10.1.tar.gz
* # wget http://www.freedesktop.org/software/fontconfig/release/fontconfig-2.11.94.tar.gz
* # tar zxvf fontconfig-2.11.94.tar.gz
*  # cd fontconfig-2.11.94
* # ./configure --prefix=/usr/local/rrdtool/fontconfig --with-freetype-config=/usr/local/rrdtool/freetype/bin/freetype-config --with-expat-lib=/usr/lib64/
* make && make install 
```

( 7 )

```bash
*  安装最新版本 pixman-0.32.6.tar.gz
* # tar zxvf pixman-0.32.6.tar.gz 
* # ./configure --prefix=/usr/local/rrdtool/pixman
* # make && make install 
```

( 8 )

```bash
* 安装最新版本cairo-1.14.2.tar.xz
*
# wget http://www.cairographics.org/releases/cairo-1.14.2.tar.xz  
*
# tar xvf cairo-1.14.2.tar.xz
# cd cairo-1.14.2
# ./configure --prefix=/usr/local/rrdtool/cairo --enable-xlib=no --enable-xlib-render=no --enable-win32=no
# make && make install 
```

( 9 )

```bash
* 安装最新版glib-2.34.2.tar.xz 
* # tar jxvf glib-2.34.2.tar.xz 
* # cd glib-2.34.2
* # ./configure --prefix=/usr/local/rrdtool/glib
* 
* 这里 我安装了 libffi   
* wget sourceware.org:/pub/libffi/libffi-3.2.1.tar.gzfi  
* tar zxvf libffi-3.2.1.tar.gz
* # ./configure --prefix=/usr/local/rrdtool/libffi
* make && make install 
* cd..
* cd  glib-2.34.2
*  export  PKG_CONFIG_PATH=/usr/local/rrdtool/libffi/lib/pkgconfig/
* ./configure --prefix=/usr/local/rrdtool/glib  --with-libffi-config=/usr/local/rrdtool/libffi/
* make && make install 
```

 ( 10 )
 
```bash
* 安装最新版 pango-1.30.1.tar.xz
* # tar xvf pango-1.30.1.tar.xz 
* # cd pango-1.30.1
* ./configure --prefix=/usr/local/rrdtool/pango 
* make && make install
( 11) 这里把下载好的rrdtool 安装上就不会报错了。 
* # tar zxvf rrdtool-1.4.5.tar.gz
* # cd rrdtool-1.4.5
* # ./configure --prefix=/usr/local/rrdtool/rrdtoll 
* # make && make install
* 安装到这里已经全部安装成功了。 
```

安装到这里就基本上完成了，主要是依赖太多，已写成脚本，需要的留言或者微博上发信息给我都可以。



    









