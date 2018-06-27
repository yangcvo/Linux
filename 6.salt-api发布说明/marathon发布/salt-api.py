#!/usr/bin/env python
#-*- coding:utf-8 –*-

#导入使用的模块#####

import urllib2,urllib
from pprint import pprint
import time
import yaml
import sys,os
import getopt
import commands
import check

try:
    import json
except ImportError:
    import simplejson as json

class SaltAPI(object):
    __token_id = ''

    def __init__(self,url,username,password):  
        self.__url = url.rstrip('/')
        self.__user = username
        self.__password = password

    def token_id(self):
        ''' user login and get token id '''
        params = {'eauth': 'pam', 'username': self.__user, 'password': self.__password}
        encode = urllib.urlencode(params)
        obj = urllib.unquote(encode)
        content = self.postRequest(obj,prefix='/login')
        try:
            self.__token_id = content['return'][0]['token']
            #print(self.__token_id)
        except KeyError:
            raise KeyError

    def postRequest(self,obj,prefix='/'):
        url = self.__url + prefix
        headers = {'X-Auth-Token'   : self.__token_id}
        req = urllib2.Request(url, obj, headers)
        opener = urllib2.urlopen(req)
        content = json.loads(opener.read())
        return content
    
    def list_all_key(self):
        params = {'client': 'wheel', 'fun': 'key.list_all'}
        obj = urllib.urlencode(params)
        self.token_id()
        content = self.postRequest(obj)
        minions = content['return'][0]['data']['return']['minions']
        minions_pre = content['return'][0]['data']['return']['minions_pre']
        return minions,minions_pre
    
    def delete_key(self,node_name):
        params = {'client': 'wheel', 'fun': 'key.delete', 'match': node_name}
        obj = urllib.urlencode(params)
        self.token_id()
        content = self.postRequest(obj)
        ret = content['return'][0]['data']['success']
        return ret
    
    def accept_key(self,node_name):
        params = {'client': 'wheel', 'fun': 'key.accept', 'match': node_name}
        obj = urllib.urlencode(params)
        self.token_id()
        content = self.postRequest(obj)
        ret = content['return'][0]['data']['success']
        return ret
    
    def remote_noarg_execution(self,tgt,fun):
        ''' Execute commands without parameters '''
        params = {'client': 'local', 'tgt': tgt, 'fun': fun}
        obj = urllib.urlencode(params)
        self.token_id()
        content = self.postRequest(obj)
        ret = content['return'][0][tgt]
        return ret

    def remote_execution(self,tgt,fun,arg):
        ''' Command execution with parameters '''        
        params = {'client': 'local', 'tgt': tgt, 'fun': fun, 'arg': arg}
        obj = urllib.urlencode(params)
        self.token_id()
        content = self.postRequest(obj)
        try:
            ret = content['return'][0][tgt]
            return ret
        except Exception:
            print('%s host minion 无响应,请检查!' % tgt)
    
    def remote_execution1(self,tgt,fun):
        ''' Command execution with parameters '''
        params = {'client': 'local', 'tgt': tgt, 'fun': fun}
        obj = urllib.urlencode(params)
        self.token_id()
	#print(self.token_id())
        content = self.postRequest(obj)
	#print(content)
        try:
            ret = content['return'][0][tgt]
            return ret
        except Exception:
            print('%s host minion 无响应,请检查!' % tgt)
        

    def target_remote_execution(self,tgt,fun,arg):
        ''' Use targeting for remote execution '''
        params = {'client': 'local', 'tgt': tgt, 'fun': fun, 'arg': arg, 'expr_form': 'nodegroup'}
        obj = urllib.urlencode(params)
        self.token_id()
        content = self.postRequest(obj)
        jid = content['return'][0]['jid']
        return jid

    def target_remote_execution1(self,tgt,fun,arg):
        ''' Use targeting for remote execution '''
        params = {'client': 'local', 'tgt': tgt, 'fun': fun, 'arg': arg}
        obj = urllib.urlencode(params)
        self.token_id()
        content = self.postRequest(obj)
        #jid = content['return'][0]['jid']
        #return jid

    def deploy(self,tgt,arg):
        ''' Module deployment '''
        params = {'client': 'local', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg}
        obj = urllib.urlencode(params)
        self.token_id()
        content = self.postRequest(obj)
        return content

    def async_deploy(self,tgt,arg):
        ''' Asynchronously send a command to connected minions '''
        params = {'client': 'local_async', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg}
        obj = urllib.urlencode(params)
        self.token_id()
        content = self.postRequest(obj)
        jid = content['return'][0]['jid']
        return jid

    def target_deploy(self,tgt,arg):
        ''' Based on the node group forms deployment '''
        params = {'client': 'local_async', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg, 'expr_form': 'nodegroup'}
        obj = urllib.urlencode(params)
        self.token_id()
        content = self.postRequest(obj)
        jid = content['return'][0]['jid']
        return jid
    
    def json_postRequest(self,obj,prefix='/'):
        ''' 复杂参数提交 json 结构提交 '''
        url = self.__url + prefix
        headers = {'X-Auth-Token'   : self.__token_id}
        headers['Accept'] = 'application/json'
        headers['Content-Type'] = 'application/json'
        req = urllib2.Request(url, obj, headers)
        opener = urllib2.urlopen(req)
        content = json.loads(opener.read())
        return content

    def json1_postRequest(self,jid,prefix='/jobs/'):
        ''' 复杂参数提交 json 结构提交 '''
        url = self.__url + prefix + jid
        headers = {'X-Auth-Token'   : self.__token_id}
        headers['Accept'] = 'application/json'
        headers['Content-Type'] = 'application/json'
        #url = json.dumps(url)
        #print headers
        req = urllib2.Request(url,headers=headers)
        #print req
        opener = urllib2.urlopen(req)
        #print opener
        content = json.loads(opener.read())
        print content
        return content


    def url_postRequest(self, jid, prefix='/jobs/'):
        ''' 复杂参数提交 json 结构提交 '''
        url = self.__url + prefix + jid
        #headers = {'X-Auth-Token'   : self.__token_id, 'Accept':'application/json'}
        #headers['Accept'] = 'application/json'
        print url 
        #req = urllib2.Request(url, headers)
        #req.add_header('X-Auth-Token', self.__token_id)
        #req.add_header('X-Auth-Token',  self.__token_id)
        headers = {'X-Auth-Token'   : self.__token_id}
        headers['Accept'] = 'application/json'
        headers['Content-Type'] = 'application/json'
        print headers
        req = urllib2.Request(url, headers)
        print req
        opener = urllib2.urlopen(req)
        #print opener
        #content = json.loads(opener.read())
        #return content
        #print content

    def sls_json_deploy(self,tgt,mods,pillar):
        ''' state.sls 模块功能执行 带pillar 参数传递 '''
        post_data = []
	
	my_post= {}
	#my_post["client"] = "local"
        my_post["client"] = "local_async"
        my_post["tgt"] = tgt
        my_post["fun"] = "state.sls"
        #arg = ["deploy", "pillar={'web': 'test'}"]
        kwarg= {'mods': mods,'pillar':pillar} 
        my_post["kwarg"]= kwarg
        post_data.append(my_post)
	obj = json.dumps(post_data)
        self.token_id()
        content = self.json_postRequest(obj)
        jid = content['return'][0]['jid']
        return jid
        #return content

