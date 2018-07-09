# coding=utf-8

import json

from django.db import models
from django.db import transaction
from django.db.models import Q
from django.forms.models import model_to_dict
from django.utils.timezone import now

from console.common.account.helper import AccountService
from console.common.logger import getLogger
from console.common.base import BaseModel
from console.common.zones.models import ZoneModel
from .utils import get_default_field_names

logger = getLogger(__name__)


class RecodeManage(models.Manager):
    def create(self, instance, ticket_id, applicant, approve, zone):
        excludes = set(["deleted", "create_datetime", "delete_datetime", "update_datetime", "instancesmodel"])
        try:
            if isinstance(instance, BaseCfgModel):
                fields = [
                    field
                    for field in get_default_field_names(type(instance))
                    if field not in excludes
                ]
                dct = model_to_dict(instance, fields=fields)
                dumps = json.dumps(dct)
                zone = ZoneModel.get_zone_by_name(zone)
                record = CfgRecordModel(model=instance.CFG_TYPE, rid=instance.id, content=dumps,
                                        ticket_id=ticket_id, applicant=applicant, approve=approve, zone=zone)
                record.save()
                return record, None
            else:
                raise TypeError('BaseCfgModel subclass instance required')
        except Exception as exp:
            logger.error('cannot create RecodeBackupModel instance')
            return None, exp


class CfgRecordModel(BaseModel):
    class Meta:
        db_table = 'cmdb_cfgrecord'

    model = models.CharField(max_length=100)
    rid = models.IntegerField()
    ticket_id = models.CharField(max_length=100)
    applicant = models.CharField(max_length=100)
    approve = models.CharField(max_length=100)
    content = models.TextField()
    zone = models.ForeignKey(to=ZoneModel)

    objects = RecodeManage()


class CfgModelManager(models.Manager):
    def build_model_params(self, _update=False, **kwargs):
        excludes = set(["deleted", "create_datetime", "delete_datetime", "id", "update_datetime", "instancesmodel", "zone_id"])
        fields = get_default_field_names(self.model)
        params = dict()
        for name in fields:
            if name not in excludes:
                if name not in kwargs:
                    if not _update:
                        raise ValueError("field '%s' required" % name)
                else:
                    params[name] = kwargs.get(name)
        return params

    def create(self, ticket_id, applicant, approve, zone, **kwargs):
        try:
            zone = ZoneModel.get_zone_by_name(zone)
            kwargs.update({'zone': zone})
            params = self.build_model_params(**kwargs)
            with transaction.atomic():
                item = self.model(**params)
                item.save()
                CfgRecordModel.objects.create(item, ticket_id, applicant, approve, zone)
                return item, None
        except Exception as exp:
            logger.error("cannot save the new data to database, %s" % exp.message)
            return None, exp

    def update(self, id, ticket_id, applicant, approve, zone, **kwargs):
        try:
            params = self.build_model_params(True, **kwargs)
            with transaction.atomic():
                item = self.model.get_item_by_id(id)
                for name, value in params.items():
                    setattr(item, name, value)
                item.save()
                CfgRecordModel.objects.create(item, ticket_id, applicant, approve, zone)
                return item, None
        except Exception as exp:
            logger.error("cannot update data to database, %s" % exp.message)
            return None, exp


class BaseCfgModel(BaseModel):
    class Meta:
        abstract = True

    CFG_TYPE = None
    SEARCH_FIELDS = ['cfg_id']

    cfg_id = models.CharField(max_length=100)

    objects = CfgModelManager()

    zone = models.ForeignKey(to=ZoneModel)

    def __unicode__(self):
        return self.cfg_id

    @classmethod
    def delete_item_by_id(cls, id, deleted=False):
        try:
            item = cls.objects.get(id=id, deleted=deleted)
            item.deleted = True
            item.delete_datetime = now()
            item.save()
        except Exception as exp:
            logger.error("cannot delete data , %s" % exp.message)

    @classmethod
    def item_exists_by_id(cls, id, deleted=False):
        return cls.objects.filter(id=id, deleted=deleted).exists()

    @classmethod
    def get_item_by_id(cls, id, deleted=False):
        if cls.item_exists_by_id(id, deleted=deleted):
            return cls.objects.get(id=id, deleted=deleted)
        else:
            return None

    @classmethod
    def get_all_items(cls, keyword=None, zone=None, page_index=1, page_size=10, deleted=False):
        zone = ZoneModel.get_zone_by_name(zone)
        query = cls.objects.filter(zone=zone, deleted=deleted)
        if cls.SEARCH_FIELDS and keyword:
            queries = list()
            for field in cls.SEARCH_FIELDS:
                kwargs = dict()
                key = '%s__contains' % field
                kwargs[key] = keyword
                queries.append(Q(**kwargs))
            search = queries.pop()
            for item in queries:
                search |= item
            query = query.filter(search)
        start = (page_index - 1) * page_size
        stop = page_index * page_size if page_size else None
        all_items = query.order_by('-create_datetime')
        return all_items[start:stop], len(all_items)


