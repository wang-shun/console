#!/usr/bin/env bash

INIT_START=`date +%s`

PASSWD=123456
LICENSE="i31PaFNqSSWpug9G0YhXlua4RaS9LR5mdGl/iBtoD/hcY0SgwWcT1Pym2i4qS9lbeqy9YdB53Rc6Y2S6FvldTkan64Mw7pAK9jSiP6NSDe67Wrdvrf6LVczIu5I2ZU2QhtSAbHrFANgyKRYMwdhhf7jWIRCFdPRjR3F9g4NQbsY="
DATE="$(date +%Y-%m-%d)"

find . -type f -name '*.pyc' -delete

db_engine=`awk '/^db_engine = / {print $3}' conf/config.ini`

if [ "${db_engine}" == "sqlite3" ] ; then

    echo "use sqlite"
    sed -i '' -e "s/env.*/env = admin, console, finance/" conf/config.ini
    sqlite_db=`awk '/db_name = / {print $3}' conf/config.ini`
    rm -f ${sqlite_db}

elif [ "${db_engine}" == "mysql" ] ; then

    echo "use mysql"
    mysql_host=`awk '/^db_host = / {print $3}' conf/config.ini`
    mysql_user=`awk '/^db_user = / {print $3}' conf/config.ini`
    mysql_pass=`awk '/^db_password = / {print $3}' conf/config.ini`
    mysql_db=`awk '/^db_name = / {print $3}' conf/config.ini`
    echo "mysql -u$mysql_user -p$mysql_pass  -h $mysql_host"
    mysql -u$mysql_user -p$mysql_pass -h $mysql_host -e "drop database if exists ${mysql_db}"
    mysql -u$mysql_user -p$mysql_pass -h $mysql_host -e "create database ${mysql_db} default charset utf8"
    sed -i '' 's/env.*/env = admin, console, finance/g' conf/config.ini

fi

sleep 1

pip install -r requirements.txt

python manage.py migrate

# set license
cat << EOF | python manage.py shell
from console.common.license.helper import LicenseService
ret = LicenseService.set_license_key("${LICENSE}")

EOF

# 必须创建名为root的用户
# python manage.py createsuperuser
echo "root admin@cloudin.cn admin"
echo "
from django.contrib.auth.models import User;
User.objects.create_superuser('root', 'root@cloudin.cn', 'root')
" | python manage.py shell

for zone in bj test dev prod
do

    python manage.py import_zones ${zone} not
    python manage.py import_images ${zone} not
    python manage.py import_quotas ${zone} not
done

python manage.py import_zones all not
python manage.py import_flavors all not
python manage.py import_ip_pool all not

# base_net
cat << EOF | python manage.py shell
# coding=utf-8

from console.console.nets.models import BaseNetModel

for i in range(100, 151):
    for j in range(0, 256):
        cidr = "10.{0}.{1}.0".format(i, j)
        is_save = BaseNetModel.objects.init_base_net_model(cidr)

EOF

cat << EOF | python manage.py shell
# coding=utf-8

from console.console.nets.models import PowerNetModel

cidr = "10.100.0.0"
is_save = PowerNetModel.objects.init_power_net(cidr)

EOF

# admin user
echo "Create Admin Account:"
cat << EOF | python manage.py shell
# coding=utf-8
from console.common.account.helper import AccountService
account, err = AccountService.create('${USER}@cloudin.cn', '${USER}', '18910585600', name='${USER}')
account.user.is_superuser = True
account.user.save()

EOF

# accounts
cat << EOF | python manage.py shell
# coding=utf-8
import csv

from console.common.account.helper import AccountService

for name, username, phone in csv.reader(open('init/csv/members.csv')):
    email = '%s@cloudin.cn' % username
    if not AccountService.get_account_by_email(email):
        account, err = AccountService.create(email, username, phone, name=name)

EOF

# department
echo CloudIn | python manage.py init_department clear

# permissions
python manage.py import_permissions init/csv/permissions.csv clear

# rds
cat init/init_rds.sql|  python manage.py dbshell

# ticket
python manage.py import_flow clear sqlite3
python manage.py import_flow not sqlite3

# put the these code after init finance ticket so that ticket related permissions can be imported
# create permission_group administrator
cat << EOF | python manage.py shell
from console.common.account.helper import AccountService

from console.common.permission.helper import PermissionService, PermissionGroupService

account = AccountService.get_by_email("${USER}@cloudin.cn")
group = PermissionGroupService.create(account, "Administrator")
count, permissions = PermissionService.get_all()

n = PermissionGroupService.append_users(group, [account])
n = PermissionGroupService.append_permissions(group, permissions)

EOF

for zone in bj test dev prod
do
    # cmdb
    python manage.py import_cmdb init/csv/cmdb.cabinet.csv cabinet ${zone} clear
    python manage.py import_cmdb init/csv/cmdb.switch.csv switch ${zone} clear
    python manage.py import_cmdb init/csv/cmdb.pserver.csv pserver ${zone} clear

    # suites
    for vtype in KVM VMWARE
    do
        python manage.py import_suites ${zone} ${vtype} init/csv/suites-kvm-vmware.csv clear
    done

    for vtype in POWERVM
    do
        python manage.py import_suites ${zone} ${vtype} init/csv/suites-powervm.csv clear
    done

done

# apps
echo "start import appstore"
cat << EOF | python manage.py shell
# coding=utf-8
import csv

from console.finance.appstore.helper import AppstoreService

for app_name, app_publisher, app_version, app_zone in csv.reader(open('init/csv/apps.csv')):
    code, msg = AppstoreService.create(app_name, app_publisher, app_version, app_zone)

EOF

# tips
echo ""
echo "================================================================================"
echo "默认登录邮箱：${USER}@cloudin.cn"
echo "默认登录密码：${USER}"

INIT_END=`date +%s`
RUNTIME=$((INIT_END - INIT_START))
echo  "初始化用时$(($RUNTIME / 60))分$(($RUNTIME % 60))秒."