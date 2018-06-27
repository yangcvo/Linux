# salt grains

| 版本| 日期 | 状态 |   修订人  |    摘要  |
| ------ | ----- | ----- | ------- | ------ |
| v1.1  | 2017-07-10  | 创建 |  开源 | salt |


> 官方地址https://docs.saltstack.com/en/latest/ref/grains/all/index.html

用来定义minion端的静态数据，采集服务端你所需要的数据

# 部署环境

| 主机   |   角色   |   操作系统 |   软件版本  |    备注  |
| ------ | ----- | ----- | ------- | ------ |
| hz01-online-ops-salt-01(172.16.8.11)  | salt-master  |   Centos 7.3(x86-64)|  salt-master,salt-api |  主节点|
| hz01-online-ops-salt-02(172.16.8.12)  | salt-master  |   Centos 7.3(x86-64)|  salt-master,salt-api |  主节点|
| hz01-online-ops-salt-03(172.16.8.13)  | salt-minion |   Centos 7.3(x86-64)|  salt-minion |  slave节点 |


- 用个最简单的例子采集minion端监听的端口

> 自定义returner默认路径是/srv/salt/_grains

```
[master]# mkdir -p /srv/salt/_grains
```

- 定义测试grains

```
[master]# cat port_list.py 
#!/usr/bin/python

import os
import re

def test():
  grains = {}
  tcp_list = []
  port_list = []
  cmd="ss -l -n -t | grep LISTEN |awk '{print $4}' |sed 's/.*\://g' |sort -un"
  command = os.popen(cmd)
  for line in command:
    #grains['open_port_list'] = line
    port_list.append(line)
  #port_list = list(set(port_list))
  grains['port_list'] = port_list
  return grains
```

- 同步grains

```
[master]# salt 'hz01-online-ops-salt-01*' saltutil.sync_grains
hz01-online-ops-salt-01.cs1cloud.internal:
    ----------
    beacons:
    engines:
    grains:
        - grains.port_list
    log_handlers:
    modules:
    output:
    proxymodules:
    renderers:
    returners:
    sdb:
    states:
    utils:
```

- 执行命令

```
[master]# salt 'hz01-online-ops-salt-01*' grains.item port_list
hz01-online-ops-salt-01.cs1cloud.internal:
    ----------
    port_list:
        - 22
        - 25
        - 80
        - 111
        - 443
        - 1936
        - 4505
        - 4506
        - 8080
        - 10050
        - 10250
        - 10443
        - 10444

```






















