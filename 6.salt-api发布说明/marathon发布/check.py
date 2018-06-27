#!/usr/bin/env python
#-*- coding:utf-8 –*-

import urllib2,urllib
from pprint import pprint
import time
import yaml
import sys,os
import getopt
import commands

try:
    import json
except ImportError:
    import simplejson as json

class check:
    '''初始化参数'''
    def __init__(self):

        self.halfurl = 'http://ops-cd-mesos01.sysadmin.xinguangnet.com:8080/v2/apps'
    
    def usage(self):
        print '''
    Usage: %s [options...]
    Options:
        -e/--deploy_env               : deploy env
        -p/--project_name             : project name the appname belong to
        -a/--app_name                 : appname info

    Example:
        # %s a openapi -e dev -p tubobo -a iot
        ''' % (sys.argv[0],sys.argv[0])
    
    def getRequest(self,deploy_env,project_name,app_name):

        if not deploy_env or not project_name or not app_name:
            self.usage()
            sys.exit()  

        prefix = '/' + deploy_env + '/' + project_name + '/' + app_name
        url = self.halfurl + prefix
        print(url)
        req = urllib2.Request(url)
        req.add_header('Content-type','application/json')
        try:
            data = urllib2.urlopen(req)
        except:
            print '-----------------------------------------------------'
            print "无法获取Marathon api信息，此appid不存在或错误的appid!"
            print "请联系管理员进行处理!"
            print '-----------------------------------------------------'
            sys.exit(1)
        content = json.loads(data.read())
        #content = data.read()
        return content

    def gettasks(self,deploy_env,project_name,app_name):

        if not deploy_env or not project_name or not app_name:
            self.usage()
            sys.exit()

        prefix = '/' + deploy_env + '/' + project_name + '/' + app_name + '/' + 'tasks'
        url = self.halfurl + prefix
        print(url)
        req = urllib2.Request(url)
        req.add_header('Content-type','application/json')
        try:
            data = urllib2.urlopen(req)
        except:
            print '-----------------------------------------------------'
            print "无法获取Marathon api信息，此appid不存在或错误的appid!"
            print "请联系管理员进行处理!"
            print '-----------------------------------------------------'
            sys.exit(1)
        content = json.loads(data.read())
        #content = data.read()
        return content
 
def main(deploy_env,project_name,app_name):
    #app_name = None
    #deploy_env = None
    #project_name = None
    mara = check()

    #try:
    #    opts, args = getopt.getopt(sys.argv[1:],'e:p:a:')
    #except getopt.GetoptError:
    #    mara.usage()
    #    sys.exit()

    #for opt, arg in opts:
    #    if opt in ('-h', '--help'):
    #        usage()
    #        sys.exit()
    #    elif opt == '-e':
    #        deploy_env = arg
    #    elif opt == '-p':
    #        project_name = arg
    #    elif opt == '-a':
    #        app_name = arg
    tasks = mara.gettasks(deploy_env,project_name,app_name)
    try:
        taskid = tasks[u'tasks'][0][u'id']
    except:
        pass
    status = mara.getRequest(deploy_env,project_name,app_name)
  #  print status
    for (d,x) in status[u'app'].items():
        #print "key:"+d+",value:"+str(x)
        if d == 'state':
            try:
                state = str(x)
            except:
                pass 
        if d == 'cpus':
            try:         
                cpu = str(x) + '核'
            except:
                pass
        if d == 'tasks':
            try:
                server = str(x[0][u'host'])
            except:
                print '-------------------------------'
                print '无法获取主机资源，可能服务器资源不足，请联系管理员!'
                print '-------------------------------'
                sys.exit(1)
            try:         
                state = str(x[0][u'state'])
            except:
                pass
        if d == 'mem':
            try:
                memory = str(x) + 'M'
            except:
                pass
        if d == 'labels':
            try:
                vhost = str(x[u'HAPROXY_0_VHOST'])   
            except:
                pass
        if d == 'tasksRunning':
            try:         
                tasksRunning = str(x)
            except:
                pass
        if d == 'tasksUnhealthy':
            try:
                tasksUnhealthy = str(x)
            except:
                pass
    
    if tasksUnhealthy == '0' and tasksRunning == '1' and state == 'TASK_RUNNING':
        print '-----------------------------------------------------------------'
        print '服务健康检查正常，服务运行正常!'
        print '------------------------------------------------------------------'
        print '######################服务部署详细信息#######################'
        print '服务使用内存: ' + memory
        print '服务使用CPU: ' +  cpu 
        print '服务部署的服务器地址为: ' + server
        print '服务的访问地址为: ' + vhost
        try:
            os.system('ssh root@%s docker ps --filter label=MESOS_TASK_ID=%s -q' %(server,taskid))
        except:
            pass
        print '#############################################################'
        time.sleep(10)
        sys.exit() 
    else:
        #print '服务正在部署中,请稍后......'
        #print '服务健康检查失败，请检查相关配置及日志,日志地址为:log.dev.ops.com'
        print '------------------------------------------------------------------'
        print '服务正在部署中,请稍后......'
        print '服务部署的服务器地址为: ' + server
        print '------------------------------------------------------------------'
        return 1
