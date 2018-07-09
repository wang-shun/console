# coding=utf-8


from django.conf.urls import include, url

urlpatterns = [

    url(r'^', include('console.admin_.admin_flavor.urls')),
    url(r'^', include('console.admin_.admin_image.urls')),
    url(r'^', include('console.admin_.admin_instance.urls')),
    url(r'^', include('console.admin_.admin_router.urls')),
    url(r'^', include('console.admin_.admin_subnet.urls')),
    url(r'^', include('console.admin_.compute_pool.urls')),
    url(r'^', include('console.admin_.ip_pool.urls')),
    url(r'^', include('console.admin_.physic_machine.urls')),
    url(r'^', include('console.admin_.platform.urls')),
    url(r'^', include('console.admin_.storage_pool.urls')),
]
