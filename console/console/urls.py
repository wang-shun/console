# coding=utf-8
"""Console URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import views
from console.admin_.platform.views import ResourcesOverview
from console.common.account import views as account_view
from console.router import Router

urlpatterns = [
    url(r'^$', views.Index.as_view()),
    url(r'^index$', views.Index.as_view(), name='index'),
    url(r'^logout$', account_view.Logout.as_view()),  # done
    url(r'^register/done/(?P<key>\w+)$', account_view.RegisterDone.as_view()),
    url(r'^ticket$', views.Ticket.as_view()),
    url(r'^message$', views.Message.as_view()),
    url(r'^bill$', views.Billing.as_view()),
    url(r'^user$', views.UserView.as_view()),
    url(r'^terminal$', views.Terminal.as_view()),
    url(r'^perm/deny$', views.PermissionDeny.as_view()),
    url(r'^help$', views.HelpPage.as_view()),
    url(r'^compatibility$', views.Compatibility.as_view()),
    url(r'^api/$', Router.as_view()),  # doing
    url(r'^password/reset$', account_view.ResetPassword.as_view()),
    url(r'^password/reset/done/(?P<key>\w+)$', account_view.ResetPasswordDone.as_view()),
    url(r'^password/reset/phone/(?P<key>\w+)$', account_view.CellPhoneResetPassword.as_view()),
    url(r'^password/reset/confirm/(?P<uidb64>\w+)/(?P<token>[\w-]+)$', account_view.ResetPasswordConfirm.as_view()),
    url(r'^password/reset/complete$', account_view.ResetPasswordComplete.as_view()),
    url(r'^id/check$', account_view.CheckIdentifier.as_view()),
    url(r'^register$', account_view.Register.as_view()),
    url(r'^devops$', views.DevOps.as_view()),

    url(r'^portal/', views.PortalDashboard.as_view())
]

urlpatterns += [
    url(r'^email/check$', account_view.CheckEmail.as_view()),
    url(r'^phone/check$', account_view.CheckCellphone.as_view()),
    url(r'^phone/change$', account_view.ChangeCellPhone.as_view()),
    url(r'^captcha/load$', account_view.LoadCaptcha.as_view()),  # done
    url(r'^captcha/check$', account_view.CheckCaptcha.as_view()),  # done
    url(r'^email/check$', account_view.CheckEmail.as_view()),
    url(r'^phone/check$', account_view.CheckCellphone.as_view()),
    url(r'^phone/change$', account_view.ChangeCellPhone.as_view()),
    url(r'^code$', account_view.SendCode.as_view()),
    url(r'^code/captcha$', account_view.SendCodeCaptcha.as_view()),
    url(r'^code/check$', account_view.CheckCode.as_view()),
    url(r'^resources/overview$', ResourcesOverview.as_view()),
]

# common urls

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [url(r'^admin/', include(admin.site.urls))]
    urlpatterns += [url(r'^debug/email$', account_view.PreviewEmailTemplate.as_view())]
