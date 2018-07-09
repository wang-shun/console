# coding=utf-8
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _

from console.common.zones.models import ZoneModel

IMAGE_PLATFORM_CHOICES = (
    ("windows", _("Windows")),
    ("linux", _("Linux"))
)

IMAGE_STATUS_CHOICES = (
    ("available", _("Available")),
    ("error", _("Not Available")),
    ("creating", _("creating")),
    ("deleting", _("deleting")),
)


class ImageModelManager(models.Manager):

    def create(self, api_image_id, image_name, status, platform,
               system, size, zone, owner, image_id=None):
        try:
            zone = ZoneModel.objects.get(name=zone)
            user = User.objects.get(username=owner)
            if image_id is None:
                while True:
                    image_id = 'img-%s' % (str(uuid.uuid4())[:8])
                    if ImageModel.image_exists(image_id) is False:
                        break
            image = ImageModel(
                image_id=image_id,
                api_image_id=api_image_id,
                image_name=image_name,
                status=status,
                platform=platform,
                system=system,
                size=size,
                zone=zone,
                user=user
            )
            image.save()
            return image, None
        except Exception as exp:
            return None, exp

    def delete(self, api_image_id):
        try:
            resp = ImageModel.objects.get(api_image_id=api_image_id).delete()
            return resp, None
        except Exception as exp:
            return None, exp


class ImageModel(models.Model):

    class Meta:
        db_table = "images"
        unique_together = ('zone', 'api_image_id')

    image_id        = models.CharField(max_length=20, unique=True)
    api_image_id    = models.CharField(max_length=100)
    image_name      = models.CharField(max_length=100)
    status          = models.CharField(max_length=30, choices=IMAGE_STATUS_CHOICES)
    platform        = models.CharField(max_length=30, choices=IMAGE_PLATFORM_CHOICES)
    system          = models.CharField(max_length=100, unique=False)
    size            = models.CharField(max_length=30)
    create_datetime = models.DateTimeField(auto_now_add=True)

    zone            = models.ForeignKey(ZoneModel, on_delete=models.PROTECT)
    user            = models.ForeignKey(User, on_delete=models.PROTECT)
    objects         = ImageModelManager()

    def __unicode__(self):
        return self.image_id

    @classmethod
    def image_exists(cls, image_id):
        return cls.objects.filter(image_id=image_id).exists()

    @classmethod
    def get_image_by_id(cls, image_id):
        if cls.image_exists(image_id):
            return cls.objects.get(image_id=image_id)
        return None

    @classmethod
    def get_image_by_uuid(cls, uuid, zone_id):
        try:
            return cls.objects.get(api_image_id=uuid, zone_id=zone_id)
        except ImageModel.DoesNotExist:
            return None
