# coding=utf-8

from django.utils.translation import ugettext as _


class DiskType(object):
    (SSD, SATA) = range(1, 3)

    CHOICES = [
        (SSD, "ssd"),
        (SATA, "sata")
    ]

    TYPE_CHOICES = (
        ("ssd", _(u"SSD盘")),
        ("sata", _(u"SATA盘"))
    )

    CN = {
        SSD: _(u"SSD盘"),
        SATA: _(u"SATA盘")
    }

    MAP = {k: v for k, v in CHOICES}


class DiskStatus(object):
    CHOICES = (
        ('available', u'available'),
        ('in-use', u'in-use'),
        ('creating', u'creating'),
        ('deleting', u'deleting'),
        ('attaching', u'attaching'),
        ('detaching', u'detaching'),
        ('error', u'error'),
        ('error_deleting', u'error'),
        ('backing-up', u'saving'),
        ('restoring-backup', u'recovering')
    )

    MAP = {k: v for k, v in CHOICES}

    REVERSE_CHOICES = (
        ("available", u"available"),
        ("in-use", u"in-use"),
        ("creating", u"creating"),
        ("deleting", u"deleting"),
        ("attaching", u"attaching"),
        ("detaching", u"detaching"),
        ("error", u"error"),
        ("saving", u"backing-up"),
        ("recovering", u"restoring-backup")
    )


PATTERN_MAP = {
    "sata": 2,
    "ssd": 3
}

DISK_FILTER_MAP = {"disk_id": "name",
                   "disk_name": "disk_name",
                   "status": "status",
                   "attach_instance": "attach_instance",
                   "drive": "drive",
                   "size": "size",
                   "backup_datetime": "backup_datetime",
                   "create_datetime": "created_at",
                   "uuid": "id",
                   "new_size": "new_size",
                   "device": "device",
                   "disk_type": "volume_type",
                   "charge_mode": "charge_mode",
                   "is_normal": "is_normal"
                   }

STATUS_MAP = {"available": "available",
              "in-use": "in-use",
              "creating": "creating",
              "deleting": "deleting",
              "attaching": "attaching",
              "detaching": "detaching",
              "error": "error",
              "error_deleting": "error",
              "backing-up": "saving",
              "restoring-backup": "recovering"
              }

REVERSE_STATUS_MAP = {"available": "available",
                      "in-use": "in-use",
                      "creating": "creating",
                      "deleting": "deleting",
                      "attaching": "attaching",
                      "detaching": "detaching",
                      "error": "error",
                      "saving": "backing-up",
                      "recovering": "restoring-backup",
                      }
