# coding=utf-8
import json

from django.db import models
from django.utils.timezone import now

from console.common.logger import getLogger
from console.common.base import BaseModel
from console.common.utils import make_random_id

logger = getLogger(__name__)
__author__ = 'shangchengfei'


class TicketTypeModel(BaseModel):

    class Meta:
        db_table = "ticket_type"

    ticket_type = models.AutoField(
        primary_key=True,
    )
    ticket_name = models.CharField(
        max_length=20,
        unique=True,
    )

    def __unicode__(self):
        return "%s" % self.ticket_name

    @classmethod
    def get_all_ticket_type(cls):
        try:
            return cls.objects.all()
        except Exception as exp:
            logger.error(msg=exp)
            return None

    @classmethod
    def create_ticket_type(cls, ticket_type):
        try:
            return cls.objects.create(ticket_type=ticket_type)
        except Exception as exp:
            logger.error(msg=exp)
            return False

    @classmethod
    def delete_ticket_type(cls, ticket_type):
        try:
            ticket_type = cls.objects.get(ticket_type=ticket_type)
            ticket_type.deleted = True
            ticket_type.delete_datetime = now()
            ticket_type.save()
        except Exception as exp:
            logger.error(msg=exp)
            return False

    @classmethod
    def update_ticket_type(cls, ticket_type, ticket_name):
        try:
            ticket_type = cls.objects.get(ticket_type=ticket_type)
            ticket_type.name = ticket_name
            ticket_type.save()
        except Exception as exp:
            logger.error(msg=exp)
            return False


class FillUnitModel(BaseModel):

    class Meta:
        db_table = "fill_unit"

    unit_id = models.CharField(
        max_length=20,
        unique=True,
    )
    name = models.CharField(
        max_length=20,
    )
    attribute = models.CharField(
        max_length=20,
    )
    choices_list = models.CharField(
        max_length=1000,
    )

    def __unicode__(self):
        return "%s %s" % (self.name, self.choices_list)

    @classmethod
    def create_fill_unit(cls, name, attribute, choices_list):
        try:
            unit_id = make_random_id("un", cls.get_exists_by_id)
            choices_list = json.dumps(choices_list)
            return cls.objects.create(
                unit_id=unit_id,
                name=name,
                attribute=attribute,
                choices_list=choices_list,
            )
        except Exception as exp:
            logger.error(msg=exp)
            return False

    @classmethod
    def get_all_fill_unit(cls):
        try:
            return cls.objects.all()
        except Exception as exp:
            logger.error(msg=exp)
            return None

    @classmethod
    def get_unit_by_id(cls, unit_id):
        try:
            return cls.objects.filter(unit_id=unit_id)
        except Exception as exp:
            logger.error(msg=exp)
            return None

    @classmethod
    def get_exists_by_id(cls, unit_id):
        try:
            return cls.objects.filter(unit_id=unit_id).exists()
        except Exception as exp:
            logger.error(msg=exp)
            return False

    @classmethod
    def delete_fill_unit(cls, unit_id):
        try:
            unit = cls.objects.get(unit_id=unit_id)
            unit.deleted = True
            unit.delete_datetime = now()
            unit.save()
        except Exception as exp:
            logger.error(msg=exp)
            return False

    @classmethod
    def update_fill_unit(cls, unit_id, name, attribute, choices_list):
        try:
            choices_list = json.dumps(choices_list)
            unit = cls.objects.get(unit_id=unit_id)
            unit.name = name
            unit.attribute = attribute
            unit.choices_list = choices_list
            unit.save()
        except Exception as exp:
            logger.error(msg=exp)
            return False


