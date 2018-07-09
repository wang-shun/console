from django.conf.urls import url

from views import (
    GetStorageDevicesNumber,
    GetStoragePoolInfos,
    ListStoragePools,
    CreateStoragePools,
    ResizeStoragePools,
    DeleteStoragePools,
    StoragePoolIndexPage,
    StoragePoolCreatePage,
    StoragePoolDetailPage,
    StoragePoolModifyPage

)

urlpatterns = [

    url(r'^pools/storage_resource/list$', ListStoragePools.as_view()),
    url(r'^pools/storage_resource/info$', GetStoragePoolInfos.as_view()),
    url(r'^pools/storage_resource/device', GetStorageDevicesNumber.as_view()),
    url(r'^pools/storage_resource/create$', CreateStoragePools.as_view()),
    url(r'^pools/storage_resource/adjust$', ResizeStoragePools.as_view()),
    url(r'^pools/storage_resource/delete$', DeleteStoragePools.as_view()),

    url(r'^sourceManage/memorySourceEdit$', StoragePoolModifyPage.as_view()),
    url(r'^sourceManage/memorySource$', StoragePoolIndexPage.as_view()),
    url(r'^sourceManage/memorySourceCreate$', StoragePoolCreatePage.as_view()),
    url(r'^sourceManage/memorySourceDetails$', StoragePoolDetailPage.as_view()),
]
