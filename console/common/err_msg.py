# coding=utf-8
from django.utils.translation import ugettext as _

from console.common.logger import getLogger

logger = getLogger(__name__)

# todo: use CONSOLE_APP = settings.INSTALLED_APPS instead
CONSOLE_APP = (
    "console.console.account",
    "console.console.zones",
    "console.console.disks",
    "console.console.quotas",
    "console.console.images",
    "console.console.records",
    "console.console.backups",
    "console.console.wallets",
    "console.console.billings",
    "console.console.security",
    "console.console.ips",
    "console.console.keypairs",
    "console.console.routers",
    "console.console.nets",
    "console.console.notice_center",
    "console.console.instances",
    "console.console.alarms",
    "console.console.rds",
)

MESSAGE_MODULES = [module.rsplit(".", 1)[-1].upper() for module in CONSOLE_APP]


# code info
class Code(object):
    OK = 0
    ERROR = 1


# common error ret_code
class CommonErrorCode(object):
    PARAMETER_ERROR = 90001
    REQUEST_API_ERROR = 90002
    REQUEST_API_UNRESPONSIVE = 90003
    REQUEST_API_FORBIDDEN = 90004 # 1400
    REQUEST_API_NOT_FOUND = 90005 # 2100
    REQUEST_API_INTERNAL_ERROR = 90006 # 5000
    REQUEST_API_SERVICE_BUSY = 90007 # 5100
    REQUEST_API_RESOURCE_INSUFFICIENT = 90008 # 5200
    REQUEST_API_SERVE_UPDATING = 90009 # 5300
    EMAIL_ALREADY_USED = 90010    # FIXME: should not be here
    CELLPHONE_ALREADY_USED = 90011
    TWO_PASSWORDS_DONOT_MATCH = 90012
    PASSWORD_THE_SAME_WITH_THE_OLD_ONE = 90013
    USERNAME_ALREADY_USED = 90014
    RESPONSE_NOT_CONSOLE_RESPONSE = 90015

    RESPONSE_SUCCESS = 200

    UNKNOWN_ERROR = 90100

    SERVER_INTERNAL_ERROR = 500

# 公共错误码信息
MESSAGES = {
    0: _('服务器响应成功'),
    90001: _(u"参数错误"),
    90002: _(u"服务器响应错误"),
    90003: _(u"服务器无响应"),
    90004: _(u"请求服务器被拒绝"),
    90005: _(u"服务器资源不存在"),
    90006: _(u"服务器内部错误"),
    90007: _(u"服务器服务器繁忙"),
    90008: _(u"服务器资源不足"),
    90009: _(u"服务器服务器更新中"),
    90010: _(u"邮箱已被注册"),
    90011: _(u"手机号已被注册"),
    90012: _(u"两次密码输入不一致"),
    90013: _(u"新密码不能与旧密码一样"),
    90014: _(u"用户名已被使用"),
    90015: _(u"返回不是ConsoleResponse示例"),

    90100: _(u"未知错误"),

    500: _(u"Server Internal Error")
}


# api code convert to console code

API_CODE = {
    1400: CommonErrorCode.REQUEST_API_FORBIDDEN,
    2100: CommonErrorCode.REQUEST_API_NOT_FOUND,
    5000: CommonErrorCode.REQUEST_API_INTERNAL_ERROR,
    5100: CommonErrorCode.REQUEST_API_SERVICE_BUSY,
    5200: CommonErrorCode.REQUEST_API_RESOURCE_INSUFFICIENT,
    5300: CommonErrorCode.REQUEST_API_SERVE_UPDATING
}


# class AccountErrorCode(object):
# billings
class BillingErrorCode(object):
    BALANCE_NOT_ENOUGH = 12001

BILLINGS_MSG = {
    12001: _(u"余额不足")
}


# instance error ret_code
class InstanceErrorCode(object):
    INSTANCE_LOGIN_PARAMETER_FAILED = 15001
    RUN_INSTANCES_FAILED = 15002
    DESCRIBE_INSTANCES_FAILED = 15003
    DELETE_INSTANCES_FAILED = 15004
    UPDATE_INSTANCE_FAILED = 15005
    INVALID_INSTANCE_TYPE = 15006
    INVALID_MAC_ADDRESS = 15007
    INVALID_IP_STATUS = 15008
    DUPLICATED_NETWORK = 15009
    INVALID_INSTANCE_STATE = 15010
    ATTACHED_DISKS_LIMIT_EXCEED = 15011
    INSTANCE_NOT_FOUND = 15012
    INVALID_EXT_NETWORK = 15013