class FlowNodeModel(BaseModel):

    class Meta:
        db_table = "flow_node"

    ticket_type = models.ForeignKey(
        TicketTypeModel,
        on_delete=models.PROTECT,
    )
    node_id = models.CharField(
        max_length=20,
        unique=True,
    )
    name = models.CharField(
        max_length=60,
    )
    combination = models.ManyToManyField(
        FillUnitModel
    )
    # 结点类型 create, doing, finish
    status = models.CharField(
        max_length=20,
    )
    is_fallback = models.BooleanField(
    )

    def __unicode__(self):
        return "%s" % self.name

    @classmethod
    def create_flow_node(cls, ticket_type, name, combination, status, is_fallback, com_type=None):
        try:
            node_id = make_random_id("nd", cls.get_exists_by_id)
            ticket_type = TicketTypeModel.objects.get(ticket_type=ticket_type)
            node = FlowNodeModel(
                ticket_type=ticket_type,
                node_id=node_id,
                name=name,
                status=status,
                is_fallback=is_fallback
            )
            node.save()
            for unit_id in combination:
                if com_type is None:
                    unit = FillUnitModel.objects.get(unit_id=unit_id)
                else:
                    unit = FillUnitModel.objects.get(id=unit_id)
                node.combination.add(unit)
                node.save()
            return node
        except Exception as exp:
            logger.error(msg=exp)
            return None

    @classmethod
    def get_all_node_by_ticket_type(cls, ticket_type):
        try:
            return cls.objects.filter(ticket_type__ticket_type=ticket_type)
        except Exception as exp:
            logger.error(msg=exp)
            return None

    @classmethod
    def get_node_by_id(cls, node_id):
        try:
            return cls.objects.get(node_id=node_id)
        except Exception as exp:
            logger.error(msg=exp)
            return None

    @classmethod
    def get_exists_by_id(cls, node_id):
        try:
            return cls.objects.filter(node_id=node_id).exists()
        except Exception as exp:
            logger.error(msg=exp)
            return False

    @classmethod
    def get_create_node_by_type(cls, ticket_type):
        try:
            ticket_type = TicketTypeModel.objects.get(ticket_type=ticket_type)
            return cls.objects.get(ticket_type=ticket_type, status="create")   # 此处可以get 是因为已经为每一种类型的工单在数据库中初始化了create节点
        except Exception as exp:
            logger.error(msg=exp)
            return False

    @classmethod
    def delete_flow_node(cls, node_id):
        try:
            node = cls.objects.get(node_id=node_id)
            node.deleted = True
            node.delete_datetime = now()
            node.save()
        except Exception as exp:
            logger.error(msg=exp)
            return False

    @classmethod
    def update_flow_node(cls, node_id, name, combination):
        try:
            node = cls.objects.get(node_id=node_id)
            node.name = name
            node.save()
            node.combination.clear()
            for unit_id in combination:
                unit = FillUnitModel.objects.get(unit_id=unit_id)
                node.combination.add(unit)
                node.save()
            return True
        except Exception as exp:
            logger.error(msg=exp)
            return False


class FlowEdgeModel(BaseModel):

    class Meta:
        db_table = "flow_edge"

    ticket_type = models.ForeignKey(
        TicketTypeModel,
        on_delete=models.PROTECT
    )
    edge_id = models.CharField(
        max_length=20,
        unique=True,
    )
    start_node = models.ForeignKey(
        FlowNodeModel,
        on_delete=models.PROTECT,
        related_name="start_node"
    )
    end_node = models.ForeignKey(
        FlowNodeModel,
        on_delete=models.PROTECT,
        related_name="end_node"
    )

    @classmethod
    def create_flow_edge(cls, ticket_type, start_node, end_node):
        try:
            edge_id = make_random_id("eg", cls.get_exists_by_id)
            ticket_type = TicketTypeModel.objects.get(ticket_type=ticket_type)
            return cls.objects.create(
                ticket_type=ticket_type,
                edge_id=edge_id,
                start_node=start_node,
                end_node=end_node
            )
        except Exception as exp:
            logger.error(msg=exp)
            return False

    @classmethod
    def get_edge_by_id(cls, edge_id):
        try:
            return cls.objects.get(edge_id=edge_id)
        except Exception as exp:
            logger.error(msg=exp)
            return None

    @classmethod
    def get_edge_by_start_node(cls, start_node):
        try:
            return cls.objects.filter(start_node=start_node)
        except Exception as exp:
            logger.error(msg=exp)
            return None

    @classmethod
    def get_edge_by_endpoint(cls, start_node, end_node):
        try:
            return cls.objects.get(start_node=start_node, end_node=end_node)
        except Exception as exp:
            logger.error(msg=exp)
            return None

    @classmethod
    def get_exists_by_id(cls, edge_id):
        try:
            return cls.objects.filter(edge_id=edge_id).exists()
        except Exception as exp:
            logger.error(msg=exp)
            return False

    @classmethod
    def delete_flow_edge(cls, edge_id):
        try:
            edge = FlowEdgeModel.objects.get(edge_id=edge_id)
            edge.deleted = True
            edge.delete_datetime = now()
            edge.save()
        except Exception as exp:
            logger.error(msg=exp)
            return False

    # @classmethod
    # def update_edge(cls):
    #     pass
