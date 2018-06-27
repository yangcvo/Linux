---
title: zimbra邮件系统的环境部署
date: 2014-11-24 18:13:30
tags:
- Linux note
categories: Linux
---

## zimbra 

本实验以CENTOS6.6 64位为例. 最小化安装外加开发包

### 1.关闭防火墙

```bash
/etc/init.d/iptables stop 
```
这里说下如果没有关闭防火墙，一定要写规则增加`iptables`内容如下:

```
# enable zimbra ports
-A INPUT -m state --state NEW -m tcp -p tcp --dport 25 -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 80 -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 110 -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 389 -j ACCEPT -s 10.10.10.0/24
-A INPUT -m state --state NEW -m tcp -p tcp --dport 443 -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 465 -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 993 -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 995 -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 5222 -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 7071 -j ACCEPT -s 10.10.10.0/24
-A INPUT -m state --state NEW -m tcp -p tcp --dport 873 -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 7110 -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 7780 -j ACCEPT
```
### 3.修改`主机名`

```bash
vim /etc/sysconfig/network
hostname=mail.benet.com
```
### 4.修改`/etc/hosts`文件

```
vi/etc/hosts
192.168.1.230 mail.benet.com mail
```
### 5.停止系统默认邮件服务

```
chkconfig postfix off
/etc/init.d/postfix stop
```

这里yum安装依赖库

```bash
yum -y install libidn11 curl fetchmail libpcre3 libgmp3c2 libxml2 libstdc++6 openssl perl sysstat libtool-ltdl compat-libstdc* nc file yum -y update
```

安装依赖组件

```bash
yum install sysstat
```

### 6.关闭SELINUX

```bash
 sed -i 's/^SELINUX=.*/#&/;s/^SELINUXTYPE=.*/#&/;/SELINUX=.*/a SELINUX=disabled' /etc/sysconfig/selinux
 
上面SELINUX需要重启才能生效。

下面的命令实现临时关闭SELinux
/usr/sbin/setenforce 0
/usr/sbin/setenforce: SELinux is disabled
```
由于zimbra严重依赖DNS  所以本实验安装一个DNS服务器为zimbar提供服务

bind-9.8.6-P1  安装的这个版本

从这里下载:https://www.isc.org/downloads/

我这里有编译安装和yum源安装

```
yum install bind*
```
安装过程中会有几个要求输入的地方，都输入y。这里安装的最新版为9.8.2。
安装`bind`，给`zimbra`提供解析，注意，这个步骤很重要，因为`zimbra`严重依赖DNS，内部用自己解析，不知道的都转发到公网。

```bash
yum install bind* -y
```

编辑`named.conf`文件

vim /var/named/chroot/etc/named/named.conf

内容如下:

```
options {
        directory       "/var/named";
       forwarders { 202.96.134.133; 202.96.128.166; };
        };
zone "lxb.com" IN {
        type master;
        file "lxb.com.zone";
        allow-update { none; };
        };
zone "0.168.192.in-addr.arpa" IN {
        type master;
        file "192.168.0.arpa";
        allow-update { none; };
   };
```
配置文件正确性检查，没有任何提示就表示正确

```bash
named-checkconf /var/named/chroot/etc/named/named.conf
```

创建正向解析文件

```bash
vim /var/named/chroot/var/named/lxb.com.zone
```

内容如下

```bash
$TTL    86400
@       IN      SOA     lxb.com.        root.lxb.com. (
        20110308
        3H              ; refresh
        15M             ; retry
        1W              ; expiry
        1D )            ; minimum
@       IN      NS      lxb.com.
        IN      A       192.168.0.1
        IN      MX      10      mail.lxb.com.
mail    IN      A       192.168.0.1
*       IN      A       192.168.0.1
```


创建反向解析文件

```bash
vim /var/named/chroot/var/named/192.168.0.arpa
```

内容如下

```bash
$TTL    86400
@       IN      SOA     lxb.com.        root.lxb.com. (
        20110308
        3H              ; refresh
        15M             ; retry
        1W              ; expiry
        1D )            ; minimum
        IN      NS      lxb.com.
        IN      A       192.168.0.1
        IN      MX      10      mail.lxb.com.
1       IN      PTR     mail.lxb.com.
```