INSTANCES_MSG = {
    15001: _(u"主机登录参数失败"),
    15002: _(u"创建主机失败"),
    15003: _(u"获取主机列表失败"),
    15004: _(u"删除主机失败"),
    15005: _(u"更新主机失败"),
    15006: _(u"失败：主机类型不合法"),
    15007: _(u"失败：MAC地址不合法"),
    15008: _(u"失败：非法的IP状态"),
    15009: _(u"失败：公网网络重复"),
    15010: _(u"失败：主机状态非法"),
    15011: _(u"失败：超过最大挂载硬盘限制"),
    15012: _(u"失败：主机未找到"),
    15013: _(u"失败：公网网络非法")
}


class FlavorErrorCode(object):
    FLAVOR_NAME_EXIST = 1101
    FLAVOR_ID_EXIST = 1102

FLAVOR_MSG = {
    1101:_(u"Flavor 名称已存在"),
    1102:_(u"Flavor 配额已存在"),
}

# net error ret_code
class NetErrorCode(object):
    DELETE_NET_FAILED = 18001
    JOIN_NET_FAILED = 18002
    JOIN_NETS_FAILED = 18003
    LEAVE_NETS_FAILED = 18004
    JOIN_BASE_NET_FAILED = 18005
    LEAVE_BASE_NET_FAILED = 18006
    SAVE_NET_FAILED = 18007
    SAVE_NETWORK_FAILED = 18008
    GET_NETWORK_FAILED = 18009
    JOIN_PUBLIC_NET_CONFLICT = 18010
    GET_NET_FAILED = 18011
    JOIN_NET_DUPLICATE = 18012

NETS_MSG = {
    18001: _(u"子网删除失败"),
    18002: _(u"实例加入子网失败"),
    18003: _(u"实例加入子网失败"),
    18004: _(u"实例离开子网失败"),
    18005: _(u"实例加入基础网络失败"),
    18006: _(u"实例离开基础网络失败"),
    18007: _(u"保存子网失败"),
    18008: _(u"保存网络失败"),
    18009: _(u"获取网络失败"),
    18010: _(u"主机已经加入公网子网或基础网络"),
    18011: _(u"获取子网失败"),
    18012: _(u"实例重复加入子网错误"),
}


# router error ret_code
class RouterErrorCode(object):
    ROUTER_EXTERNAL_GATEWAY_DISABLE = 21001
    PRIVATE_NET_JOIN_ROUTER_DISABLE = 21002


ROUTERS_MSG = {
    21001: _(u"路由器未加入公网网关"),
    21002: _(u"内网子网不可加入路由器")
}


class MonitorErrorCode(object):
    REQUIRED_POINT_NUM_TOO_LARGE = 27001


MONITOR_MSG = {
    27001: _(u"需要的点数超过真实点数"),
}


# ret_code info
class ErrorCode(object):
    # common
    common = CommonErrorCode

    # net
    net = NetErrorCode

    # reouter
    router = RouterErrorCode


# 以下为错误信息转义区
# 模块命名方式
# apps中得模块名大写+"MSG"：APP_MSG

PARAMETER_CODE = {
    # common
    "action": 80001,
    "owner": 80002,
    "zone": 80003,
    "sort_key": 80004,
    "page_size": 80005,
    "page": 80006,
    "count": 80007,

    # net
    "net_id": 80051,
    "nets": 80052,
    "net_name": 80053,
    "gateway_ip": 80054,
    "net_type": 80055,
    "enable_dhcp": 80056,
    "cidr": 80057,

    # ip
    "ip_id": 80101 ,
    "ips": 80102,
    "ip_name": 80103,
    "billing_mode": 80104,
    "bandwidth": 80105,
    "ip_address": 80106,

    # router
    "router_id": 80151,
    "routers": 80152,
    "router_name": 80153,
    "enable_gateway": 80154,

    # instance:
    "instance_id": 80201,
    "instances": 80202,
    "instance_name": 80203,
    "instance_type_id": 80204,
    "use_basenet": 80205,
    "login_mode": 80206,
    "login_keypair": 80207,
    "login_password": 80208,
    "reboot_type": 80209,
    "console_type": 80210,
    "preserve_device": 80211,
    "disk_config": 80212,
    "mac_address": 80213,

}

