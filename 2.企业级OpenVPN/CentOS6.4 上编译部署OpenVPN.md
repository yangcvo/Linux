## CentOS6.4 上编译部署OpenVPN

背景介绍：
最近，GFW开始针对VPN进行了屏蔽，之前在VPS上搭建的PPTP/L2TP VPN在有些时候都开始变得不稳定了。
因此，打算在VPS上再搭建一个OpenVPN Server，以备不时之需。

OpenVPN是一个用于创建虚拟专用网络(Virtual Private Network)加密通道的免费开源软件。



一、服务器端安装及配置
    服务器环境:CentOS 6.4 x86_64 Minimal
    内网IP：192.168.8.2
    外网IP：220.189.213.186
    OpenVPN版本:openvpn-2.4.1-3.el6.x86_64

1、安装前准备

```bash
# 关闭selinux
setenforce 0
sed -i '/^SELINUX=/c\SELINUX=disabled' /etc/selinux/config
```

###### 安装EPEL扩展库

```
# rpm -ivh http://mirrors.sohu.com/fedora-epel/6/x86_64/epel-release-6-8.noarch.rpm
# sed -i 's/^mirrorlist=https/mirrorlist=http/' /etc/yum.repos.d/epel.repo
```

###### 安装所需依赖软件包 : 安装openssl和lzo，lzo用于压缩通讯数据加快传输速度

```
# yum install -y openssl openssl-devel lzo lzo-devel pam pam-devel automake pkgconfig
```

###### 安装及配置OpenVPN和easy-rsa

```
# 安装openvpn和easy-rsa
yum -y install openvpn easy-rsa

```

###### 修改vars文件

```bash
cd /usr/share/easy-rsa/2.0/
vim vars
```
###### 注意是修改，不是替换整个文件
###### 修改注册信息，比如公司地址、公司名称、部门名称等。

```bash
export KEY_COUNTRY="CN"
export KEY_PROVINCE="ZhengJang"
export KEY_CITY="HangZhou"
export KEY_ORG="Jollychic"
export KEY_EMAIL="me@myhost.mydomain"
export KEY_OU="MyOrganizationalUnit"
```
###### 初始化环境变量

```bash
source vars
```
 
###### 清除keys目录下所有与证书相关的文件
###### 下面步骤生成的证书和密钥都在/usr/share/easy-rsa/2.0/keys目录里

```bash
./clean-all
```
 
###### 生成根证书ca.crt和根密钥ca.key（一路按回车即可）

```bash
./build-ca
```
 
###### 为服务端生成证书和密钥（一路按回车，直到提示需要输入y/n时，输入y再按回车，一共两次）

```bash
./build-key-server server
```
###### 每一个登陆的VPN客户端需要有一个证书，每个证书在同一时刻只能供一个客户端连接，下面建立2份
###### 为客户端生成证书和密钥（一路按回车，直到提示需要输入y/n时，输入y再按回车，一共两次）

```bash
./build-key yancy
./build-key client2
```
###### 创建迪菲·赫尔曼密钥，会生成dh1024.pem文件

```bash
./build-dh
``` 
###### 生成ta.key文件（防DDos攻击、UDP淹没等恶意攻击）

```bash
openvpn --genkey --secret keys/yancy.key
```

 查看keys目录下生成的文件：