解析文件正确性检查，出现OK提示就表示正确

```bash
named-checkzone lxb.com /var/named/chroot/var/named/lxb.com.zone
named-checkzone lxb.com /var/named/chroot/var/named/192.168.0.arpa
```

把原来的配置文件改名，应用刚才创建的配置文件

```bash
mv /etc/named.conf named.conf.bak
ln -s /var/named/chroot/etc/named/named.conf /etc/
service named start
chkconfig named on
```

解析测试：



3、若其他计算机设置该DNS地址后却无法解析，需修改iptabls规则，将tcp和udp的53端口开放。

vi /etc/sysconfig/iptables，在其中加入：

```
-A INPUT -m state --state NEW -m tcp -p tcp --dport 53 -j ACCEPT
-A INPUT -m state --state NEW -m udp -p udp --dport 53 -j ACCEPT
```
修改完成后，重启iptables：

```
#service iptables restart
```

### 8、解压安装文件

```
[root@zcs soft]# tar -xzvf /mnt/nfs/zcs-8.0.2_GA_5569.RHEL6_64.20121210115059.tgz 
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/packages/
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/packages/zimbra-apache-8.0.2_GA_5569.RHEL6_64-20121210115059.x86_64.rpm
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/packages/zimbra-core-8.0.2_GA_5569.RHEL6_64-20121210115059.x86_64.rpm
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/packages/zimbra-ldap-8.0.2_GA_5569.RHEL6_64-20121210115059.x86_64.rpm
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/packages/zimbra-logger-8.0.2_GA_5569.RHEL6_64-20121210115059.x86_64.rpm
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/packages/zimbra-memcached-8.0.2_GA_5569.RHEL6_64-20121210115059.x86_64.rpm
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/packages/zimbra-mta-8.0.2_GA_5569.RHEL6_64-20121210115059.x86_64.rpm
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/packages/zimbra-proxy-8.0.2_GA_5569.RHEL6_64-20121210115059.x86_64.rpm
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/packages/zimbra-snmp-8.0.2_GA_5569.RHEL6_64-20121210115059.x86_64.rpm
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/packages/zimbra-spell-8.0.2_GA_5569.RHEL6_64-20121210115059.x86_64.rpm
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/packages/zimbra-store-8.0.2_GA_5569.RHEL6_64-20121210115059.x86_64.rpm
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/bin/
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/bin/get_plat_tag.sh
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/bin/zmdbintegrityreport
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/data/
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/data/versions-init.sql
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/YPL.txt
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/zcl.txt
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/zimbra_public_eula_2.1.txt
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/oracle_jdk_eula.txt
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/en_US/
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/en_US/admin.pdf
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/en_US/Fedora Server Config.pdf
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/en_US/Import_Wizard_Outlook.pdf
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/en_US/Migration_Exch_Admin.pdf
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/en_US/Migration_Exch_User.pdf
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/en_US/MigrationWizard_Domino.pdf
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/en_US/MigrationWizard.pdf
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/en_US/OSmultiserverinstall.pdf
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/en_US/quick_start.pdf
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/en_US/RNZCSO_2005Beta.pdf
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/en_US/User Instructions for ZCS Import Wizard.pdf
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/en_US/Zimbra iCalendar Migration Guide.pdf
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/en_US/Zimbra_Release_Note.pdf
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/en_US/Zimbra Schema.pdf
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/docs/en_US/zimbra_user_guide.pdf
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/util/
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/util/modules/
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/util/modules/getconfig.sh
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/util/modules/packages.sh
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/util/modules/postinstall.sh
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/util/addUser.sh
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/util/globals.sh
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/util/utilfunc.sh
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/readme_source_en_US.txt
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/readme_binary_en_US.txt
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/install.sh
zcs-8.0.2_GA_5569.RHEL6_64.20121210115059/README.txt
```
### 9、安装

由于是`centos`使用`redhat`安装包，所以安装要添加参数`–platform-override`

```bash
./install.sh --platform-override
```
安装过程，主要是`“Create domain“`改变域名为`qzalab.cn`；修改管理员密码3->4->r->a；本安装是把所有服务安装在一台服务器上，分布式的安装请参考其他资料。


