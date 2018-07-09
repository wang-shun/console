# coding: utf-8

from django.db import models

from console.common.logger import getLogger

logger = getLogger(__name__)


class UploadFileModel(models.Model):
    class Meta:
        db_table = "upload_file"

    file_name = models.CharField(
        max_length=255,
        unique=True,
    )

    total_size = models.IntegerField(
        help_text=u'单位为B'
    )

    split_size = models.IntegerField(
        help_text=u'单位为B'
    )

    end_index = models.IntegerField(
    )

    image_id = models.CharField(
        max_length=100,
    )

    @classmethod
    def create_upload_file(cls, file_name, total_size, split_size, end_index):
        try:
            cls.objects.create(file_name=file_name, total_size=total_size, split_size=split_size, end_index=end_index)
        except Exception as e:
            logger.debug(msg=e)
            return False
        return True

    @classmethod
    def get_upload_file_by_file_name(cls, file_name):
        try:
            upload_file = cls.objects.get(file_name=file_name)
        except Exception as e:
            logger.debug(msg=e)
            return None
        return upload_file

    @classmethod
    def add_image_id_by_file_name(cls, file_name, image_id):
        try:
            file_ins = cls.objects.get(file_name=file_name)
            file_ins.image_id = image_id
            file_ins.save()
        except Exception as e:
            logger.debug(msg=e)
            return False
        return True

    @classmethod
    def get_file_name_by_image_id(cls, image_id):
        try:
            file_ins = cls.objects.get(image_id=image_id)
            file_name = file_ins.file_name
        except Exception as e:
            logger.debug(msg=e)
            return None
        return file_name

    @classmethod
    def del_file_by_file_name(cls, file_name):
        try:
            cls.objects.get(file_name=file_name).delete()
        except Exception as e:
            logger.debug(msg=e)
            return False
        return True


class ImageFileModel(models.Model):
    class Meta:
        db_table = "image_file"

    image_file = models.ForeignKey(
        UploadFileModel
    )

    image_id = models.CharField(
        max_length=100,
    )

    @classmethod
    def add_image_id_by_file_name(cls, file_name, image_id):
        try:
            file_ins = UploadFileModel.get_upload_file_by_file_name(file_name)
            cls.objects.create(image_file=file_ins, image_id=image_id)
        except Exception as e:
            logger.debug(msg=e)
            return False
        return True

    @classmethod
    def del_file_by_image_id(cls, image_id):
        try:
            image_file = cls.objects.filter(image_id=image_id)
            if image_file.exists():
                image_file.first().delete()
            else:
                logger.info('%s is not exist before do deletion' % image_id)
        except Exception as e:
            logger.debug(msg=e)
            return False
        return True

    @classmethod
    def get_file_name_by_image_id(cls, image_id):
        try:
            file_ins = cls.objects.get(image_id=image_id).image_file
            file_name = file_ins.file_name
        except Exception as e:
            logger.debug(msg=e)
            return None
        return file_name

    @classmethod
    def get_file_exists(cls, file_name):
        try:
            file_ins = UploadFileModel.get_upload_file_by_file_name(file_name)
            return cls.objects.filter(image_file=file_ins).exists()
        except Exception as e:
            logger.debug(msg=e)
            return False
