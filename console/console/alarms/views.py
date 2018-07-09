# coding=utf-8

from rest_framework.response import Response
from rest_framework.views import APIView

from console.common.err_msg import CommonErrorCode
from console.common.payload import Payload
from console.common.utils import console_response

from .models import StrategyModel
from .constants import valid_notify_at_choice
from .constants import valid_notify_method
from .helper import activate_notify_member
from .helper import add_alarm_notify_method
from .helper import add_alarm_rule
from .helper import bind_alarm_resource
from .helper import create_alarm
from .helper import create_notify_group
from .helper import create_notify_member
from .helper import delete_alarm
from .helper import delete_alarm_notify_method
from .helper import delete_alarm_rule
from .helper import delete_notify_group
from .helper import delete_notify_member
from .helper import describe_alarm_detail
from .helper import describe_alarm_history
from .helper import describe_alarm_history_detail
from .helper import describe_alarm_list
from .helper import describe_bindable_resource
from .helper import describe_notify_group
from .helper import describe_notify_member
from .helper import reschedule_alarm_monitor_period
from .helper import unbind_alarm_resource
from .helper import update_alarm_notify_method
from .helper import update_alarm_rule
from .helper import update_notify_group
from .helper import update_notify_member
from .helper import validate_alarm_trigger
from .helper import validate_multiple_choice_string
from .helper import validate_resource
from .serializers import ActivateNotifyMemberValidator
from .serializers import AddAlarmNotifyMethodValidator
from .serializers import AddAlarmRuleValidator
from .serializers import BindAlarmResourceValidator
from .serializers import CreateAlarmValidator
from .serializers import CreateNotifyGroupValidator
from .serializers import CreateNotifyMemberValidator
from .serializers import DeleteAlarmNotifyMethodValidator
from .serializers import DeleteAlarmRuleValidator
from .serializers import DeleteAlarmValidator
from .serializers import DeleteNotifyGroupValidator
from .serializers import DeleteNotifyMemberValidator
from .serializers import DescribeAlarmBindableResourceValidator
from .serializers import DescribeAlarmHistoryValidator
from .serializers import DescribeAlarmValidator
from .serializers import DescribeNotifyMemberValidator
from .serializers import RescheduleAlarmMonitorPeriodValidator
from .serializers import UnbindAlarmResourceValidator
from .serializers import UpdateAlarmNotifyMethodValidator
from .serializers import UpdateAlarmRuleValidator
from .serializers import UpdateNotifyGroupValidator
from .serializers import UpdateNotifyMemberValidator


class CreateAlarmNotifyGroup(APIView):
    """
    Create an alarm notify group
    """

    def post(self, request, *args, **kwargs):
        form = CreateNotifyGroupValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        payload = Payload(
            request=request,
            action='alarmCreateUgroup',
            name=data.get("group_name")
        )
        resp = create_notify_group(payload=payload.dumps())
        return Response(resp)


class DeleteAlarmNotifyGroup(APIView):
    """
    Delete alarms notify groups
    """

    def post(self, request, *args, **kwargs):
        form = DeleteNotifyGroupValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(CommonErrorCode.PARAMETER_ERROR,
                                             form.errors))
        data = form.validated_data
        payload = Payload(
            request=request,
            action='alarmDelUgroup',
            group_ids=data.get("group_ids")
        )
        resp = delete_notify_group(payload=payload.dumps())
        return Response(resp)


class UpdateAlarmNotifyGroup(APIView):
    """
    Update the info for the notify group. Currently,
    only name modification is supported.
    """

    def post(self, request, *args, **kwargs):
        form = UpdateNotifyGroupValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(CommonErrorCode.PARAMETER_ERROR,
                                             form.errors))
        data = form.validated_data
        payload = Payload(
            request=request,
            action='',
            group_id=data.get("group_id"),
            name=data.get("name")
        )
        resp = update_notify_group(payload=payload.dumps())
        return Response(resp)


