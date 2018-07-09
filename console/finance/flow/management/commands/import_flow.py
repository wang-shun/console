# coding=utf-8
from django.core.management import BaseCommand
from django.db import connection

from console.common.account.models import Account
from console.common.permission.helper import PermissionService
from console.common.ticket_engine.models import (
    TicketTypeModel, FillUnitModel, FlowNodeModel, FlowEdgeModel
)
from console.finance.flow.management.commands.init_info import (
    TICKET_TYPE, FILL_UNIT, NODE_STATUS, FLOW_EDGE
)
from console.finance.tickets.models import FinanceTicketModel, TicketRecordModel

__author__ = 'shangchengfei'


handle_list = {
    "not": ['init_type', 'init_unit', 'init_node', 'init_edge'],
    "clear": ['del_record', 'del_ticket', 'del_edge', 'del_node', 'del_unit', 'del_type']
}


class Command(BaseCommand):

    @staticmethod
    def init_type(sql_type):
        try:
            for this_type in TICKET_TYPE:
                ticket_type = TicketTypeModel(ticket_name=this_type)
                ticket_type.save()
            return True
        except Exception as exp:
            print exp
            return False

    @staticmethod
    def del_type(sql_type):
        try:
            TicketTypeModel.objects.all().delete()
            cursor = connection.cursor()
            if sql_type == 'sqlite3':
                sql = "DELETE FROM {0}"
            else:
                sql = "ALTER TABLE {0} AUTO_INCREMENT = 1"
            cursor.execute(sql.format(TicketTypeModel._meta.db_table))
            cursor.close()
            return True
        except Exception as exp:
            print exp
            return False

    @staticmethod
    def init_unit(sql_type):
        try:
            for this_unit in FILL_UNIT:
                FillUnitModel.create_fill_unit(
                    name=this_unit['unit_name'],
                    attribute=this_unit['unit_attribute'],
                    choices_list=this_unit['unit_choices_list'],
                )
            return True
        except Exception as exp:
            print exp
            return False

    @staticmethod
    def del_unit(sql_type):
        try:
            FillUnitModel.objects.all().delete()
            cursor = connection.cursor()
            if sql_type == 'sqlite3':
                sql = "DELETE FROM {0}"
            else:
                sql = "ALTER TABLE {0} AUTO_INCREMENT = 1"
            cursor.execute(sql.format(FillUnitModel._meta.db_table))
            cursor.close()
            return True
        except Exception as exp:
            print exp
            return False

    @staticmethod
    def init_node(sql_type):
        try:
            user = Account.objects.get(id=1)
            for this_node in NODE_STATUS:
                node = FlowNodeModel.create_flow_node(
                    ticket_type=this_node['ticket_type'],
                    name=this_node['name'],
                    combination=this_node['combination'],
                    status=this_node['status'],
                    com_type='id',
                    is_fallback=this_node['is_fallback']
                )
                ticket_name = TicketTypeModel.objects.get(ticket_type=this_node['ticket_type']).ticket_name
                if node is None:
                    return False
                resp = PermissionService.create_ticket_node_permission(user, node.node_id, ticket_name+'->'+node.name)
                if resp is False:
                    print 'create node permission error!'
                    return False
            return True
        except Exception as exp:
            print exp
            return False

    @staticmethod
    def del_node(sql_type):
        try:
            node_list = FlowNodeModel.objects.all()
            user = Account.objects.filter(id=1)
            for node in node_list:
                PermissionService.delete_ticket_node_permission(user, node.node_id)
            FlowNodeModel.objects.all().delete()
            cursor = connection.cursor()
            if sql_type == 'sqlite3':
                sql = "DELETE FROM {0}"
            else:
                sql = "ALTER TABLE {0} AUTO_INCREMENT = 1"
            cursor.execute(sql.format(FlowNodeModel._meta.db_table))
            cursor.close()
            return True
        except Exception as exp:
            print exp
            return False

    @staticmethod
    def init_edge(sql_type):
        try:
            for this_edge in FLOW_EDGE:
                start_node = FlowNodeModel.objects.get(id=this_edge['start_node'])
                end_node = FlowNodeModel.objects.get(id=this_edge['end_node'])
                FlowEdgeModel.create_flow_edge(
                    ticket_type=this_edge['ticket_type'],
                    start_node=start_node,
                    end_node=end_node
                )
            return True
        except Exception as exp:
            print exp
            return False

    @staticmethod
    def del_edge(sql_type):
        try:
            FlowEdgeModel.objects.all().delete()
            cursor = connection.cursor()
            if sql_type == 'sqlite3':
                sql = "DELETE FROM {0}"
            else:
                sql = "ALTER TABLE {0} AUTO_INCREMENT = 1"
            cursor.execute(sql.format(FlowEdgeModel._meta.db_table))
            cursor.close()
            return True
        except Exception as exp:
            print exp
            return False

    @staticmethod
    def del_ticket(sql_type):
        try:
            FinanceTicketModel.objects.all().delete()
            cursor = connection.cursor()
            if sql_type == 'sqlite3':
                sql = "DELETE FROM {0}"
            else:
                sql = "ALTER TABLE {0} AUTO_INCREMENT = 1"
            cursor.execute(sql.format(FinanceTicketModel._meta.db_table))
            cursor.close()
            return True
        except Exception as exp:
            print exp
            return False

    @staticmethod
    def del_record(sql_type):
        try:
            TicketRecordModel.objects.all().delete()
            cursor = connection.cursor()
            if sql_type == 'sqlite3':
                sql = "DELETE FROM {0}"
            else:
                sql = "ALTER TABLE {0} AUTO_INCREMENT = 1"
            cursor.execute(sql.format(TicketRecordModel._meta.db_table))
            cursor.close()
            return True
        except Exception as exp:
            print exp
            return False

    def add_arguments(self, parser):
        parser.add_argument('clear_or_not')
        parser.add_argument('sql_type')

    def handle(self, *args, **options):
        clear_or_not = options.get('clear_or_not')
        sql_type = options.get('sql_type')
        str = "import" if clear_or_not == "not" else "clear"
        for I in handle_list.get(clear_or_not):
            resp = getattr(self, I)(sql_type)
            if resp is False:
                print "model " + I + " " + str+" False!"
                return
        print "ticket " + str + " OK!"




