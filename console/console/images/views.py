# coding=utf-8

from rest_framework.response import Response
from rest_framework.views import APIView

from console.common.logger import getLogger
from console.common.utils import console_response
from console.common.utils import datetime_to_timestamp
from console.console.resources.helper import show_image_by_admin
from console.console.backups.models import InstanceBackupModel
from .serializers import DescribeImagesValidator

logger = getLogger(__name__)


class DescribeImages(APIView):  # done

    def post(self, request, *args, **kwargs):
        _data = request.data
        zone = request.data["zone"]
        owner = request.data["owner"]
        hypervisor_type = request.data.get("hypervisor_type", "KVM")
        form = DescribeImagesValidator(data=_data)
        if not form.is_valid():
            return Response(
                {"code": 1,
                 "msg": form.errors,
                 "data": {},
                 "ret_code": 90001}
            )
        validated_data = form.validated_data
        image_id = validated_data.get("image_id")
        # image_id = validated_data.get("image_id")
        # if image_id:
        #     _image = ImageModel.get_image_by_id(image_id)
        #     _image_serializer = ImagesSerializer(_image)
        #     _image_info = _image_serializer.data
        #
        #     timestamp = datetime_to_timestamp(_image_info["create_datetime"])
        #     _image_info.update({"create_datetime": timestamp})
        #
        #     return Response({"code": 0, "msg": "succ", "data": {"ret_set": [_image_info], "total_count": 1}},
        #                     status=status.HTTP_200_OK)
        # # 过滤结果
        # # Todo 搜索关键词需要实现在innodb引擎下的全文检索，方案：自定义全文检索
        # sort_key = validated_data.get("sort_key", "create_datetime")
        # reverse = validated_data.get("reverse", False)
        # sort_key = (reverse * "-") + sort_key
        #
        # try:
        #     images = ImageModel.objects.filter(
        #         (Q(user__username=owner) | Q(user__username='system_image')),
        #         Q(zone__name=zone), Q(status='available')).order_by(sort_key)
        #
        #     image_serializer = ImagesSerializer(images, many=True)
        #     total = len(image_serializer.data)
        #     _image_info_list = image_serializer.data
        #
        #     for _image_info in _image_info_list:
        #         timestamp = datetime_to_timestamp(_image_info["create_datetime"])
        #         _image_info.update({"create_datetime": timestamp})
        #
        #     _data = {"total_count": total, "ret_set": image_serializer.data}
        #
        #     payload = {
        #         "action" : "DescribeImage",
        #         "owner" : owner,
        #         "zone" : zone,
        #         "private_image" : True
        #     }
        # dd
        #     private_images = get_private_images(payload)
        #     _data["ret_set"].extend(private_images)
        #
        #     return Response(console_response(0, "succ", len(_data["ret_set"]), _data["ret_set"]),
        #                     status=status.HTTP_200_OK)
        # except Exception as exp:
        #     return Response(console_response(1, str(exp)),
        #                     status=status.HTTP_200_OK)
        payload = {
            "owner": owner,
            "zone": zone,
            "action": "DescribeImage"
        }
        resp = show_image_by_admin(payload)
        result = []
        # we need compare hypervisor_type from frontend and backend case insensitive
        hypervisor_type = hypervisor_type.lower()
        for image in resp:
            image_hypervisor_type = image.get('hyper_type', "KVM").lower()
            if hypervisor_type != image_hypervisor_type:
                continue
            if owner != image.get("image_owner") and image.get("visibility") == "private":
                continue
            if image_id is not None and image.get('id') != image_id:
                continue
            image_name = image.get("name")
            if image_name.find("fortress") >= 0 or image_name.find("waf") >= 0 or image_name.find("bak-") >= 0:
                continue

            image_name = InstanceBackupModel.get_backup_by_id(image.get("name"))
            image_name = image_name.backup_name if image_name else image.get("name")
            tmp_info = dict()
            tmp_info["create_datetime"] = datetime_to_timestamp(image.get("created_at"))
            tmp_info["image_name"] = image_name
            tmp_info["platform"] = image.get("image_type")
            tmp_info["size"] = image.get("size")
            if image.get("status") == "active":
                tmp_info["status"] = "available"
            elif image.get("status") == "queued":
                tmp_info["status"] = "queued"
            else:
                tmp_info["status"] = "error"
            tmp_info["system"] = image.get("image_type")
            tmp_info["image_id"] = image.get("id")
            tmp_info["min_disk"] = image.get("min_disk")
            result.append(tmp_info)
        return Response(console_response(ret_set=result))