def usage():
    print '''
Usage: %s [options...]
Options:
    -a/--app_name                       : appname info
    -e/--env                            : deploy env
    -u/--url                            : download resource url
    -w/--war                            : war package name
    -h/--help                           : this help info page

Example:
    #
    %s -iia openapi -e dev -u http://172.16.20.1:9090 -w openapi-plt-01.war
    ''' % (sys.argv[0],sys.argv[0])

def load_config():
    base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    configFile = "%s/%s" % (base_dir,"deploy.yaml")
    stream = file(configFile, 'r')
    try:
        data = yaml.load(stream)
        return data
    except BaseException,e:
        print "yaml配置错误，请检查deploy.yaml文件,错误信息如下:" 
        print e
        sys.exit()
 
def main():

    global base_dir,DEBUG
    DEBUG = False
    base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

    try:
        opts, args = getopt.getopt(sys.argv[1:],'a:e:u:w:h:c')
    except getopt.GetoptError:
        usage()
        sys.exit()

    #各个变量保存
    app_name = None         
    deploy_env = None       
    war_package_name = None
    download_url = None
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt == '-a':
            app_name = arg
        elif opt == '-e':
            deploy_env = arg
        elif opt == '-u':
            download_url = arg
        elif opt == '-w':
            war_package_name = arg
        elif opt == '-c':
            load_config()

    if not app_name or not deploy_env or not war_package_name or not download_url:
        usage()
        sys.exit()
