---
title: linux系统环境变量优化
date: 2014-09-07 18:43:45
tags:
- Linux note
categories: Linux
---

## linux 系统环境变量优化

可以统一写在/etc/profile.d/下面

* 变化目录结构字体颜色:

 >vim color.sh


``` bash
PS1='[\[\033[0;34m\]\u\[\033[0;37m\]@\[\033[0;35m\]\h\[\033[0;33m\] \w\[\033[0;37m\]]\[\033[0;31m\]\$\[\033[00m\] '
export PROMPT_COMMAND='{ msg=$(history 1 | { read x y; echo $y; });user=$(whoami); echo $(date "+%F %H:%M:%S"):$user:`pwd`/:$msg ---- $(who am i); } >> /tmp/`date "+%F"`.`hostname`.`whoami`.history-timestamp'
export PROMPT_COMMAND='{ msg=$(history 1 | { read x y; echo $y; });user=$(whoami); echo $(date "+%F %H:%M:%S"):$user:`pwd`/:$msg ---- $(who am i); } >> /tmp/`date "+%F"`.`hostname`.`whoami`.history-timestamp'
export PROMPT_COMMAND='{ msg=$(history 1 | { read x y; echo $y; });user=$(whoami); echo $(date "+%F %H:%M:%S"):$user:`pwd`/:$msg ---- $(who am i); } >> /tmp/`date "+%F"`.`hostname`.`whoami`.history-timestamp'
```


* 设置登录提醒状态:

 >loadaverage.sh

```bash
unset i
unset -f pathmunge
echo -e "\t\t\t\t\t\e[1;31m登录情况\e[0m\n"
last -n 6|nali
echo -e "\n\t\t\t\t\t\e[1;31mcpu负载情况\e[0m\n"
uptime
```

* 设置历史记录提醒

 > vim history.sh

``` bash
export HISTTIMEFORMAT="%F %T `whoami`"
USER_IP=`who -u am i 2>/dev/null| awk '{print $NF}'|sed -e 's/[()]//g'`
if [ "$USER_IP" = "" ];
then
USER_IP=`hostname`
fi
export HISTTIMEFORMAT="%F %T $USER_IP:`whoami` "
```


