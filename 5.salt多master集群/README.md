# Centos7部署本地局域网yum源

| 版本| 日期 | 状态 |   修订人  |    摘要  |
| ------ | ----- | ----- | ------- | ------ |
| v1.1  | 2017-07-10  | 创建 |  开源 | salt |

对于运维来说,基于状态的配置管理已经向自动化迈进了一大步,以状态为核心的运维,让状态本身有了可管理性
在运维过程中我们会发现,同样的一个配置,我们会在不同的时间,不同的地点重复的配置,这个时候,配置管理就有了重复性
而另外一些则是按照一定的规律在发展,这些按照一定规律发展的配置,就是可预测的.
运维工作的本身是可管理,可重复,可预测的.基于这样的理念,就可以更进一步的推进运维自动化,甚至到智能化. 

# 部署环境

| 主机   |   角色   |   操作系统 |   软件版本  |    备注  |
| ------ | ----- | ----- | ------- | ------ |
| hz01-online-ops-salt-01(172.16.8.11)  | salt-master  |   Centos 7.3(x86-64)|  salt-master,salt-api |  主节点|
| hz01-online-ops-salt-02(172.16.8.12)  | salt-master  |   Centos 7.3(x86-64)|  salt-master,salt-api |  主节点|
| hz01-online-ops-salt-03(172.16.8.13)  | salt-slave |   Centos 7.3(x86-64)|  salt-slave |  slave节点 |


# salt服务端安装

> 根据之前安装的yum仓库配置，这里直接安装即可 

```
[hz01-online-ops-salt-01 /opt]# yum install salt-master -y
```

- 设置配置文件

/etc/salt/master 配置文件选项介绍
最基本字段: 
  interface: 服务端监听IP
  auto_accept: True 自动接受客户端key 

```
interface: 172.16.8.11
auto_accept: True
```

- 运行服务端

```
[hz01-online-ops-salt-01 /opt]#systemctl enable salt-master.service
[hz01-online-ops-salt-01 /opt]#systemctl start salt-master.service
```

> 调试模式: salt-master -l debug ,后台运行: salt-master -d

> 4505(publish_port):salt的消息发布系统,4506(ret_port):salt客户端与服务端通信的端口,主要用来接受消息 所以确保客户端能跟服务端的这2个端口通信

# salt客户端安装

```
[hz01-online-ops-salt-01 /opt]#yum install salt-minion -y
```

- 设置配置文件

/etc/salt/minion 配置文件选项介绍

最基本字段:
    master: 服务端主机名或ip(请设置域名)
    id: 客户端主机名(在服务端看到的客户端的名字,不设置默认是主机名) 

- 运行客户端

```
[hz01-online-ops-salt-01 /opt]#systemctl enable salt-minion.service
[hz01-online-ops-salt-01 /opt]#systemctl start salt-minion.service
```

- 服务端和客户端认证过程

> 客户端minion在第一次启动时,会在/etc/salt/pki/minion/下自动生成minion.pem(private key), minion.pub(public key)，
然后将minion.pub发送给master,master在接收到minion的public key后，通过salt-key命令accept minion public key，
这样在master的/etc/salt/pki/master/minions下的将会存放以minion id命名的public key, 然后master就能对minion发送指令了

```
#服务端查看key
[hz01-online-ops-salt-01 /opt]#salt-key
Accepted Keys:
hz01-online-ops-opennode-01.cs1cloud.internal
Denied Keys:
Unaccepted Keys:
Rejected Keys:

#服务端接受key
[hz01-online-ops-salt-01 /opt]#salt-key -a 'client-name'

#测试test.ping命令
[hz01-online-ops-salt-01 /opt]#salt '*' 'test.ping'
hz01-online-ops-opennode-01.cs1cloud.internal:
    True
	
#查看使用手册
[hz01-online-ops-salt-01 /opt]#salt '*' sys.doc
```

- 设置客户端定时运行

```
salt '*' schedule.add job1 function=’test.ping’ seconds=3600
salt '*' schedule.build_schedule_item job1 function=’test.ping’ seconds=3600
salt '*' schedule.delete job1
salt '*' schedule.disable
salt '*' schedule.disable_job job1
salt '*' schedule.enable
salt '*' schedule.enable_job job1
salt '*' schedule.list
salt '*' schedule.list show_all=True
salt '*' schedule.modify job1 function=’test.ping’ seconds=3600
salt '*' schedule.purge
salt '*' schedule.reload
salt '*' schedule.run_job job1
salt '*' schedule.run_job job1 force=True
salt '*' schedule.save
```

> 每10分钟运行一次