# 每个resource参数编码为50个
PARAMETER_MSG = {
    # common
    80001: _(u"参数action不合法"),
    80002: _(u"参数owner不合法"),
    80003: _(u"参数zone不合法"),
    80004: _(u"参数sort_key不合法"),
    80005: _(u"参数page_size不合法"),
    80006: _(u"参数page不合法"),
    80007: _(u"参数count不合法"),

    # net
    80051: _(u"参数net_id不合法"),
    80052: _(u"参数nets不合法"),
    80053: _(u"子网名称不合法"),
    80054: _(u"网关地址不合法"),
    80055: _(u"网络类型不合法"),
    80056: _(u"参数enable_dhcp不合法"),
    80057: _(u"网络地址不合法"),

    # ip
    80101: _(u"参数ip_id不合法"),
    80102: _(u"参数ips不合法"),
    80103: _(u"公网IP名称不合法"),
    80104: _(u"公网IP计费模式不合法"),
    80105: _(u"公网IP计费带宽不合法"),
    80106: _(u"公网IP地址不合法"),

    # router
    80151: _(u"参数router_id不合法"),
    80152: _(u"参数routers不合法"),
    80153: _(u"路由器名称不合法"),
    80154: _(u"参数enable_gateway不合法"),

    # instance
    80201: _(u"参数instance_id不合法"),
    80202: _(u"参数instances不合法"),
    80203: _(u"主机名称不合法"),
    80204: _(u"参数instance_type_id不合法"),
    80205: _(u"参数use_basenet不合法"),
    80206: _(u"参数login_mode不合法"),
    80207: _(u"参数login_keypair不合法"),
    80208: _(u"参数login_password不合法"),
    80209: _(u"参数reboot_type不合法"),
    80210: _(u"参数console_type不合法"),
    80211: _(u"参数preserve_device不合法"),
    80212: _(u"参数disk_config不合法"),
    80213: _(u"参数mac_address不合法"),

    # keypair
    80251: _(u"参数keypair_id不合法"),
    80252: _(u"参数keypairs不合法"),
    80253: _(u"参数keypair_name不合法"),
    80254: _(u"参数encryption_method不合法"),
    80255: _(u"参数public_key不合法"),
    80256: _(u"参数disable_password不合法"),

    # disk
    80301: _(u"参数disk_id不合法"),
    80302: _(u"参数disks不合法"),
    80303: _(u"参数disk_name不合法"),
    80304: _(u"参数size不合法"),
    80305: _(u"参数many不合法"),
    80306: _(u"参数new_size不合法"),
    80307: _(u"参数backup_id不合法"),

    # todo backup
    80351: _(u"参数resource_id不合法"),
    80352: _(u"参数backup_name不合法"),

    # todo security group
    80401: _(u"参数 不合法"),

    # todo monitor
    80451: _(u"参数 不合法"),
}

ACCOUNT_MSG = {
    "10001": _(u"账号未找到"),
    "10002": _(u"账号未激活"),
    "10003": _(u"保存用户登录历史错误"),
    "10004": _(u"用户认证失败"),
    "10005": _(u"手机验证码错误或失效"),
    "10006": _(u"用户原始密码错误"),
    "10007": _(u"手机验证码发送过于频繁"),
    "10008": _(u"图片验证码错误"),
    "10009": _(u"未找到用户信息"),
    "10010": _(u"发送用户激活邮件失败"),
    "10011": _(u"手机动态密码发送失败")
}


class BackupErrorCode(object):
    SAVE_BACKUP_FAILED = 11001
    BACKUP_NOT_FOUND = 11002
    DELETE_BACKUP_FAILED = 11003
    ASSOCIATE_INSTANCE_NOT_FOUND = 11004
    ASSOCIATE_DISK_NOT_FOUND = 11005
    RESTORE_RESOURCE_NOT_FOUND = 11006
    CONFIG_FOR_INSTANCE_BACKUP_NOT_FOUND = 11007
    BACKUP_CURRENTLY_IN_USE = 11008
    #  = 11007
    #  = 11008
    #  = 11009