class VirtServModel(BaseCfgModel):
    class Meta:
        db_table = 'cmdb_vserver'

    CFG_TYPE = 'vserver'

    name = models.CharField(max_length=100)
    cpu = models.IntegerField()
    memory = models.IntegerField()
    net = models.CharField(max_length=100)
    wan_ip = models.CharField(max_length=100)
    os = models.CharField(max_length=100)
    sys = models.CharField(max_length=100)


class PhysServModel(BaseCfgModel):
    class Meta:
        db_table = 'cmdb_pserver'

    CFG_TYPE = 'pserver'
    SEARCH_FIELDS = ['cfg_id', 'name', 'cabinet', 'lan_ip', 'wan_ip']

    name = models.CharField(max_length=100)
    cpu = models.IntegerField()
    memory = models.IntegerField()
    cabinet = models.CharField(max_length=100)
    gbe = models.IntegerField()
    gbex10 = models.IntegerField()
    lan_ip = models.CharField(max_length=100)
    wan_ip = models.CharField(max_length=100)
    ipmi = models.CharField(max_length=40)
    cputype = models.CharField(max_length=10)
    harddrive = models.CharField(max_length=10)
    state = models.CharField(max_length=10)


class CabinetModel(BaseCfgModel):
    class Meta:
        db_table = 'cmdb_cabinet'

    CFG_TYPE = 'cabinet'

    phys_count = models.IntegerField()
    cpu = models.IntegerField()
    memory = models.IntegerField()
    sata = models.FloatField()
    ssd = models.FloatField()


class SwitchModel(BaseCfgModel):
    class Meta:
        db_table = 'cmdb_switch'

    CFG_TYPE = 'switch'

    gbe = models.IntegerField()
    gbex10 = models.IntegerField()
    forward = models.IntegerField()


class DataBaseModel(BaseCfgModel):
    class Meta:
        db_table = 'cmdb_db'

    CFG_TYPE = 'db'
    SEARCH_FIELDS = ['cfg_id', 'name', 'version', 'memo', 'net']

    name = models.CharField(max_length=100)
    version = models.CharField(max_length=100)
    memo = models.CharField(max_length=100, null=True)
    instance = models.CharField(max_length=100)
    net = models.CharField(max_length=100)
    capacity = models.IntegerField()


class SystemModel(BaseCfgModel):
    class Meta:
        db_table = 'cmdb_sys'

    CFG_TYPE = 'sys'
    SEARCH_FIELDS = ['cfg_id', 'name', 'version', 'hosts']

    name = models.CharField(max_length=100)
    version = models.CharField(max_length=100)
    man = models.CharField(max_length=100)
    hosts = models.CharField(max_length=100)
    weight = models.CharField(max_length=32)

    @classmethod
    def get_all_items(cls, keyword=None, zone=None, page_index=1, page_size=0, deleted=False):
        zone = ZoneModel.get_zone_by_name(zone)
        query = cls.objects.filter(zone=zone, deleted=deleted)
        if cls.SEARCH_FIELDS and keyword:
            queries = list()
            accounts = AccountService.search_by_name(keyword)
            if accounts:
                usernames = [
                    account.user.username
                    for account in accounts
                ]
                queries.append(Q(man__in=usernames))
            for field in cls.SEARCH_FIELDS:
                kwargs = dict()
                key = '%s__contains' % field
                kwargs[key] = keyword
                queries.append(Q(**kwargs))
            search = queries.pop()
            for item in queries:
                search |= item
            query = query.filter(search)
        all_items = query.order_by('-create_datetime')
        return all_items[(page_index - 1) * page_size:page_index * page_size or None], len(all_items)


class MiddlewareModel(BaseCfgModel):
    """
    cmdb 中间件模块
    """

    class Meta:
        db_table = "cmdb_midware"

    CFG_TYPE = "middleware"
    SEARCH_FIELDS = ["cfg_id", "name", "version", "hosts"]

    name = models.CharField(max_length=100)
    version = models.CharField(max_length=100)
    hosts = models.CharField(max_length=100)


ALL_CFG_MODELS = {cls.CFG_TYPE: cls for cls in BaseCfgModel.__subclasses__()}
