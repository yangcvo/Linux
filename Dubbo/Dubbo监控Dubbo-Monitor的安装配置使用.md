## Dubbo监控Dubbo-Monitor的安装配置使用


前面我安装了Dubbo监控管控台dubbo-admin的安装配置可以到我dubbo书签🔖查看。


### Dubbo Monitor 详细介绍

Dubbo Monitor是针对Dubbo开发的监控系统，参考`dubbo-monitor-simple`改进而成，可以理解为其演化版本。该系统MySQL或者Mongodb记录日志的方式替代了`dubbo-monitor-simple`写文件的方式。

PS: 项目目前依赖的是dubbox的2.8.4版本，但是dubbox并没有修改过监控相关的代码，因此理论上也可以支持dubbo的最新版本。

master分支：MySQL

mongodb分支：mongodb


Dubbo-monitor 码云上面有共享源代码：[基于Dubbox最新版本重新开发的简单监控](http://git.oschina.net/handu/dubbo-monitor)

### Dubbo-Monitor配置介绍

下载监控代码： `git clone https://git.oschina.net/handu/dubbo-monitor.git `

`第一步`：创建数据库
首先创建名称为monitor数据库，编码格式UTF-8。然后将项目sql文件夹下面的create.sql导入到数据库，生成dubbo_invoke表代表成功导入。

`第二步`：编辑项目中application.properties，配置如下：

```bash
#### Dubbo Settings
dubbo.application.name=dubbo-monitor
dubbo.application.owner=ihaozhuo.com
dubbo.registry.address=zookeeper://10.28.32.30:2181?backup=10.47.100.23:2181,10.27.23.75:2181 ##这里我是zk多台集群。一台直接在2181后面结尾就行。
dubbo.protocol.port=6060

#### Database Settings
db.url=jdbc:mysql://<database_host>:<database_port>/monitor?prepStmtCacheSize=517&cachePrepStmts=true&autoReconnect=true&characterEncoding=utf-8    ###这里说明下<database_host>是数据库地址  <database_port> 数据库端口  monitor 数据库
db.username=yjk_user   数据库用户名
db.password=wrefdsf3426 数据库密码
db.maxActive=500  

#### System Manager

manager.username=ihaozhuo    这个是登录监控的时候用户名和密码
manager.password=haozhuo2015
```

`第三步`：打包运行项目
执行maven命令：`mvn clean package`
target文件夹下生成的`dubbo-monitor.war`即为项目部署文件，将其放置到对应服务器目录下，启动服务器即可。例如：`tomcat的webapps`文件夹下。

第四步：访问项目
启动web服务器后，访问地址：`http://IP:[port]/moniotor`，采用配置文件中manager.username和`manager.password`设置值进行登录。


### 服务提供端配置

[Dubbo服务提供端监控配置](http://dubbo.io/User+Guide-zh.htm#UserGuide-zh-%3Cdubbo%3Amonitor%2F%3E)

这里放了张我们现在集群监控图：

![](http://7xrthw.com1.z0.glb.clouddn.com/Dubbo-monitor.png)

