#!/bin/sh
#***************************************************************************************************************#
# ScriptName:           dns.cgi                                                                             	#
# Author:               hua.fu                                                                                  #
# Date:                 2006-06-22                                                                              #
# LogFile:              /var/log/script.log                                                                     #
#***************************************************************************************************************#
DIR=`dirname $0`
. $DIR/functions
NAMEDB="/var/named"
LOGFILE="/var/log/named/oper.log"
ZONEDIR="$NAMEDB"
ZONE_HEADER="$DIR/zone_head"
ZONE_NAMED="$DIR/zone_named"
BACKUPDIR="$NAMEDB/op_backup"
NAMED_CONF="/var/named/named.conf"
NAMED_SLAVE_CONF="$NAMEDB/named_slave.conf"
CHECK_LOG="/var/log/named/check_zone.log"
# detemin check zone file or not
CHECK_ZONE_TAG=""
# detemin check named.conf file or not
CHECK_CONF_TAG=""
################## Verfiy Define ############################
TMPFILE="/tmp/tmpfile"
RETURNCODE=""
################## Function Define ##########################
# Main Menu

# add format ) 
#	add example.alibaba.com A 172.16.23.2 
#	add example.alibaba.com MX 10 mx1.example.com
#	add example.alibaba.com CNAME www.example.com

# mod format )
#	mod example.alibaba.com A 172.16.23.2 
#	mod example.alibaba.com MX 10 mx1.example.com
#	mod example.alibaba.com CNAME www.example.com

# del format )
#	del example.alibaba.com A 172.16.23.2 
#	del example.alibaba.com MX 10 mx1.example.com
#	del example.alibaba.com CNAME www.example.com
         
# query format )
#	query example.alibaba.com

# Function Add Domain
add_record()
{
	# $1 domain name www.alibaba.com
	# $2 record type A MX CNAME PTR
	# $3 ip or domain name 
	# $# arg count
	# check input format
	domainname=$1
	type=$2
	if (! (echo $domainname | grep -q "\.$" ))
	then
		domainname=`echo $domainname|sed -e 's/$/./g'` 
	fi
	#echo "$1\\$2\\$3"
	case $type in
		A|a)
			IP=$3
			if (! (echo "$IP" |grep -q -P "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$" ))
			then
			  RETURNCODE="Input Ip Format Wrong"
			  return 
			fi
			addcontent="$domainname\tA\t$IP"
		;;
		CNAME|cname)
			CNAME=$3
			if [ -z "$CNAME" ];then
				RETURNCODE="Input CNAME Format Wrong"
                          	return
			fi
			if (! (echo $CNAME | grep -q "\.$" ))
			then
				CNAME=`echo $CNAME|sed -e 's/$/./g'` 
			fi
			addcontent="$domainname\tCNAME\t$CNAME"
		;;
		MX|mx)
			MX_PRIORITY=$3
			MX_NAME=$4
			if [ -z "$MX_PRIORITY" ] || [ -z "$MX_NAME" ];then
				RETURNCODE="Input MX Format Wrong"
                                return
			fi
			if (! (echo $MX_NAME | grep -q "\.$" ))
			then
				MX_NAME=`echo $MX_NAME|sed -e 's/$/./g'` 
			fi
			addcontent="$domainname\tMX\t$MX_PRIORITY\t$MX_NAME"
		;;
	esac

	# Find Domain Hosts File
	#ZONE=`echo $domainname | awk -F . '{print $(NF-2)"."$(NF-1)}'`
	#ZONE=`echo $domainname | sed  -r -e "s/\w+.(.*)./\1/g"`
	ZONE=`echo $domainname | sed 's/^[^.]\+.//'`
	#HOSTFILE=`find $ZONEDIR -name "hosts.$ZONE"`
	HOSTFILE=`find $ZONEDIR -name "${ZONE}hosts"`
	INSTIME=`date +%Y-%m-%d-%k:%M:%S`
	
	# only one cname for domain
	type=`echo $type |tr [:upper:] [:lower:]` 
	if [ $type = "cname" ] && [ -n "$HOSTFILE" ];then
		if( grep -q -P "$domainname" $HOSTFILE)
                then
                        RETURNCODE="Record Already Exist,Cant't Add Cname Record"
                        log "add $addcontent at $INSTIME Failed : Record Already Exist,Cant't Add Cname Record" $LOGFILE
			return
		fi
	fi
	
	if [ -n "$HOSTFILE" ];then
		# hosts file already exist
		if( grep -q -P "$addcontent" $HOSTFILE)
		then
			RETURNCODE="Record Already Exist"
			log "add $addcontent at $INSTIME Failed : Record Already Exist" $LOGFILE
		else
			# first backup host file
			log "bakcup $HOSTFILE To $BACKUPDIR" $LOGFILE
			#cp $HOSTFILE $BACKUPDIR/"hosts.$ZONE.`date +%Y-%m-%d-%k:%M:%S`"
			cp $HOSTFILE $BACKUPDIR/"${ZONE}.hosts.`date +%Y-%m-%d-%k:%M:%S`"
			echo -e "$addcontent" >> $HOSTFILE
			log "add $addcontent at $INSTIME Success" $LOGFILE
			RETURNCODE="OK"
			CHECK_ZONE_TAG="CHECK"
		fi
	else
                return
		#HOSTFILE="$ZONEDIR/hosts.$ZONE"
		HOSTFILE="$ZONEDIR/hosts.$ZONE"
		## create new hosts file ##
		serial=`date +%Y%m%d%H`
		if [ -n "$IP" ];then
			sed -e "s/DOMAIN_IP/$IP/g" -e "s/DOMAIN_NAME/$ZONE./g" -e "s/SERIAL/$serial/g" $ZONE_HEADER >$HOSTFILE
		else
			IP="121.0.16.7"
			sed -e "s/DOMAIN_IP/$IP/g" -e "s/DOMAIN_NAME/$ZONE./g" -e "s/SERIAL/$serial/g" $ZONE_HEADER >$HOSTFILE
		fi
		echo -e "$addcontent" >> $HOSTFILE
		## add new zone to named.conf ##
		sed -e "s/DOMAIN_NAME/$ZONE/g" $ZONE_NAMED >>$NAMED_CONF
		log "add $addcontent at $INSTIME Success" $LOGFILE
		RETURNCODE="OK"
		CHECK_CONF_TAG="CHECK"	
		CHECK_ZONE_TAG="CHECK"    
	fi
}

