# coding: utf-8

from console.common.logger import getLogger

logger = getLogger(__name__)
from django.db import models

class ComputeResPoolModel(models.Model):
    class Meta:
        db_table = "compute_res_pool"

    compute_name = models.CharField(
        max_length=100
    )

    pool_name = models.CharField(
        max_length=100
    )

    type = models.CharField(
        max_length=100
    )

    status = models.CharField(
        max_length=100
    )