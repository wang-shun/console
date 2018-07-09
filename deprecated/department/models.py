from django.db import models

from console.common.department.models import DepartmentBase, OrganizationBase


class PortalDepartment(DepartmentBase):
    class Meta:
        db_table = "portal_department"


class PortalOrganization(OrganizationBase):
    class Meta:
        db_table = "portal_organization"

    department = models.ForeignKey(PortalDepartment, max_length=20)
