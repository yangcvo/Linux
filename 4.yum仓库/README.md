# Centos7部署本地局域网yum源

| 版本| 日期 | 状态 |   修订人  |    摘要  |
| ------ | ----- | ----- | ------- | ------ |
| v1.1  | 2017-07-10  | 创建 |  开源 |  yum仓库 |

如果管理大量的服务器，rpm软件包的安装和更新,都需要访问连接Internet，会浪费带宽,并且不安全 为了避免上述情况的弊端，
我们可以通过自己创建本地的repository（仓库）的方法来实现软件包的快速安装和更新. 

# 部署环境

| 主机   |   角色   |   操作系统 |   软件版本  |    备注  |
| ------ | ----- | ----- | ------- | ------ |
| hz01-online-ops-yum-01(172.16.8.10)  | yum-master  |   Centos 7.3(x86-64)|  httpd、createrepo、reposync |  主服务器|


- 获取阿里云镜像repo到本地

```
[hz01-online-ops-yum-01 /opt]# wget -O /etc/yum.repos.d/epel.repo https://mirrors.aliyun.com/repo/epel-7.repo
[hz01-online-ops-yum-01 /opt]# wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo
```

- 安装httpd服务，用于提供存放yum源

```
[hz01-online-ops-yum-01 /opt]# yum install httpd -y 
[hz01-online-ops-yum-01 /opt]# service httpd start
```

使用默认配置即可，如果有特殊需求可以修改配置文件/etc/httpd/conf/httpd.conf。http默认家目录/var/www/html

- 安装yum-utils提供reporsync服务

```
[hz01-online-ops-yum-01 /opt]# yum install yum-utils -y
```

- 选择指定仓库标识作为本地yum源

> 执行yum repolist命令查看yum仓库标识

```
[hz01-online-ops-yum-01 /opt]#yum repolist
已加载插件：fastestmirror
Loading mirror speeds from cached hostfile
源标识                                                                                              源名称                                                                                                                      状态
centos-openshift-origin                                                                             CentOS OpenShift Origin                                                                                                        185
epel/x86_64      #此为阿里云的源                                                                    Extra Packages for Enterprise Linux 7 - x86_64                                                                              12,542
local-centosbase7                                                                                   CentOS-7 - Base                                                                                                              9,363
local-centosextras7                                                                                 CentOS-7 - extras                                                                                                              449
local-centosplus7                                                                                   CentOS-7 - plus                                                                                                                101
local-centosupdates7                                                                                CentOS-7 - updates                                                                                                           2,146
local-epel7                                                                                         epel-7                                                                                                                      12,780
local-mesosphere7                                                                                   mesosphere-7                                                                                                                   119
local-ops                                                                                           local-ops                                                                                                                        7
local-ossec-openvas7                                                                                ossec-openvas-7                                                                                                                718
local-saltstack7                                                                                    saltstack-7                                                                                                                     85
local-zabbix7                                                                                       zabbix-7                                                                                                                       157
repolist: 38,652
```

> 使用epel作为本地yum源，用/var/www/html作为yum仓库根目录

```
[hz01-online-ops-yum-01 /opt]# reposync -r epel -p /var/www/html/
[hz01-online-ops-yum-01 /opt]# reposync -a x86_64 -m -p centos7-x86-64 -r base -r updates -r extras -p /var/www/html/centos7/
```

> 命令执行完毕后，会将阿里云中的epel,centos7系统源同步到本地/var/www/html中,在/var/www/html中自动创建epel/centos7目录用于存放rpm包；第一次同步是时间可能较长，大概1W多个rpm包。

- createrepo 命令创对/var/www/html/epel下的 rpm 包 创建为本地的 YUM 仓库，目的是为生成repodata目录并自动创建索引信息

