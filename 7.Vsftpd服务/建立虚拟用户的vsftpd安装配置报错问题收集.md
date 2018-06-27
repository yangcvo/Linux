# vsftp报错问题收集 
#### 1.解决vsftp错误500 OOPS: cannot change directory:/home/**** 目录

```bash
打开/etc/selinux/config
将selinux=enforcing或permissive改成disabled。
然后给目录权限：给那个www目录设置vsftp的权限，或者直接777.
```
### 2. 530 Login incorrect

```bash
[root@gtl ~]# ftp localhost
Connected to localhost.localdomain.
220 (vsFTPd 2.0.5)
530 Please login with USER and PASS.
530 Please login with USER and PASS.
KERBEROS_V4 rejected as an authentication type
Name (localhost:root): user
331 Please specify the password.
Password:
530 Login incorrect.
Login failed.
ftp> bye
221 Goodbye.
只有用匿名anonymous才可登录,其余所有用户都报530 Login incorrect错
local_enable=YES
write_enable=YES
pam_service_name=vsftpd
userlist_enable=YES
```
原因分析：


其实就是少了一行`pam_service_name=vsftpd`

解决方法：

只要把这行pam_service_name=vsftpd添加到vsftpd.conf配置文件中，然后重启vstfpd即可。

### 3.530 Permission denied

查看vsftpd的配置，配置文件中限定了vsftpd用户连接控制配置。

```bash
vsftpd.ftpusers：位于/etc目录下。它指定了哪些用户账户不能访问FTP服务器，例如root等。
vsftpd.user_list：位于/etc目录下。该文件里的用户账户在默认情况下也不能访问FTP服务器，仅当vsftpd .conf配置文件里启用userlist_enable=NO选项时才允许访问。
vsftpd.conf：位于/etc/vsftpd目录下。来自定义用户登录控制、用户权限控制、超时设置、服务器功能选项、服务器性能选项、服务器响应消息等FTP服务器的配置。
```

3.配置修改完成后，执行`service vsftpd restart`重启vsftpd服务。

虚拟用户如果是外网，从公司内网访问出现报错。

错误: 无法建立数据连接：`ECONNREFUSED - Connection refused by server`
错误: 连接超时

打开 FileZilla 的“站点管理器”，选中你要设置的站点连接，切换到“传输设置”选项，勾选“限制并发连接数”并设置“最大并发连接数”为1即可。

打开 FileZilla 的“站点管理器”，选中你要设置的站点连接，切换到“传输设置”选项，选择`主动`即可。


