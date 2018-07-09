# coding=utf-8

import json
import random
import subprocess
import tempfile
from cStringIO import StringIO

import os
import re
import six
from PIL import (Image, ImageDraw, ImageFont)
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, Http404

from console.common.captcha.models import CloudinCaptchaStore as CaptchaStore
from console.common.captcha.helpers import captcha_image_url
from console.common.captcha.conf import settings
from console.common.logger import getLogger

logger = getLogger(__name__)

NON_DIGITS_RX = re.compile('[^\d]')
from_top = 4


def getsize(font, text):
    if hasattr(font, 'getoffset'):
        return [x + y for x, y in zip(font.getsize(text), font.getoffset(text))]
    else:
        return font.getsize(text)


def makeimg(size, background_color=None):
    background_color = background_color
    logger.debug("Background color: %s" % background_color)
    if background_color == "transparent":
        image = Image.new('RGBA', size)
    else:
        image = Image.new('RGB', size, background_color)
    return image


def captcha_image(request, key, scale=1):
    try:
        store = CaptchaStore.objects.get(hashkey=key)
    except CaptchaStore.DoesNotExist:
        return HttpResponse(status=410)

    foreground_color = request.GET.get("foreground_color") or settings.CAPTCHA_FOREGROUND_COLOR
    if not foreground_color.startswith("#"):
        foreground_color = "#%s" % foreground_color
    background_color = request.GET.get("background_color") or settings.CAPTCHA_BACKGROUND_COLOR
    if background_color and not background_color.startswith("#") and background_color != "transparent":
        background_color = "#%s" % background_color

    text = store.challenge

    if isinstance(settings.CAPTCHA_FONT_PATH, six.string_types):
        fontpath = settings.CAPTCHA_FONT_PATH
    elif isinstance(settings.CAPTCHA_FONT_PATH, (list, tuple)):
        fontpath = random.choice(settings.CAPTCHA_FONT_PATH)
    else:
        raise ImproperlyConfigured('settings.CAPTCHA_FONT_PATH needs to be a path to a font or list of paths to fonts')

    if fontpath.lower().strip().endswith('ttf'):
        font = ImageFont.truetype(fontpath, settings.CAPTCHA_FONT_SIZE * scale)
    else:
        font = ImageFont.load(fontpath)

    if settings.CAPTCHA_IMAGE_SIZE:
        size = settings.CAPTCHA_IMAGE_SIZE
    else:
        size = getsize(font, text)
        size = (size[0] * 2, int(size[1] * 1.4))

    image = makeimg(size, background_color)

    try:
        PIL_VERSION = int(NON_DIGITS_RX.sub('', Image.VERSION))
    except:
        PIL_VERSION = 116
    xpos = 2

    charlist = []
    for char in text:
        if char in settings.CAPTCHA_PUNCTUATION and len(charlist) >= 1:
            charlist[-1] += char
        else:
            charlist.append(char)
    for char in charlist:
        fgimage = Image.new('RGB', size, foreground_color)
        charimage = Image.new('L', getsize(font, ' %s ' % char), '#000000')
        chardraw = ImageDraw.Draw(charimage)
        chardraw.text((0, 0), ' %s ' % char, font=font, fill='#ffffff')
        if settings.CAPTCHA_LETTER_ROTATION:
            if PIL_VERSION >= 116:
                charimage = charimage.rotate(random.randrange(*settings.CAPTCHA_LETTER_ROTATION), expand=0, resample=Image.BICUBIC)
            else:
                charimage = charimage.rotate(random.randrange(*settings.CAPTCHA_LETTER_ROTATION), resample=Image.BICUBIC)
        charimage = charimage.crop(charimage.getbbox())
        maskimage = Image.new('L', size)

        maskimage.paste(charimage, (xpos, from_top, xpos + charimage.size[0], from_top + charimage.size[1]))
        size = maskimage.size
        image = Image.composite(fgimage, image, maskimage)
        xpos = xpos + 2 + charimage.size[0]

    if settings.CAPTCHA_IMAGE_SIZE:
        # centering captcha on the image
        tmpimg = makeimg(size, background_color)
        tmpimg.paste(image, (int((size[0] - xpos) / 2), int((size[1] - charimage.size[1]) / 2 - from_top)))
        image = tmpimg.crop((0, 0, size[0], size[1]))
    else:
        image = image.crop((0, 0, xpos + 1, size[1]))
    draw = ImageDraw.Draw(image)

    for f in settings.noise_functions():
        draw = f(draw, image)
    for f in settings.filter_functions():
        image = f(image)

    out = StringIO()
    image.save(out, "PNG")
    out.seek(0)

    response = HttpResponse(content_type='image/png')
    response.write(out.read())
    response['Content-length'] = out.tell()

    return response


def captcha_audio(request, key):
    if settings.CAPTCHA_FLITE_PATH:
        try:
            store = CaptchaStore.objects.get(hashkey=key)
        except CaptchaStore.DoesNotExist:
            # HTTP 410 Gone status so that crawlers don't index these expired urls.
            return HttpResponse(status=410)

        text = store.challenge
        if 'captcha.helpers.math_challenge' == settings.CAPTCHA_CHALLENGE_FUNCT:
            text = text.replace('*', 'times').replace('-', 'minus')
        else:
            text = ', '.join(list(text))
        path = str(os.path.join(tempfile.gettempdir(), '%s.wav' % key))
        subprocess.call([settings.CAPTCHA_FLITE_PATH, "-t", text, "-o", path])
        if os.path.isfile(path):
            response = HttpResponse()
            f = open(path, 'rb')
            response['Content-Type'] = 'audio/x-wav'
            response.write(f.read())
            f.close()
            os.unlink(path)
            return response
    raise Http404


def captcha_refresh(request):
    """  Return json with new captcha for ajax refresh request """
    if not request.is_ajax():
        raise Http404

    new_key = CaptchaStore.generate_key()
    to_json_response = {
        'key': new_key,
        'image_url': captcha_image_url(new_key),
    }
    return HttpResponse(json.dumps(to_json_response), content_type='application/json')
