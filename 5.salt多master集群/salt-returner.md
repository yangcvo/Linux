# salt returner

| 版本| 日期 | 状态 |   修订人  |    摘要  |
| ------ | ----- | ----- | ------- | ------ |
| v1.1  | 2017-07-10  | 创建 |  开源 | salt |


> 官方地址https://docs.saltstack.com/en/latest/ref/returners/

在minion端执行后的结果数据一般是返回到master端的，这个作用就是用来定义执行的结果数据存储的
地方，可以是文件、内存、数据库、消息队列等等，主要就看如何去写returner。

# 部署环境

| 主机   |   角色   |   操作系统 |   软件版本  |    备注  |
| ------ | ----- | ----- | ------- | ------ |
| hz01-online-ops-salt-01(172.16.8.11)  | salt-master  |   Centos 7.3(x86-64)|  salt-master,salt-api |  主节点|
| hz01-online-ops-salt-02(172.16.8.12)  | salt-master  |   Centos 7.3(x86-64)|  salt-master,salt-api |  主节点|
| hz01-online-ops-salt-03(172.16.8.13)  | salt-minion |   Centos 7.3(x86-64)|  salt-minion |  slave节点 |


- 用个最简单的例子如将结果写入文件

> 自定义returner默认路径是/srv/salt/_returners

```
[master]# mkdir -p /srv/salt/_returners
```

- 定义测试returner

```
[master]# cat file.py 
import json
import time
 
def returner(ret):
    now = time.localtime() 
    now = time.strftime("%Y-%m-%d %H:%M:%S",now)
    result_file = '/tmp/returner'
    result = file(result_file,'a+')
    result.write('At'+str(json.dumps(now))+'\n')
    result.write(str(json.dumps(ret))+'\n')
    result.close()
```

- 同步returners

```
[master]# salt '*' saltutil.sync_returners 
hz01-online-ops-salt-01:
    - returners.file
hz01-online-ops-salt-02:
    - returners.file
hz01-online-ops-salt-03:
    - returners.file
```

- 执行命令

```
[master]# salt '*' cmd.run 'hostname' --return file
```

- 查看returner存储的日志文件

```
# salt '*' cmd.run 'cat /tmp/returner'
hz01-online-ops-salt-01:
    At"2018-06-06 17:11:09"
    {"fun_args": ["hostname"], "jid": "20180606171109870043", "return": "hz01-online-ops-salt-01", "retcode": 0, "success": true, "fun": "cmd.run", "id": "hz01-online-ops-opennode-01.cs1cloud.internal"}
hz01-online-ops-salt-02:
    At"2018-06-06 17:11:09"
    {"fun_args": ["hostname"], "jid": "20180606171109870043", "return": "hz01-online-ops-salt-02", "retcode": 0, "success": true, "fun": "cmd.run", "id": "hz01-online-ops-opennode-02.cs1cloud.internal"}
hz01-online-ops-salt-03:
    At"2018-06-06 17:11:09"
    {"fun_args": ["hostname"], "jid": "20180606171109870043", "return": "hz01-online-ops-salt-03", "retcode": 0, "success": true, "fun": "cmd.run", "id": "hz01-online-ops-opennode-03.cs1cloud.internal"}
```






















