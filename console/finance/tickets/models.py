# coding=utf-8
import json

from django.contrib.auth.models import User
from django.db import models

from console.common.zones.models import ZoneModel
from console.common.logger import getLogger
from console.common.ticket_engine.models import FlowNodeModel, TicketTypeModel

logger = getLogger(__name__)
__author__ = 'shangchengfei'


class FinanceTicketModel(models.Model):
    """
    工单表，负责工单列表的展示
    """

    class Meta:
        db_table = "finance_ticket"

    ticket_type = models.ForeignKey(
        TicketTypeModel,
        on_delete=models.PROTECT,
    )
    ticket_id = models.AutoField(
        primary_key=True
    )
    # 申请者
    applicants = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="applicants",
    )
    # 标题
    title = models.CharField(
        max_length=50,
        null=True,
        default=None,
    )
    # 申请时间
    commit_time = models.DateTimeField(
        auto_now_add=True,
    )
    # 经过的边的一个栈，用于返回上一级
    path_stack = models.CharField(
        max_length=10000,
        default='[]'
    )
    # 最近处理时间
    last_update_time = models.DateTimeField(
        auto_now=True,
    )
    # 最近处理人
    last_handle = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="last_handle",
    )
    # 当前结点
    cur_node = models.ForeignKey(
        FlowNodeModel,
        on_delete=models.PROTECT,
    )
    # 当前状态：create, doing, finish, delay
    cur_status = models.CharField(
        max_length=20,
    )
    # 系统名称
    system_name = models.CharField(
        max_length=20,
        null=True,
        default=None,
    )
    # 所属应用系统
    app_system = models.CharField(
        max_length=20,
        default=None,
        null=True,
    )
    # 变更级别（变更工单）
    update_level = models.CharField(
        max_length=20,
        default=None,
        null=True,
    )
    # 计划开始时间（变更工单和软件发布工单）
    plan_start_time = models.DateTimeField(
        null=True,
        default=None,
    )
    # 计划结束时间（变更工单和软件发布工单）
    plan_end_time = models.DateTimeField(
        null=True,
        default=None,
    )
    # 上线系统（软件发布）
    release_system = models.CharField(
        max_length=20,
        default=None,
        null=True,
    )
    # 修改配置项分类（CMDB）
    cmdb_item = models.CharField(
        max_length=20,
        default=None,
        null=True,
    )
    warning_times = models.CharField(
        max_length=50,
        null=True,
        default=None,
    )
    resp_time = models.IntegerField(
        default=0,
    )
    step = models.IntegerField(
        default=0,
    )
    # # 是否关注此事件
    # attention = models.BooleanField(
    #     default=False,
    # )
    # attention_user = models.ForeignKey(
    #     User,
    #     on_delete=models.PROTECT,
    # )
    # attention_at = models.DateTimeField(
    #
    # )
    # # 显示字段
    # display = models.CharField(
    #     max_length=1000,
    #     null=True,
    # )
    zone = models.ForeignKey(to=ZoneModel)

    def __unicode__(self):
        return "%s-%s" % (self.ticket_type, self.ticket_id)

    @classmethod
    def create_ticket(cls,
                      ticket_type=None,
                      applicants=None,
                      title=None,
                      last_handle=None,
                      path_stack='[]',
                      cur_node=None,
                      system_name=None,
                      app_system=None,
                      update_level=None,
                      plan_start_time=None,
                      plan_end_time=None,
                      release_system=None,
                      cmdb_item=None,
                      warning_times=None,
                      zone=zone
                      ):
        zone = ZoneModel.get_zone_by_name(zone)
        ticket_type = TicketTypeModel.objects.get(ticket_type=ticket_type)
        applicants = User.objects.get(username=applicants)
        last_handle = User.objects.get(username=last_handle)
        try:
            ticket = cls.objects.create(
                ticket_type=ticket_type,
                applicants=applicants,
                title=title,
                last_handle=last_handle,
                cur_node=cur_node,
                system_name=system_name,
                app_system=app_system,
                update_level=update_level,
                plan_start_time=plan_start_time,
                plan_end_time=plan_end_time,
                release_system=release_system,
                cmdb_item=cmdb_item,
                warning_times=warning_times,
                path_stack=path_stack,
                zone=zone
            )
            return ticket.ticket_id
        except Exception as exp:
            logger.error(msg=exp)
            return None

    @classmethod
    def get_ticket_by_type(cls, ticket_type, zone):
        try:
            return cls.objects.filter(ticket_type__ticket_type=ticket_type, zone__name=zone)
        except Exception as exp:
            logger.error(msg=exp)
            return []

    @classmethod
    def get_ticket_by_id(cls, ticket_id):
        try:
            ticket = cls.objects.get(ticket_id=ticket_id)
            return ticket
        except Exception as exp:
            logger.error(msg=exp)
            return None

    @classmethod
    def get_exists_by_id(cls, ticket_id):
        try:
            return cls.objects.filter(ticket_id=ticket_id).exists()
        except Exception as exp:
            logger.error(msg=exp)
            return []

    @classmethod
    def get_ticket_by_type_and_status(cls, ticket_type, ticket_status, zone):
        try:
            ticket_list = cls.objects.filter(ticket_type__ticket_type=ticket_type).filter(cur_status=ticket_status, zone__name=zone)
            return ticket_list
        except Exception as exp:
            logger.error(msg=exp)
            return []

    @classmethod
    def attention_ticket(cls, ticket_id):
        pass


class TicketRecordModel(models.Model):
    """
    工单记录表，负责记录工单的节点，以及节点的内容
    此表关联 工单表，node节点
    """

    class Meta:
        db_table = "ticket_record"

    ticket = models.ForeignKey(
        FinanceTicketModel,
        on_delete=models.PROTECT,
    )
    opera_time = models.DateTimeField(
        auto_now_add=True,
    )
    fill_data = models.CharField(
        max_length=10000,
    )   # 这个用来填充node节点
    handle = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
    )
    cur_node = models.ForeignKey(
        FlowNodeModel,
        on_delete=models.PROTECT,
        related_name='cur_node'
    )
    next_node = models.ForeignKey(
        FlowNodeModel,
        on_delete=models.PROTECT,
        related_name='next_node'
    )
    opera_type = models.CharField(
        max_length=20,
    )

    @classmethod
    def create_ticket_record(cls, ticket, fill_data, handle, cur_node, next_node, opera_type):
        try:
            fill_data = json.dumps(fill_data)
            return cls.objects.create(
                ticket=ticket,
                fill_data=fill_data,
                handle=handle,
                cur_node=cur_node,
                next_node=next_node,
                opera_type=opera_type,
            )
        except Exception as exp:
            logger.error(msg=exp)
            return False

    @classmethod
    def get_record_by_ticket_id(cls, ticket_id):
        try:
            ticket = FinanceTicketModel.objects.get(ticket_id=ticket_id)
            return cls.objects.filter(ticket=ticket)   # 可替换为 return cls.objects.filter(ticket__ticket_id=ticket_id)
        except Exception as exp:
            logger.error(msg=exp)
            return []

    @classmethod
    def get_ticket_list_by_owner_and_status(cls, owner, status, zone):
        try:
            ticket_list = cls.objects.filter(owner=owner, zone__name=zone).filter(ticket__cur_status=status)
            distinct_list = ticket_list.values('owner').distinct()
            return distinct_list
        except Exception as exp:
            logger.error(msg=exp)
            return None
