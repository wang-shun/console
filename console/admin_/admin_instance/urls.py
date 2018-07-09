from django.conf.urls import url

from views import (
    CreateSpeedyCreationInstances,
    AssignSpeedyCreationInstances,
    DescribeSpeedyCreationInstances,
    SpeedyCreationListPage,
    DisperseInstances,
    MigrateInstances,
    DescribeInstances

)

urlpatterns = [
    url(r'^pools/compute_resource/top_speed_admin$', CreateSpeedyCreationInstances.as_view()),
    url(r'^pools/compute_resource/top_speed_console$', AssignSpeedyCreationInstances.as_view()),
    url(r'^pools/compute_resource/descr_top_speed$', DescribeSpeedyCreationInstances.as_view()),

    url(r'^sourceManage/topSpeed$', SpeedyCreationListPage.as_view()),

    url(r'^host_disperse/api$', DisperseInstances.as_view()),
    url(r'^host_migrate/api$', MigrateInstances.as_view()),
    url(r'^describe_instances$', DescribeInstances.as_view()),
]
