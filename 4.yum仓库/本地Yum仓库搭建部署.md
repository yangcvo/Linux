---
title: Centos6.7 本地Yum仓库搭建部署
date: 2016-03-21 16:12:23
tags:
- Linux note
categories: Linux
---

#### 本地Yum仓库搭建部署

搭建私有 yum 仓库
服务端配置
系统：Centos6.7
去阿里镜像下载Centos6的yum源，安装系统eple-release源：

```bash
# 1. 去阿里镜像下载Centos6的yum源，安装系统eple-release源
wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-6.repo
yum install epel-release -y

# 2. 创建 yum 仓库目录，rpm 包都上至此目录 也可以参考第4.5.6步：
mkdir -p /data/yum_repo/rhel6_64/Packages/ 

# 3. 安装nginx服务和createrepo 创建yum仓库的命令：    
yum install createrepo  nginx -y

# 4. 创建cdrom挂在点：
mkdir /mnt/cdrom

# 5. 从本地把iso上传到服务端 将光盘CD挂载在到/mnt/cdrom/目录下 需要时也可以加上参数iso9660：
mount -t iso9660 -o  loop CentOS-6.7-x86_64-minimal.iso /mnt/cdrom/

# 6. copy iso中的rpm包到刚创建好的本地yum仓库目录： 
cp /mnt/cdrom/Packages/* /data/yum_repo/rhel6_64/Packages/

# 7. 将rpm包做成yum仓库的软件包：

createrepo /data/yum_repo/rhel6_64/

[root@yancy rhel6_64]# createrepo /data/yum_repo/rhel6_64/Packages/
Spawning worker 0 with 249 pkgs
Workers Finished
Gathering worker results

Saving Primary metadata
Saving file lists metadata
Saving other metadata
Generating sqlite DBs
Sqlite DBs complete

# 8. 可以用 Apache 或 Nginx 提供 Web 服务
# 但用 Python 的 http 模块更简单，适用于内网环境，可以通过浏览器输入本机 IP 查看。
python -m SimpleHTTPServer 80 &>/dev/null &  


# 9. 这里我采用Nginx方法： yum仓库nginx资源映射：
#将默认的default.conf文件备份.

mv default.conf default.conf.bak

#创建nginx yum.conf文件配置：

server  {

        listen 80;
        server_name localhost;
        # Load configuration files for the default server block.
        #include /etc/nginx/default.d/*.conf;


        location / {
        root /data/yum_repo/rhel6_64;
        index  index.html index.htm;
        autoindex on;
        }
         error_page  404     /404.html;
         location = /404.html {
         root   /usr/share/nginx/html;
}
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
        root   /usr/share/nginx/html;
        }
}

编辑nginx.conf文件，开启文件浏览功能，方便web访问yum源，查看是否正确：

http {
    autoindex on; #开启nginx目录浏览功能
    autoindex_exact_size off; #文件大小从KB开始显示
    autoindex_localtime on; #显示文件修改时间为服务器本地时间
}
#启动nginx服务：
/etc/init.d/nginx start


# 10. 每加入一个 rpm包就要更新一下
createrepo –update /data/yum_repo/rhel6_64/Packages/       

# 11. 修改 yum 配置文件 keepacache=0 改为 1，保存下载过的软件
sed -i ‘s#keepcache=0#keepcache=1#g’ /etc/yum.conf         



```
#### 客户端配置

```bash
cd /etc/yum.repos.d

vim jollychic.repo          # 连接本地 yum 源
repo 文件内容如下：
[jolly_yum]
name=jolly_yum
baseurl=http://$LAN_IP
enable=1
gpgcheck=0
protect=1
yum –-enablerepo=jamin –-disablerepo=base,extras,updates,epel list # 指定使用 jollychic 库(临时生效)

yum 源同步

暂时没做，具体可参考 Ref 中的配置
```


#### 客户端测试：

```bash
[root@tomcat yum.repos.d]# yum search all acl
已加载插件：fastestmirror
Loading mirror speeds from cached hostfile
=============================================================================================================== Matched: acl ===============================================================================================================
acl.x86_64 : Access control list utilities
libacl.x86_64 : Dynamic library for access control list support
attr.x86_64 : Utilities for managing filesystem extended attributes
db4.x86_64 : The Berkeley DB database library (version 4) for C
db4-utils.x86_64 : Command line tools for managing Berkeley DB (version 4) databases
libattr.x86_64 : Dynamic library for extended attribute support


[root@tomcat yum.repos.d]# yum install -y acl
已加载插件：fastestmirror
设置安装进程
Loading mirror speeds from cached hostfile
解决依赖关系
--> 执行事务检查
---> Package acl.x86_64 0:2.2.49-6.el6 will be 安装
--> 完成依赖关系计算

依赖关系解决

============================================================================================================================================================================================================================================
 软件包                                              架构                                                   版本                                                            仓库                                                       大小
============================================================================================================================================================================================================================================
正在安装:
 acl                                                 x86_64                                                 2.2.49-6.el6                                                    jolly_yum                                                  75 k

事务概要
============================================================================================================================================================================================================================================
Install       1 Package(s)

总下载量：75 k
Installed size: 189 k
下载软件包：
acl-2.2.49-6.el6.x86_64.rpm                                                                                                                                                                                          |  75 kB     00:00
运行 rpm_check_debug
执行事务测试
事务测试成功
执行事务
  正在安装   : acl-2.2.49-6.el6.x86_64                                                                                                                                                                                                  1/1
  Verifying  : acl-2.2.49-6.el6.x86_64                                                                                                                                                                                                  1/1

已安装:
  acl.x86_64 0:2.2.49-6.el6

完毕！
```

