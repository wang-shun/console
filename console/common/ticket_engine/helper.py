# coding=utf-8
import json
import datetime
from django.contrib.auth.models import User

from console.common.logger import getLogger
from console.common.ticket_engine.models import FlowEdgeModel, FlowNodeModel, TicketTypeModel, FillUnitModel

"""
工单模块设计思路：
ticket_engine:  基础模块，定义工单类型，元素，节点，流程；工单类型，元素，节点，流程在创建表的时候初始化在数据库中
finance/ticket:  实现工单的创建，编辑，整个流程展示，定义工单类，工单记录表
               |------- 工单表
工单记录表------|
               |-------  节点表
               |-------  节点数据   不管创建多少个工单，节点的个数是一定的，通过每一条工单记录，关联一个节点，和节点包含的元素以及
                                    元素的值
"""

logger = getLogger(__name__)
__author__ = 'shangchengfei'


def utc_to_local_time(utc_time):
    return (utc_time + datetime.timedelta(hours=8)).replace(tzinfo=None)


class TicketFlow(object):

    # object
    ticket = None
    # class
    record_model = None
    # int
    ticket_type = None

    def __init__(self, **kwargs):
        self.ticket = kwargs['ticket']
        self.record_model = kwargs['record_model']
        self.ticket_type = kwargs['ticket_type']

    def get_node_fill_info(self):
        """
        编辑或者创建工单时调用，用来获取工单包含的节点
        """
        all_data = []
        # 历史
        if self.ticket is None:
            record_list = []
        else:
            record_list = self.record_model.get_record_by_ticket_id(self.ticket.ticket_id)  # 获得工单已有的节点
        for record in record_list:
            fill_data = record.fill_data
            fill_data = json.loads(fill_data)
            data = {}
            data.update({"node_data": fill_data})
            node_name = record.cur_node.name
            data.update({"node_name": node_name})

            user = record.handle
            operation_time = record.opera_time
            operation_usr_info = {
                "user_id": user.username,
                "operation_time": utc_to_local_time(operation_time)
            }
            data.update({"operation_usr_info": operation_usr_info})
            logger.debug(msg="get_node_fill_history: %s" % data)
            all_data.append(data)

        # 当前
        if self.ticket is None:
            cur_node = FlowNodeModel.get_create_node_by_type(self.ticket_type)
        else:
            cur_node = self.ticket.cur_node
        node_name = cur_node.name
        node_combination = []
        for unit in cur_node.combination.all().order_by('flow_node_combination.id'):
            node_combination.append({
                "unit_name": unit.name,
                "unit_attribute": unit.attribute,
                "unit_choice_list": json.loads(unit.choices_list)
            })
        data = {"node_name": node_name, "node_combination": node_combination, "node_id": cur_node.node_id}
        next_node_choices = []
        next_edge_choices = FlowEdgeModel.get_edge_by_start_node(cur_node)  # 根据当前节点，获取下一步的节点
        if cur_node.is_fallback is True:
            next_node = {}
            path_stack = json.loads(self.ticket.path_stack)
            last_edge = FlowEdgeModel.objects.get(edge_id=path_stack[-1])
            next_node.update({"node_id": last_edge.start_node.node_id})
            next_node.update({"node_name": u'返回上一级修改'})
            next_node_choices.append(next_node)
        for next_edge in next_edge_choices:
            next_node = {}
            next_node.update({"node_id": next_edge.end_node.node_id})
            next_node.update({"node_name": next_edge.end_node.name})
            next_node_choices.append(next_node)
        data.update({"next_node_choices": next_node_choices})
        logger.debug(msg="get_node_fill_current: %s" % data)
        all_data.append(data)
        return all_data

    def go_next(self, owner, fill_data):
        """
        工单提交时调用，给工单添加节点
        """
        code = True
        msg = None
        cur_node = self.ticket.cur_node
        cur_node_id = fill_data.pop('cur_node_id')
        if cur_node_id != cur_node.node_id:
            code = False
            err = "this ticket has been dealing with others"
            logger.debug(msg="this ticket has been dealing with others: %s" % err)
            return code, err
        next_node_id = fill_data.pop('next_node_id')
        next_node = FlowNodeModel.get_node_by_id(next_node_id)
        cur_edge = FlowEdgeModel.get_edge_by_endpoint(cur_node, next_node)
        path_stack = json.loads(self.ticket.path_stack)
        opera_type = next_node.status if cur_node.status != 'create' else 'create'
        # 回退上一级
        if cur_edge is None:
            cur_edge_id = path_stack.pop()
            cur_edge = FlowEdgeModel.get_edge_by_id(edge_id=cur_edge_id)
            opera_type = 'fallback'
        else:
            path_stack.append(cur_edge.edge_id)
        try:
            self.ticket.last_node = cur_node
            handle = User.objects.get(username=owner)

            # 更新工单的状态
            self.ticket.last_handle = handle
            self.ticket.cur_node = next_node
            self.ticket.cur_status = next_node.status
            self.ticket.step += 1
            self.ticket.path_stack = json.dumps(path_stack)
            self.ticket.save()

            # 创建工单记录
            self.record_model.create_ticket_record(
                ticket=self.ticket,
                fill_data=fill_data['node_data'],
                handle=handle,
                cur_node=cur_node,
                next_node=next_node,
                opera_type=opera_type,
            )
            if self.ticket.step == 2:
                self.ticket.resp_time = int((self.ticket.last_update_time - self.ticket.commit_time).total_seconds())
                self.ticket.save()
        except Exception as e:
            return False, e
        return code, msg


