# coding=utf-8

# from django.db import models
# from console.common.logger import getLogger
# from ..models import BaseSecurityGroupModel, BaseSecurityGroupRuleModel

# logger = getLogger(__name__)


# class RdsSecurityGroupManger(models.Manager):
#     def create(self, uuid, sg_id, sg_name, zone, user):
#         try:
#             _sg_model = RdsSecurityGroupModel(
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
#             _sg_model = RdsSecurityGroupModel.get_security_by_id(sg_id=sg_id)
#             _sg_model.sg_name = sg_new_name
#             _sg_model.save()
#             return sg_new_name, None
#         except Exception as exp:
#             logger.error("cannot save the new data to database, %s" % exp.message)
#             return None, exp.message
#
#
# class RdsSecurityGroupModel(BaseSecurityGroupModel):
#     class Meta:
#         app_label = "security"
#         db_table = 'rds_security_groups'
#         unique_together = ('zone', 'uuid')
#
#     objects = RdsSecurityGroupManger()
#
#     def __unicode__(self):
#         return self.sg_id
#
#
# class RdsSecurityGroupRuleManger(models.Manager):
#     def create(self, uuid, sgr_id, security_gruop, protocol, priority,\
#                direction, port_range_min, port_range_max, remote_ip):
#         try:
#             _sgr_model = RdsSecurityGroupRuleModel(
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
# class RdsSecurityGroupRuleModel(BaseSecurityGroupRuleModel):
#     class Meta:
#         app_label = "security"
#         db_table = 'security_group_rule'
#         unique_together = ('security_group', 'uuid')
#     # A rule only belongs to a security group
#     security_group = models.ForeignKey(RdsSecurityGroupManger,
#                                        on_delete=models.PROTECT)
#
#     objects = RdsSecurityGroupRuleManger()