class DescribeAlarmNotifyGroup(APIView):
    """
    List all alarm notify groups
    """

    def post(self, request, *args, **kwargs):
        payload = Payload(
            request=request,
            action=""
        )
        payload = payload.dumps()
        resp = describe_notify_group(payload)

        return Response(resp)


class CreateAlarmNotifyMember(APIView):
    """
    Create an alarm notify member
    """

    def post(self, request, *args, **kwargs):
        form = CreateNotifyMemberValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        if not data.get("phone") and not data.get("email"):
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                "Require at least one of phone and email"
            ))
        payload = Payload(
            request=request,
            action='alarmCreateUser',
            group_id=data.get("group_id"),
            name=data.get("member_name"),
        )
        payload = payload.dumps()
        if data.get("phone"):
            payload.update({"phone": str(data["phone"])})
        if data.get("email"):
            payload.update({"email": data["email"]})
        resp = create_notify_member(payload=payload)
        return Response(resp)


class ActivateAlarmNotifyMember(APIView):
    """
    Activate an alarm notify member
    """

    def post(self, request, *args, **kwargs):
        form = ActivateNotifyMemberValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        member_id = data.get("member_id")
        method = data.get("method")

        resp = activate_notify_member(unicode(member_id), unicode(method))
        return Response(resp)


class DeleteAlarmNotifyMember(APIView):
    """
    Delete alarm notify groups
    """

    def post(self, request, *args, **kwargs):
        form = DeleteNotifyMemberValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        payload = Payload(
            request=request,
            action='alarmDelUser',
            member_ids=data.get("member_ids")
        )
        resp = delete_notify_member(payload=payload.dumps())
        return Response(resp)


class UpdateAlarmNotifyMember(APIView):
    """
    Update the info for the notify member.
    """

    def post(self, request, *args, **kwargs):
        form = UpdateNotifyMemberValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(CommonErrorCode.PARAMETER_ERROR,
                                             form.errors))
        data = form.validated_data
        if not data.get("phone") \
                and not data.get("email") \
                and not data.get("member_name"):
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                "Require at least one of phone, email and member_name"
            ))
        data = form.validated_data
        changed = []
        payload = Payload(
            request=request,
            action='alarmUpdateUser',
            member_id=data.get("member_id")
        )
        payload = payload.dumps()
        if data.get("phone"):
            payload.update({"phone": data.get("phone")})
            changed.append("phone")
        if data.get("email"):
            payload.update({"email": data.get("email")})
            changed.append("email")
        if data.get("member_name"):
            payload.update({"name": data.get("member_name")})
            changed.append("name")
        payload.update({"modify_item": changed})
        resp = update_notify_member(payload=payload)
        return Response(resp)


class DescribeAlarmNotifyMember(APIView):
    """
    List all alarm notify members
    """

    def post(self, request, *args, **kwargs):
        form = DescribeNotifyMemberValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(CommonErrorCode.PARAMETER_ERROR,
                                             form.errors))
        data = form.validated_data
        payload = Payload(
            request=request,
            action='',
            group_id=data.get("group_id")
        )
        payload = payload.dumps()
        resp = describe_notify_member(payload)

        return Response(resp)


class CreateAlarm(APIView):
    """
    Create an alarm strategy
    """

    def post(self, request, *args, **kwargs):
        form = CreateAlarmValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))

        data = form.validated_data
        resource_type = data["resource_type"]
        resource = data["resource"]
        notify_at = data["notify_at"]
        method = data["notify_method"]

        error = (validate_resource(resource_type, resource) or
                 validate_multiple_choice_string(notify_at, valid_notify_at_choice) or
                 validate_multiple_choice_string(method, valid_notify_method))

        if error:
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                unicode(error)
            ))

        triggers = data["trigger_condition"]

        if validate_alarm_trigger(triggers, resource_type):
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                "trigger parameter is not right"
            ))

        payload = Payload(
            request=request,
            action='alarmCreateRule',
            type=resource_type,
            name=data["alarm_name"],
            period=data["period"],
            trigger=triggers,
            resource=resource,
            notify_at=notify_at,
            group_id=data["notify_group_id"],
            method=method
        )
        resp = create_alarm(payload.dumps())

        return Response(resp)


