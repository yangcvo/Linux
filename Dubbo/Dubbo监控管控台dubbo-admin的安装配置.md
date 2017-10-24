## Dubbo管控台dubbo-admin的安装配置


## 前言：

公司之前的java框架都是根据一层层代理去实现的，这次整体架构换Dubbo去实现分布式服务，Dubbo对于服务提供方和服务消费方。监控也是监控服务状态可以降权，在运维管理维护方面也提高了很大帮助。

Dubbo框架设计一共划分了10个层，而最上面的Service层是留给实际想要使用Dubbo开发分布式服务的开发者实现业务逻辑的接口层。图中左边淡蓝背景的为服务消费方使用的接口，右边淡绿色背景的为服务提供方使用的接口， 位于中轴线上的为双方都用到的接口。

下面，结合Dubbo官方文档，我们分别理解一下框架分层架构中，各个层次的设计要点：

```
1. 服务接口层（Service）：该层是与实际业务逻辑相关的，根据服务提供方和服务消费方的业务设计对应的接口和实现。
2. 配置层（Config）：对外配置接口，以ServiceConfig和ReferenceConfig为中心，可以直接new配置类，也可以通过spring解析配置生成配置类。
3. 服务代理层（Proxy）：服务接口透明代理，生成服务的客户端Stub和服务器端Skeleton，以ServiceProxy为中心，扩展接口为ProxyFactory。
4. 服务注册层（Registry）：封装服务地址的注册与发现，以服务URL为中心，扩展接口为RegistryFactory、Registry和RegistryService。可能没有服务注册中心，此时服务提供方直接暴露服务。
5. 集群层（Cluster）：封装多个提供者的路由及负载均衡，并桥接注册中心，以Invoker为中心，扩展接口为Cluster、Directory、Router和LoadBalance。将多个服务提供方组合为一个服务提供方，实现对服务消费方来透明，只需要与一个服务提供方进行交互。
6. 监控层（Monitor）：RPC调用次数和调用时间监控，以Statistics为中心，扩展接口为MonitorFactory、Monitor和MonitorService。
7. 远程调用层（Protocol）：封将RPC调用，以Invocation和Result为中心，扩展接口为Protocol、Invoker和Exporter。Protocol是服务域，它是Invoker暴露和引用的主功能入口，它负责Invoker的生命周期管理。Invoker是实体域，它是Dubbo的核心模型，其它模型都向它靠扰，或转换成它，它代表一个可执行体，可向它发起invoke调用，它有可能是一个本地的实现，也可能是一个远程的实现，也可能一个集群实现。
8. 信息交换层（Exchange）：封装请求响应模式，同步转异步，以Request和Response为中心，扩展接口为Exchanger、ExchangeChannel、ExchangeClient和ExchangeServer。
9. 网络传输层（Transport）：抽象mina和netty为统一接口，以Message为中心，扩展接口为Channel、Transporter、Client、Server和Codec。
10. 数据序列化层（Serialize）：可复用的一些工具，扩展接口为Serialization、 ObjectInput、ObjectOutput和ThreadPool。
```

### 一、Dubbo管控台简介

管理控制台的功能主要包括：`路由规则`，`动态配置`，`服务降级`，`访问控制`，`权重调整`，`负载均衡`，等管理功能。


二、环境准备

IP：10.132.18.23 
部署容器：tomcat7
端口：8080

