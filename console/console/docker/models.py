from django.db import models

from django.contrib.auth.models import User
from console.common.zones.models import ZoneModel

# Create your models here.

class ClusterManager(models.Manager):
    def create(self,
               owner,
               zone,
               cluster_id,
               name,
               size):
        try:
            user = User.objects.get(username=owner)
            zone = ZoneModel.objects.get(name=zone)
            _cluster_model = ClusterModel(
                user=user,
                zone=zone,
                cluster_id=cluster_id,
                name=name,
                size=size
            )
            _cluster_model.save()
            return _cluster_model, None
        except Exception as exp:
            return None, exp

class ClusterModel(models.Model):
    class Meta:
        db_table = 'cluster'

    cluster_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    size = models.IntegerField(
        default=0
    )
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,
                             on_delete=models.PROTECT)
    zone = models.ForeignKey(ZoneModel,
                             on_delete=models.PROTECT)
    status = models.BooleanField(default=False)
    cluster_uuid = models.CharField(unique=True, null=True, max_length=37, help_text='openstack heat stack id')
    objects = ClusterManager()