class DeleteAlarm(APIView):
    """
    Delete an alarm strategy
    """

    def post(self, request, *args, **kwargs):
        form = DeleteAlarmValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(CommonErrorCode.PARAMETER_ERROR,
                                             form.errors))
        data = form.validated_data
        payload = Payload(
            request=request,
            action='alarmDelRule',
            alarm_id=data["alarm_ids"]
        )
        resp = delete_alarm(payload.dumps())

        return Response(resp)


class DescribeAlarm(APIView):
    """
    List all alarms or show the detail of a single alarm
    """

    def post(self, request, *args, **kwargs):
        form = DescribeAlarmValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(CommonErrorCode.PARAMETER_ERROR,
                                             form.errors))
        data = form.validated_data
        payload = Payload(
            request=request,
            action='',
        )
        payload = payload.dumps()
        if data.get("alarm_id"):
            payload.update({"alarm_id": data.get("alarm_id")})
            resp = describe_alarm_detail(payload)
        else:
            resp = describe_alarm_list(payload)
        return Response(resp)


class BindAlarmResource(APIView):
    """
    Bind a resource or a list of resources to an exact alarm strategy
    """

    def post(self, request, *args, **kwargs):
        form = BindAlarmResourceValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        resource_list = data["resource_list"]
        alarm_id = data["alarm_id"]
        resource_type = StrategyModel.get_strategy_by_id(alarm_id).resource_type
        if len(resource_list) == 0 or \
                validate_resource(resource_type, resource_list):
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                "resource list not correct"
            ))
        payload = Payload(
            request=request,
            action='alarmCreateHost',
            resource_type=resource_type,
            alarm_id=alarm_id,
            resource_list=resource_list
        )
        resp = bind_alarm_resource(payload.dumps())
        return Response(resp)


class UnbindAlarmResource(APIView):
    """
    Unbind a resource from an exact alarm strategy
    """

    def post(self, request, *args, **kwargs):
        form = UnbindAlarmResourceValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        alarm_id = data["alarm_id"]
        resource = data["resource"]
        resource_type = StrategyModel.get_strategy_by_id(alarm_id).resource_type
        if validate_resource(resource_type, [resource]):
            return Response(console_response(CommonErrorCode.PARAMETER_ERROR,
                                             "resource not correct"))
        payload = Payload(
            request=request,
            action='alarmDelHost',
            alarm_id=data["alarm_id"],
            resource_id=resource
        )
        resp = unbind_alarm_resource(payload.dumps())

        return Response(resp)


class RescheduleAlarmMonitorPeriod(APIView):
    """
    Reschedule the monitor period for the alarm strategy
    """

    def post(self, request, *args, **kwargs):
        form = RescheduleAlarmMonitorPeriodValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(CommonErrorCode.PARAMETER_ERROR,
                                             form.errors))
        data = form.validated_data
        payload = Payload(
            request=request,
            action='alarmMonitorTime',
            alarm_id=data["alarm_id"],
            period=data["period"]
        )
        resp = reschedule_alarm_monitor_period(payload.dumps())
        return Response(resp)


class DescribeAlarmHistory(APIView):
    """
    Output all alarm history.

    """

    def post(self, request, *args, **kwargs):
        form = DescribeAlarmHistoryValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        payload = Payload(
            request=request,
            action='alarmHistory',
        )
        payload = payload.dumps()
        payload.update({"page": data["page"], "pagesize": data["pagesize"]})
        if data.get("eventid"):
            payload.update({"eventid": data["eventid"]})
            resp = describe_alarm_history_detail(payload)
        else:
            resp = describe_alarm_history(payload)
        return Response(resp)


