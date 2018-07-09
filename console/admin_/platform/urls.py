from django.conf.urls import url

from views import (
    Dashboard,
    NetworkResourceDetailPage,
    VirtualMachineResourcePage,
    ResourcesOverview,
    PlatformSettings,
    ConfigDashboard,
    GetPlatformName

)

urlpatterns = [
    url(r'^$', Dashboard.as_view()),
    url(r'^index$', Dashboard.as_view()),

    url(r'^dashboard$', Dashboard.as_view()),
    url(r'^platform_setting$', GetPlatformName.as_view()),

    url(r'^resources/overview$', ResourcesOverview.as_view()),
    url(r'^setting/advanced_config$', PlatformSettings.as_view()),
    url(r'^common/dashboard/config$', ConfigDashboard.as_view()),
    url(r'^sourceManage/virtualSource$', VirtualMachineResourcePage.as_view()),

    url(r'^sourceManage/outServer$', NetworkResourceDetailPage.as_view()),

]
