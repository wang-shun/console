# coding=utf-8
"""Console URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from console.console import views as console_view
from cmdb.views import file_down
from console.finance.monitor.views import upload_monitor_business_script
from console.finance.report.views import DownloadReportView
urlpatterns = []

finance_urlpatterns = [

    url(r'^$', console_view.FinanceCloud.as_view()),  # screen
    url(r'index$', console_view.FinanceIndex.as_view()),
    url(r'upload_monitor_business_script', upload_monitor_business_script),
    url(r'(ops|operationModule|resourceManage|store|safety|monitor|backstage|cmdb(?!/file))', console_view.FinanceIndex.as_view()),
    # url(r'ops', console_view.OpsModule.as_view()),
    # url(r'safety$', console_view.SafetyModule.as_view()),
    # url(r'monitor$', console_view.MonitorModule.as_view()),
    # url(r'resource$', console_view.ResourceModule.as_view()),
    # url(r'backstage$', console_view.BackstageModule.as_view()),
    # url(r'cmdb$', console_view.CMDBModule.as_view()),
    # url(r'serviceCenter$', console_view.ServiceModule.as_view()),

    url(r'user$', console_view.UserModule.as_view()),
    url(r'screen$', console_view.FinanceScreen.as_view()),  # new screen
    url(r'cmdb\/file$', file_down),
    url(r'^report/download', DownloadReportView.as_view()),
]

urlpatterns += finance_urlpatterns
urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [url(r'admin/', include(admin.site.urls))]
