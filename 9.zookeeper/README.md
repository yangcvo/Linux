| 版本 | 日期 | 状态 | 修订人 | 摘要 |
| - | - | - | - | - |
| V1.0 | 2018-05-20 | 初次编写 | 开源 | 初次编写 |

# 集群环境说明 

| 主机名称 | 操作系统类型 | 内网IP地址 |
| - | - | - |
| ali03-prod-toko-zookeeper-01 | CentOS Linux release 7.4 | 10.11.11.22 |
| ali03-prod-toko-zookeeper-02 | CentOS Linux release 7.4 | 10.11.11.27 |
| ali03-prod-toko-zookeeper-03 | CentOS Linux release 7.4 | 10.11.11.28 |


# 二、部署Zookeeper集群

- 安装Java环境

Zookeeper是用Java编写，需要依赖Java的运行环境，安装完后执行<kbd>java -version</kbd>命令检查JDK是否安装成功。如下输出信息：
```
[root@ali03-prod-toko-zookeeper-01 ~]# java -version
java version "1.8.0_65"
Java(TM) SE Runtime Environment (build 1.8.0_65-b17)
Java HotSpot(TM) 64-Bit Server VM (build 25.65-b01, mixed mode)
```
> 本环境中的JDK均是使用脚本进行安装，安装路径均在/xinguang/下 安装过程就略过。以下是脚本内容:

```
#!/bin/bash

SRC_URI="https://tol-res.oss-cn-shanghai-internal.aliyuncs.com/java/jdk-8u65-linux-x64.tar.gz"
PKG_NAME=`basename $SRC_URI`
DIR=`pwd`
DATE=`date +%Y%m%d%H%M%S`

\mv /xinguang/java /xinguang/java.bak.$DATE &> /dev/null
mkdir -p /xinguang/java
mkdir -p /xinguang/install
cd /xinguang/install

if [ ! -s $PKG_NAME ]; then
  wget -c $SRC_URI
fi

mv jdk1.8.0_65 jdk1.8.0_65_bak.$DATE &> /dev/null

tar zxvf $PKG_NAME
mv jdk1.8.0_65/*  /xinguang/java
rm -rf jdk1.8.0_65
#add PATH
if ! cat /etc/profile | grep 'export CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar:$JAVA_HOME/lib:$JRE_HOME/lib:$CLASSPATH' &> /dev/null;then
	echo "export JAVA_HOME=/xinguang/java" >> /etc/profile
	echo "export JRE_HOME=/xinguang/java/jre" >> /etc/profile
	echo 'export CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar:$JAVA_HOME/lib:$JRE_HOME/lib:$CLASSPATH' >> /etc/profile
	echo 'export PATH=$PATH:$JAVA_HOME/bin' >> /etc/profile
fi

cd $DIR
source /etc/profile
bash
```

- 下载Zookeeper安装包

从Apache仓库中下载Zookeeper的二进制执行文件，本环境所用的Zookeeper版本为3.4.6

```
[root@ali03-prod-toko-zookeeper-01 ~]# wget https://archive.apache.org/dist/zookeeper/zookeeper-3.4.6/zookeeper-3.4.6.tar.gz
```

- 解压并成zoo.cfg文件

将下载好的Zookeeper二进制文件包解压到/xinguang下，更改Zookeeper所属主和组为root，生成zoo.cfg配置文件

```
[root@ali03-prod-toko-zookeeper-01 ~]# tar -xf zookeeper-3.4.6.tar.gz -C /xinguang
[root@ali03-prod-toko-zookeeper-01 ~]# cd /xinguang && mv zookeeper-3.4.6 zookeeper
[root@ali03-prod-toko-zookeeper-01 ~]# chown -R root:root /xinguang/zookeeper/
[root@ali03-prod-toko-zookeeper-01 ~]# cd /xinguang/zookeeper/conf && cp zoo_sample.cfg zoo.cfg
```

- 设置zoo.cfg文件

以下以ali03-prod-toko-zookeeper-01节点为例设置Zookeeper的配置文件，另外2个节点的配置文件也是同样设置

```
[root@ali03-prod-toko-zookeeper-01 ~]# vim /xinguang/zookeeper/conf/zoo.cfg 
tickTime=2000
initLimit=10
syncLimit=5
dataDir=/xinguang/zookeeper/data
dataLogDir=/xinguang/zookeeper/logs
clientPort=2181
server.1=10.11.11.22:2888:3888
server.2=10.11.11.27:2888:3888
server.3=10.11.11.28:2888:3888
```

- 创建myid文件

以下是ali03-prod-toko-zookeeper-01节点创建myid文件

