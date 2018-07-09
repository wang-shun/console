#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from django.conf import settings
from django.db import models
from jsonfield import JSONField

from console.common.base import BaseModel
from console.common.zones.models import ZoneModel


class ElasticGroup(BaseModel):
    ID_PREFIX = 'elt'

    class Status(object):
        INACTIVE, ACTIVE = ALL = range(2)

    id = models.CharField(primary_key=True, max_length=len(ID_PREFIX) + settings.NAME_ID_LENGTH + 1)
    info = JSONField()
    info_name = models.CharField(max_length=40, db_index=True)
    info_loadbalance_id = models.CharField(max_length=20, db_index=True)
    config = JSONField()
    trigger = JSONField()
    trigger_name = models.CharField(max_length=40, db_index=True)
    status = models.PositiveSmallIntegerField(default=Status.INACTIVE)
    stack_id = models.CharField(unique=True, null=True, max_length=37, help_text='openstack heat stack id')
    zone = models.ForeignKey(to=ZoneModel)