```
salt '*' schedule.add job1 function='state.highstate' seconds=600
salt '*' schedule.save
```

- 第二种方法设置定时任务(推荐)

> 在pillar中设置top.sls 

```
# cat srv/pillar/top.sls
base:
  '*':
    - schedule
```

> schedule 配置(每10分钟运行一次) 

```
# cat /srv/pillar/schedule.sls 
# 每天一点半执行
schedule:        
  highstate:
    function: state.highstate
    cron: '30 1 * * *'

#每十分钟执行
schedule:
    highstate:
      function: state.highstate
      seconds: 0
      minutes: 10
      hours: 0
```

> 同步pillar数据
```
salt "*" saltutil.refresh_pillar
```

>查看定时配置 

```
salt "salt-dns-doc" pillar.get schedule
```

- 安装salt-api 功能(HTTP API)

```
[hz01-online-ops-salt-01 /opt]#yum install salt-api -y
```

- 配置Salt-API,生成/etc/salt/master.d/api.conf

```
[hz01-online-ops-salt-01 /opt]#vim /etc/salt/master.d/api.conf
rest_cherrypy:
    port: 8080
    ssl_crt: /etc/pki/tls/certs/localhost.crt
    ssl_key: /etc/pki/tls/certs/localhost.key
```

- 生成自签名证书(用于ssl)

```
[hz01-online-ops-salt-01 /opt]#yum install pyOpenSSL -y
[hz01-online-ops-salt-01 /opt]#yum install salt-minion
[hz01-online-ops-salt-01 /opt]#salt-call -l info tls.create_self_signed_cert
    Created Private Key: "/etc/pki/tls/certs/localhost.key." Created Certificate: "/etc/pki/tls/certs/localhost.crt."
```

- 创建用于salt-api的用户

```
[hz01-online-ops-salt-01 /opt]#useradd -M -s /sbin/nologin saltapi
[hz01-online-ops-salt-01 /opt]#echo "123456" | passwd saltapi --stdin
```  

- 配置eauth认证

```
[hz01-online-ops-salt-01 /opt]#vim /etc/salt/master.d/eauth.conf
external_auth:
  pam:
    saltapi:
      - .*
      - '@wheel'
      - '@runner'
```

- 重启api服务

```
[hz01-online-ops-salt-01 /opt]#systemctl restart salt-master
[hz01-online-ops-salt-01 /opt]#systemctl enable salt-api
[hz01-online-ops-salt-01 /opt]#systemctl restart salt-api
```

- saltapi验证测试

登陆接口:
```
[hz01-online-ops-salt-01 /opt]#curl -k https://localhost:8080/login -H "Accept: application/json" \
        -d username='saltapi' \
        -d password='123456' \
        -d eauth='pam'
```

响应值:

```
{"return": [{"perms": [".*", "@wheel", "@runner"], "start": 1527228515.855898, "token": "1139e5a50866495f53359871aa7d620e91903b84", "expire": 1527271715.855898, "user": "saltapi", "eauth": "pam"}]}
```

测试test.ping命令

```
[hz01-online-ops-salt-01 /opt]#curl -k https://localhost:8080/ \
        -X POST \
        -H "Accept: application/json" \
        -H "X-Auth-Token: "1139e5a50866495f53359871aa7d620e91903b84"" \
        -H "Content-Type: application/json" \
        -d \
   '[
     {
       "client": "local",
       "tgt": "hz01-online-ops-salt-01*",
       "fun": "test.ping"
     }
   ]'
```

响应值
```
{"return": [{"hz01-online-ops-salt-01": true}]}
```



# 多master安装部署

多主系统，允许Salt主冗余，促进与minion多点通信。所有主都在运行，任何主都可以给minion发送命令。 主不同步任何信息，Keys需要被所有主接收，
为了确保file_roots等共享文件一致，需要使用lsyncd、nfs、共享存储等手段来实现。以lsyncd为例： 

在另一台机器上安装salt-master（同上）

- 将原来master上的master密钥拷贝到新的master上一份 

```
[hz01-online-ops-salt-01 /opt]#scp /etc/salt/pki/master/master.* root@z01-online-ops-salt-02:/etc/salt/pki/master/
root@z01-online-ops-salt-02's password: 
master.pem                                                                                                                                                                                          100% 1674     1.6KB/s   00:00    
master.pub   
```

- 重启master节点

```
[hz01-online-ops-salt-01 /opt]#systemctl enable salt-minion.service
[hz01-online-ops-salt-01 /opt]#systemctl start salt-minion.service
```

- 修改minion配置文件/etc/salt/minion，设置两个master 

