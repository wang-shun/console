from django.contrib.auth.models import User
from django.db import models

from console.common.base import BaseModel


class DepartmentBase(BaseModel):
    class Meta:
        abstract = True
        unique_together = ('department_id',)

    name = models.CharField(max_length=30)
    description = models.CharField(max_length=200)
    department_id = models.CharField(max_length=20)
    parent_department = models.ForeignKey('self', null=True)
    path = models.CharField(max_length=200)
    level = models.IntegerField(null=False)

    def __str__(self):
        return self.name

    def to_dict(self):
        return dict(
            name=self.name,
            description=self.description,
            department_id=self.department_id
        )


class OrganizationBase(BaseModel):
    class Meta:
        abstract = True
        unique_together = ('department', 'member')

    # department = models.ForeignKey(Department, max_length=20)
    # member = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Department(DepartmentBase):
    class Meta:
        db_table = "department"


class Organization(OrganizationBase):
    class Meta:
        db_table = "organization"

    department = models.ForeignKey(Department, max_length=20)
    member = models.ForeignKey(User, on_delete=models.PROTECT, related_name='organization')

    def __str__(self):
        return self.name


# TODO: remove this two model if no used
# class PortalDepartment(DepartmentBase):
#     class Meta:
#         db_table = "portal_department"
#
#
# class PortalOrganization(OrganizationBase):
#     class Meta:
#         db_table = "portal_organization"
#
#     department = models.ForeignKey(PortalDepartment, max_length=20)
#     member = models.ForeignKey(User, on_delete=models.PROTECT, related_name='portal_organization')