```bash
[root@zcs zcs-8.0.2_GA_5569.RHEL6_64.20121210115059]# ./install.sh --platform-override

Operations logged to /tmp/install.log.1317
Checking for existing installation...
    zimbra-ldap...NOT FOUND
    zimbra-logger...NOT FOUND
    zimbra-mta...NOT FOUND
    zimbra-snmp...NOT FOUND
    zimbra-store...NOT FOUND
    zimbra-apache...NOT FOUND
    zimbra-spell...NOT FOUND
    zimbra-convertd...NOT FOUND
    zimbra-memcached...NOT FOUND
    zimbra-proxy...NOT FOUND
    zimbra-archiving...NOT FOUND
    zimbra-cluster...NOT FOUND
    zimbra-core...NOT FOUND


PLEASE READ THIS AGREEMENT CAREFULLY BEFORE USING THE SOFTWARE.
ZIMBRA, INC. ("ZIMBRA") WILL ONLY LICENSE THIS SOFTWARE TO YOU IF YOU
FIRST ACCEPT THE TERMS OF THIS AGREEMENT. BY DOWNLOADING OR INSTALLING
THE SOFTWARE, OR USING THE PRODUCT, YOU ARE CONSENTING TO BE BOUND BY
THIS AGREEMENT. IF YOU DO NOT AGREE TO ALL OF THE TERMS OF THIS
AGREEMENT, THEN DO NOT DOWNLOAD, INSTALL OR USE THE PRODUCT.

License Terms for the Zimbra Collaboration Suite:
  http://www.zimbra.com/license/zimbra_public_eula_2.1.html



Do you agree with the terms of the software license agreement? [N] y




Oracle

LICENSE 略...

Last updated May 17, 2011




Do you agree with the terms of the software license agreement? [N] y

Checking for prerequisites...
    FOUND: NPTL
    FOUND: nc-1.84-22
    FOUND: sudo-1.7.4p5-13
    FOUND: libidn-1.18-2
    FOUND: gmp-4.3.1-7
    FOUND: /usr/lib64/libstdc++.so.6

Checking for suggested prerequisites...
    FOUND: perl-5.10.1
    FOUND: sysstat
    FOUND: sqlite
Prerequisite check complete.

Checking for installable packages

Found zimbra-core
Found zimbra-ldap
Found zimbra-logger
Found zimbra-mta
Found zimbra-snmp
Found zimbra-store
Found zimbra-apache
Found zimbra-spell
Found zimbra-memcached
Found zimbra-proxy


Select the packages to install

Install zimbra-ldap [Y]

Install zimbra-logger [Y]

Install zimbra-mta [Y]

Install zimbra-snmp [Y]

Install zimbra-store [Y]

Install zimbra-apache [Y]

Install zimbra-spell [Y]

Install zimbra-memcached [N] y

Install zimbra-proxy [N] y
Checking required space for zimbra-core
Checking space for zimbra-store

Installing:
    zimbra-core
    zimbra-ldap
    zimbra-logger
    zimbra-mta
    zimbra-snmp
    zimbra-store
    zimbra-apache
    zimbra-spell
    zimbra-memcached
    zimbra-proxy

You appear to be installing packages on a platform different
than the platform for which they were built.


This platform is CentOS6_64
Packages found: RHEL6_64
This may or may not work.

Using packages for a platform in which they were not designed for
may result in an installation that is NOT usable. Your support
options may be limited if you choose to continue.


Install anyway? [N] y

The system will be modified.  Continue? [N] y


Removing /opt/zimbra
Removing zimbra crontab entry...done.
Cleaning up zimbra init scripts...done.
Cleaning up /etc/ld.so.conf...done.
Cleaning up /etc/security/limits.conf...done.

Finished removing Zimbra Collaboration Server.

Installing packages

    zimbra-core......zimbra-core-8.0.2_GA_5569.RHEL6_64-20121210115059.x86_64.rpm...done
    zimbra-ldap......zimbra-ldap-8.0.2_GA_5569.RHEL6_64-20121210115059.x86_64.rpm...done
    zimbra-logger......zimbra-logger-8.0.2_GA_5569.RHEL6_64-20121210115059.x86_64.rpm...done
    zimbra-mta......zimbra-mta-8.0.2_GA_5569.RHEL6_64-20121210115059.x86_64.rpm...done
    zimbra-snmp......zimbra-snmp-8.0.2_GA_5569.RHEL6_64-20121210115059.x86_64.rpm...done
    zimbra-store......zimbra-store-8.0.2_GA_5569.RHEL6_64-20121210115059.x86_64.rpm...done
    zimbra-apache......zimbra-apache-8.0.2_GA_5569.RHEL6_64-20121210115059.x86_64.rpm...done
    zimbra-spell......zimbra-spell-8.0.2_GA_5569.RHEL6_64-20121210115059.x86_64.rpm...done
    zimbra-memcached......zimbra-memcached-8.0.2_GA_5569.RHEL6_64-20121210115059.x86_64.rpm...done
    zimbra-proxy......zimbra-proxy-8.0.2_GA_5569.RHEL6_64-20121210115059.x86_64.rpm...done
Operations logged to /tmp/zmsetup.01082013-094551.log
Installing LDAP configuration database...done.



Operations logged to /tmp/zmsetup.01082013-094551.log
Installing LDAP configuration database...done.
Setting defaults...
        Interface: 10.10.10.20
        Interface: 127.0.0.1
        Interface: ::1


DNS ERROR - none of the MX records for zcs.qzalab.cn
resolve to this host
Change domain name? [Yes] no
Create domain: [zcs.qzalab.cn] qzalab.cn
        MX: mail.qzalab.cn (10.10.10.20)
        MX: zcs.qzalab.cn (10.10.10.20)

        Interface: 10.10.10.20
        Interface: 127.0.0.1
        Interface: ::1
done.
Checking for port conflicts

Main menu

  1) Common Configuration:                                                 
  2) zimbra-ldap:                            Enabled                     
  3) zimbra-store:                            Enabled                     
        +Create Admin User:                    yes                         
        +Admin user to create:                admin@qzalab.cn                 
******* +Admin Password                        UNSET                       
        +Anti-virus quarantine user:          virus-quarantine.lelx1uqjz@qzalab.cn
        +Enable automated spam training:      yes                         
        +Spam training user:                  spam.2letin98@qzalab.cn         
        +Non-spam(Ham) training user:          ham.q94pdr4mo1@qzalab.cn       
        +SMTP host:                            zcs.qzalab.cn                   
        +Web server HTTP port:                80                           
        +Web server HTTPS port:                443                         
        +Web server mode:                      https                       
        +IMAP server port:                    7143                         
        +IMAP server SSL port:                7993                         
        +POP server port:                      7110                         
        +POP server SSL port:                  7995                         
        +Use spell check server:              yes                         
        +Spell server URL:                    http://zcs.qzalab.cn:7780/aspell.php
        +Enable version update checks:        TRUE                         
        +Enable version update notifications:  TRUE                         
        +Version update notification email:    admin@qzalab.cn                 
        +Version update source email:          admin@qzalab.cn                 

  4) zimbra-mta:                              Enabled                     
  5) zimbra-snmp:                            Enabled                     
  6) zimbra-logger:                          Enabled                     
  7) zimbra-spell:                            Enabled                     
  8) zimbra-proxy:                            Enabled                     
  9) Default Class of Service Configuration:                               
  r) Start servers after configuration        yes                         
  s) Save config to file                                                   
  x) Expand menu                                                           
  q) Quit                                   

Address unconfigured (**) items  (? - help) 3

#这里输入3，修改密码的管理员密码




Store configuration

  1) Status:                                  Enabled                     
  2) Create Admin User:                      yes                         
  3) Admin user to create:                    admin@qzalab.cn                 
** 4) Admin Password                          UNSET                       
  5) Anti-virus quarantine user:              virus-quarantine.lelx1uqjz@qzalab.cn
  6) Enable automated spam training:          yes                         
  7) Spam training user:                      spam.2letin98@qzalab.cn         
  8) Non-spam(Ham) training user:            ham.q94pdr4mo1@qzalab.cn       
  9) SMTP host:                              zcs.qzalab.cn                   
  10) Web server HTTP port:                    80                           
  11) Web server HTTPS port:                  443                         
  12) Web server mode:                        https                       
  13) IMAP server port:                        7143                         
  14) IMAP server SSL port:                    7993                         
  15) POP server port:                        7110                         
  16) POP server SSL port:                    7995                         
  17) Use spell check server:                  yes                         
  18) Spell server URL:                        http://zcs.qzalab.cn:7780/aspell.php
  19) Enable version update checks:            TRUE                         
  20) Enable version update notifications:    TRUE                         
  21) Version update notification email:      admin@qzalab.cn                 
  22) Version update source email:            admin@qzalab.cn                 

Select, or 'r' for previous menu [r] 4



#再输入 4，修改密码的管理员密码



Password for admin@qzalab.cn (min 6 characters): [220BynXaRx] #管理员密码 benet1006 gosum.com

Store configuration

  1) Status:                                  Enabled                     
  2) Create Admin User:                      yes                         
  3) Admin user to create:                    admin@qzalab.cn                 
  4) Admin Password                          set                         
  5) Anti-virus quarantine user:              virus-quarantine.lelx1uqjz@qzalab.cn
  6) Enable automated spam training:          yes                         
  7) Spam training user:                      spam.2letin98@qzalab.cn         
  8) Non-spam(Ham) training user:            ham.q94pdr4mo1@qzalab.cn       
  9) SMTP host:                              zcs.qzalab.cn                   
  10) Web server HTTP port:                    80                           
  11) Web server HTTPS port:                  443                         
  12) Web server mode:                        https                       
  13) IMAP server port:                        7143                         
  14) IMAP server SSL port:                    7993                         
  15) POP server port:                        7110                         
  16) POP server SSL port:                    7995                         
  17) Use spell check server:                  yes                         
  18) Spell server URL:                        http://zcs.qzalab.cn:7780/aspell.php
  19) Enable version update checks:            TRUE                         
  20) Enable version update notifications:    TRUE                         
  21) Version update notification email:      admin@qzalab.cn                 
  22) Version update source email:            admin@qzalab.cn                 

Select, or 'r' for previous menu [r] r


#按回车，返回上级菜单

Main menu

  1) Common Configuration:                                                 
  2) zimbra-ldap:                            Enabled                     
  3) zimbra-store:                            Enabled                     
  4) zimbra-mta:                              Enabled                     
  5) zimbra-snmp:                            Enabled                     
  6) zimbra-logger:                          Enabled                     
  7) zimbra-spell:                            Enabled                     
  8) zimbra-proxy:                            Enabled                     
  9) Default Class of Service Configuration:                               
  r) Start servers after configuration        yes                         
  s) Save config to file                                                   
  x) Expand menu                                                           
  q) Quit                                   

*** CONFIGURATION COMPLETE - press 'a' to apply
Select from menu, or press 'a' to apply config (? - help) a

#输入a,应用

Save configuration data to a file? [Yes]

#回车

Save config in file: [/opt/zimbra/config.9262]

#回车

Saving config in /opt/zimbra/config.9262...done.
The system will be modified - continue? [No] yes

#输入yes

Operations logged to /tmp/zmsetup.01082013-094551.log
Setting local config values...done.
Initializing core config...Setting up CA...done.
Deploying CA to /opt/zimbra/conf/ca ...done.
Creating SSL zimbra-store certificate...done.
Creating new zimbra-ldap SSL certificate...done.
Creating new zimbra-mta SSL certificate...done.
Creating new zimbra-proxy SSL certificate...done.
Installing mailboxd SSL certificates...done.
Installing MTA SSL certificates...done.
Installing LDAP SSL certificate...done.
Installing Proxy SSL certificate...done.
Initializing ldap...done.
Setting replication password...done.
Setting Postfix password...done.
Setting amavis password...done.
Setting nginx password...done.
Creating server entry for zcs.qzalab.cn...done.
Setting Zimbra IP Mode...done.
Saving CA in ldap ...done.
Saving SSL Certificate in ldap ...done.
Setting spell check URL...done.
Setting service ports on zcs.qzalab.cn...done.
Adding zcs.qzalab.cn to zimbraMailHostPool in default COS...done.
Setting zimbraFeatureTasksEnabled=TRUE...done.
Setting zimbraFeatureBriefcasesEnabled=FALSE...done.
Setting MTA auth host...done.
Setting TimeZone Preference...done.
Initializing mta config...done.
Setting services on zcs.qzalab.cn...done.
Creating domain qzalab.cn...done.
Setting default domain name...done.
Creating domain qzalab.cn...already exists.
Creating admin account admin@qzalab.cn...done.
Creating root alias...done.
Creating postmaster alias...done.
Creating user spam.2letin98@qzalab.cn...done.
Creating user ham.q94pdr4mo1@qzalab.cn...done.
Creating user virus-quarantine.lelx1uqjz@qzalab.cn...done.
Setting spam training and Anti-virus quarantine accounts...done.
Initializing store sql database...done.
Setting zimbraSmtpHostname for zcs.qzalab.cn...done.
Configuring SNMP...done.
Setting up syslog.conf...done.
Starting servers...done.
Installing common zimlets...
        com_zimbra_clientuploader...done.
        com_zimbra_tooltip...done.
        com_zimbra_viewmail...done.
        com_zimbra_srchhighlighter...done.
        com_zimbra_adminversioncheck...done.
        com_zimbra_proxy_config...done.
        com_zimbra_email...done.
        com_zimbra_date...done.
        com_zimbra_webex...done.
        com_zimbra_ymemoticons...done.
        com_zimbra_phone...done.
        com_zimbra_cert_manager...done.
        com_zimbra_attachcontacts...done.
        com_zimbra_attachmail...done.
        com_zimbra_bulkprovision...done.
        com_zimbra_url...done.
Finished installing common zimlets.
Restarting mailboxd...done.
Creating galsync account for default domain...done.

You have the option of notifying Zimbra of your installation.
This helps us to track the uptake of the Zimbra Collaboration Server.
The only information that will be transmitted is:
        The VERSION of zcs installed (8.0.2_GA_5569_CentOS6_64)
        The ADMIN EMAIL ADDRESS created (admin@qzalab.cn)

Notify Zimbra of your installation? [Yes] y
Notifying Zimbra of installation via http://www.zimbra.com/cgi-bin/notify.cgi?VER=8.0.2_GA_5569_CentOS6_64&MAIL=admin@qzalab.cn

ERROR: Notification failed
Setting up zimbra crontab...done.


Moving /tmp/zmsetup.01082013-094551.log to /opt/zimbra/log


Configuration complete - press return to exit

```


