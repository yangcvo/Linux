## Sonarqube和jacoco搭建代码检查

1. 准备工作：`sonarqube，jacoco，git，maven，ant，sonar-runner`
sonarqube 去官网下载，文件太大，不能上传
git，mavne，ant自己安装
sonarqube和sonar-runnrt安装：查看[链接](http://blog.csdn.net/u011925176/article/details/51536563)

2. 监控机子配置：
启动sonarqube，git下载源代码，进入源码路径，添加一下文件；

```bash
1）sonar-project.properties
#Set sonar-runner Configuration
sonar.projectKey=haozhuo-hm-01
sonar.projectVersion=6.1
sonar.projectName=haozhuo-hm
sonar.language=java
```

(1). 需要分析代码的路径

```bash
sonar.sources=src/main/java/com/haozhuo/hm/service, src/main/java/com/haozhuo/hm/dubbo
```

(2). 这个地方很重要，工程class文件的位置，代码覆盖率就是根据这个不匹配的，如果线上的代码和线下的代码不同步，可能会造成覆盖率计算不精确。

```bash
sonar.java.binaries=/Users/yejun/git/YJK-Java/haozhuo/haozhuo-hm/target
sonar.test.binaries=test
sonar.sourceEncoding=UTF-8
sonar.my.property=value
sonar.java.coveragePlugin=jacoco
#Path to the JaCoCo report file containing coverage data by unit tests. The path may be absolute or relative to the project base directory
sonar.jacoco.reportPath=/Users/yejun/git/YJK-Java/haozhuo/haozhuo-hm/jacoco.exec
#Path to the JaCoCo report file containing coverage data by integration tests. The path may be absolute or relative to the project base directory
sonar.jacoco.itReportPath=/Users/yejun/git/YJK-Java/haozhuo/haozhuo-hm/jacoco.exec
#sonar.jacoco.reportMissing.force.zero
sonar.jacoco.reportMissing.force.zero=false
```

(3). build.xml

```bash
<?xml version="1.0" encoding="UTF-8"?>
<project name="testCodeCoveage" default="all" basedir="." xmlns:jacoco="antlib:org.jacoco.ant">
<!--
<property name="jacocoantPath" value="/root/jacocoant.jar"/> 
<property name="jacocoexecPath" value="."/>
-->
<!-- Import the JaCoCo Ant Task -->
<taskdef uri="antlib:org.jacoco.ant" resource="org/jacoco/ant/antlib.xml">
<classpath path="/srv/jacoco/jacocoant.jar" />
</taskdef>
<target name="merge" depends="dump">
<jacoco:merge destfile="jacoco.exec">
<!-- 导出exec文件地址，在这里统一生产一个exec文件 -->
<fileset dir="/opt/haozhuo-hm/jacoco" includes="*.exec"/>
</jacoco:merge>
</target>
<target name="dump">
<!-- reset="true"是指在dump完成之后，重置jvm中的覆盖率数据为空。append="true"是指dump出来的exec文件为增量方式 -->
<jacoco:dump address="192.168.1.19" reset="false" destfile="/opt/haozhuo-hm/jacoco/jacoco_haozhuo-hm.exec" port="10001" append="true"/>
<!-- <jacoco:dump address="10.199.145.117" reset="true" destfile="/srv/jacoco/target/jacoco_10.199.145.117_2.exec" port="10002" append="true"/>
<jacoco:dump address="10.199.145.118" reset="true" destfile="/srv/jacoco/target/jacoco_10.199.145.118_1.exec" port="10001" append="true"/>
<jacoco:dump address="10.199.145.118" reset="true" destfile="/srv/jacoco/target/jacoco_10.199.145.118_2.exec" port="10002" append="true"/> -->
<!--
<jacoco:dump address="10.199.170.26" reset="true" destfile="/Users/yejun/git/YJK-Java/haozhuo/haozhuo-hm/jacoco_10.199.170.26.exec" port="10001" append="true"/>
-->
</target>
<!-- ========= The main target "all" ========= -->
<target name="all" depends="merge" />
</project>
```

(4). jacoco.sh

```bash
#!/bin/sh
#加载环境变量
source /etc/profile
#sonar-runner 路径
cd /Users/yejun/software/sonar-runner-2.4/haozhuo-hm
#初始化当前时间、周
time=`date '+%s'`
lastweek=`cat /var/run/coverage.pid`
newweek=`date +%W`
#获取最新代码
git pull
#编译最新代码，如果使用jacoco agent通过classdumpdir路径dump出来的class文件，则不需要mvn clean进行class文件编译。否则需要编译class文件。
#mvn clean install -Dmaven.test.skip=true -Ptest
#获取历史版本和最新版本
#oldVersion=`cat /var/run/coverage.pid`
newversion=`grep -r "<version>" pom.xml |awk -F "</" '{print $1}'|awk -F ">" '{print $2}'`
#判断如果版本未发生变更，则直接合并代码覆盖率数据;如果代码发生变更，则删除历史jacoco.exe覆盖率数据，重新统计
if [ $lastweek = $newweek ];then
#sed -i '/sonar.projectVersion/d' sonar-project.properties
#sed -i "2a sonar.projectVersion=$lastVersion.$time" sonar-project.properties
ant
/Users/yejun/software/sonar-runner-2.4/bin/sonar-runner
else
echo $newweek>/var/run/coverage.pid
rm -rf *.exec
sed -i '/sonar.projectKey/d' sonar-project.properties
sed -i '/sonar.projectVersion/d' sonar-project.properties
sed -i "1a sonar.projectKey=vips-mobile-operation-key-$newweek" sonar-project.properties
sed -i "2a sonar.projectVersion=$newversion" sonar-project.properties
ant
/Users/yejun/software/sonar-runner-2.4/bin/sonar-runner
fi
```

### 3.被监控机子配置：


1）上传一个jacocoanget.jar文件，文件在jacoco.zip里面，放到一个目录下。例如：/srv/jacoco/jacocoagent.jar

2) 修改工程tomcat/bin/下的catalina.sh，新增

```bash
JAVA_OPTS="$JAVA_OPTS -javaagent:/srv/jacoco/jacocoagent.jar=includes=*,output=tcpserver,port=10001,address=192.168.1.19”
```

参数：

```bash
port:如果一台机子有多个tomcat，注意端口号不要重复
address：本机的ip地址
其他参数一样。
```
3)配置完以后，到启动jacoco.sh然后执行mvn clean package，就可以到sonarqube上面查看想要的信息了。