BACKUPS_MSG = {
    11001: _(u"保存备份出错"),
    11002: _(u"备份未找到"),
    11003: _(u"备份删除失败"),
    11004: _(u"关联主机未找到"),
    11005: _(u"关联硬盘未找到"),
    11006: _(u"待恢复资源未找到"),
    11007: _(u"主机备份的配置未找到"),
    11008: _(u"备份目前在使用中"),
}


class DiskErrorCode(object):
    CREATE_DISK_FAILED = 13001
    DELETE_DISK_FAILED = 13002
    DISK_RENAME_FAILED = 13003

DISKS_MSG = {
    13001: _(u"硬盘创建失败"),
    13002: _(u"硬盘删除失败"),
    13003: _(u"硬盘重命名失败"),
}


class SecurityErrorCode(object):
    SECURITY_GROUP_NOT_FOUND = 22001
    CREATE_SECURITY_GROUP_FAILED = 22002
    SAVE_SECURITY_GROUP_FAILED = 22003
    DEFAULT_SECURITY_CANNOT_MODIFIED = 22004
    SAVE_SECURITY_GROUP_RULE_FAILED = 22005
    SECURITY_GROUP_RENAME_FAILED = 22006
    ONE_SECURITY_PER_INSTANCE_ERROR = 22007
    SECURITY_GROUP_RULE_ALREADY_EXIST = 22008
    SECURITY_GROUP_TO_BE_DELETE_IN_USE = 22009
    SECURITY_GROUP_TYPE_ERROR = 22010


SECURITY_MSG = {
    22001: _(u"安全组未找到"),
    22002: _(u"创建安全组失败"),
    22003: _(u"保存安全组失败"),
    22004: _(u"默认安全组不可修改"),
    22005: _(u"保存安全组规则失败"),
    22006: _(u"安全组重命名失败"),
    22007: _(u"一台主机只能有一个安全组"),
    22008: _(u"安全组规则已存在"),
    22009: _(u"安全组正在使用中，不可删除"),
    22010: _(u"安全组规则类型错误")
}


class KeypairErrorCode(object):
    CREATE_KEYPAIR_FAILED = 17001

KEYPAIRS_MSG = {
    17001: _(u"创建密钥失败"),
}


class QuotaErrorCode(object):
    QUOTA_QUERY_FAILED = 19001
    QUOTA_EXCEED = 19002
    QUOTA_MODIFICATION_ERROR = 19003
    QUOTA_NOT_FOUND = 19004
    INVALID_QUOTA_TYPE = 19005
    SAVE_QUOTA_FAILED = 19006
    QUOTA_UNKNOWN_ERROR = 19007


QUOTAS_MSG = {
    19001: _(u"查找配额失败"),
    19002: _(u"配额不足"),
    19003: _(u"配额修改错误"),
    19004: _(u"配额记录不存在"),
    19005: _(u"不是有效的配额类型"),
    19006: _(u"配额保存失败"),
    19007: _(u"配额未知错误"),
}


class IpErrorCode(object):
    pass


IP_MSG = {
    16001: _(u"")
}


class AlarmErrorCode(object):
    SAVE_NOTIFY_GROUP_FAILED = 29001
    CREATE_NOTIFY_GROUP_FAILED = 29002
    DELETE_NOTIFY_GROUP_FAILED = 29003
    SAVE_NOTIFY_MEMBER_FAILED = 29004
    CREATE_NOTIFY_MEMBER_FAILED = 29005
    DELETE_NOTIFY_MEMBER_FAILED = 29006
    NOTIFY_MEMBER_ALREADY_ACTIVATED = 29007
    ACTIVATE_NOTIFY_MEMBER_FAILED = 29008
    UPDATE_NOTIFY_MEMBER_FAILED = 29009
    CREATE_ALARM_FAILED = 29010
    SAVE_ALARM_FAILED = 29011
    DELETE_ALARM_FAILED = 29012
    BIND_ALARM_RESOURCE_FAILED = 29013
    UNBIND_ALARM_RESOURCE_FAILED = 29014
    RESCHEDULE_ALARM_MONITOR_PERIOD_FAILED = 29015
    ADD_ALARM_RULE_FAILED = 29016
    UPDATE_ALARM_RULE_FAILED = 29017
    DELETE_ALARM_RULE_FAILED = 29018
    SAVE_ALARM_RULE_FAILED = 29019
    ADD_NOTIFY_METHOD_FAILED = 29020
    UPDATE_NOTIFY_METHOD_FAILED = 29021
    DELETE_NOTIFY_METHOD_FAILED = 29022
    SAVE_NOTIFY_METHOD_FAILED = 29024
    DESCRIBE_NOTIFY_HISTORY_FAILED = 29023
    DESCRIBE_NOTIFY_HISTORY_DETAIL_FAILED = 29025


