from django.conf.urls import url

from views import (
    FlavorCreatePage,
    FlavorIndexPage,
    FlavorEditPage,
    FlavorDetailPage
)

urlpatterns = [

    url(r'^customize/flavor$', FlavorIndexPage.as_view()),
    url(r'^customize/flavor_detail$', FlavorDetailPage.as_view()),
    url(r'^customize/create_flavor$', FlavorCreatePage.as_view()),
    url(r'^customize/edit_flavor$', FlavorEditPage.as_view()),
]
