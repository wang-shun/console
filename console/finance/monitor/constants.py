#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

VM_OPTIONS = {
    'cpu_util': 'CPU 利用率',
    'memory.usage': '内存利用率',
    'load': '负载'
}

VM_SUBTYPES = {
    'kvm': {
        'name': 'KVM',
        'subtypes': {},
        'options': VM_OPTIONS
    },
    'vmware': {
        'name': 'VMWare',
        'subtypes': {},
        'options': VM_OPTIONS
    }
}

VOLUME_SUBTYPES = VM_SUBTYPES

TYPES = {
    # 'cabinet': {
    #     'name': '机柜',
    #     'subtypes': {},
    #     'options': {}
    # },
    # 'switch': {
    #     'name': '交换机',
    #     'subtypes': {},
    #     'options': {}
    # },
    # 'host': {
    #     'name': '物理机',
    #     'subtypes': {},
    #     'options': {}
    # },
    # 'pm': {
    #     'name': '物理机硬盘',
    #     'subtypes': {},
    #     'options': {}
    # },
    'vm': {
        'name': '虚拟机',
        'subtypes': VM_SUBTYPES,
        'options': {}
    },
    'volume': {
        'name': '虚拟机硬盘',
        'subtypes': VOLUME_SUBTYPES,
        'options': {}
    },
    # 'traffic': {
    #     'name': '公网流量',
    #     'subtypes': {},
    #     'options': {}
    # },
    # 'business': {
    #     'name': '业务监控',
    #     'subtypes': {},
    #     'options': {}
    # }
}