```
[hz01-online-ops-yum-01 /opt]#createrepo -pdo /var/www/html/epel/ /var/www/html/epel/     #第一个目录是repodata存放目录，第二个目录是需要生成索引信息yum源仓库目录
Spawning worker 0 with 1572 pkgs
Spawning worker 1 with 1572 pkgs
Spawning worker 2 with 1571 pkgs
Spawning worker 3 with 1571 pkgs
Spawning worker 4 with 1571 pkgs
Spawning worker 5 with 1571 pkgs
Spawning worker 6 with 1571 pkgs
Spawning worker 7 with 1571 pkgs
Workers Finished
Saving Primary metadata
Saving file lists metadata
Saving other metadata
Generating sqlite DBs
Sqlite DBs complete

[hz01-online-ops-yum-01 /opt]# createrepo -g /var/www/html/centos7/base/comps.xml /var/www/html/centos7/base/
Spawning worker 0 with 1239 pkgs
Spawning worker 1 with 1239 pkgs
Spawning worker 2 with 1239 pkgs
Spawning worker 3 with 1239 pkgs
Spawning worker 4 with 1239 pkgs
Spawning worker 5 with 1239 pkgs
Spawning worker 6 with 1239 pkgs
Spawning worker 7 with 1238 pkgs
Workers Finished
Saving Primary metadata
Saving file lists metadata
Saving other metadata
Generating sqlite DBs
Sqlite DBs complete

[hz01-online-ops-yum-01 /opt]# createrepo /var/www/html/centos7/extras/
Spawning worker 0 with 39 pkgs
Spawning worker 1 with 38 pkgs
Spawning worker 2 with 38 pkgs
Spawning worker 3 with 38 pkgs
Spawning worker 4 with 38 pkgs
Spawning worker 5 with 38 pkgs
Spawning worker 6 with 38 pkgs
Spawning worker 7 with 38 pkgs
Workers Finished
Saving Primary metadata
Saving file lists metadata
Saving other metadata
Generating sqlite DBs
Sqlite DBs complete

[hz01-online-ops-yum-01 /opt]# createrepo /var/www/html/centos7/updates/
Spawning worker 0 with 82 pkgs
Spawning worker 1 with 82 pkgs
Spawning worker 2 with 82 pkgs
Spawning worker 3 with 82 pkgs
Spawning worker 4 with 82 pkgs
Spawning worker 5 with 82 pkgs
Spawning worker 6 with 81 pkgs
Spawning worker 7 with 81 pkgs
Workers Finished
Saving Primary metadata
Saving file lists metadata
Saving other metadata
Generating sqlite DBs
Sqlite DBs complete

[hz01-online-ops-yum-01 /opt]# ll /var/www/html/epel/repodata/
总用量 36132
-rw-r--r-- 1 root root 11026375 5月  22 09:53 0935db2c5c884bf50d253da67d459207e8d6be8ef211ea66384de969238df4e4-filelists.sqlite.bz2
-rw-r--r-- 1 root root  3185280 5月  22 09:52 20f75a7c2ef859771944f4abc351b8b8843111a43311e717e2f38458e0347411-other.sqlite.bz2
-rw-r--r-- 1 root root  6630057 5月  22 09:53 2f81c07f7dbf491f09cd29dd9f830f0ca09d73b719bdb6c36dac38dd64434b97-primary.sqlite.bz2
-rw-r--r-- 1 root root 10240542 5月  22 09:52 381807e2fa40041857d8bb57ab8c74879f16227d372ee286e76100240b02b823-filelists.xml.gz
-rw-r--r-- 1 root root  3636059 5月  22 09:52 7f9ec5b7b8e1d98b4611b8f6a18f06c197e6bb999f78626c048ea3a90c1e2202-primary.xml.gz
-rw-r--r-- 1 root root  2269109 5月  22 09:52 8d2c397b4363b2e7e3524eeff348695a21185b8d79a20e1ebd04b8b0f92a6b4d-other.xml.gz
-rw-r--r-- 1 root root     3014 5月  22 09:53 repomd.xml

[hz01-online-ops-yum-01 /opt]# ll /var/www/html/centos7/base/repodata/
total 28124
-rw-r--r-- 1 root root 6161792 Jun  9 13:11 03d0a660eb33174331aee3e077e11d4c017412d761b7f2eaa8555e7898e701e0-primary.sqlite.bz2
-rw-r--r-- 1 root root  169476 Jun  9 13:11 29b154c359eaf12b9e35d0d5c649ebd62ce43333f39f02f33ed7b08c3b927e20-comps.xml.gz
-rw-r--r-- 1 root root 7133920 Jun  9 13:10 3b7ec5d1dd09f452a54bacf567f486771f3333400169baa8f62d8107d3d6f2aa-filelists.xml.gz
-rw-r--r-- 1 root root 1617685 Jun  9 13:10 430581635daba01e8b69ff4227305a67f7f7d967d2313277f7368aab8c338d36-other.xml.gz
-rw-r--r-- 1 root root 2916112 Jun  9 13:10 6afcd31233c69da026f363eece2a99e5a79842313fef23bc76b96b69e90dd49d-primary.xml.gz
-rw-r--r-- 1 root root  912297 Jun  9 13:11 d87379a47bc2060f833000b9cef7f9670195fe197271d37fce5791e669265e8b-comps.xml
-rw-r--r-- 1 root root 2669706 Jun  9 13:10 ede157be4cf5c030483ab639f8f18c6daf268d4c233037a1578b3ed8258fa461-other.sqlite.bz2
-rw-r--r-- 1 root root 7202122 Jun  9 13:10 f35d0029ad59e9fca0823be708150f5ee28ee1707cdc9bdaf420da676daafe28-filelists.sqlite.bz2
-rw-r--r-- 1 root root    3716 Jun  9 13:11 repomd.xml

```