### 10、重启一下zimbra


我习惯安装完成之后，重新启动一下zimbra。

```
su - zimbra
zmcontrol stop
zmcontrol start

```
### 11、http://zcs.qzalab.cn访问

```
http://zcs.qzalab.cn访问了
管理https://zcs.qzulab.cn:7071
```


### zimbra 邮件服务器管理


```
添加管理员账号：zmprov ca  testadmin@test.com  password  zimbraIsAdminAccount TRUE
升级现有账号为管理员： zmprov ma test@test.com zimbraIsAdminAccount  TRUE
添加普通账号：zmprov ca test@test.com password
删除普通账号：zmprov da test@test.com
重设密码： zmprov sp test@test.com pawwsord
查询mysql密码：zmlocalconfig -s  |grep pass |grep mysql
查询邮箱使用情况：zmprov gqu  mail.test.com
查询指定邮箱详细信息：zmprov gmi test@test.com
查看最大系统邮件大小： postconf message_size_limit
修改最大附件大小：zmprov modifyConfig zimbraMtaMaxMessageSize 2048000
                                    postfix reload
zimbra命令行方式常用的操作
将HTTP登陆方式更改为HTTPHTTPS登陆方式
$ zmprov ms zimbraMailSSLPort （将HTTPS更改成非443端口）
$ zmtlsctl httphttps
$ tomcat restart
smtp认证错误的解决
zmprov ms `zmhostname` zimbraMtaAuthHost mail.example.com
日志服务器错误的解决
$ zmprov getConfig zimbraLogHostname
$ zmprov modifyConfig zimbraLogHostname mail.domain.com
查看系统参数
可以通过zmlocalconfig -s命令查看系统的参数
$ postconf //查看postfix的所有配置
$ zmlocalconfig //查看各种组件的配置信息
$ zmlocalconfig -s|grep zimbra_ldap_userdn　　　　　　 //查看zimbra帐号在LDAP中的DN
$ zmlocalconfig -s|grep zimbra_ldap_userdn //查看zimbra帐号在LDAP中的密码
$ zmlocalconfig -s|grep zimbra_mysql //查看mysql的配置信息
更改系统最大邮件大小：
查看最大系统邮件大小，显示当前系统最大邮件为10M。
$ postconf message_size_limit
message_size_limit = 10240000
将系统最大邮件大小更改为20M。
$ zmprov modifyConfig zimbraMtaMaxMessageSize 2048000
$ postfix reload
更改系统最大附件大小：
将系统中所有帐户允许最大的附件更改为5M
$ zmprov modifyConfig zimbraFileUploadMaxSize 5000000
将系统中mail2.domain.com帐户允许最大的附件更改为20M
$ zmprov modifyServer mail2.domain.com zimbraFileUploadMaxSize 20000000
更改管理员密码：
$ zmprov gaaa　　　　　　　　　　　　　　　　　　　　//列出所有管理员
$ zmprov sp //更改管理员密码
例如：zmprov sp admin q1w2e3r4 或 zmprov sp admin@wish.com q12e3r4
更改LDAP密码：
$ ldap status(start)
$ zmldappasswd –root newpass （root）
$ zmldappasswd newpass (zimbra)
更改MYSQL Database密码：
$ mysql.server status(start)
$ zmmypasswd –root newrootpass
$ zmmypasswd newpass
更改Logger MYSQL Database密码：
$ logmysql.server status(start)
$ zmmylogpasswd –root newrootpass (root）
$ zmmylogpasswd newpass (zimbra)
清空邮箱
$ zmmailbox -z -m rootking@wish.net emptyFolder /[inbox][chats][sent][drafts][junk][trash]
inbox(收件箱) chats(聊天) snet(已发送邮件) drafts(草稿箱) junk(垃圾邮件) trash(已删除邮件)
备份还原LDAP
1、备份LDAP(两个命令是相等的)
1)、ldapsearch -h 服务器对外的地址 -x -D “uid=zimbra,cn=admins,cn=zimbra” -w 密码 objectclass=* > 201014.ldif
2)、ldapsearch -h 服务器对外的地址 -x -D “uid=zimbra,cn=admins,cn=zimbra” -w 密码 > 201014.ldif
2、还原LDAP
ldapadd -h 服务器对外的地址 -x -c -D “uid=zimbra,cn=admins,cn=zimbra” -w 密码 < 20101214.ldif
导出导入用户的邮件
#!/bin/bash
while read USER
do
TODAY=`date`
LOGFILE=”/tmp/bak/backuplog.txt”
echo $TODAY >> $LOGFILE
echo $USER >> $LOGFILE
/opt/zimbra/bin/zmmailbox -z -m $USER gms >> $LOGFILE
zmmailbox -z -m $USER@test.com getRestURL “//?fmt=tgz” > /tmp/bak/$USER.tgz
done < /tmp/user.txt
PS:user.txt里是用户名，不需要跟域名
恢复用户的邮件
zmmailbox -z -m $USER@test.com postRestURL “//?fmt=tgz&resolve=reset” tmp/bak/$USER.tgz
Zimbra之黑名单、白名单
由于zimbra采用ClamAV 做防病毒软件和SpamAssassin 做反垃圾邮件过滤器，但在WEB控制台中ClamAV+SpamAssassin只有6个调节选项。所以如果要想详细的调节防病毒、反垃圾邮件的功能只有更改相应的配置文件了。
例如调节SpamAssassin的配置文件实现黑名单、白名单的功能。
编辑/opt/zimbra/conf/amavisd.conf.in
寻找下列段落，然后加上你要信任的域：
{ # a hash-type lookup table (associative array)
‘nobody@cert.org’ => -3.0,
‘cert-advisory@us-cert.gov’ => -3.0,
‘owner-alert@iss.net’ => -3.0,
‘slashdot@slashdot.org’ => -3.0,
‘bugtraq@securityfocus.com’ => -3.0,
‘ntbugtraq@listserv.ntbugtraq.com’ => -3.0,
‘security-alerts@linuxsecurity.com’ => -3.0,
-10就是无条件信任了，相反+10就是无条件阻挡了。然后存盘，
$ su zimbra
$ zmamavisdctl stop
$ zmamavisdctl start
```


