---
title: Centos7本地yum源搭建及实时同步
date: 2016-10-21 16:12:23
tags:
- Linux note
categories: Linux
---

### 搭建本地yum源


* YUM介绍

YUM主要用于自动升级、安装\移除rpm软件包，它能自动查找并解决rpm包之间的依赖关系，要成功的使用YUM工具更新系统和软件，需要有一个包含各种rpm软件包的repository（软件仓库），提供软件仓库的服务器习惯上成为“源”服务器。网络上有大量的源服务器，但是，由于受到网络连接速度、带宽的限制，导致软件安装耗时过长甚至失败。特别是当有大量服务器大量软件包需要升级时，更新的缓慢程序令人难以忍受。
相比较而言，本地YUM源服务器最大优点在局域网的快速网络连接和稳定性。

> 主要我们公司用到这点：

* 有了局域网中的YUM源服务器，即便在Internet连接中断的情况下，也不会影响其他YUM客户端的软件升级和安装。
* 为了减少公司内部大量vps使用外部yum源导致带宽不足情况，于是就搭建一台本地yum源服务器，通过脚本服务器定时去镜像站点更新yum数据。


1. 尽管有很多的免费镜像提供yum源服务，但是还是有必要建立自己的yum服务器，主要出于以下几点考虑：

   - l 网络速度：访问互联网可能比较慢
   - l 节省带宽：如果有大量的服务器，架设自己的yum源可以有效节省互联网带宽
   - l 联网限制：对于有些内网服务器，不能连接到互联网
   - l 对于RHEL(Redhat Enterprise Linux)，需要购买服务
   - l 便于发布自己开发的rpm包

2. 找到适合你的站点的yum同步源,主要是CentOS标准软件仓库、epel、以及rpmforge

　　CentOS标准仓库选择列表

```bash
　　Asian：
　　http://www.centos.org/modules/tinycontent/index.php?id=32

　　North American
　　http://www.centos.org/modules/tinycontent/index.php?id=30

　　Epel源选择列表
　　http://mirrors.fedoraproject.org/publiclist/EPEL/

　　Rpmforge源
　　http://apt.sw.be/

```
　　要选尽量离你的local服务器近的地区,并支持RSYNC,方便更新同步

　　我选择的是`Linux Kernel Archives`


```bash
　　CentOS标准软件仓库
　　rsync://mirrors.kernel.org/centos

　　Epel源
　　rsync://mirrors.kernel.org/fedora-epel

　　Rpmforge源
　　rsync://ftp-stud.fht-esslingen.de/dag
　　rsync://mirror.cpsc.ucalgary.ca/dag
```
　　

### 下面就介绍下 本地yum源的搭建。

