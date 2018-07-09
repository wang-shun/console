# coding=utf-8

__author__ = 'chenlei'

import logging
import os
import sys
import time

from fabric import api
from fabric.context_managers import lcd
from fabric.contrib import files
from fabric.contrib import project
from fabric.operations import sudo

logging.basicConfig(level=logging.NOTSET,
                    format='[%(levelname)s]\t%(asctime)s\t%(pathname)s:%(lineno)s\t%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S %Z')

logger = logging.getLogger(__name__)


WORKSPACE = os.getenv('WORKSPACE')

DEPLOY_HOST = os.getenv('deploy_host')
DEPLOY_SERVICE = os.getenv('deploy_service')

PACKAGE_VERSION = os.getenv('CONSOLE_VERSION')
PACKAGE_FILE = 'source.%s.tar.gz' % PACKAGE_VERSION

LOCAL_TEMP_PATH = '/tmp/console_deploy'
LOCAL_SOURCE_PACKAGE = os.path.join(LOCAL_TEMP_PATH, PACKAGE_FILE)
LOCAL_PORTAL_CONF = os.path.join(LOCAL_TEMP_PATH, 'portal.ini')
LOCAL_FINANCE_CONF = os.path.join(LOCAL_TEMP_PATH, 'finance.ini')

REMOTE_TEMP_PATH = '/opt/console_deploy'
REMOTE_PORTAL_CONF = os.path.join(REMOTE_TEMP_PATH, 'portal.ini')
REMOTE_FINANCE_CONF = os.path.join(REMOTE_TEMP_PATH, 'finance.ini')
REMOTE_SOURCE_PACKAGE = os.path.join(REMOTE_TEMP_PATH, PACKAGE_FILE)

SOURCE_PATH_BASE = '/opt/console/projects'
PROJECT_CONF_PATH = os.path.join(SOURCE_PATH_BASE, 'conf')
PORJECT_PORTAL_PATH = os.path.join(SOURCE_PATH_BASE, 'portal')
PROJECT_FINANCE_PATH = os.path.join(SOURCE_PATH_BASE, 'finance')

ALL_CONF_PATH = [REMOTE_FINANCE_CONF, REMOTE_PORTAL_CONF]
ALL_PROJECT_PATH = [PROJECT_FINANCE_PATH, PORJECT_PORTAL_PATH]

DEFAULT_BRANCH = 'dev'
SELECTED_TAG = os.getenv('ConsoleGitVersion')

SUPERVISORD_CONFIG = os.path.join(SOURCE_PATH_BASE, 'conf/supervisor/supervisord.ini')
SOURCE_ENV_CMD = 'source /opt/console/bin/activate'

api.env.hosts = [DEPLOY_HOST]
api.env.user = 'jenkins'
api.env.warn_only = False


def package_source():
    """
    打包jenkins workspace 中的代码
    :return:
    """
    logger.info('=' * 30)
    logger.info('打包jenkins workspace 中的代码')

    with lcd(WORKSPACE):
        if not os.path.isdir(LOCAL_TEMP_PATH):
            logger.info('make directory for save source zip file: %s' % LOCAL_TEMP_PATH)
            os.mkdir(LOCAL_TEMP_PATH)
            logger.info('Done.')

        if SELECTED_TAG:
            logger.info('checkout source with tag %s from branch %s' % (SELECTED_TAG, DEFAULT_BRANCH))
            checkout_cmd = 'git checkout -b %s %s' % (DEFAULT_BRANCH, SELECTED_TAG)
            api.local(checkout_cmd)
            logger.info('Done.')

        logger.info('create and compress source package')
        tar_package_cmd = '/bin/tar zcf %s --exclude .git .' % LOCAL_SOURCE_PACKAGE
        show_package_cmd = 'ls -alh %s' % LOCAL_SOURCE_PACKAGE
        api.local(tar_package_cmd)
        api.local(show_package_cmd)


def rsync_package_and_config():
    """
    将本地的代码压缩包和配置文件，同步到部署目标服务器的部署目录
    :return:
    """
    logger.info('=' * 30)
    logger.info('将本地的代码压缩包和配置文件，同步到部署目标服务器的部署目录')

    if not files.exists(REMOTE_TEMP_PATH):
        logger.info('make directory for save source zip file: %s' % REMOTE_TEMP_PATH)
        sudo('mkdir -p %s' % REMOTE_TEMP_PATH)
        sudo('chown -R %s:%s %s' % (api.env.user, api.env.user, REMOTE_TEMP_PATH))
        logger.info('Done.')

    source_and_config = os.path.join(LOCAL_TEMP_PATH, '*')
    project.rsync_project(local_dir=source_and_config, remote_dir=REMOTE_TEMP_PATH, delete=True,
                          ssh_opts='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null')


def unpack_package():
    """
    解压部署目录中的代码到对应的源码位置
    :return:
    """
    logger.info('=' * 30)
    logger.info('解压部署目录中的代码到对应的源码位置')

    if not files.exists(REMOTE_SOURCE_PACKAGE):
        logger.info('remote package %s is not exist' % REMOTE_SOURCE_PACKAGE)
        sys.exit(-1)

    for source_dir in ALL_PROJECT_PATH:
        logger.info('extract source to%s' % source_dir)
        sudo('/bin/tar zxf %s -C %s' % (REMOTE_SOURCE_PACKAGE, source_dir))


def sync_configs():
    """
    同步各个服务所用的配置文件
    :return:
    """
    for conf in ALL_CONF_PATH:
        logger.info('copy %s to %s' % (conf, PROJECT_CONF_PATH))
        sudo('cp %s %s' % (conf, PROJECT_CONF_PATH))
        logger.info('Done.')


def restart_services():
    """
    利用supervisor 重启各个服务
    :return:
    """
    logger.info('=' * 30)
    logger.info('利用supervisor 重启各类服务')

    supervisor_restart = 'supervisorctl -c %s restart all' % SUPERVISORD_CONFIG
    supervisor_status = 'supervisorctl -c %s status' % SUPERVISORD_CONFIG

    with api.prefix(SOURCE_ENV_CMD):
        sudo(supervisor_restart)
        api.run('sleep 5')
        time.sleep(5)
        sudo(supervisor_status)


def collect_static_files():
    """
    收集console的静态文件
    :return:
    """
    logger.info('=' * 30)
    logger.info('收集console的静态文件到nginx静态文件服务目录')
    with api.prefix(SOURCE_ENV_CMD):
        for source_dir in ALL_PROJECT_PATH:
            with api.cd(source_dir):
                sudo('pwd')
                sudo('./manage.py collectstatic --noinput')


def migrate_database():
    """
    迁移数据,同步数据表
    :return:
    """
    logger.info('=' * 30)
    logger.info('同步console的数据表')
    with api.prefix(SOURCE_ENV_CMD):
        for source_dir in ALL_PROJECT_PATH:
            with api.cd(source_dir):
                sudo('pwd')
                sudo('./manage.py migrate --noinput')


def install_requirements():
    """
    安装依赖包
    """
    logger.info('=' * 30)
    logger.info('安装依赖包。。。')

    with api.prefix(SOURCE_ENV_CMD):
        for source_dir in ALL_PROJECT_PATH[0]:
            with api.cd(source_dir):
                sudo('pip install -r requirements.txt')
