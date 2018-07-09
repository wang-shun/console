# coding: utf-8

import os
from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.views.generic import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from console.common.auth import requires_admin_login
from console.common.context import RequestContext
from console.common.utils import console_response, get_md5, get_serializer_error
from console.console.resources.common import DataTableConsoleBase
from console.console.resources.helper import create_image_file, update_image_file, delete_image_file
from console.console.resources.helper import delete_image_by_admin
from console.console.resources.helper import show_image_by_admin
from console.settings import MIRRORING_UPLOAD_PATH
from .models import ImageFileModel
from .models import UploadFileModel
from .serializers import (
    GetImageFileValidator,
    CreateImageFileValidator,
    DeleteImageFileValidator,
    DeleteImageListValidator,
    DescribeImagesListValidator,
    JudgeImageFileExistValidator,
    UpdateImageFileValidator
)


class ImageListPage(View):
    """
    image管理
    """
    template = "customize/image.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "customize_image"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class ImageCreatePage(View):
    """
    创建image
    """
    template = "customize/image_create.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "customize_image"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class ImageEditPage(View):
    """
    修改image
    """
    template = "customize/image_edit.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "customize_image"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class ListImage(APIView):
    '''
    admin 端展示镜像列表
    '''

    def post(self, request, *args, **kwargs):
        form = DescribeImagesListValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1,
                                             ret_msg=get_serializer_error(form.errors)),
                            status=status.HTTP_200_OK)

        payload = {
            "owner": form.validated_data.get("owner"),
            "zone": form.validated_data.get("zone"),
            "action": "ShowImage",
            "image_id": request.data.get("image_id")
        }

        output_list = show_image_by_admin(payload)
        handle = HandleList()
        return Response(handle.handle(request, output_list))


class HandleList(DataTableConsoleBase):
    '''
    处理admin 展示镜像查找，排序，分页
    '''

    def handle(self, request, output_list):
        self._query = request.data
        self._output_list = output_list
        return self._get_output()


class DeleteOneImage(APIView):
    '''
    admin 端删除一个镜像
    '''

    def post(self, request, *args, **kwargs):
        form = DeleteImageListValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1,
                                             ret_msg=get_serializer_error(form.errors)),
                            status=status.HTTP_200_OK)

        payload = {
            "owner": form.validated_data.get("owner"),
            "zone": form.validated_data.get("zone"),
            "image_id": form.validated_data.get("image_id"),
            "action": "DeleteImage"
        }

        resp = delete_image_by_admin(payload)
        return Response(resp)


class JudgeImageFileExist(APIView):
    """
    admin 判断是否要断点续传
    """

    def post(self, request, *args, **kwargs):
        form = JudgeImageFileExistValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1,
                                             ret_msg=get_serializer_error(form.errors)),
                            status=status.HTTP_200_OK)
        resp = []
        date = request.data.get('date')
        name = request.data.get('name')
        owner = form.validated_data.get('owner')
        file_name = owner + '*' + date + '*' + name
        file_ins = UploadFileModel.get_upload_file_by_file_name(file_name)
        if file_ins is not None:
            resp.append({
                'index': file_ins.end_index,
                'fileSplitSize': file_ins.split_size
            })
        return Response(console_response(0, "succ", len(resp), resp))


class GetImageFile(APIView):
    """
    admin 获取上传镜像的接口
    """

    def post(self, request, *args, **kwargs):
        form = GetImageFileValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1,
                                             ret_msg=get_serializer_error(form.errors)),
                            status=status.HTTP_200_OK)
        code = 0
        msg = 'succ'
        this_file = request.data.get('image_file')
        date = request.data.get('date')
        name = request.data.get('name')
        owner = form.validated_data.get('owner')
        total_size = request.data.get('total_size')
        split_size = request.data.get('fileSplitSize')
        end_index = request.data.get('index')
        md5 = request.data.get('md5')
        file_name = owner + '*' + date + '*' + name
        real_md5 = get_md5(this_file)
        if real_md5 == md5:
            with open(os.path.join(MIRRORING_UPLOAD_PATH, file_name), 'a') as destination:
                for chunk in this_file.chunks():
                    destination.write(chunk)
            file_ins = UploadFileModel.get_upload_file_by_file_name(file_name)
            if file_ins is None:
                resp = UploadFileModel.create_upload_file(file_name, total_size, split_size, end_index)
                if resp is False:
                    msg = 'file upload failed! （save to db failed）'
                    code = 1
            else:
                file_ins.end_index = end_index
                file_ins.save()

        return Response(console_response(code, msg, 0, []))


class CreateImageFile(APIView):
    """
    admin 创建新镜像
    """

    def post(self, request, *args, **kwargs):
        form = CreateImageFileValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1,
                                             ret_msg=get_serializer_error(form.errors)),
                            status=status.HTTP_200_OK)
        owner = form.validated_data.get('owner')
        date = form.validated_data.get('date')
        name = form.validated_data.get('name')
        file_name = form.validated_data.get('file_name')
        disk_format = form.validated_data.get('disk_format')
        if disk_format == 'other':
            disk_format = 'raw'
        container_format = 'bare'
        is_public = form.validated_data.get('is_public')
        image_type = form.validated_data.get('image_type')
        is_protect = form.validated_data.get('is_protect')
        zone = request.data.get('zone')
        file_name = owner + '*' + date + '*' + file_name
        payload = {
            'action': 'CreateImage',
            'name': name,
            'file_name': file_name,
            'disk_format': disk_format,
            'container_format': container_format,
            'is_public': is_public,
            'image_type': image_type,
            'is_protect': is_protect,
            'owner': owner,
            'zone': zone
        }
        resp = create_image_file(payload)

        return Response(resp)


class UpdateImageFile(APIView):
    """
    admin 修改镜像
    """

    def post(self, request, *args, **kwargs):
        form = UpdateImageFileValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1,
                                             ret_msg=get_serializer_error(form.errors)),
                            status=status.HTTP_200_OK)
        image_id = form.validated_data.get('image_id')
        owner = form.validated_data.get('owner')
        name = form.validated_data.get('name')
        disk_format = form.validated_data.get('disk_format')
        container_format = 'bare'
        is_public = form.validated_data.get('is_public')
        image_type = form.validated_data.get('image_type')
        is_protect = form.validated_data.get('is_protect')
        zone = request.data.get('zone')
        payload = {
            'action': 'UpdateImage',
            'image_id': image_id,
            'name': name,
            'disk_format': disk_format,
            'container_format': container_format,
            'is_public': is_public,
            'image_type': image_type,
            'is_protect': is_protect,
            'owner': owner,
            'zone': zone
        }
        resp = update_image_file(payload)
        return Response(resp)


class DeleteImageFile(APIView):
    """
    admin 修改镜像
    """

    def post(self, request, *args, **kwargs):
        form = DeleteImageFileValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1,
                                             ret_msg=get_serializer_error(form.errors)),
                            status=status.HTTP_200_OK)
        image_id = form.validated_data.get('image_id')
        owner = form.validated_data.get('owner')
        file_name = ImageFileModel.get_file_name_by_image_id(image_id)
        zone = request.data.get('zone')
        payload = {
            'action': 'DeleteImage',
            'image_id': image_id,
            'file_name': file_name,
            'owner': owner,
            'zone': zone
        }
        resp = delete_image_file(payload)
        return Response(resp)