- 验证本地yum源是否能正常使用：

> 登录其他内网其他服务器，要能与yum源服务器通信；编写repo文件：

将所有repo文件删除创建新的repo文件
```
[root@hz01-online-ops-opennode-03 /etc/yum.repos.d]#yum repolist
已加载插件：fastestmirror
Determining fastest mirrors
repolist: 0

[root@hz01-online-ops-opennode-03 /etc/yum.repos.d]#vim epel7-local.repo
[epel]
name=epel7-local
baseurl=http://172.16.8.42/epel
enabled=1
gpgcheck=0
```

- 验证是否加载成功

```
[root@hz01-online-ops-opennode-03 /etc/yum.repos.d]# yum clean all
已加载插件：fastestmirror
正在清理软件源： epel
Cleaning up everything
Cleaning up list of fastest mirrors

[root@hz01-online-ops-opennode-03 /etc/yum.repos.d]# yum makecache
已加载插件：fastestmirror
epel                                                                                                                                                                                                           | 2.9 kB  00:00:00     
(1/3): epel/primary_db                                                                                                                                                                                         | 6.3 MB  00:00:00     
(2/3): epel/other_db                                                                                                                                                                                           | 3.0 MB  00:00:00     
(3/3): epel/filelists_db                                                                                                                                                                                       |  11 MB  00:00:01     
Determining fastest mirrors
元数据缓存已建立

[root@hz01-online-ops-opennode-03 /etc/yum.repos.d]# yum repolist
已加载插件：fastestmirror
Loading mirror speeds from cached hostfile
源标识                                                                                                       源名称                                                                                                             状态
epel                                                                                                         epel7-local                                                                                                        12,570
repolist: 12,570
```

- 定时同步

```
vim /root/yum-update.sh
#!/bin/bash

datetime=`date +"%Y-%m-%d"`
exec > /var/log/epel.log　　#同步日志输出
reposync -d -r epel -p /var/www/html/  　　#同步镜像源
if [ $? -eq 0 ];then
    createrepo --update  /var/www/html/epel 　　#每次添加新的rpm时,必须更新epel索引信息
    echo "SUCESS: $datetime epel update successful"else
    echo "ERROR: $datetime epel update failed"fi
#定时任务：每周六凌晨三点同步yum源
crontab -e
0 3 * * 6 /bin/bash /root/yum-update.sh
```

- 添加saltstack源

> 首先去官网获取saltstack的repo