一、启动 httpd 服务（一般httpd服务已经安装）可以参考我写的安装httpd：[CentOS安装httpd](http://blog.yangcvo.me/2014/12/07/Linux%E7%AC%94%E8%AE%B0/LAMP/yum%E4%B8%80%E9%94%AE%E5%AE%89%E8%A3%85%E4%B8%8E%E5%8D%B8%E8%BD%BDLAMP%E7%8E%AF%E5%A2%83/)

取一台 CentOS操作系统的机器作为源服务器。启动服务器的httpd 服务：

```bash
service httpd start
```

 
可查看配置文件: `/etc/httpd/conf/httpd.conf`  
了解httpd相关配置信息这里我们配置的文档根目录为：`/var/www/html/` 
端口: `Listen 80`

默认yum安装的目录就在/var/www/html

```bash
vim /etc/httpd/conf/httpd.conf
DocumentRoot "/var/www/html"
```
确认服务启动，浏览器访问： `http://localhost:80` 出现apache页面（如果从其他机器访问，请先关闭防火墙：service iptables stop ）

### 二、安装 createrepo 工具 （若使用 linux iso 镜像 则为非必须）

`createrepo`是linux下的创建仓库的软件包。

1、在机器联网的情况下可直接安装： `yum install createrepo `  
2、可使用`rpm -ivh createrepo-xxx.noarch.rpm `安装由网上下载的rpm包，一般会有两个依赖
3、linux常用工具rpm包，一般在镜像文件中都存在


## 三、安装 yum 源

#### 1、使用 Linux ISO 镜像中的RPM包安装

* （1）将 ISO 文件 copy 到服务器上，并在文件夹: `/var/www/html/`下创建文件夹 CentOS

* （2）将 ISO文件挂载至文件夹 `/var/www/html/CentOS`
 
执行： `mount -o loop /var/www/html/CentOS-6.7-x86_64-minimal.iso /var/www/html/CentOS`

```bash
[root@yum_01 html]# ll
总用量 404488
drwxr-xr-x 2 root root      4096 3月  14 16:33 CentOS
-rw-r--r-- 1 root root 414187520 3月  14 16:32 CentOS-7-x86_64-Minimal-1503-01.iso
[root@yum_01 html]# mount -o loop /var/www/html/CentOS-7-x86_64-Minimal-1503-01.iso /var/www/html/CentOS
mount: /dev/loop0 写保护，将以只读方式挂载
```

**(取消挂载 umount /var/www/html/CentOS)**

``` bash
[root@yum_01 html]# umount /var/www/html/CentOS
```

* （3）查看文件夹 /var/www/html/CentOS 

```bash
[root@yum_01 html]# cd CentOS
[root@yum_01 CentOS]# ll
-rw-r--r-- 1 root root    16 4月   1 2015 CentOS_BuildTag
drwxr-xr-x 3 root root  2048 3月  28 2015 EFI
-rw-r--r-- 1 root root   215 3月  28 2015 EULA
-rw-r--r-- 1 root root 18009 3月  28 2015 GPL
drwxr-xr-x 3 root root  2048 3月  28 2015 images
drwxr-xr-x 2 root root  2048 3月  28 2015 isolinux
drwxr-xr-x 2 root root  2048 3月  28 2015 LiveOS
drwxr-xr-x 2 root root 53248 4月   1 2015 Packages
drwxr-xr-x 2 root root  4096 4月   1 2015 repodata
-rw-r--r-- 1 root root  1690 3月  28 2015 RPM-GPG-KEY-CentOS-7
-rw-r--r-- 1 root root  1690 3月  28 2015 RPM-GPG-KEY-CentOS-Testing-7
-r--r--r-- 1 root root  2883 4月   1 2015 TRANS.TBL
```
可以看到 `repodata `文件夹的存在，`repodata`作为软件的仓库信息文件。 
ISO镜像 yum源搭建OK
浏览器访问：`http://localhost:80/CentOS/`

#### 2、使用 自己准备的 RPM 包 （这里以 apache ambari为例）

* （1）在目录 /var/www/html/ 下建立一个文件夹，把准备的 RPM包放到里面.
* （2）更新 yum源


   - yum clean  清除yum源缓存
   - yum repolist 列出可用yum源


```bash
[root@yum_01 yum.repos.d]# yum clean all  #清空软件仓库缓存
已加载插件：fastestmirror
正在清理软件源： base
Cleaning up everything
Cleaning up list of fastest mirrors
[root@yum_01 yum.repos.d]# yum repolist  
已加载插件：fastestmirror
base                                                                                                                                 | 3.6 kB  00:00:00
(1/2): base/group_gz                                                                                                                 | 1.4 kB  00:00:00
(2/2): base/primary_db                                                                                                               | 516 kB  00:00:00
Determining fastest mirrors
源标识                                                                      源名称                                                                      状态
base                                                                        CentOS                                                                      6776
repolist: 6776
```

（3）使用 （尝试安装postgresql）


```bash
# yum isntall -y postgresql
```


五、可能会出现的问题

1、问题

you don't have permission to access / on this server(Apache Server权限访问问题）

Apache Http Server已经在linux上安装完成，可是通过浏览器访问，却出现了“you don't have permission to access / on this server”.

解决：

```bash
在httpd.conf文件中，有这么一段

<Directory/> # 这里的目录为自己的目录

Options FollowSymLinks

AllowOverride None

Order deny,allow

Deny from all

</Directory>

可以尝试把Deny改成Allow，然后重启apache服务，访问页面，看问题是否解决。
```



2、问题：

    Loaded plugins: fastestmirror, refresh-packagekit, security

    Determining fastest mirrors

    http://10.1.33.21/ambari/repodata/repomd.xml: [Errno 14] PYCURL ERROR 22 - "The requested URL returned error: 403 Forbidden"

    Trying other mirror.

    Error: Cannot retrieve repository metadata (repomd.xml) for repository: ambari-1.x. Please verify its path and try again

    解决：

    yum源服务器运行如下命令

    setenforce 0               # 暂时禁用SELinux服务



3、问题：

```
yum install xxx.rpm

warning：

Package xxx.rpm is not signed

解决：

只要在在后面加上--nogpgcheck就可以了，格式如下

yum install *rpm --nogpgcheck
```


