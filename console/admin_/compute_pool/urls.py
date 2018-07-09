from django.conf.urls import url

from views import (
    ListComputeResourcePools,
    CreateComputeResourcePool,
    DeleteComputeResourcePool,
    RenameComputeResourcePool,
    AddHostsInComputeResourcePool,
    DelHostsInComputeResourcePool,
    ListInstancesInComputePools,
    ListOneComputeResourcePool,
    omputePoolIndexPage,
    ComputePoolCreatePage,
    ComputePoolDetailPage,
    ComputePoolEditPage

)

urlpatterns = [
    url(r'^pools/compute_resource/list$', ListComputeResourcePools.as_view()),
    url(r'^pools/compute_resource/create$', CreateComputeResourcePool.as_view()),
    url(r'^pools/compute_resource/delete$', DeleteComputeResourcePool.as_view()),
    url(r'^pools/compute_resource/rename$', RenameComputeResourcePool.as_view()),
    url(r'^pools/compute_resource/addhosts$', AddHostsInComputeResourcePool.as_view()),
    url(r'^pools/compute_resource/delhosts$', DelHostsInComputeResourcePool.as_view()),
    url(r'^pools/compute_resource/list_instance$', ListInstancesInComputePools.as_view()),
    url(r'^pools/compute_resource/list_one_pool$', ListOneComputeResourcePool.as_view()),

    url(r'^sourceManage/computeSource$', omputePoolIndexPage.as_view()),
    url(r'^sourceManage/computeSourceCreate$', ComputePoolCreatePage.as_view()),
    url(r'^sourceManage/computeSourceEdit$', ComputePoolEditPage.as_view()),
    url(r'^sourceManage/computeSourceDetails$', ComputePoolDetailPage.as_view()),
]
