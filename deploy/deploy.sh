#!/usr/bin/env bash

TIMEOUT=60
RETRY_TIMES=10

# 分别写入config.ini, fabfile.py
echo -e "${config_file}" | \
sed -e "s/env.*/env = admin, console, finance/" \
    -e "s/db_name.*/db_name = finance_bjb/" \
    -e "s|static_root.*|static_root = /var/www/finance/statics|" \
    > /tmp/console_deploy/finance.ini

echo -e "${config_file}" | \
sed -e "s/env.*/env = portal/" \
    -e "s/db_name.*/db_name = portal/" \
    -e "s|static_root.*|static_root = /var/www/portal/statics|" \
    > /tmp/console_deploy/portal.ini

deploy_console()
{
    cd ${WORKSPACE}/deploy

    fab -f fab.py package_source
    fab -f fab.py rsync_package_and_config
    fab -f fab.py unpack_package
    fab -f fab.py sync_configs
    fab -f fab.py install_requirements
    fab -f fab.py migrate_database
    fab -f fab.py collect_static_files
    fab -f fab.py restart_services
}


# 把逗号替换成空格， 并形成一个数组
deploy_hosts=(${deploy_hosts//,/ })

# 分别部署数组中中的每一台机器
for deploy_host in ${deploy_hosts[@]}
do
	deploy_host="${deploy_host}" deploy_console
    sleep 5
done