ALARMS_MSG = {
    29001: _(u"通知组保存失败"),
    29002: _(u"通知组创建失败"),
    29003: _(u"通知组删除失败"),
    29004: _(u"通知人保存失败"),
    29005: _(u"通知人创建失败"),
    29006: _(u"通知人删除失败"),
    29007: _(u"通知人的此种通知方式已激活"),
    29008: _(u"通知人激活失败"),
    29009: _(u"通知人更新失败"),
    29010: _(u"告警策略创建失败"),
    29011: _(u"告警策略保存失败"),
    29012: _(u"告警策略删除失败"),
    29013: _(u"告警资源绑定失败"),
    29014: _(u"告警资源解绑失败"),
    29015: _(u"告警监控周期调整失败"),
    29016: _(u"告警规则添加失败"),
    29017: _(u"告警规则更新失败"),
    29018: _(u"告警规则删除失败"),
    29019: _(u"告警规则保存失败"),
    29020: _(u"通知策略添加失败"),
    29021: _(u"通知策略更新失败"),
    29022: _(u"通知策略删除失败"),
    29023: _(u"告警历史查询失败"),
    29024: _(u"通知策略保存失败"),
    29025: _(u"告警历史详情查询失败")
}


class RdsErrorCode(object):
    QUERY_RDS_VERSION_FAILED = 31001
    CREATE_RDS_FAILED = 31002
    DESCRIBE_RDS_FAILED = 31003
    DELETE_RDS_FAILED = 31004
    REBOOT_RDS_FAILED = 31005
    CREATE_RDS_CONFIG_FAILED = 31006
    DESCRIBE_RDS_CONFIG_FAILED = 31007
    DESCRIBE_RDS_CONFIG_DETAIL_FAILED = 31008
    DELETE_RDS_CONFIG_FAILED = 31009
    UPDATE_RDS_CONFIG_FAILED = 31010
    CREATE_RDS_BACKUP_FAILED = 31011
    DELETE_RDS_BACKUP_FAILED = 31012
    DESCRIBE_RDS_BACKUP_FAILED = 31013
    QUERY_RDS_FLAVOR_FAILED = 31014
    SAVE_RDS_FAILED = 31015
    SAVE_RDS_CONFIG_FAILED = 31016
    SAVE_RDS_BACKUP_FAILED = 31017
    CREATE_RDS_ACCOUNT_FAILED = 31018
    SAVE_RDS_ACCOUNT_FAILED = 31019
    DESCRIBE_RDS_ACCOUNT_FAILED = 31020
    DELETE_RDS_ACCOUNT_FAILED = 31021
    CREATE_RDS_DATABASE_FAILED = 31022
    SAVE_RDS_DATABASE_FAILED = 31023
    DESCRIBE_RDS_DATABASE_FAILED = 31024
    DELETE_RDS_DATABASE_FAILED = 31025
    GET_RDS_MONITOR_INFO_FAILED = 31026
    MODIFY_RDS_ACCOUNT_AUTHORITY_FAILED = 31027
    CHANGE_RDS_ACCOUNT_PASSWORD_FAILED = 31028
    APPLY_RDS_CONFIG_FAILED = 31029
    REMOVE_RDS_CONFIG_FAILED = 31030
    REBOOT_RDS_AFTER_CONFIG_CHANGE_TIMEOUT = 31031
    CREATE_RDS_DEFAULT_SECURITY_GROUP_FAILED = 31032
    SAVE_RDS_DEFAULT_SECURITY_GROUP_FAILED = 31033
    CREATE_RDS_DEFAULT_SECURITY_GROUP_RULE_FAILED = 31034
    QUERY_RDS_IOPS_INFO_FAILED = 31035
    RDS_DATABASE_AlREADY_EXIST = 31036
    RDS_ACCOUNT_AlREADY_EXIST = 31037
    DESCRIBE_RDS_DETAIL_FAILED = 31038
    INAPPROPRIATE_RDS_STATUS_FOR_CHANGE_CONFIG = 31039