#    elif(check in vars()):
#        load_config()
        
    # 单元测试内容
    #print sapi.list_all_key()
    #print sapi.remote_noarg_execution('salt-dns-doc','test.ping')
    #print sapi.remote_execution('salt-dns-doc','cmd.run','hostname -f')
    #print sapi.remote_execution('salt-dns-doc','cmd.run','hostname -f')

    # read config info from yaml
    api_config = load_config()
        
    sapi = SaltAPI(url=api_config['salturl'],username=api_config['saltusername'],password=api_config['saltpassword'])
    logurl = api_config['logurl']
    try:
        project=api_config[app_name][deploy_env]['project']
        pillar = { "projectname":project,"appname":app_name,"url":download_url,"warname":war_package_name}
    except:
        print "没有找到app归属的项目名，请检查config.yaml中project参数的配置!"
    # get host list for deploy
    app_mods="%s.%s.%s" % ('deploy',app_name,deploy_env)
    try:
        dev_host_list=api_config[app_name][deploy_env]['host']
    except:
        print "无法获取deploy.yaml中的salt-key,请检查配置!"
    
    for host in dev_host_list:
        check_minion_job_count = 1
        while (check_minion_job_count < 10):
            time.sleep(10)
            #print(host['hostname'])
            a=sapi.remote_execution1(host['hostname'],'saltutil.running')
            if not a:
                try:
                    jid = sapi.sls_json_deploy(host['hostname'],app_mods,pillar) 
                    print ('%s:Executed command with job ID: {0}'.format(jid)) %(host['hostname'])
                    break
                except BaseException,e:
                    print "无法调用salt-minion,请检查salt-key是否有误!"
                    sys.exit()
            else:
               for (k,v) in a[0].items():
                    if k == 'jid':
                        try:
                            minionjid = str(v)
                            print "%s:客户端正在执行任务,任务id为%s" %(host['hostname'],minionjid)
                            break
                        except:
                            pass
               check_minion_job_count = check_minion_job_count + 1
               if check_minion_job_count == 9:
                   print '检查9次发现jid还在运行,杀掉僵死进程!'
                   sapi.target_remote_execution1(host['hostname'],'saltutil.kill_job',minionjid)

    time.sleep(12)
    marahost = dev_host_list[-1]['hostname'] 
    marathon_dir = ('bash /xinguang/%s/bin/tomcat/marathon.sh' %(app_name))
 
    run_marathon = sapi.remote_execution(marahost,'cmd.run','%s %s %s %s' %(marathon_dir,app_name,deploy_env,project))

    if run_marathon is not None and  "No such file" in run_marathon:
        print "此项目为传统方式部署,无法找到marathon相关文件,不执行marathon方式检查!"
        sys.exit()
    else:
        time.sleep(60)
        count = 1
        while (count < 10):
            time.sleep(35) 
            result = check.main(deploy_env,project,app_name)
            if [ result == 1 ]:
                print '第%i次检测结果:服务正在部署中,请稍后......' %(count)
                count = count + 1
  
    print "检测服务多次,状态一直为部署中,服务启动可能失败,请自行查看业务启动日志!"
    sys.exit(1)

if __name__ == "__main__":
    main()
