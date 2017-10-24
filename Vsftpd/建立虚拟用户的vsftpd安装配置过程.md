# 建立虚拟用户的vsftpd安装配置过程

虚拟用户的特点是只能访问服务器为其提供的FTP服务，而不能访问系统的其它资源。所以，如果想让用户对FTP服务器站内具有写权限，但又不允许访问系统其它资源，可以使用虚拟用户来提高系统的安全性。
在VSFTP中，认证这些虚拟用户使用的是单独的口令库文件（pam_userdb），由可插入认证模块（PAM）认证。使用这种方式更加安全，并且配置更加灵活。 下面介绍配置过程。

建立虚拟用户的vsftpd安装配置过程

1.安装vsftpd服务，和测试命令ftp

```bash
# yum -y install vsftpd ftp
```
2.建立虚拟用户的用户名/密码数据库vsftpd服务的虚拟用户数据库使用的是Berkeley DB格式的数据文件。建立数据库文件要用到db_load命令工具，所以要安装db4软件包

```bash
# yum -y install db4*
```

3.生成虚拟用户口令库文件。为了建立此口令库文件，先要生成一个文本文件。该文件的格式如下，单数行为用户名，偶数行为口令：
建立文本格式的用户名/密码列表文件，奇数行为用户名，偶数行对应为上一行用户名密码。

```bash
# vim /etc/vsftpd/virtual_login
accp     虚拟用户
123.com   虚拟用户密码
```

4.用db_load工具将列表文件转化为DB数据库文件。

```bash
# db_load -T -t hash -f /etc/vsftpd/virtual_login /etc/vsftpd/virtual_login.db
# chown /etc/vsftpd/vuser.*  //降低文件权限以提高安全性
```

5.建立PAM认证文件

```bash
#vi /etc/pam.d/vsftpd 添加如下内容
#%PAM-1.0
auth       required           pam_userdb.so  db=/etc/vsftpd/  vusers
account    required           pam_userdb.so  db=/etc/vsftpd/vusers
```

6.建立FTP访问根目录以及虚拟用户对应的系统账号  这里我给用户指定这里的虚拟用户和对应的系统账号
   
```bash
#useradd -s /sbin/nologin vsftpd
#useradd -d /var/www/html/ftp3 -s /sbin/nologin  ftp3
#chmod 755 /var/www/html/ftp3
#cp /etc/vsftpd/vsftpd.conf /etc/vsftpd/vsftpd.conf.bak
```
经过该步骤的设置，/var/www/html/accp就是virtual_user用户的主目录，该用户也是accp目录的拥有者。除root用户之外，只有该用户具有对该目录的读、写和执行的权限。

7.修改vsftpd的主配置文件，添加对虚拟用户的支持。

```bash  
#vi /etc/vsftpd/vsftpd.conf   #内容如下
anonymous_enable=NO    这里设置禁止匿名登录
local_enable=YES
write_enable=YES    全局配置可写
local_umask=022
anon_upload_enable=NO
anon_mkdir_write_enable=NO
dirmessage_enable=YES
xferlog_enable=YES
connect_from_port_20=YES
chown_uploads=NO
xferlog_file=/var/log/vsftpd.log
xferlog_std_format=YES
nopriv_user=vsftpd
async_abor_enable=YES
ascii_upload_enable=YES
ascii_download_enable=YES
ftpd_banner=Welcome to $username FTP service
chroot_list_enable=YES
chroot_list_file=/etc/vsftpd/chroot_list
listen=YES
pam_service_name=vsftpd
userlist_enable=YES
tcp_wrappers=YES
guest_enable=YES
virtual_use_local_privs=YES
guest_username=ftp3   这里添加你虚拟用户的支持
user_config_dir=/etc/vsftpd/vsftpd_config
```

7.为accp和java建立独立配置目录及文件

```bash
mkdir /etc/vsftpd/vsftpd_config/
touch /var/log/vsftpd.log
chmod 600 /var/log/vsftpd.log
chown vsftpd.vsftpd /var/log/vsftpd.log
touch /etc/vsftpd/chroot_list
cd /etc/vsftpd/vsftpd_config/
```

```bash
#vim accp   ###添加如下内容
anon_upload_enable=YES
anon_mkdir_write_enable=YES
guest_enable=yes
guest_username=$username
local_root=/var/www/html/$username
idle_session_timeout=600
data_connection_timeout=120
max_clients=10
max_per_ip=5
local_max_rate=0
```

#### touch java 建立空文件，默认配置文件中的权限

8.启动vsftpd服务

```bash
service vsftpd start
```

权限：john可以登录到ftp服务器，可以浏览，下载，也可以上传文件
      mike可以登录到ftp服务器，可以浏览，下载，但是不可以上传

#### 9.本地测试：

（一）john的测试

