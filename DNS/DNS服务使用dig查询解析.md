---
title: DNS服务使用dig查询解析
date: 2016-02-28 20:39:51
tags:
- DNS
categories: Linux
---


##使用dig查询DNS解析


今天整理下前段时间搭建的DNS主从服务器，DNS主从复制虚拟域名设置等等，总结写了篇文档：[DNS服务器主从复制搭建](http://blog.yangcvo.me/2015/12/28/DNS/DNS%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%B8%BB%E4%BB%8E%E5%A4%8D%E5%88%B6%E6%90%AD%E5%BB%BA/)

这里就顺便写了下dig使用查询DNS解析：

一般来说linux下查询域名解析有两种选择，`nslookup或者dig`，而在使用上我觉得`dig`更加方便顺手。
如果是在centos下的话，只要yum装上`dig`这个包就可以使用`dig`命令了。

`nslookup` 使用在我印象中在读大学Windows服务器用的非常多。

* 最基本的使用方式就是

```bash
dig rap.test.intranet.
```

```bash
[root@DNS-master ~]# dig rap.test.intranet.

; <<>> DiG 9.9.4-RedHat-9.9.4-29.el7_2.3 <<>> rap.test.intranet.
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 40150
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 3

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;rap.test.intranet.             IN      A

;; ANSWER SECTION:
rap.test.intranet.      1200    IN      A       192.168.1.211

;; AUTHORITY SECTION:
test.intranet.          1200    IN      NS      ns1.test.intranet.
test.intranet.          1200    IN      NS      ns2.test.intranet.

;; ADDITIONAL SECTION:
ns1.test.intranet.      1200    IN      A       192.168.1.204
ns2.test.intranet.      1200    IN      A       192.168.1.205

;; Query time: 0 msec
;; SERVER: 127.0.0.1#53(127.0.0.1)
;; WHEN: 三 9月 14 14:47:45 CST 2016
;; MSG SIZE  rcvd: 130
```
即查询域名的A记录，查询的`dns`服务器将采用系统配置的服务器，即`/etc/resovle.conf` 中的。
如果要查询其他类型的记录，比如`MX，CNAME，NS，PTR`等，只需将类型加在命令后面即可

```bash
dig rap.test.intranet mx
dig rap.test.intranet ns
```
此外，如果你是一个系统管理员，部署好了一台dns服务器之后想对它进行解析测试，就必须要显式指定待测试的dns服务器地址了，例如:

```bash
dig @1.168.192 rap.test.intranet a
```
默认情况下dig将采用udp协议进行查询，如果要采用tcp方式，可以加上 +tcp参数
```
dig rap.test.intranet a +tcp
```

另外一个重要的功能是+trace参数，使用这个参数之后将显示从根域逐级查询的过程

```bash
dig rap.test.intranet a +trace
```

```bash
[root@DNS-master ~]# dig rap.test.intranet a +trace

; <<>> DiG 9.9.4-RedHat-9.9.4-29.el7_2.3 <<>> rap.test.intranet a +trace
;; global options: +cmd
.                       329687  IN      NS      g.root-servers.net.
.                       329687  IN      NS      a.root-servers.net.
.                       329687  IN      NS      j.root-servers.net.
.                       329687  IN      NS      d.root-servers.net.
.                       329687  IN      NS      e.root-servers.net.
.                       329687  IN      NS      c.root-servers.net.
.                       329687  IN      NS      l.root-servers.net.
.                       329687  IN      NS      i.root-servers.net.
.                       329687  IN      NS      f.root-servers.net.
.                       329687  IN      NS      m.root-servers.net.
.                       329687  IN      NS      b.root-servers.net.
.                       329687  IN      NS      k.root-servers.net.
.                       329687  IN      NS      h.root-servers.net.
.                       518303  IN      RRSIG   NS 8 0 518400 20160927050000 20160914040000 46551 . oGlpdQKJ+s6h7AW/HfNVN6w8zzrwU8Q5LP4So9LP65JBqHQqLDtpNz1j OtTiJVwdpxlF/uTQ1HOqUVNOxV7Anpcj08x/LXjCQYUco2X12/Gxats6 oX1h9FfzFtd3JKrxuo08x7fBQ7uVY9WvkHW/AcWCIRBMMpuIJqZcHlGz 92c=

;; Received 941 bytes from 127.0.0.1#53(127.0.0.1) in 1421 ms


.                       86400   IN      SOA     a.root-servers.net. nstld.verisign-grs.com. 2016091400 1800 900 604800 86400
.                       86400   IN      RRSIG   SOA 8 0 86400 20160927050000 20160914040000 46551 . t2MmM3Ei/JkicFHIjsQHz4vOvfld02aXKa4Jc3cHHnzTYQ6sqcKBGoNB mhrSs51ImUQj7SXjm9T4xb7ZvnzezqWqNA2mQc6j2eFHcJgtIfryitIt WumvYo6j3PzgufTtlidWob60Y7KE0sy3Y1g3jVKwjH9YFE+8imwEPhiI vhY=
international.          86400   IN      NSEC    intuit. NS DS RRSIG NSEC
international.          86400   IN      RRSIG   NSEC 8 1 86400 20160927050000 20160914040000 46551 . PBLSHTQ/qRan5U7tZ2KEIJkQaOs356o0YRJP2SY+WjCwOfBRcVb6ljYG pgh+X45M1IXFzOEs5V36UmNZ9EZ5m+hy67dQs64Mam10WTRHsmO55RCN abR8nkLuAU20qdp2d5RbqlPUPqOmvLMhmxFwy2eRW+4+OdSmEwaYKubP YSc=
.                       86400   IN      NSEC    aaa. NS SOA RRSIG NSEC DNSKEY
.                       86400   IN      RRSIG   NSEC 8 0 86400 20160927050000 20160914040000 46551 . PlKRTXs02kT6qpQJw2FJibwuU56Olwo5hEzXZ4X6DQ4ONUI76mpAWuKM jtZi2OK111STK6cehRK/RTfH6qX8YF+06DpGxLkJx9oShk/G5Zj9xXid 7CRDf9ccpC+740iGK/KSWdE36LCkPw+6lU9oyXlFbqhS0YDRz4xuzbqi pSc=
;; Received 662 bytes from 192.58.128.30#53(j.root-servers.net) in 120 ms

```
比如，对本站域名 `rap.test.intranet` A记录的trace查询可以看到根域.，顶级域.intranet，以及test.intranet的域名权威服务器的地址及其各自的返回结果，这样对于追踪dns解析中的问题有很大的帮助。