RDS_MSG = {
    31001: _(u'查询数据库版本失败'),
    31002: _(u'创建RDS失败'),
    31003: _(u'查询RDS信息失败'),
    31004: _(u'删除RDS失败'),
    31005: _(u'重启RDS失败'),
    31006: _(u'创建RDS数据库配置失败'),
    31007: _(u'查询RDS数据库配置失败'),
    31008: _(u'查询RDS数据库配置详情失败'),
    31009: _(u'删除RDS数据库配置失败'),
    31010: _(u'更新RDS数据库配置失败'),
    31011: _(u'创建RDS备份失败'),
    31012: _(u'删除RDS备份失败'),
    31013: _(u'查询RDS备份失败'),
    31014: _(u'查询RDS flavor 失败'),
    31015: _(u'保存RDS失败'),
    31016: _(u'保存RDS配置失败'),
    31017: _(u'保存RDS备份失败'),
    31018: _(u'创建RDS数据库账户失败'),
    31019: _(u'保存RDS数据库账户失败'),
    31020: _(u'查询RDS数据库账户失败'),
    31021: _(u'删除RDS数据库账户失败'),
    31022: _(u'创建RDS数据库失败'),
    31023: _(u'保存RDS数据库失败'),
    31024: _(u'查询RDS数据库失败'),
    31025: _(u'删除RDS数据库失败'),
    31026: _(u'获取RDS监控信息失败'),
    31027: _(u'修改 RDS 账户权限失败'),
    31028: _(u'修改 RDS 账户密码失败'),
    31029: _(u"应用 RDS 配置文件失败"),
    31030: _(u"移除 RDS 配置文件失败"),
    31031: _(u"更换 RDS 配置文件重启超时"),
    31032: _(u"创建 RDS 默认安全组失败"),
    31033: _(u"保存 RDS 默认安全组到数据库失败"),
    31034: _(u"创建 RDS 默认安全组规则失败"),
    31035: _(u"查询 RDS 磁盘读写速度信息失败"),
    31036: _(u"待创建的 RDS 数据库已经存在"),
    31037: _(u"待创建的 RDS 账户已经存在"),
    31038: _(u"查询 RDS 实例详情失败"),
    31039: _(u"非运行中状态的 RDS 实例无法更改配置文件")
}


class SubaccountErrorCode(object):
    SUBACCOUNT_PARAMS_ERROR = 33001
    MODIFY_SUBACCOUNT_ERROR = 33002
    DELETE_SUBACCOUNT_ERROR = 33003
    CREATE_PERM_REQUEST_ERROR = 33011
    SET_USER_PERM_INFO_ERROR = 33012
    PARENT_STORE_ERROR = 33013
    CREATE_SUBACCOUNT_ERROR = 33014
    MODIFY_USERNAME_ERROR = 33015
    MAX_SUBACCOUNT_REACHED = 33016
    CANT_DELETE_MAIN_ACCOUNT = 33017
    CANT_DELETE_SELF_ACCOUNT = 33018
    CANT_FREEZE_MAIN_ACCOUNT = 33019
    CANT_FREEZE_SELF_ACCOUNT = 33020
    CANT_FREEZE_INACTIVE_ACCOUNT = 33021
    SUBACCOUNT_DONOT_FOUND = 33022
    PUBLIC_KEY_NOT_VALID = 33023
    INPUT_INVALID_USERNAME = 33024
    ROLE_NOT_FOUND = 33025
    PERM_PERIOD_TOO_SHORT = 33026
    PERM_REQUEST_NOT_FOUND = 33027

