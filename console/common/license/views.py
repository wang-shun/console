# -*- coding: utf-8 -*-

from rest_framework.response import Response
from rest_framework.views import APIView

from console.common.logger import getLogger
from .helper import LicenseService

logger = getLogger(__name__)


class License(APIView):
    """
    设置、验证liecense
    """

    def post(self, request, *args, **kwargs):
        action = request.data.get("action")
        if action == "DecryptLicense":
            license_key = LicenseService.get_license_key()
            return Response(LicenseService.decrypt_license(license_key))

        if action == "SetLicenseKey":
            license_key = request.data.get("license_key")
            return Response(LicenseService.set_license_key(license_key))
