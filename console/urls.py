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
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from admin_.platform.views import Dashboard as AdminIndex
from common.account.views import Login, Logout, LoginUserInfo, ListLoginHistory, ChangePassword
from common.license.views import License
from console.views import FinanceCloud
from console.views import FinanceIndex
from console.views import Index as ConsoleIndex
from portal.root.views import PortalIndex
from router import Router

common_urlpatterns = staticfiles_urlpatterns() + [
    url(r'^license$', License.as_view()),
    url(r'^login$', Login.as_view(), name='login'),  # done
    url(r'^login/history$', ListLoginHistory.as_view()),
    url(r'^logout$', Logout.as_view()),  # done
    url(r'^user/info$', LoginUserInfo.as_view()),  # done
    url(r'^password/change$', ChangePassword.as_view()),
]

console_urlpatterns = [
    url(r'^console$', ConsoleIndex.as_view()),
    url(r'^console/', include('console.console.urls')),
    url(r'^console/api', Router.as_view(), {'loader': 'console.console.%s.views'})
]

admin_urlpatterns = [
    url(r'^admin$', AdminIndex.as_view()),
    url(r'^admin/', include('console.admin_.urls')),
    url(r'^admin/api', Router.as_view(), {'loader': 'console.console.%s.views'})
]
finance_urlpatterns = [
    url(r'^$', FinanceIndex.as_view()),
    url(r'^finance$', FinanceIndex.as_view()),
    url(r'^finance/', include('console.finance.urls')),
    url(r'^finance/api', Router.as_view(), {'loader': 'console.finance.%s.views'}),
    url(r'^financeCloud$', FinanceCloud.as_view())
]

portal_urlpatterns = [
    url(r'^$', PortalIndex.as_view()),
    url(r'^portal$', PortalIndex.as_view()),
    url(r'^portal/api', Router.as_view(), {'loader': 'console.portal.%s.views'}),
]

urlpatterns = common_urlpatterns

if 'console' in settings.ENV:
    urlpatterns += console_urlpatterns  # run: console

if 'admin' in settings.ENV:
    urlpatterns += admin_urlpatterns  # run: console admin

if 'finance' in settings.ENV:
    urlpatterns += finance_urlpatterns  # run: console admin finance

if 'portal' in settings.ENV:
    urlpatterns = common_urlpatterns + portal_urlpatterns  # run: portal