```
[hz01-online-ops-yum-01 /opt]#cat saltstack.repo 
[saltstack-repo]
name=SaltStack repo for Red Hat Enterprise Linux $releasever
baseurl=https://repo.saltstack.com/yum/redhat/$releasever/$basearch/2016.11
enabled=1
gpgcheck=1
gpgkey=https://repo.saltstack.com/yum/redhat/$releasever/$basearch/latest/SALTSTACK-GPG-KEY.pub
       https://repo.saltstack.com/yum/redhat/$releasever/$basearch/latest/base/RPM-GPG-KEY-CentOS-7

```

> 将官网的源同步到本地
```
[hz01-online-ops-yum-01 /opt]#reposync -r saltstack-repo -p /var/www/html/
```

> 生成索引文件
```
[hz01-online-ops-yum-01 /opt]#createrepo -pdo /var/www/html/saltstack-repo/ /var/www/html/saltstack-repo/
Spawning worker 0 with 10 pkgs
Spawning worker 1 with 10 pkgs
Spawning worker 2 with 10 pkgs
Spawning worker 3 with 10 pkgs
Spawning worker 4 with 9 pkgs
Spawning worker 5 with 9 pkgs
Spawning worker 6 with 9 pkgs
Spawning worker 7 with 9 pkgs
Workers Finished
Saving Primary metadata
Saving file lists metadata
Saving other metadata
Generating sqlite DBs
Sqlite DBs complete

[hz01-online-ops-yum-01 /opt]#ll /var/www/html/saltstack-repo/repodata/
总用量 268
-rw-r--r-- 1 root root 76839 5月  22 13:24 0318c5a104feb4541c3eceba4a0da53b8956688fc3465909b42287e249beb82b-filelists.xml.gz
-rw-r--r-- 1 root root 87189 5月  22 13:24 055703cdbd83ee9b537db585998e5886eb9dd3032de2a9fb917043c862a177a3-filelists.sqlite.bz2
-rw-r--r-- 1 root root 16937 5月  22 13:24 0aa49b095b4620c2108e9f7c0e0f8186f086d07ddd1e667e14e1edbdbe40163b-other.xml.gz
-rw-r--r-- 1 root root 31871 5月  22 13:24 4c6cf849557022c8c1c08c83ec9f458109a644a761b68497d1932f099be053e4-primary.sqlite.bz2
-rw-r--r-- 1 root root 26612 5月  22 13:24 f03715e896fc4b9db7b2442801cf7bbde82e8bc316c06ee4d99154cc05ebf9f7-other.sqlite.bz2
-rw-r--r-- 1 root root 19677 5月  22 13:24 fe7eac489d97d90593f17e6d19ae19c615822a763072df970f4e587f4774eb39-primary.xml.gz
-rw-r--r-- 1 root root  2988 5月  22 13:24 repomd.xml
```

在随便一个内网机器上配置salt源

```
[root@hz01-online-ops-opennode-03 /etc/yum.repos.d]#cat epel7-local.repo 
[epel]
name=epel7-local
baseurl=http://172.16.8.42/epel
enabled=1
gpgcheck=0

[salstack]
name=saltstack-7
baseurl=http://172.16.8.42/saltstack-repo/
gpgcheck=0
```

```
[root@hz01-online-ops-opennode-03 /etc/yum.repos.d]#yum list |grep salt
PyYAML.x86_64                           3.11-1.el7                     @local-saltstack7
python-tornado.x86_64                   4.2.1-1.el7                    @local-saltstack7
python-zmq.x86_64                       15.3.0-2.el7                   @local-saltstack7
salt.noarch                             2016.11.7-1.el7                @local-saltstack7
salt-minion.noarch                      2016.11.7-1.el7                @local-saltstack7
python-salttesting.noarch               2015.7.10-1.el7                epel     
salt.noarch                             2016.11.9-2.el7                salstack 
salt-api.noarch                         2016.11.9-2.el7                salstack 
salt-cloud.noarch                       2016.11.9-2.el7                salstack 
salt-master.noarch                      2016.11.9-2.el7                salstack 
salt-minion.noarch                      2016.11.9-2.el7                salstack 
salt-ssh.noarch                         2016.11.9-2.el7                salstack 
salt-syndic.noarch                      2016.11.9-2.el7                salstack 
```

如果其他需要稳定版本的yum源方法和这个是一样的。






