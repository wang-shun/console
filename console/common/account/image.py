# -*- coding: utf8 -*-

from cStringIO import StringIO

from PIL import Image


def resize_image(image, height, width):
    image_obj = Image.open(image)
    image_obj.thumbnail((height, width), Image.ANTIALIAS)

    p = StringIO()
    image_obj.save(p, image_obj.format)
    p.seek(0)
    return p


def get_image_format(image):
    image_obj = Image.open(image)
    return image_obj.format
