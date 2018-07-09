from django.shortcuts import RequestContext as _RequestContext

from console import settings
from console.common.license.models import PlatformInfoModel


class RequestContext(_RequestContext):
    def __init__(self, request, dict_=None, processors=None, *args, **kwargs):
        platform_info = PlatformInfoModel.get_instance()
        platform_names = {"admin_name" : platform_info.admin_name,
                          "console_name" : platform_info.console_name}
        common_context = {
            "platform_names" : platform_names
        }
        if dict_:
            dict_.update(common_context)
            dict_.update(settings.__dict__)
        super(RequestContext, self).__init__(request, dict_, processors, *args, **kwargs)