class FlowEngine(object):

    def __new__(cls, **kwargs):
        obj_cls = TicketFlow
        return obj_cls(**kwargs)

    # ticket_type
    @classmethod
    def get_all_ticket_type(cls):
        return TicketTypeModel.get_all_ticket_type()

    @classmethod
    def create_ticket_type(cls, ticket_type):
        return TicketTypeModel.create_ticket_type(ticket_type)

    @classmethod
    def delete_ticket_type(cls, ticket_type):
        return TicketTypeModel.delete_ticket_type(ticket_type)

    @classmethod
    def update_ticket_type(cls, ticket_id, ticket_name):
        return TicketTypeModel.update_ticket_type(ticket_id, ticket_name)

    # flow_node
    @classmethod
    def get_all_flow_node(cls):
        return FlowNodeModel.get_all_flow_node()

    @classmethod
    def create_flow_node(cls, ticket_type, name, combination, status):
        return FlowNodeModel.create_flow_node(ticket_type, name, combination, status)

    @classmethod
    def delete_flow_node(cls, node_id):
        return FlowNodeModel.delete_flow_node(node_id)

    @classmethod
    def update_flow_node(cls, node_id, name, combination):
        return FlowNodeModel.update_flow_node(node_id, name, combination)

    @classmethod
    def get_create_node_by_type(cls, ticket_type):
        return FlowNodeModel.get_create_node_by_type(ticket_type)

    # flow_edge
    @classmethod
    def get_edge_by_start_node(cls, cur_node):
        return FlowEdgeModel.get_edge_by_start_node(cur_node)

    @classmethod
    def get_all_flow_edge(cls):
        return FlowEdgeModel.get_all_flow_edge()

    @classmethod
    def create_flow_edge(cls, ticket_type, start_node, end_node):
        return FlowEdgeModel.create_flow_edge(ticket_type, start_node, end_node)

    @classmethod
    def delete_flow_edge(cls, edge_id):
        return FlowEdgeModel.delete_flow_edge(edge_id)

    @classmethod
    def update_flow_edge(cls):
        # 不需要修改，直接删再添加
        pass

    # fill_unit
    @classmethod
    def get_all_fill_unit(cls):
        return FillUnitModel.get_all_fill_unit()

    @classmethod
    def create_fill_unit(cls, name, attribute, choices_list):
        return FillUnitModel.create_fill_unit(name, attribute, choices_list)

    @classmethod
    def delete_fill_unit(cls, unit_id):
        return FillUnitModel.delete_fill_unit(unit_id)

    @classmethod
    def update_fill_unit(cls, unit_id, name, attribute, choices_list):
        return FillUnitModel.update_fill_unit(unit_id, name, attribute, choices_list)
