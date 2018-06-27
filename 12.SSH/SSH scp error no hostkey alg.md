---
title: 'SSH scp error no hostkey alg'
date: 2014-11-27 15:23:10
tags:
- Linux note
categories: Linux
---

### SSH scp error no hostkey alg

ssh works well but when you try to copy a file via scp you get this error

```
no hostkey alg
```
Go on your server and check if you have /etc/ssh/ssh_host_rsa_key and /etc/ssh/ssh_host_dsa_key files, if not, generate them


```
ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key
ssh-keygen -t dsa -f /etc/ssh/ssh_host_dsa_key
```

### SSH 登录是错误：Permission denied (publickey,gssapi-with-mic)


```bash
$ ssh root@192.168.xx.xx

Permission denied (publickey,gssapi-with-mic).
```
报了这么个错，原因是我上次做测试时修改了`/etc/ssh/sshd_config` 中的`"PasswordAuthentication"`参数值为"no",修改回"yes"，重启sshd服务即可。


#### 这里我做了免秘钥ssh-key认证，可是还提示我输入密码。


ssh-copy-id 192.168.1.210

已经把公钥传输到对应机器上面。
可是ssh root@192.168.1.210 还是提示密码。


这里我做了测试：

```bash
ssh -vvv root@192.168.1.210
OpenSSH_5.2p1+sftpfilecontrol-v1.3, OpenSSL 0.9.8k 25 Mar 2009
HP-UX Secure Shell-A.05.20.004, HP-UX Secure Shell version
debug1: Reading configuration data /root/etc/ssh/sshd_config
debug3: RNG is ready, skipping seeding
debug2: ssh_connect: needpriv 0
debug1: Connecting to arnold [172.16.96.6] port 22.
debug1: Connection established.
debug1: identity file /root/.ssh/identity type -1
debug3: Not a RSA1 key file /root/.ssh/id_rsa.
debug2: key_type_from_name: unknown key type '-----BEGIN'
debug3: key_read: missing keytype
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug2: key_type_from_name: unknown key type '-----BEGIN'
debug3: key_read: missing keytype
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug3: key_read: missing whitespace
debug2: key_type_from_name: unknown key type '-----END'
....
```

解决思路：

这里我查看了192.168.1.210 服务器SELinux已关闭的。
防火墙也没问题
sshd服务也没有问题。配置也没问题。
后来我查看登录日志：

```bash
[root@tomcat_C1 ~]$ tailf /var/log/secure
Mar 24 16:00:48 tomcat_C1 sshd[15053]: pam_unix(sshd:session): session closed for user root
Mar 24 16:00:55 tomcat_C1 sshd[15061]: Authentication refused: bad ownership or modes for directory /root
Mar 24 16:00:59 tomcat_C1 sshd[15061]: Accepted password for root from 192.168.1.220 port 33810 ssh2
Mar 24 16:00:59 tomcat_C1 sshd[15061]: pam_unix(sshd:session): session opened for user root by (uid=0)
Mar 24 16:02:29 tomcat_C1 sshd[13733]: Received signal 15; terminating.
Mar 24 16:02:30 tomcat_C1 sshd[15143]: Server listening on 0.0.0.0 port 22.
Mar 24 16:02:30 tomcat_C1 sshd[15143]: Server listening on :: port 22.
Mar 24 16:04:48 tomcat_C1 sshd[15160]: Authentication refused: bad ownership or modes for directory /root
```
认证拒绝：/root/目录没权限呗。所以这里我在这台服务器设置了下权限。775

```bash
[root@tomcat_C1 ~]$ chmod 755 /root/
[root@tomcat_C1 ~]$ tailf /var/log/secure
Mar 24 16:00:48 tomcat_C1 sshd[15053]: pam_unix(sshd:session): session closed for user root
Mar 24 16:00:55 tomcat_C1 sshd[15061]: Authentication refused: bad ownership or modes for directory /root
Mar 24 16:00:59 tomcat_C1 sshd[15061]: Accepted password for root from 192.168.1.220 port 33810 ssh2
Mar 24 16:00:59 tomcat_C1 sshd[15061]: pam_unix(sshd:session): session opened for user root by (uid=0)
Mar 24 16:02:29 tomcat_C1 sshd[13733]: Received signal 15; terminating.
Mar 24 16:02:30 tomcat_C1 sshd[15143]: Server listening on 0.0.0.0 port 22.
Mar 24 16:02:30 tomcat_C1 sshd[15143]: Server listening on :: port 22.
Mar 24 16:04:48 tomcat_C1 sshd[15160]: Authentication refused: bad ownership or modes for directory /root
Mar 24 16:07:19 tomcat_C1 sshd[15197]: Accepted publickey for root from 192.168.1.220 port 42620 ssh2
Mar 24 16:07:19 tomcat_C1 sshd[15197]: pam_unix(sshd:session): session opened for user root by (uid=0)
```

免秘钥已设置通了。