```
[root@ali03-prod-toko-zookeeper-01 ~]# mkdir /xinguang/zookeeper/{data,logs}
[root@ali03-prod-toko-zookeeper-01 ~]# echo "1" > /xinguang/zookeeper/data/myid 
```

以下是ali03-prod-toko-zookeeper-02节点创建myid文件

```
[root@ali03-prod-toko-zookeeper-02 ~]# mkdir /xinguang/zookeeper/{data,logs}
[root@ali03-prod-toko-zookeeper-02 ~]# echo "2" > /xinguang/zookeeper/data/myid 
```

以下是ali03-prod-toko-zookeeper-03节点创建myid文件

```
[root@ali03-prod-toko-zookeeper-03 ~]# mkdir /xinguang/zookeeper/{data,logs}
[root@ali03-prod-toko-zookeeper-03 ~]# echo "3" > /xinguang/zookeeper/data/myid 
```

> myid值需要根据各个节点来调整,节点1 echo "1"，节点2 echo "2"，节点3 echo "3"

- 设置环境变量

将Zookeeper的相关命令追加至系统的PATH环境变量中。编辑/etc/profile文件，添加如下文本内容至文件末尾

```
[root@ali03-prod-toko-zookeeper-01 ~]# vim /etc/profile 
#Zookeeper 3.4.6
export ZOOKEEPER_HOME=/xinguang/zookeeper
export PATH=$PATH:$ZOOKEEPER_HOME/bin
```

执行source命令使修改的配置生效

```
[root@ali03-prod-toko-zookeeper-01 ~]# source /etc/profile
```

- 创建Zookeeper开机启动文件

以下脚本内容为Zookeeper开机启动脚本，需放到/etc/init.d/路径下

```
[root@ali03-prod-toko-zookeeper-01 ~]# vim /etc/init.d/zookeeper 
#!/bin/bash

#chkconfig:2345 20 90
#description:zookeeper
#processname:zookeeper

export JAVA_HOME=/xinguang/java
export JRE_HOME=/xinguang/java/jre
export CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar:$JAVA_HOME/lib:$JRE_HOME/lib:$CLASSPATH
export PATH=$PATH:$JAVA_HOME/bin

case "$1" in
    start)
        /xinguang/zookeeper/bin/zkServer.sh start
        ;;
    stop)
        /xinguang/zookeeper/bin/zkServer.sh stop
        ;;
    restart)
        /xinguang/zookeeper/bin/zkServer.sh restart
        ;;
    status)
        /xinguang/zookeeper/bin/zkServer.sh status
        ;;
    *)
        echo $"Usage: $0 {start|stop|status|restart}"
        exit 2
        ;;
esac
```

- 给脚本添加可执行权限并设置Zookeeper开机启动

```
[root@ali03-prod-toko-zookeeper-01 ~]# chmod +x /etc/init.d/zookeeper
[root@ali03-prod-toko-zookeeper-01 ~]# chkconfig --add zookeeper
```

- 启动zookeeper并查看状态

以下是ali03-prod-toko-zookeeper-01节点状态信息

```
[root@ali03-prod-toko-zookeeper-01 ~]# /etc/init.d/zookeeper start
JMX enabled by default
Using config: /xinguang/zookeeper/bin/../conf/zoo.cfg
Starting zookeeper ... STARTED

[root@ali03-prod-toko-zookeeper-01 ~]# /etc/init.d/zookeeper status
JMX enabled by default
Using config: /xinguang/zookeeper/bin/../conf/zoo.cfg
Mode: follower
```

以下是ali03-prod-toko-zookeeper-02节点状态信息

```
[root@ali04-prod-xls-zookeeper-02 ~]# /etc/init.d/zookeeper start
JMX enabled by default
Using config: /xinguang/zookeeper/bin/../conf/zoo.cfg
Starting zookeeper ... STARTED

[root@ali04-prod-xls-zookeeper-02 ~]# /etc/init.d/zookeeper status
JMX enabled by default
Using config: /xinguang/zookeeper/bin/../conf/zoo.cfg
Mode: leader
```

以下是ali03-prod-toko-zookeeper-03节点状态信息

```
[root@ali04-prod-xls-zookeeper-03 ~]# /etc/init.d/zookeeper start
JMX enabled by default
Using config: /xinguang/zookeeper/bin/../conf/zoo.cfg
Starting zookeeper ... STARTED

[root@ali04-prod-xls-zookeeper-03 ~]# /etc/init.d/zookeeper status
JMX enabled by default
Using config: /xinguang/zookeeper/bin/../conf/zoo.cfg
Mode: follower
```