SUBACCOUNT_MSG = {
    33001: _(u"子账号参数错误"),
    33002: _(u"修改子账号错误"),
    33003: _(u"删除子账号错误"),
    33011: _(u"创建权限申请错误"),
    33012: _(u"设置用户权限信息"),
    33013: _(u"父账号补充个人信息错误"),
    33014: _(u"创建子账号错误"),
    33015: _(u"修改用户名错误"),
    33016: _(u"达到了最大创建子账号的上限"),
    33017: _(u"不能注销主账号"),
    33018: _(u"不能注销自己的账号"),
    33019: _(u"不能冻结主账号对应的子账号"),
    33020: _(u"不能冻结自己的账号"),
    33021: _(u"不允许冻结未激活的子账号"),
    33022: _(u"用户子账号未找到"),
    33023: _(u"输入的是无效的公钥"),
    33024: _(u"输入的用户名与关键词冲突"),
    33025: _(u"角色未找到"),
    33026: _(u"机器申请时间不得少于一天"),
    33027: _(u"权限申请未找到"),
}


class DevopsErrorCode(object):
    DEVOPS_PARAMS_ERROR = 32001
    DEVOPS_JUMPSERVER_PARAMS_ERROR = 32002
    SAVE_CONFIG_ITEM_ERROR = 32003
    COMBINE_CONFIG_ITEM_ERROR = 32004
    CREATE_JUMPSERVER_ERROR = 32005
    DELETE_JUMPSERVER_ERROR = 32006
    GET_SALT_MASTER_IP_ERROR = 32007
    CREATE_CONFIG_ITEM_ERROR = 32008
    CREATE_CONFIG_GROUP_ERROR = 32009
    ISSUED_CONFIG_ITEM_ERROR = 32010
    MODIFY_CONFIG_ITEM_ERROR = 32011
    DELETE_CONFIG_ITEM_ERROR = 32012
    DESCRIBE_CONFIG_ITEM_STATUS_ERROR = 32013
    INSTANCE_NOT_FOUND = 32014
    INSTANCE_NOT_JUMPSERVER = 32015
    CONFIG_GROUP_NOT_FOUND = 32016
    INSTANCE_SHOULD_NOT_JUMPSERVER = 32017
    UPDATE_CONFIG_ITEM_STATUS_ERROR = 32018


DEVOPS_ERROR_MSG = {
    32001: _(u"DEVOPS参数错误"),
    32002: _(u"跳板机参数错误"),
    32003: _(u"保存配置项错误"),
    32004: _(u"关联配置项错误"),
    32005: _(u"创建跳板机错误"),
    32006: _(u"删除跳板机错误"),
    32007: _(u"获取Salt Master IP错误"),
    32008: _(u"创建配置项错误"),
    32009: _(u"创建配置组错误"),
    32010: _(u"下发配置项错误"),
    32011: _(u"修改配置项错误"),
    32012: _(u"删除配置项错误"),
    32013: _(u"获取配置项下发状态错误"),
    32014: _(u"主机未找到"),
    32015: _(u"主机不是跳板机"),
    32016: _(u"配置组未找到"),
    32017: _(u"主机不能是跳板机"),
    32018: _(u"更新配置项状态错误"),
}


class AdminErrorCode(object):
    DESCRIBE_DRS_FAILED = 34001
    SET_DRS_FAILED = 34002
    DESCRIBE_POLICY_FAILED = 34003
    SET_POLICY_FAILED = 34004
    SET_LICENSE_KEY_FAILED = 34005
    DECRYPT_LICENSE_KEY_FAILED = 34006
    DESCRIBE_SUBNET_FAILED = 34007
    CREATE_SUBNET_FAILED = 34008
    UPDATE_SUBNET_FAILED = 34009
    DELETE_SUBNET_FAILED = 34010
    CREATE_NETWORK_FAILED = 34011
    DELETE_NETWORK_FAILED = 34012
    DESCRIBE_ROUTER_FAILED = 34013
    JOIN_I_TO_SUB_FAILED = 34014
    CREATE_ROUTER_FAILED = 34015
    DELETE_ROUTER_FAILED = 34016
    JOIN_ROUTER_FAILED = 34017
    QUIT_ROUTER_FAILED = 34018
    UPDATE_ROUTER_FAILED = 34019
    SET_ROUTER_SWITCH_FAILED = 34020
    CLEAR_ROUTER_FAILED = 34021
    LEAVE_I_TO_SUB_FAILED = 34022

