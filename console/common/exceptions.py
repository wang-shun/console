# coding=utf-8


from .interfaces import ViewExceptionInterface


class SaveDataError(Exception):
    pass


class AlipayException(Exception):
    """Base Alipay Exception"""


class MissingParameter(AlipayException):
    """Raised when the create payment url process is missing some
    parameters needed to continue"""


class ParameterValueError(AlipayException):
    """Raised when parameter value is incorrect"""


class TokenAuthorizationError(AlipayException):
    """The error occurred when getting token"""


class UnSupportedPlatform(Exception):
    """
    The platform do not supported
    """


class EmailAllReadyUsedError(Exception):
    pass


class CellPhoneAllReadyUsedError(Exception):
    pass


class SaveOpenRegisterModelError(Exception):
    pass


class CreateAccountModelError(Exception):
    pass


class AccountProperyValueNotValidError(Exception):
    """
    账号属性值错误
    """
    pass


class LotteryOwnerInfoValueNotValidError(Exception):
    """
    运营获奖者信息错误
    """
    pass


class ViewException(ViewExceptionInterface):
    pass
