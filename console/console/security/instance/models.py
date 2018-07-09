# coding=utf-8

__author__ = 'chengwanfei@gmail.com'

# from django.db import models
# from console.common.logger import getLogger
# from ..models import BaseSecurityGroupModel, BaseSecurityGroupRuleModel

# logger = getLogger(__name__)
#
# ERR_CODE_MAPPER = {
#     1100: "01",
#     1200: "02",
#     1300: "03",
#     1400: "04",
#     2100: "05",
#     2400: "06",
#     2500: "07",
#     5000: "08",
#     5100: "09",
#     5200: "10",
#     5300: "11",
# }


# class SecurityGroupManger(models.Manager):
#     def create(self, uuid, sg_id, sg_name, zone, user):
#         try:
#             _sg_model = SecurityGroupModel(
#                 uuid=uuid,
#                 sg_id=sg_id,
#                 sg_name=sg_name,
#                 zone=zone,
#                 user=user,
#             )
#             _sg_model.save()
#             return _sg_model, None
#         except Exception as exp:
#             logger.error("cannot save the new data to database, %s" % exp.message)
#             return None, exp
#
#     def update_name(self, sg_id, sg_new_name):
#         try:
#             # _sg_model = SecurityGroupModel.objects.get(sg_id=sg_id)
#             _sg_model = SecurityGroupModel.get_security_by_id(sg_id=sg_id)
#             _sg_model.sg_name = sg_new_name
#             _sg_model.save()
#             return sg_new_name, None
#         except Exception as exp:
#             logger.error("cannot save the new data to database, %s" % exp.message)
#             return None, exp
#
#
# class SecurityGroupModel(BaseSecurityGroupModel):
#     class Meta:
#         app_label = "security"
#         db_table = 'security_groups'
#         unique_together = ('zone', 'uuid')
#
#     objects = SecurityGroupManger()
#
#     def __unicode__(self):
#         return self.sg_id
#
#
# class SecurityGroupRuleManger(models.Manager):
#     def create(self, uuid, sgr_id, security_gruop, protocol, priority,\
#                direction, port_range_min, port_range_max, remote_ip):
#         try:
#             _sgr_model = SecurityGroupRuleModel(
#                 uuid=uuid,
#                 sgr_id=sgr_id,
#                 protocol=protocol,
#                 priority=priority,
#                 port_range_min=port_range_min,
#                 port_range_max=port_range_max,
#                 remote_ip=remote_ip,
#                 direction=direction,
#                 security_group=security_gruop
#             )
#             _sgr_model.save()
#             return _sgr_model, None
#         except Exception as exp:
#             logger.error(exp.message)
#             return None, exp
#
#
# class SecurityGroupRuleModel(BaseSecurityGroupRuleModel):
#     class Meta:
#         app_label = "security"
#         db_table = 'security_group_rule'
#         unique_together = ('security_group', 'uuid')
#     # A rule only belongs to a security group
#     security_group = models.ForeignKey(SecurityGroupModel,
#                                        on_delete=models.PROTECT)
#
#     objects = SecurityGroupRuleManger()
