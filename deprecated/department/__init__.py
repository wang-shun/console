# coding=utf-8
__author__ = 'FF'

from django.apps import AppConfig


class PortalDepartmentConfig(AppConfig):
    name = 'console.portal.department'
    verbose_name = 'department'
    label = 'portal_department'


default_app_config = 'console.portal.department.PortalDepartmentConfig'
