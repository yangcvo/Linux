# 系统功能概述
用户域名解析功能

# 应用/系统拓扑图
 ![image](https://github.com/jinyuchen724/linux-base/raw/master/1.域名系统DNS/dns.jpg)

# 部署安装

## 部署环境

| 主机   |   角色   |   操作系统 |   软件版本  |    备注  |
| ------ | ----- | ----- | ------- | ------ |
| marathon-master01(172.22.1.50)  | dns-master  |   Centos 7.3(x86-64)|  bind-9.9.4 |  主服务器|
|marathon-master02(172.22.1.51)   | dns-slave |Centos 7.3(x86-64)  | bind-9.9.4 | 备服务器 |

#  安装 bind 软件

- 安装dns软件 

```
[root@marathon-master01 opt]# yum install bind bind-utils -y
```

# dns系统配置

- 配置文件
所有的配置文件都是在 /etc/named 目录下
主配置文件 /var/named/named.conf
日志文件在标准目录 /var/log/named 目录下
所有的解析域名数据都在 /var/named/data 目录下

- 拷贝默认配置到 /var/named 目录 

```
[root@marathon-master01 zookeeper]#cp /etc/named.iscdlv.key  /var/named
[root@marathon-master01 zookeeper]#cp /etc/named.root.key  /var/named
```

- 更新根域名服务器列表 

```
[root@marathon-master01 opt]#cd /var/named
[root@marathon-master01 opt]#wget ftp://ftp.rs.internic.net/domain/named.root
```

- 建立目录 

```
[root@marathon-master01 opt]#mkdir -p /var/log/named
[root@marathon-master01 opt]#chown named:named /var/log/named
[root@marathon-master01 opt]#mkdir -p /var/named/op_backup
```
- 删除默认目录配置文件 

```
[root@marathon-master01 opt]#rm -fr /var/named/slaves
```

- 修改主配置文件 /var/named/named.conf 

```
  options {
          listen-on port 53 { any; };
          directory       "/var/named";
          dump-file       "/var/named/cache_dump.db";
      statistics-file "/var/named/named_stats.txt";
      memstatistics-file "/var/named/named_mem_stats.txt";
          allow-query     { any; };
          recursion yes;
          notify yes;
          allow-recursion { any; };
          dnssec-enable yes;
          dnssec-validation yes;
          dnssec-lookaside auto;
          /* 需要调整为slave的ip */
      allow-transfer  { 172.22.1.51;};
          /* Path to ISC DLV key 不加会导致CPU 100%*/
          bindkeys-file "/var/named/named.iscdlv.key";
          managed-keys-directory "/var/named/dynamic";
	  #转发到阿里的dns
          forward first;
          forwarders{
                100.100.2.138;
                100.100.2.136;
        };
  };
  include "/var/named/named.root.key";
  logging {
    category "queries" { "query"; };
    category "default" { "message"; };
    category "general" { "message"; };
    category "database" { "message"; };
    category "security" { "message"; };
    category "config" { "message"; };
    category "resolver" { "message"; };
    category "xfer-in" { "message"; };
    category "xfer-out" { "message"; };
    category "notify" { "message"; };
    category "client" { "message"; };
    category "unmatched" { "message"; };
    category "network" { "message"; };
    category "update" { "message"; };
    category "dispatch" { "message"; };
    category "dnssec" { "message"; };
    category "lame-servers" { "null"; };
  
    channel "query" {
      file "/var/log/named/query.log" versions 5 size 50m;
      severity info;
      print-time yes;
      print-category yes;
    };
  
  
    channel "message" {
      file "/var/log/named/message.log" versions 5 size 20m;
      severity info;
      print-time yes;
      print-category yes;
    };
  
  };
  /* rndc config */
  key "rndc-key" {
        algorithm hmac-md5;
        secret "lIuxoeMronDF7w+zpRc8RQ==";
  };
  controls {
        inet 127.0.0.1 port 953
                allow { 127.0.0.1; } keys { "rndc-key"; };
  };
  /* system zone config */
  zone "." IN {
          type hint;
          file "named.root";
  };
  zone "localhost" IN {
          type master;
          file "named.localhost";
          allow-update { none; };
  };
  zone "1.0.0.127.in-addr.arpa" IN {
          type master;
          file "named.loopback";
          allow-update { none; };
  };
  /* user zone config */
  zone "ops.com" IN {
             type master;
             file "data/ops.com.hosts";
          notify yes;
          allow-update {
                  none;
                  };
  };
  
```

- 如果是slave bind 其他配置都不改，只需把zone配置改下 

```
 zone "sysadmin.xinguangnet.com" IN {
             type slave;
             file "data/ops.com.hosts";
          masters {
                  172.22.1.50;
                  };
  };
```

- 示例zone 文件配置 

```
$TTL 86400
$ORIGIN ops.com.
@       IN  SOA ns1 root(
              1805175654      ;serial
              12h     ;refresh
              7200        ;retry
              604800      ;expire
              86400       ;mininum
              )
              NS  ns1.ops.com.
              NS  ns2.ops.com.
              MX  10  mail.ops.com.

ns1     IN  A   172.22.1.50
ns2     IN  A   172.22.1.51

$TTL 600
marathon-slave01.ops.com.       A       172.22.1.53
marathon-master03.ops.com.      A       172.22.1.52
marathon-master02.ops.com.      A       172.22.1.51
marathon-master01.ops.com.      A       172.22.1.50
```

- 设置 /etc/sysconfig/named 使用自定义named.conf 启动

```
  # cat /etc/sysconfig/named
  # BIND named process options
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~
  #
  # OPTIONS="whatever"     --  These additional options will be passed to named
  #                            at startup. Don't add -t here, enable proper
  #                            -chroot.service unit file.
  #
  # DISABLE_ZONE_CHECKING  --  By default, service file calls named-checkzone
  #                            utility for every zone to ensure all zones are
  #                            valid before named starts. If you set this option
  #                            to 'yes' then service file doesn't perform those
  #                            checks.
  
  OPTIONS=" -c /var/named/named.conf"
```

- rndc key 配置(和named.conf 的key 配置一致)

```
  [root@marathon-master01 opt]## cat /etc/rndc.key
  key "rndc-key" {
          algorithm hmac-md5;
          secret "lIuxoeMronDF7w+zpRc8RQ==";
  };
  
```

- 启动服务和检查

- 加入启动服务中

```
[root@marathon-master01 opt]#chkconfig --level 345 named on
[root@marathon-master01 opt]#systemctl enable named
```

- 启动服务

```
[root@marathon-master01 opt]#service named start
[root@marathon-master01 opt]#systemctl start named.service
```

- 解析测试确认是否正常

```
[root@marathon-master01 opt]#dig @localhost localhost
```

- 修改/etc/reslove.conf文件

```
[root@marathon-master01 opt]# cat /etc/resolv.conf 
;options timeout:2 attempts:3 rotate single-request-reopen
;dns地址
nameserver 172.22.1.50
nameserver 172.22.1.51
;generated by /usr/sbin/dhclient-script
;nameserver 100.100.2.136
;nameserver 100.100.2.138
;查询这个域下的机器
search ops.com
```

- dns api 接口功能安装

```
[root@marathon-master01 opt]#yum install httpd -y
```

- 需要将 apache 用户加入到 named 组 ，这样才有权限访问 zone 文件配置

```
[root@marathon-master01 opt]#usermod -a -G named apache
```

- 设置目录的属主和权限 

```
[root@marathon-master01 opt]#chown named:apache /var/log/named
[root@marathon-master01 opt]#chown -R named:apache /var/named
[root@marathon-master01 opt]#chmod 770 /var/named/op_backup
[root@marathon-master01 opt]#chmod 770 /var/named/
[root@marathon-master01 opt]#chmod 770 /var/log/named
```
- 将cgi-bin 代码 放入到 /var/www/cgi-bin 目录中

具体代码参考 https://github.com/jinyuchen724/linux-base/tree/master/1.%E5%9F%9F%E5%90%8D%E7%B3%BB%E7%BB%9FDNS/cgi-bin

- 启动httpd 服务 

```
[root@marathon-master01 opt]#systemctl enable httpd
[root@marathon-master01 opt]#systemctl start httpd
```

- 将cgi-bin整个目录拷贝至/var/www/下

- 如果操作是查询域名,则返回值是域名的查询结果,IP地址

| 参数名称   |   参数名称   |   
| ------ | ----- | 
| 参数1 : action  | 操作类型,可选项 [add,modify,del,query]  |
|参数2 : domain   | 对其操作的域名操 |
|参数3 : ip   | 域名对应的ip地址 |

- 接口返回值定义

| 返回值   |   返回值   |   
| ------ | ----- | 
| STATUS=OK | STATUS=IP地址  |
|STATUS=错误信息内容   | 返回错误的具体信息 |
|STATUS=IP地址  | 如果操作是查询域名,则返回值是域名的查询结果,IP地址 |

- 接口返回值定义

- 添加域名 : marathon-master01.ops.com ip指向是172.22.1.50 

```
[root@marathon-master01 cgi-bin]# wget -O update_dns.log "http://ns1.ops.com/cgi-bin/dns.cgi?action=add&domain=marathon-master01.ops.com&ip=172.22.1.50&type=A"
[root@marathon-master01 opt]# cat update_dns.log 
STATUS=OK
172.22.1.50
```

- 修改域名 : marathon-master01.ops.com ip指向变更为172.22.1.51

```
[root@marathon-master01 opt]#wget -O 1.txt "http://ns1.sysadmin.xinguangnet.com/cgi-bin/dns.cgi?action=modify&domain=marathon-master01.ops.com&ip=172.22.1.51&type=A"
[root@marathon-master01 opt]#cat 1.txt
STATUS=OK
172.22.1.51
```

- 删除域名 : marathon-master01.ops.com ip指向是172.22.1.51 

```
[root@marathon-master01 opt]#wget -O 1.txt "http://ns1.sysadmin.xinguangnet.com/cgi-bin/dns.cgi?action=del&domain=marathon-master01.ops.com&ip=172.22.1.51&type=A"
```

- 查询域名 : www.sina.com.cn

```
[root@marathon-master01 opt]#wget -O 1.txt "http://ns1.sysadmin.xinguangnet.com/cgi-bin/dns.cgi?action=query&domain=www.sina.com.cn"
[root@marathon-master01 opt]# cat 1.txt
STATUS=101.71.100.123
172.16.1.210
```

注意: 目前saltstack 就使用dns api 接口方式进行自动注册主机名到域名系统中 
 
# 通过命令行方式进行 增 删 改 查 域名
 
- 直接编辑 域文件 例如: /var/named/data/ops.com.hosts 
 
- 直接编辑 域文件 例如: /var/named/data/ops.com.hosts 
  
- 更改 域文件的序列号,默认 +1 即可,用于主备同步 

``` 
@     IN  SOA ns1 root(
          1708252706      ;serial
          12h     ;refresh
          7200        ;retry
          604800      ;expire
          86400       ;mininum
```
 
- 执行 重新载入命令 
 
```
[root@marathon-master01 opt]#rndc reload
```
 
- 检查日志和测试域名解析即可 
 
```
[root@marathon-master01 opt]#tail /var/log/named/messages
[root@marathon-master01 opt]#dig @localhost test.ops.com
```
注意: 上述操作都是在 主服务器上操作,备服务器不许要操作(自动同步)
如果增加新域解析,需要在主备服务器上修改 /var/named/named.conf 增加新的zone配置