![](https://github.com/yangcvo/Linux/blob/master/2.企业级OpenVPN/14980202259436.jpg)

## 3、创建服务器端配置文件

###### 3.1 在openvpn的配置目录下新建一个keys目录

```
mkdir /etc/2.企业级OpenVPN/keys
```

###### 3.2将需要用到的openvpn证书和密钥复制一份到刚创建好的keys目录中

```bash
cp /usr/share/easy-rsa/2.0/keys/* /etc/2.企业级OpenVPN/keys/
```
###### 3.3复制一份服务器端配置文件模板server.conf到/etc/2.企业级OpenVPN/

```bash
cp /usr/share/doc/openvpn-2.4.3/sample/sample-config-files/server.conf /etc/2.企业级OpenVPN/
```

###### 3.4编辑server.conf

```bash
vim /etc/2.企业级OpenVPN/server.conf
port 1194
```

###### 改成tcp，默认使用udp，如果使用HTTP Proxy，必须使用tcp协议

```bash
proto tcp
;proto udp
;dev tap
dev tun
```
###### 路径前面加keys，全路径为/etc/2.企业级OpenVPN/keys/ca.crt

```bash
ca keys/ca.crt
cert keys/server.crt
key keys/server.key  # This file should be kept secret
dh keys/dh1024.pem
```
###### 默认虚拟局域网网段，不要和实际的局域网冲突即可

```bash
server 10.188.188.0 255.255.255.0
ifconfig-pool-persist ipp.txt
```
####### 10.188.188.0/8是我这台VPN服务器所在的内网的网段，根据自身实际情况进行修改

```bash
push "route 10.188.188.0 255.255.255.0"
push "redirect-gateway def1 bypass-dhcp"                                                                                                     
push "dhcp-option DNS 223.5.5.5"
```

###### 可以让客户端之间相互访问直接通过openvpn程序转发，根据需要设置

```bash
client-to-client
```
###### 如果客户端都使用相同的证书和密钥连接VPN，一定要打开这个选项，否则每个证书只允许一个人连接VPN

```bash
duplicate-cn
keepalive 10 120
tls-auth keys/yancy.key 0 # This file is secret
comp-lzo
persist-key
persist-tun
```
###### OpenVPN的状态日志，默认为/etc/2.企业级OpenVPN/openvpn-status.log

```bash
status openvpn-status.log
```
###### OpenVPN的运行日志，默认为/etc/2.企业级OpenVPN/openvpn.log 

```bash
log-append openvpn.log
```
###### 改成verb 5可以多查看一些调试信息

```bash
verb 5
```

###### 配置密码认证

```bash
auth-user-pass-verify /etc/2.企业级OpenVPN/checkpsw.sh via-env
```
###### 配置无需密钥认证

```bash
client-cert-not-required 
username-as-common-name
script-security 3
;explicit-exit-notify 1
```

```bash
[root@yancy openvpn]# vim /etc/2.企业级OpenVPN/checkpsw.sh
#!/bin/sh
###########################################################
# checkpsw.sh (C) 2004 Mathias Sundman <mathias@openvpn.se>
#
# This script will authenticate OpenVPN users against
# a plain text file. The passfile should simply contain
# one row per user with the username first followed by
# one or more space(s) or tab(s) and then the password.

PASSFILE="/etc/2.企业级OpenVPN/psw-file"
LOG_FILE="/etc/2.企业级OpenVPN/openvpn-password.log"
TIME_STAMP=`date "+%Y-%m-%d %T"`
###########################################################
if [ ! -r "${PASSFILE}" ]; then
  echo "${TIME_STAMP}: Could not open password file \"${PASSFILE}\" for reading." >>  ${LOG_FILE}
  exit 1
fi
CORRECT_PASSWORD=`awk '!/^;/&&!/^#/&&$1=="'${username}'"{print $2;exit}' ${PASSFILE}`
if [ "${CORRECT_PASSWORD}" = "" ]; then
  echo "${TIME_STAMP}: User does not exist: username=\"${username}\", password=

\"${password}\"." >> ${LOG_FILE}
  exit 1
fi
if [ "${password}" = "${CORRECT_PASSWORD}" ]; then
  echo "${TIME_STAMP}: Successful authentication: username=\"${username}\"." >> ${LOG_FILE}
  exit 0
fi

echo "${TIME_STAMP}: Incorrect password: username=\"${username}\", password=

\"${password}\"." >> ${LOG_FILE}
exit 1
[root@yancy openvpn]# chmod +x checkpsw.sh
```

openVPN 创建的用户 - 用户名和密码：

```bash
[root@yancy openvpn]# vim /etc/2.企业级OpenVPN/psw-file
yancy yancy
```
## 4、配置内核和防火墙，启动服务


###### 4.1 开启路由转发功能

```bash
sed -i '/net.ipv4.ip_forward/s/0/1/' /etc/sysctl.conf
sysctl -p
```
 
###### 4.2配置防火墙，别忘记保存

```bash
iptables -I INPUT -p tcp --dport 1194 -m comment --comment "openvpn" -j ACCEPT
iptables -t nat -A POSTROUTING -s 10.188.180.0/24 -j MASQUERADE
service iptables save
```
 
# 启动openvpn并设置为开机启动

```bash
service openvpn start
chkconfig openvpn on
```

⚠️这里启动报错：

```bash
[root@yancy openvpn]# service openvpn start
正在启动 openvpn：                                         [失败]
[root@yancy openvpn]# tailf -1000 openvpn.log
Options error: --explicit-exit-notify can only be used with --proto udp
Use --help for more information.
Options error: --explicit-exit-notify can only be used with --proto udp
Use --help for more information.
Options error: --explicit-exit-notify can only be used with --proto udp
Use --help for more information.
Options error: --explicit-exit-notify can only be used with --proto udp
Use --help for more information.
Options error: --explicit-exit-notify can only be used with --proto udp
[root@yancy openvpn]# vim server.conf
并且在客户端删除以下行，因为它不支持在TCP模式。
;explicit-exit-notify 1
配置完成以后就可以了。
```
## 5、创建客户端配置文件


###### 5.1 复制一份client.conf模板命名为client.ovpn

```bash
cp /usr/share/doc/openvpn-2.4.3/sample/sample-config-files/client.conf client.ovpn
```
###### 5.2 编辑client.ovpn

```bash
[root@yancy openvpn]# cat client.ovpn | grep -v '^#'| grep -v '^;' | grep -v '^$'
client
dev tun
proto tcp
remote 192.168.17.145 1194
resolv-retry infinite
nobind
persist-key
persist-tun
ca ca.crt
ns-cert-type server
tls-auth yancy.key 1
auth-user-pass
remote-cert-tls server
cipher AES-256-CBC
comp-lzo
verb 3
```

客户端下载
https://tunnelblick.net/downloads.html

MAC 客户端使用
1、下载 yancy.key  ca.crt client.ovpn  到本地
2、打开客户端 
双击：client.ovpn就可以。按提示输入用户和密码。

![](https://github.com/yangcvo/Linux/blob/master/2.企业级OpenVPN/14987039352391.jpg)

![](https://github.com/yangcvo/Linux/blob/master/2.企业级OpenVPN/14987039455224.jpg)


参考资料：
[OpenVPN Server on CentOS 6](https://www.digitalocean.com/community/tutorials/how-to-setup-and-configure-an-openvpn-server-on-centos-6)

[Setup And Configure OpenVPN Server On CentOS 6.5](http://www.unixmen.com/setup-openvpn-server-client-centos-6-5/)
[OpenVPN4CentOS](http://docs.ucloud.cn/software/vpn/OpenVPN4CentOS.html)


