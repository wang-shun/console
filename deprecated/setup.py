# coding=utf-8
import os
import sys
from setuptools import setup, find_packages
from shutil import rmtree
from console.console import VERSION


PACKAGES = [
    'console.console',
    'console.console.ips',
    'console.console.nets',
    'console.console.disks',
    'console.console.zones',
    'console.console.images',
    'console.console.quotas',
    'console.console.account',
    'console.console.backups',
    'console.console.records',
    'console.console.tickets',
    'console.console.wallets',
    'console.console.billings',
    'console.console.keypairs',
    'console.console.security',
    'console.console.instances',
    'console.console.routers',
    'console.console',
    'console.common',
    'console'
]

install_requires = [
    'gevent',
    'django==1.8',
    'djangorestframework==3.2.2',
    'requests',
    'netaddr',
    'MySQL-python',
    'gunicorn'
]


setup(
    name='console',
    version=VERSION,
    packages=PACKAGES,
    install_requires=install_requires,
    url='http://192.168.100.195:8000/',
    license='Private',
    author='cloudin-engineers',
    author_email='console@Cloudin.cn',
    description="Cloudin Console API",
    long_description=open("README", "r").read().decode("utf-8"),
    zip_safe=False,
    include_package_data=True,
    package=find_packages(),

)

# 安装pillow如果报错
# apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev
# liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk
