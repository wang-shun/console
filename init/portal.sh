#!/usr/bin/env bash

find . -type f -name '*.pyc' -delete

if [ $# == 0 ] ; then

    echo "use sqlite"
    sed -e "s/db_name.*sqlite3/db_name = finance.sqlite3/" \
	    -e "s/env.*/env = admin, console, finance/" \
	    conf/config.ini.sample > conf/config.ini
    rm -f finance.sqlite3

elif [ $1 == 'mysql' ] ; then

    echo "use mysql"
    mysql_host=`awk '/db_host = / {print $3}' conf/config.ini`
    mysql_user=`awk '/db_user = / {print $3}' conf/config.ini`
    mysql_pass=`awk '/db_password = / {print $3}' conf/config.ini`
    mysql_db=`awk '/db_name = / {print $3}' conf/config.ini`
    echo "mysql -u$mysql_user -p$mysql_pass  -h $mysql_host"
    mysql -u$mysql_user -p$mysql_pass -h $mysql_host -e "drop database if exists ${mysql_db}"
    mysql -u$mysql_user -p$mysql_pass -h $mysql_host -e "create database ${mysql_db} default charset utf8"
    sed -i '' 's/env.*/env = portal/g' conf/config.ini

fi

python manage.py migrate auth
python manage.py migrate

cat << EOF | python manage.py shell
# coding=utf-8
import csv
from console.common.account.helper import AccountService
from console.common.account.models import AccountType
for name, username, phone in csv.reader(open('init/csv/members.csv')):
    email = '%s@cloudin.cn' % username
    if not AccountService.get_account_by_email(email):
        account, error = AccountService.create(
            account_type=AccountType.TENANT,
            email=email,
            password=username,
            phone=phone,
            name=name
        )

EOF

LICENSE="i31PaFNqSSWpug9G0YhXlua4RaS9LR5mdGl/iBtoD/hcY0SgwWcT1Pym2i4qS9lbeqy9YdB53Rc6Y2S6FvldTkan64Mw7pAK9jSiP6NSDe67Wrdvrf6LVczIu5I2ZU2QhtSAbHrFANgyKRYMwdhhf7jWIRCFdPRjR3F9g4NQbsY="
cat << EOF | python manage.py shell
from console.common.license.helper import LicenseService
ret = LicenseService.set_license_key("${LICENSE}")

EOF

# cmdb
# echo "here"
# python manage.py import_cmdb init/csv/cmdb.cabinet.csv cabinet clear
# python manage.py import_cmdb init/csv/cmdb.pserver.csv pserver clear
# echo "here here"

cat << EOF | python manage.py create_portal_admin
admin@cloudin.cn
admin
13500000000
EOF

python manage.py init_portal_department

cat << EOF

login with admin account:
    username: admin@cloudin.cn
    password: admin

or your account:
    username: ${USER}@cloudin.cn
    password: ${USER}

EOF


#python manage.py runserver
