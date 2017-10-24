---
title: 'ACL 修改权限ssh登录报ssh_exchange_identification: read:Connection reset by peer无法登陆问题'
date: 2014-11-27 15:23:10
tags:
- Linux note
categories: Linux
---

ACL修改权限出现了严重的问题：

root用户下使用ACL在给开发给予某个文件夹下的所有文件改权限的时候，用了`setfacl`命令，咋一看这个命令没啥很正常，也能执行，但是后面的提示让人感觉很不对劲， 有一个/，这是个很危险的命令，有点常识的人都知道，根目录下的文件权限不可以乱动啊，当时吓了一跳，于是另开一个终端怎么也连接不上.

```
ssh root@192.168.1.204
Connection reset by 192.168.1.204
```
root用户登陆出现报错

```
ssh admin@192.168.1.204
ssh_exchange_identification: read: Connection reset by peer 
```
普通用户登陆也出现同样的报错。

Google下 远程连接无法连接，用下面的命令，看详细的连接过程： 

```bash
➜  ~ ssh -v root@192.168.1.204
OpenSSH_6.9p1, LibreSSL 2.1.8
debug1: Reading configuration data /etc/ssh/ssh_config
debug1: /etc/ssh/ssh_config line 21: Applying options for *
debug1: Connecting to 192.168.1.204 [192.168.1.204] port 22.
debug1: Connection established.
debug1: identity file /Users/jules/.ssh/id_rsa type 1
debug1: key_load_public: No such file or directory
debug1: identity file /Users/jules/.ssh/id_rsa-cert type -1
debug1: key_load_public: No such file or directory
debug1: identity file /Users/jules/.ssh/id_dsa type -1
debug1: key_load_public: No such file or directory
debug1: identity file /Users/jules/.ssh/id_dsa-cert type -1
debug1: key_load_public: No such file or directory
debug1: identity file /Users/jules/.ssh/id_ecdsa type -1
debug1: key_load_public: No such file or directory
debug1: identity file /Users/jules/.ssh/id_ecdsa-cert type -1
debug1: key_load_public: No such file or directory
debug1: identity file /Users/jules/.ssh/id_ed25519 type -1
debug1: key_load_public: No such file or directory
debug1: identity file /Users/jules/.ssh/id_ed25519-cert type -1
debug1: Enabling compatibility mode for protocol 2.0
debug1: Local version string SSH-2.0-OpenSSH_6.9
debug1: Remote protocol version 2.0, remote software version OpenSSH_6.6.1
debug1: match: OpenSSH_6.6.1 pat OpenSSH_6.6.1* compat 0x04000000
debug1: Authenticating to 192.168.1.204:22 as 'root'
debug1: SSH2_MSG_KEXINIT sent
Connection closed by 192.168.1.204
```

百度了很多，以关键词`ssh_exchange_identification: read: Connection reset by peer`，搜索搜到不少网友们遇到这样的问题.


有的是ip被加入到限制列表中了,有的是dns无法解析主机名，有的是说误将权限改了，这里我也看了下一些文档上面说。将`/etc/ssh/`目录下的所有文件改成400 权限，照着做了，还是不行，报同样的错误。

```
chmod -R 400 /etc/sshd/* 
```

如果还是不行这一步那么看下权限。

看到一篇外国的文档：


因为我这里设置的是普通用户在var目录下面所有权限。

去/var下看了看，果然权限很大，都是777,cd 到empty目录，果然有ssh这个文件夹，在cd进去，啥也没有了。于是直接执行两条命令： 
cd /var 
chmod -R 755 * 
然后就再次尝试了远程连接了下，竟然ok了。