class AddAlarmRule(APIView):
    """
    Add an alarm rule to the alarm strategy
    """

    def post(self, request, *args, **kwargs):
        form = AddAlarmRuleValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        alarm_id = data["alarm_id"]
        triggers = data["trigger_condition"]
        strategy_record = StrategyModel.get_strategy_by_id(alarm_id)
        resource_type = strategy_record.resource_type
        if validate_alarm_trigger([triggers], resource_type):
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                "trigger parameter is not right"
            ))
        payload = Payload(
            request=request,
            action='alarmCreateItem',
            alarm_id=alarm_id,
            trigger=triggers
        )
        resp = add_alarm_rule(payload.dumps())
        return Response(resp)


class UpdateAlarmRule(APIView):
    """
    Update an alarm rule of the alarm stratety
    """

    def post(self, request, *args, **kwargs):
        form = UpdateAlarmRuleValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        alarm_id = data["alarm_id"]
        triggers = data["trigger_condition"]
        strategy_record = StrategyModel.get_strategy_by_id(alarm_id)
        resource_type = strategy_record.resource_type
        if validate_alarm_trigger([triggers], resource_type):
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                "trigger parameter is not right"
            ))
        payload = Payload(
            request=request,
            action='alarmUpdateItem',
            alarm_id=alarm_id,
            trigger=triggers,
            rule_id=data["rule_id"]
        )
        resp = update_alarm_rule(payload.dumps())
        return Response(resp)


class DeleteAlarmRule(APIView):
    """
    Delete an alarm rule
    """

    def post(self, request, *args, **kwargs):
        form = DeleteAlarmRuleValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        payload = Payload(
            request=request,
            action='alarmDelItem',
            rule_id=data["rule_id"]
        )
        resp = delete_alarm_rule(payload.dumps())
        return Response(resp)


class AddAlarmNotifyMethod(APIView):
    """
    Add an alarm notify method
    """

    def post(self, request, *args, **kwargs):
        form = AddAlarmNotifyMethodValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        notify_at = data["notify_at"]
        method = data["notify_method"]
        error = validate_multiple_choice_string(notify_at,
                                                valid_notify_at_choice) or \
            validate_multiple_choice_string(method, valid_notify_method)
        if error:
            return Response(console_response(CommonErrorCode.PARAMETER_ERROR,
                                             unicode(error)))
        payload = Payload(
            request=request,
            action='alarmCreateAction',
            alarm_id=data["alarm_id"],
            group_id=data["notify_group_id"],
            notify_at=notify_at,
            method=method
        )
        resp = add_alarm_notify_method(payload.dumps())
        return Response(resp)


class UpdateAlarmNotifyMethod(APIView):
    """
    Update an alarm notify method
    """

    def post(self, request, *args, **kwargs):
        form = UpdateAlarmNotifyMethodValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        notify_at = data["notify_at"]
        method = data["notify_method"]
        error = validate_multiple_choice_string(notify_at,
                                                valid_notify_at_choice) or \
            validate_multiple_choice_string(method, valid_notify_method)
        if error:
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                unicode(error)
            ))
        payload = Payload(
            request=request,
            action='alarmUpdateAction',
            alarm_id=data["alarm_id"],
            group_id=data["notify_group_id"],
            notify_at=notify_at,
            method=method,
            method_id=data["method_id"]
        )
        resp = update_alarm_notify_method(payload.dumps())
        return Response(resp)


class DeleteAlarmNotifyMethod(APIView):
    """
    Delete an alarm notify method
    """

    def post(self, request, *args, **kwargs):
        form = DeleteAlarmNotifyMethodValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        payload = Payload(
            request=request,
            action='alarmDelAction',
            method_id=data["method_id"]
        )
        resp = delete_alarm_notify_method(payload.dumps())
        return Response(resp)


class DescribeAlarmBindableResource(APIView):
    """
    List bindable resource info for alarm strategy
    """

    def post(self, request, *args, **kwargs):
        form = DescribeAlarmBindableResourceValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        payload = Payload(
            request=request,
            action='',
            resource_type=data["resource_type"],
        )
        payload = payload.dumps()
        if data.get("alarm_id"):
            payload.update({"alarm_id": data["alarm_id"]})
        resp = describe_bindable_resource(payload)
        return Response(resp)
