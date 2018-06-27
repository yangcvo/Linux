#!/bin/sh

path=`dirname $0`
dns_oper="$path/dns_oper.sh"
. $path/cgi_module.shell
get_value action
get_value domain
get_value ip
get_value type
#action=query
#domain=www.alibaba.com
RETURNCODE=""
# Main Program

if [ -z "$ip" ];then
	ip=$REMOTE_ADDR
fi
if [ -n "$action" ];then
	case $action in
     	add|del|modify)
		if [ -z "$domain" ] || [ -z "$ip" ];then
			RET="STATUS=Lack Of Param"
		else
			if [ -z "$type" ];then
				RET=`$dns_oper $action $domain "CNAME" $ip`
			else
				RET=`$dns_oper $action $domain $type $ip`
			fi
		fi
     	;;
     	query)
        	if [ -z "$domain" ];then
                        RET="STATUS=Lack Of Param"
		else
			RET=`$dns_oper $action $domain`
                fi
     	;;
	*)
		RET="The Param Not Correct"
	;;
	esac
else
	 RET="STATUS=Lack Of Param"
fi

##############################################
#
#	print page
echo "Content-type: text/plain" 
echo ""
echo "$RET"
echo "$ip"