本次dubbo-admin管控台的安装是基于zookeeper注册中心，安装前请确保已成功安装zookeeper
zookeeper的集群安装可参照：[ZooKeeper集群快速搭建与优化](http://blog.yangcvo.me/2016/05/28/%E5%A4%A7%E6%95%B0%E6%8D%AEhadoop/zookeeper/ZooKeeper%E9%9B%86%E7%BE%A4%E5%BF%AB%E9%80%9F%E6%90%AD%E5%BB%BA%E4%B8%8E%E4%BC%98%E5%8C%96/)

### 三、具体的安装步骤

dubbo-admin的下载，可自行到官网下载：https://github.com/alibaba/dubbo 

```
git clone https://github.com/alibaba/dubbo.git
mvn package -Dmaven.skip.test=true
```
**1、下载或者上传tomcat7（apache-tomcat-7.0.62.tar）到/sr/**
下载或者上传Dubbo管控台程序dubbo-admin-2.5.3.war到/srv/
创建对应目录&& 创建对应服务用户，给予授权属组。

**2、解压tomcat7的安装包并重命名为dubbo-monitor**
**3、移除/srv/tomcat/tomcat_monitor/webapps/目录下的所有文件.**

```bash
[root@tomcat-monitor_01 ~]# mkdir /srv/tomcat/
[root@tomcat-monitor_01 ~]# useradd -s /sbin/nologin -G tomcat 
[root@tomcat-monitor_01 ~]# tar -zxvf apache-tomcat-7.0.62.tar.gz
[root@tomcat-monitor_01 ~]# mv apache-tomcat-7.0.62 tomcat_monitor
[root@tomcat-monitor_01 ~]# mv tomcat_monitor /srv/tomcat/.
[root@tomcat-monitor_01 ~]# cd /srv/tomcat/tomcat_monitor/webapps
[root@tomcat-monitor_01 ~]# rm -rf *
[root@tomcat-monitor_01 ~]# chown -R tomcat:tomcat /srv/tomcat
```
 
**4、将dubbo-admin-2.5.3.war直接解压对应目录/srv/tomcat/tomcat_monitor/webapps/.**
**5、解压dubbo-admin-2.5.3.war并重命名为ROOT**

```bash
[root@tomcat-monitor_01 ~]# unzip dubbo-admin-2.5.3.war -d ROOT
```

注意：解压重命名完成后，记得把之前的dubbo-admin-2.5.3.war包移除，不然后面在启动tomcat的时候又会把dubbo-admin-2.5.3.war解压，造成一些不可描述的问题。

``` bash
[root@tomcat-monitor_01 ~]# rm -rf dubbo-admin-2.5.3.war
```

**6、配置dubbo.properties**

```bash
[root@tomcat-monitor_01 ~]#  vim ROOT/WEB-INF/dubbo.properties
将配置信息配置为：
dubbo.registry.address=zookeeper://10.28.32.30:2181?backup=10.47.100.23:2181,10.27.23.75:2181
dubbo.admin.root.password=TUJ3dKXqyAzuddTTzaYseB   
dubbo.admin.guest.password=guest  
```


**参数说明：**

``` bash
dubbo.registry.address：注册中心的配置地址，上文中注册中心是使用zookeeper三台机器的集群，如果只有一台机器，则配置为：dubbo.registry.address=zookeeper://10.28.32.30:2181即可
dubbo.admin.root.password：管控台root用户的登录密码
dubbo.admin.guest.password：管控台guest用户的登录密码
```

7、切换到root用户，开启防火墙的8080端口

```bash
# vi /etc/sysconfig/iptables
增加：
## duoob-admin-tomcat
-A INPUT -i  eth0 -p tcp -m state --state NEW -m tcp --dport 8080 -j ACCEPT  ##指定内网访问
重启防火墙：
# service iptables restart  
```

**8、启动tomcat（普通用户启动）加入开机启动项 **

```bash
[tomcat@tomcat-monitor_01 ~]# /srv/tomcat/tomcat_monitor/bin/startup.sh
切换到root用户，修改rc.local文件
[tomcat@tomcat-monitor_01 ~]# vi /etc/rc.local
增加以下脚本（脚本大意为：切换到dreyer05用户，执行xx.sh）
[tomcat@tomcat-monitor_01 ~]#su - tomcat '/srv/tomcat/tomcat_monitor/bin/startup.sh start'
```

这里我做了Nginx代理，所有防火墙设置内网网卡可以互通。

访问：

![](http://7xrthw.com1.z0.glb.clouddn.com/Dubbo_01.png)