```bash
ssh -v root@192.168.1.204
OpenSSH_6.9p1, LibreSSL 2.1.8
debug1: Reading configuration data /etc/ssh/ssh_config
debug1: /etc/ssh/ssh_config line 21: Applying options for *
debug1: Connecting to 192.168.1.204 [192.168.1.204] port 22.
debug1: Connection established.
debug1: identity file /Users/jules/.ssh/id_rsa type 1
debug1: key_load_public: No such file or directory
debug1: identity file /Users/jules/.ssh/id_rsa-cert type -1
debug1: key_load_public: No such file or directory
debug1: identity file /Users/jules/.ssh/id_dsa type -1
debug1: key_load_public: No such file or directory
debug1: identity file /Users/jules/.ssh/id_dsa-cert type -1
debug1: key_load_public: No such file or directory
debug1: identity file /Users/jules/.ssh/id_ecdsa type -1
debug1: key_load_public: No such file or directory
debug1: identity file /Users/jules/.ssh/id_ecdsa-cert type -1
debug1: key_load_public: No such file or directory
debug1: identity file /Users/jules/.ssh/id_ed25519 type -1
debug1: key_load_public: No such file or directory
debug1: identity file /Users/jules/.ssh/id_ed25519-cert type -1
debug1: Enabling compatibility mode for protocol 2.0
debug1: Local version string SSH-2.0-OpenSSH_6.9
debug1: Remote protocol version 2.0, remote software version OpenSSH_6.6.1
debug1: match: OpenSSH_6.6.1 pat OpenSSH_6.6.1* compat 0x04000000
debug1: Authenticating to 192.168.1.204:22 as 'root'
debug1: SSH2_MSG_KEXINIT sent
debug1: SSH2_MSG_KEXINIT received
debug1: kex: server->client chacha20-poly1305@openssh.com <implicit> none
debug1: kex: client->server chacha20-poly1305@openssh.com <implicit> none
debug1: expecting SSH2_MSG_KEX_ECDH_REPLY
debug1: Server host key: ecdsa-sha2-nistp256 SHA256:W8lF3wwReKmYPPwp8F3AafqfnnM5Dxl669vTaEkzmwU
debug1: Host '192.168.1.204' is known and matches the ECDSA host key.
debug1: Found key in /Users/jules/.ssh/known_hosts:32
debug1: SSH2_MSG_NEWKEYS sent
debug1: expecting SSH2_MSG_NEWKEYS
debug1: SSH2_MSG_NEWKEYS received
debug1: SSH2_MSG_SERVICE_REQUEST sent
debug1: SSH2_MSG_SERVICE_ACCEPT received
debug1: Authentications that can continue: publickey,gssapi-keyex,gssapi-with-mic,password
debug1: Next authentication method: publickey
debug1: Offering RSA public key: /Users/jules/.ssh/id_rsa
debug1: Authentications that can continue: publickey,gssapi-keyex,gssapi-with-mic,password
debug1: Trying private key: /Users/jules/.ssh/id_dsa
debug1: Trying private key: /Users/jules/.ssh/id_ecdsa
debug1: Trying private key: /Users/jules/.ssh/id_ed25519
debug1: Next authentication method: password
root@192.168.1.204's password:
```
这里一般不建议用root权限去操作。 已经涨记性了修改这些ACL权限很容易导致琐死权限。


##### 报错二：Connection closed by 192.168.1.220

```bash
-rw------- 1 root root    668 9月   1 14:40 ssh_host_dsa_key
-rw-r--r-- 1 root root    590 9月   1 14:40 ssh_host_dsa_key.pub
-rw-r--r-- 1 root root      0 9月   1 14:40 ssh_host_ecdsa_key.pub
-rw------- 1 root root    963 9月   1 14:40 ssh_host_key
-rw-r--r-- 1 root root    627 9月   1 14:40 ssh_host_key.pub
-rw------- 1 root root   1675 9月   1 14:40 ssh_host_rsa_key
-rw-r--r-- 1 root root    382 9月   1 14:40 ssh_host_rsa_key.pub
```
这些查看下是否丢失，如果丢失需要重新生成。

前提是你还没有退出登录。

```bash
 touch /etc/ssh/ssh_host_ecdsa_key.pub
  service sshd restart
停止 sshd：                                                [确定]
生成 SSH2 RSA 主机键：                                     [确定]
生成 SSH1 RSA 主机键：                                     [确定]
正在生成 SSH2 DSA 主机键：                                 [确定]
正在启动 sshd：                                            [确定]
```
就可以搞定了。


### 问题三：SSH 登录时出现如下错误：requirement "uid >= 1000" not met by user "root"


### 问题描述

登录云服务器 ECS （Elastic Compute Server） Linux 服务器时，即便输入了正确的密码，也无法正常登录。该问题出现时，管理终端 或 SSH 客户端其中一种方式可以正常登录，或者两种方式均无法正常登录。同时，secure 日志中出现类似如下错误信息：

     pam_succeed_if(sshd:auth): requirement "uid >= 1000" not met by user "root".

### 问题原因

PAM 相关模块策略配置，禁止了 UID 小于 1000 的用户进行登录。

### 处理办法

要解决此问题，请进行如下配置检查：

通过 SSH 客户端或 管理终端 登录服务器。
通过 cat 等指令查看异常登录模式，对应的 PAM 配置文件。说明如下：
文件	功能说明

```bash
/etc/pam.d/login	控制台（管理终端）对应配置文件
/etc/pam.d/sshd	登录对应配置文件
/etc/pam.d/system-auth	系统全局配置文件
``` 
注：每个启用了 PAM 的应用程序，在 /etc/pam.d 目录中都有对应的同名配置文件。例如，login 命令的配置文件是 /etc/pam.d/login，可以在相应配置文件中配置具体的策略。


检查前述配置文件中，是否有类似如下配置信息：
     
     auth        required      pam_succeed_if.so uid >= 1000
如果需要修改相关策略配置，在继续之前建议进行文件备份。
使用 vi 等编辑器，修改相应配置文件中的上述配置，或者整个删除或注释（在最开头添加 # 号）整行配置，比如：

     auth        required      pam_succeed_if.so uid <= 1000      # 修改策略
    # auth        required      pam_succeed_if.so uid >= 1000   #取消相关配置
尝试重新登录服务器。
如果还有问题，可以参阅云服务器 ECS Linux SSH 无法登录问题排查指引做进一步排查分析。