### Zimbra在linux系统上的删除(卸载)方法


登陆root用户
1执行以下面的命令，su切换 到zimbra用户，停止zmcontrol服务，然后再退出zimbra帐户

```
su – zimbra
zmcontrol stop
exit
(you should be root after you run exit)
```

2执行下面的命令，查看系统中是否还有zimbra进程

``` 
ps -ef | grep -i zimbra
```

如果看到还有zimbra进程，就用下面的命令，kill掉进程


2 用kill -9强制杀死进程:

```
kill -9 <zimbra的进程号>
```

3执行以下命令:

```
df
```
如果你能看到 "amavisd"


3 那就执行以下命令:

```
umount /opt/zimbra/amavisd<-new-blah>/tmp
```

4进入你安装时解压出来的源文件目录（即安装文件目录）

```
cd /<tmp_tar_install_dir>/zcs/
```

tmp_tar_install_dir：你的文件路径，如我所下载来的安装包，都是放在/usr/local/src下面的，然后把安装包改名成zcs，这个你应该明白吧？不明白？可联系我

```
cd /usr/local/src/zcs/
```

```
[root@linuxyw zcs]# ls
README.txt data install.sh readme_binary_en_US.txt util
bin docs packages readme_source_en_US.txt
[root@linuxyw zcs]# pwd
/usr/local/src/zcs
```