# Function Modify Domain
modify_record()
{
	# $1 domain name www.alibaba.com
	# $2 record type A MX CNAME PTR
	# $3 ip or domain name 
	# $# arg count
	# check input format
	domainname=$1
	type=$2
	if (! (echo $domainname | grep -q "\.$" ))
	then
		domainname=`echo $domainname|sed -e 's/$/./g'` 
	fi
	case $type in
		A|a)
			IP=$3
			if (! (echo "$IP" |grep -q -P "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$" ))
			then
			  RETURNCODE="Input Ip Format Wrong"
			  return 
			fi
			remaining_params="$IP"
		;;
		CNAME|cname)
			CNAME=$3
			if (! (echo $CNAME | grep -q "\.$" ))
			then
				CNAME=`echo $CNAME|sed -e 's/$/./g'` 
			fi
			remaining_params="$CNAME"
		;;
		MX|mx)
			MX_PRIORITY=$3
			MX_NAME=$4
			if (! (echo $MX_NAME | grep -q "\.$" ))
			then
				MX_NAME=`echo $MX_NAME|sed -e 's/$/./g'` 
			fi
			remaining_params="$MX_PRIORITY\t$MX_NAME"
		;;
	esac

	# Find Domain Hosts File
	#ZONE=`echo $domainname | awk -F . '{print $(NF-2)"."$(NF-1)}'`
	#ZONE=`echo $domainname | sed  -r -e "s/\w+.(.*)./\1/g"`
	ZONE=`echo $domainname | sed 's/^[^.]\+.//'`
	
	#HOSTFILE=`find $ZONEDIR -name "hosts.$ZONE"`
	HOSTFILE=`find $ZONEDIR -name "${ZONE}hosts"`
	
	INSTIME=`date +%Y-%m-%d-%k:%M:%S`
	
	if [ -n "$HOSTFILE" ];then
		# hosts file already exist
		if( grep -q -P "$domainname" $HOSTFILE)
		then
			log "bakcup $HOSTFILE To $BACKUPDIR" $LOGFILE
			#cp $HOSTFILE $BACKUPDIR/"hosts.$ZONE.`date +%Y-%m-%d-%k:%M:%S`"
			cp $HOSTFILE $BACKUPDIR/"${ZONE}.hosts.`date +%Y-%m-%d-%k:%M:%S`"
			sed -i -r -e "s/($domainname\t+$type\t+).*/\1$remaining_params/" $HOSTFILE
			RETURNCODE="OK"
			log "Modify $domainname at $INSTIME Success" $LOGFILE
                	CHECK_ZONE_TAG="CHECK"  
		else
			RETURNCODE="Modify Record Not Exist"
			log "Modify $domainname at $INSTIME Failed : Record Not Exist" $LOGFILE
		fi
	else
			RETURNCODE="Modify Record Not Exist"
			log "Modify $domainname at $INSTIME Failed : Record Not Exist" $LOGFILE
	fi
}