```
[hz01-online-ops-salt-01 /opt]#vim /etc/salt/minion
master:
  - 172.16.8.11
  - 172.16.8.12

```

# 使用lsyncd自动实时同步(互相同步的主机要做ssh互信)

```
yum install lsyncd
```

- 参数介绍

```
  # vi etc/lsyncd.conf
  settings {
      logfile      ="/var/log/lsyncd/lsyncd.log",
      statusFile   ="/usr/local/lsyncd/lsyncd.status",
      inotifyMode  = "CloseWrite",
      maxProcesses = 7,
      ## nodaemon =true,
      }
  
  
  settings：全局设置
  logfile：定义日志文件
  statusFile：定义状态文件
  inotifyMode：指定inotify监控的事件，默认是CloseWrite，还可以是Modify或CloseWrite or Modify
  maxProcesses：同步进程的最大个数。假如同时有20个文件需要同步，而maxProcesses = 8，则最大能看到有8个rysnc进程
  nodaemon：表示不启用守护模式，默认true
  statusInterval：将lsyncd的状态写入上面的statusFile的间隔，默认10秒
  maxDelays：累计到多少所监控的事件激活一次同步，即使后面的delay延迟时间还未到
  
  
  sync {
      default.rsync,		
      source    = "/tmp/src",	
      target    = "/tmp/dest",
                 
  sync：定义同步参数，可以继续使用maxDelays来重写settings的全局变量
  default.：指定lsyncd以什么模式运行：rsync、rsyncssh、direct三种模式
  - default.rsync ：本地目录间同步，使用rsync，也可以达到使用ssh形式的远程rsync效果，或daemon方式连接远程rsyncd进程
  - default.direct ：本地目录间同步，使用cp、rm等命令完成差异文件备份
  - default.rsyncssh ：同步到远程主机目录，rsync的ssh模式，需要使用key来认证
  source：同步的源目录，使用绝对路径
  target：目的地址.对应不同的模式有几种写法
  - /tmp/dest：本地目录同步，可用于direct和rsync模式
  - 172.16.2.42:/tmp/dest：同步到远程服务器目录，可用于rsync和rsyncssh模式，拼接的命令类似于/usr/bin/rsync -ltsd --delete --include-from=- --exclude=* SOURCE TARGET，剩下的就是rsync的内容了，比如指定username，免密码同步
  - 172.16.2.43::module同步到远程服务器目录，用于rsync模式
  init：一个优化选项，当init = false，只同步进程启动以后发生改动事件的文件，原有的目录即使有差异也不会同步。默认是true
  delay：累计事件，等待rsync同步延时时间，默认15秒（最大累计到1000个不可合并的事件）。也就是15s内监控目录下发生的改动，会累积到一次rsync同步，避免过于频繁的同步。（可合并的意思是，15s内两次修改了同一文件，最后只同步最新的文件）
  delete：为了保持target与souce完全同步，Lsyncd默认会delete = true来允许同步删除。它除了false，还有startup、running值
  
  
  rsync     = {				
          binary    = "/usr/bin/rsync",
          archive   = true,
          compress  = true,			
          verbose   = true
          }
      }
  
  
  compress：压缩传输默认为true。在带宽与cpu负载之间权衡，本地目录同步可以考虑把它设为false
  bwlimit：限速，单位kb/s，与rsync相同
  perms：默认保留文件权限
  - 其它rsync的选项：rsyncssh模式独有的配置项，如host、targetdir、rsync_path、password_file。rsyncOps={"-avz","--delete"}这样的写法在2.1.*版本已经不支持

```


```
settings {
    logfile      ="/var/log/lsyncd/lsyncd.log",
    statusFile   ="/usr/local/lsyncd/lsyncd.status",
    inotifyMode  = "CloseWrite",
    maxProcesses = 1,
    -- nodaemon =true,
    }

sync {
    default.rsync,
    source    = "/srv",
    target = "172.16.8.104:/srv",            #对方机器的地址及目录
    -- maxDelays = 5,
    delay = 0,
    -- init = false,
    rsync    = {
        binary = "/usr/bin/rsync",
        archive = true,
        compress = true,
        verbose   = true,
        bwlimit = 2000
        }
    }

sync {
    default.rsync,
    source    = "/etc/salt/pki/master",
    target = "172.16.8.104:/etc/salt/pki/master",        #对方机器的地址及目录
    -- maxDelays = 5,
    delay = 0,
    -- init = false,
    rsync    = {
        binary = "/usr/bin/rsync",
        archive = true,
        compress = true,
        verbose   = true,
        bwlimit = 2000
        }
    }


```