5)执行以下命令：

```
./install.sh -u
```
6)执行以下的命令完成卸载

```
rm -rf /opt/zimbra
rm -rf /var/log/*zimbra*
rm -rf /tmp/*zimbra*
rm -rf /tmp/hsperfdata*
rm -rf /tmp/install.*
rm -rf /tmp/*swatch*
rm -rf /tmp/log*
```

进以下面的目录中，查看下，确保所有用户拥用者zimbra的文件全部删除

```
/var/log/
/tmp/
```

7)执行以下命令，删除zimbra用户和组:

```
userdel zimbra
userdel postfix
groupdel zimbra
groupdel postfix
```

8）在 /etc/fstab中删除这行内容（如果没有这行就跳过吧）：

```
/dev/shm /opt/zimbra/amavisd-new-2.4.1/tmp tmpfs defaults,users,size=150m,mode=777 0 0
```
9) 在/etc/syslog.conf中删除以下几行，一般在文件最后的位置（如果你是用centos6.x系统，文件名应该/etc/rsyslog.conf

```
local0.* -/var/log/zimbra.log
      auth.* -/var/log/zimbra.log
      mail.* -/var/log/zimbra.log
```
10) 执行以下命令，删除日志配置文件(CentOS, RHEL)

```
rm -f /etc/logrotate.d/zimbra
```