# Function Delte Domain
del_record()
{
	# $1 domain name www.alibaba.com
	# $2 record type A MX CNAME PTR
	# $3 ip or domain name 
	# $# arg count
	# check input format
	domainname=$1
	type=$2
	if (! (echo $domainname | grep -q "\.$" ))
	then
		domainname=`echo $domainname|sed -e 's/$/./g'` 
	fi

	case $type in
		A|a)
			IP=$3
			if (! (echo "$IP" |grep -q -P "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$" ))
			then
			  RETURNCODE="Input Ip Format Wrong"
			  return 
			fi
			delcontent="$domainname\tA\t$IP"
		;;
		CNAME|cname)
			CNAME=$3
			if (! (echo $CNAME | grep -q "\.$" ))
			then
				CNAME=`echo $CNAME|sed -e 's/$/./g'` 
			fi
			delcontent="$domainname\tCNAME\t$CNAME"
		;;
		MX|mx)
			MX_PRIORITY=$3
			MX_NAME=$4
			if (! (echo $MX_NAME | grep -q "\.$" ))
			then
				MX_NAME=`echo $MX_NAME|sed -e 's/$/./g'` 
			fi
			delcontent="$domainname\tMX\t$MX_PRIORITY\t$MX_NAME"
		;;
	esac

	# Find Domain Hosts File
	#ZONE=`echo $domainname | awk -F . '{print $(NF-2)"."$(NF-1)}'`
	#ZONE=`echo $domainname | sed  -r -e "s/\w+.(.*)./\1/g"`
	ZONE=`echo $domainname | sed 's/^[^.]\+.//'`
	#HOSTFILE=`find $ZONEDIR -name "hosts.$ZONE"`
	HOSTFILE=`find $ZONEDIR -name "${ZONE}hosts"`
	
	INSTIME=`date +%Y-%m-%d-%k:%M:%S`
	
	if [ -n "$HOSTFILE" ];then
		# hosts file already exist
		if( grep -q -P "$delcontent" $HOSTFILE)
		then
			log "bakcup $HOSTFILE To $BACKUPDIR" $LOGFILE
			#cp $HOSTFILE $BACKUPDIR/"hosts.$ZONE.`date +%Y-%m-%d-%k:%M:%S`"
			cp $HOSTFILE $BACKUPDIR/"${ZONE}.hosts.`date +%Y-%m-%d-%k:%M:%S`"
			sed -i -r -e "/$delcontent/d"	$HOSTFILE 
			CHECK_ZONE_TAG="CHECK"
			## delete zone from named.conf
			#left_record=`sed -n -e  '/record begin/,$p' $HOSTFILE |sed -e '1d'`
			#if [ -z "$left_record" ];then
			#	sed -i -r -e "/^zone.*$ZONE.*/,/^};$/d" $NAMED_CONF 
			#	rm -fr $HOSTFILE
			#	CHECK_CONF_TAG="CHECK"
			#else
			#	CHECK_ZONE_TAG="CHECK"
			#fi
			#RETURNCODE="OK"
			#log "del $delcontent at $INSTIME Success" $LOGFILE
		else
			RETURNCODE="Del Record Not Exist"
			log "Del $delcontent at $INSTIME Failed : Record Not Exist" $LOGFILE
		fi
	else
		RETURNCODE="Del Record Not Exist"
		log "Del $delcontent at $INSTIME Failed : Record Not Exist" $LOGFILE
	fi
}

# Function Query Domain
query_record()
{
	domainname=$1
	RETURNCODE=`dig +short $domainname |grep  -P "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"`	
}

# Function Reload Domain
reload_zone()
{
	hostfile=$1
	serial=`date +%y%m%d%M%S`	
	sed -r -i "s/^([ \t]*)[0-9]+([ \t]*;serial)/\1$serial\2/" $hostfile
	$RNDC_CMD reload >> $CHECK_LOG 2>&1
}
##################  Main Menu Loop ##################

# check dir
if [ ! -e "$BACKUPDIR" ];then
	mkdir -p "$BACKUPDIR"
fi
if [ ! -e "$ZONEDIR" ];then
	mkdir -p "$ZONEDIR"
fi

# define var
parm_count=$#

if [ $parm_count -lt 2 ]; then
	echo 
	display_title "Help: usage help..........................."
	display_message2 "Help: $0 add example.alibaba.com A 172.16.23.2 "
	display_message2 "Help: $0 modfiy example.alibaba.com A 172.16.23.2 "
	display_message2 "Help: $0 del example.alibaba.com A 172.16.23.2 "
	display_message2 "Help: $0 query example.alibaba.com"
	echo
        exit 0
fi

# detemine action
action=`echo $1 | tr [:upper:] [:lower:]`
shift
remaining_params="$*"
case $action in
     add|del|modify)
	if [ $parm_count -lt 4 ]; then
		RETURNCODE="Input Ip Format Wrong" 	
	else
		${action}_record $remaining_params
	fi
     ;;
     query)
	query_record $remaining_params
     ;;
     *)
	RETURNCODE="NO DEFINE FUNCTION"
     ;;
esac

# check zone and named.conf syntax
if [ -n "$CHECK_CONF_TAG" ];then
	$CHECKCONF	>> $CHECK_LOG 2>&1
#marked by jjh at 2007-10-08 16:21	
#	$RNDC_CMD reconfig >> $CHECK_LOG 2>&1
fi
if [ -n "$CHECK_ZONE_TAG" ];then
	$CHECKZONE $ZONE $HOSTFILE >> $CHECK_LOG 2>&1 
        reload_zone $HOSTFILE 
#marked by jjh at 2007-10-08 16:22
#	$RNDC_CMD reload >> $CHECK_LOG 2>&1
fi
# output return code

echo "STATUS=$RETURNCODE"