ADMIN_MSG = {
    34001: _(u"DRS信息获取失败"),
    34002: _(u"DRS信息更新失败"),
    34003: _(u"POLICY信息获取失败"),
    34004: _(u"POLICY配置更新失败"),
    34005: _(u"LICENSE设置失败"),
    34006: _(u"LICENSE解密失败"),
    34007: _(u"获取子网信息失败"),
    34008: _(u"创建子网失败"),
    34009: _(u"更新子网失败"),
    34010: _(u"删除子网失败"),
    34011: _(u"创建网络失败"),
    34012: _(u"删除网络失败"),
    34013: _(u"获取路由列表失败"),
    34014: _(u"部分主机加入子网失败"),
    34015: _(u"创建路由失败"),
    34016: _(u"删除路由失败"),
    34017: _(u"加入路由失败"),
    34018: _(u"离开路由失败"),
    34019: _(u"更新路由失败"),
    34020: _(u"设置路由开关失败"),
    34021: _(u"清除网管失败"),
    34022: _(u"部分主机离开子网失败"),
}

class LoadBalancerErrorCode(object):
    NET_NOT_FOUND = 32001
    SAVE_LB_ERROR = 32002
    DELETE_LB_ERROR = 32003
    LISTENER_PORT_CONFLICT = 32004
    COOKIE_NAME_NOT_FOUND = 32005
    CREATE_LISTENER_ERROR = 32006
    CREATE_POOL_ERROR = 32007
    CREATE_HEALTHMONITOR_ERROR = 32008
    SAVE_LB_HEALTHMONITOR_ERROR = 32009
    SAVE_LB_POOL_ERROR = 32010
    SAVE_LB_LISTENER_ERROR = 32011
    WAIT_LB_STATUS_ERROR = 32012
    WAIT_LISTENER_STATUS_ERROR = 32013
    DELETE_HEALTHMONITOR_ERROR = 32014
    DELETE_POOL_ERROR = 32015
    DELETE_LISTENER_ERROR = 32016
    LB_MEMBER_EXISTED = 32017
    CREATE_MEMBER_ERROR = 32018
    SAVE_LB_MEMBER_ERROR = 32019
    DELETE_MEMBER_ERROR = 32020
    BIND_IP_REPEATED = 32021
    PORT_ID_NOT_FOUND = 32022
    INSTANCE_IP_ADDR_NOT_FOUND = 32023

LOAD_BALANCER_MSG = {
    32001: _(u"非基础网络，请选择一个子网"),
    32002: _(u"保存负载均衡器错误"),
    32003: _(u"删除负载均衡器错误"),
    32004: _(u"监听端口冲突"),
    32005: _(u"用户KEY未找到"),
    32006: _(u"创建监听器失败"),
    32007: _(u"创建监听器失败"),
    32008: _(u"创建监听器失败"),
    32009: _(u"保存HealthMonitor失败"),
    32010: _(u"保存Pool失败"),
    32011: _(u"保存Listener失败"),
    32012: _(u"等待LB状态失败"),
    32013: _(u"等待Listener张台失败"),
    32014: _(u"删除Healthmonitor错误"),
    32015: _(u"删除Pool错误"),
    32016: _(u"删除Listener错误"),
    32017: _(u"指定IP和地址的后端已经存在"),
    32018: _(u"添加后端失败"),
    32019: _(u"保存Member失败"),
    32020: _(u"删除后端失败"),
    32021: _(u"负载均衡器重复绑定IP"),
    32022: _(u"负载均衡器PORT未找到"),
    32023: _(u"主机IP地址未找到"),
}
# 在上面写自己的错误码信息


for module in MESSAGE_MODULES:
    message_name = "%s_MSG" % module
    if not message_name in locals():
        continue
    MESSAGES.update(eval(message_name, globals(), locals()))

MESSAGES.update(eval('PARAMETER_MSG', globals(), locals()))
MESSAGES.update(eval('MONITOR_MSG', globals(), locals()))
MESSAGES.update(eval('ADMIN_MSG', globals(), locals()))


if __name__ == "__main__":
    # print MESSAGES
    logger.debug("MESSAGES: " + str(MESSAGES.keys()))