```bash
[root@YTB-APP-1 ~]# ls
anaconda-ks.cfg  bin  importipas.sh  install.log  install.log.syslog  my.cnf.bak
[root@YTB-APP-1 ~]# ftp 127.0.0.1
Trying ::1...
ftp: connect to address ::1Connection refused
Trying 127.0.0.1...
Connected to localhost (127.0.0.1).
220 (vsFTPd 2.2.2)
Name (localhost:ytb): john
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls
227 Entering Passive Mode (127,0,0,1,82,29).
150 Here comes the directory listing.
-rw-r--r--    1 0        0             574 Jul 01 14:50 vutest.file
226 Directory send OK.
ftp> get vutest.file
local: vutest.file remote: vutest.file
227 Entering Passive Mode (127,0,0,1,103,164).
150 Opening BINARY mode data connection for vutest.file (574 bytes).
226 Transfer complete.
574 bytes received in 3.4e-05 secs (16882.35 Kbytes/sec)
ftp> put install.log
local: install.log remote: install.log
227 Entering Passive Mode (127,0,0,1,115,162).
150 Ok to send data.
226 Transfer complete.
29388 bytes sent in 0.024 secs (1222.97 Kbytes/sec)
ftp> quit
221 Goodbye.
[root@YTB-APP-1 ~]# ls
anaconda-ks.cfg  bin  importipas.sh  install.log  install.log.syslog  my.cnf.bak  vutest.file
[root@YTB-APP-1 ~]# ls /data/pub/
install.log  vutest.file
[root@YTB-APP-1 ~]#
（二）mike的测试
[root@YTB-APP-1 ~]# ls
anaconda-ks.cfg  bin  importipas.sh  install.log  install.log.syslog  my.cnf.bak  vutest.file
[root@YTB-APP-1 ~]# rm -rf vutest.file
[root@YTB-APP-1 ~]# ftp localhost
Trying ::1...
ftp: connect to address ::1Connection refused
Trying 127.0.0.1...
Connected to localhost (127.0.0.1).
220 (vsFTPd 2.2.2)
Name (localhost:ytb): mike
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls
227 Entering Passive Mode (127,0,0,1,223,141).
150 Here comes the directory listing.
-rw-r--r--    1 503      503         29388 Jul 03 02:23 install.log
-rw-r--r--    1 0        0             574 Jul 01 14:50 vutest.file
226 Directory send OK.
ftp> get vutest.file
local: vutest.file remote: vutest.file
227 Entering Passive Mode (127,0,0,1,154,230).
150 Opening BINARY mode data connection for vutest.file (574 bytes).
226 Transfer complete.
574 bytes received in 3.8e-05 secs (15105.26 Kbytes/sec)
ftp> put install.log.syslog
local: install.log.syslog remote: install.log.syslog
227 Entering Passive Mode (127,0,0,1,227,247).
550 Permission denied.
ftp> quit
221 Goodbye.
[root@YTB-APP-1 ~]# ls
anaconda-ks.cfg  bin  importipas.sh  install.log  install.log.syslog  my.cnf.bak  vutest.file
[root@YTB-APP-1 ~]# ls /dat/pub/
ls: cannot access /dat/pub/: No such file or directory
[root@YTB-APP-1 ~]# ls /data/pub/
install.log  vutest.file
[root@YTB-APP-1 ~]#
```

10.Mac连接方式使用方法：

```bash
Mac连接方式：sftp ftp3@192.168.1.211
ftp3@192.168.1.211's password: 输入密码
查看方式：
sftp> ls -lh
-rw-r--r-- 0 1004 1004 39.2M Apr 1 17:23  ccc.war
```

上传使用put 下载使用get
put /Users/jules/Downloads/haozhuo-check.war  就是把本地的时check上传。

这里就连接成功了，如果后续还要添加账户只需要在vi /etc/vsftpd/vusers.list
然后在用db_load工具将列表文件转化为DB数据库文件。

```bash
# cd /etc/vsftpd/
#db_load -T -t hash -f vusers.list vusers.db
```

添加好以后给该用户指定一个对应的创建目录。

```bash
useradd -d /data/www -s /sbin/nologin  accp 虚拟用户名
```

然后就可以连接了。
最后给每个用户做用户权限的时候也是可以的。

直接在/etc/vsftpd/vusers_dir目录下面创建用户txt 给予权限。

因为我在vsftpd.conf做了配置。

指定给特殊用户权限访问。


---------------------------------------------------------


12. help

那么现在大家看看我的匿名服务器配置文件吧

```bash
anonymous_enable=YES //允许匿名访问，这是匿名服务器必须的
write_enable=YES //全局配置可写
no_anon_password=YES //匿名用户login时不询问口令
anon_umask=077 //匿名用户上传的文件权限是-rw----
anon_upload_enable=YES //允许匿名用户上传文件
anon_mkdir_write_enable=YES //允许匿名用户建立目录
anon_other_write_enable=YES //允许匿名用户具有建立目录，上传之外的权限，如重命名，删除
dirmessage_enable=YES //当使用者转换目录,则会显示该目录下的.message信息
xferlog_enable=YES //记录使用者所有上传下载信息
xferlog_file=/var/log/vsftpd.log //将上传下载信息记录到/var/log/vsftpd.log中
xferlog_std_format=YES //日志使用标准xferlog格式
idle_session_timeout=600 //客户端超过600S没有动作就自动被服务器踢出
data_connection_timeout=120 //数据传输时超过120S没有动作被服务器踢出
chown_uploads=YES
chown_username=daemon //上传文件的属主
ftpd_banner=Welcome to d-1701.com FTP service. //FTP欢迎信息
anon_max_rate=80000 //这是匿名用户的下载速度为80KBytes/s
check_shell=NO //不检测SHELL
```

需要脚本的留言我即可。 