11) 在 /etc/prelink.conf文件中删除以下内容 (CentOS, RHEL)

```
# added for Zimbra
-l /opt/zimbra/lib
-l /opt/zimbra/sleepycat/lib
-l /opt/zimbra/openldap/lib
-l /opt/zimbra/cyrus-sasl/lib
-l /opt/zimbra/mysql/lib
```

12) 在/etc/rc* 中删除zimbra自启动(CentOS, RHEL)

```
chkconfig --del zimbra
```
到此就完成Zimbra卸载了其它的操作系统操作：

```
Other methods:(assuming you didn't already try the above)
(dijichi2) if you get stuck and really want to just purge it from the system, try:


rpm -e `rpm -qa |grep zimbra`
rm -rf /opt/zimbra


delete zimbra entries from /etc/sudoers
delete zimbra entries from root and zimbra crontabs
```
Ubuntu系统操作：

```
On Ubuntu servers dpkg may think that Zimbra is still installed. Check by running dpkg --list (-l) or dpkg -q zimbra* and see if zimbra items are still listed. You can remove them by running:
dpkg --remove zimbra-apache zimbra-ldap zimbra-mta zimbra-spell zimbra-core zimbra-logger zimbra-snmp zimbra-store or


sudo rm -r /opt/zimbra





UnInstalling Zimbra on Linux
```

参考原文地址：http://wiki.zimbra.com/wiki/UnInstalling_Zimbra_on_Linux

参考阿文大师兄的zimbra文档:


