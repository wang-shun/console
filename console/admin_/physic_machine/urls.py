from django.conf.urls import url

from views import (
    GetPhysicalMachineBaseInfo,
    GetPhysicalMachineIPMIAddr,
    BootPhysicalMachine,
    HaltPhysicalMachine,
    ListPhysicalMachine,
    GetPhysicalMachineInComputePool,
    GetPhysicalMachinePowerStatus,
    GetVirtualMachineNumberOnPhysicalMachine,
    GetPhysicalMachineResourceUsage,
    PhysicMachineListPage,
    PhysicMachineDetailPage,
    VirtualMachineDetailPage

)

urlpatterns = [
    url(r'^physical_machine/IPMIAddr/api$', GetPhysicalMachineIPMIAddr.as_view()),
    url(r'^physical_machine/baseinfo/api$', GetPhysicalMachineBaseInfo.as_view()),
    url(r'^physical_machine/boot/api$', BootPhysicalMachine.as_view()),
    url(r'^physical_machine/halt/api$', HaltPhysicalMachine.as_view()),
    url(r'^physical_machine/hostname_list/api$', GetPhysicalMachineInComputePool.as_view()),
    url(r'^physical_machine/list/api$', ListPhysicalMachine.as_view()),
    url(r'^physical_machine/resourceusage/api$', GetPhysicalMachineResourceUsage.as_view()),
    url(r'^physical_machine/status/api$', GetPhysicalMachinePowerStatus.as_view()),
    url(r'^physical_machine/vm_amount/api$', GetVirtualMachineNumberOnPhysicalMachine.as_view()),

    url(r'^sourceManage/physicsSource$', PhysicMachineListPage.as_view()),
    url(r'^sourceManage/physicsSourceDetail$', PhysicMachineDetailPage.as_view()),
    url(r'^sourceManage/virtualList$', VirtualMachineDetailPage.as_view()),
]
