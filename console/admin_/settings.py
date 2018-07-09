# coding=utf-8
__author__ = 'chenlei'

import os
from django.utils.translation import ugettext as _

from console.config import load_config

config = load_config()

ADMIN_APP_PATH = os.path.abspath(os.path.dirname(__file__))

BASE_DIR = ADMIN_APP_PATH

# Logo文件所在位置
ADMIN_LOGO_PATH = "statics/images/admin_logo.png"
CONSOLE_LOGO_PATH = "statics/images/console_logo.png"

# 报表发送收件人配置
DEFAULT_EMAIL_RECEIVER = config.get("email", "receiver")

# 用户信息允许更新的字段（除相片之外）
ALLOWED_UPDATE_COLUMNS = ["name", "nickname", "cell_phone"]

# 多长时间清理一次禁用账户
CLEAN_DELETED_INTERVAL = 7  # days

# URL的BASE路径
BASE_URL = "/ConsoleAdmin"

if config.get("other", "env") == "admin":
    BASE_URL = ""

# 默认登录URL
LOGIN_URL = os.path.join(BASE_URL, "login")

# 默认跳转URL
DEFAULT_REDIRECT_TO = os.path.join(BASE_URL, "/dashboard")

# 新建用户后默认跳转URL
DEFAULT_ADMIN_PATH = os.path.join(BASE_URL, "/system/account")

# 默认页面大小列表
DEFAULT_PAGE_SIZE_LIST = [5, 10, 20, 50, 100]

# 缩略图大小
THUMBNAIL_SIZE = (60, 60)

# 相片上传目录
IMAGE_UPLOAD_PATH = "id_images"

# 默认的页码
DEFAULT_PAGE = 1

# 默认页面大小
DEFAULT_PAGE_SIZE = 10

# 默认相片路径
DEFAULT_IMAGE_PATH = os.path.join(ADMIN_APP_PATH, "statics/images/default_image.jpg")

# 默认消息过期时间(秒)
MSG_DEFAULT_EXPIRE = 365 * 24 * 3600

PERMISSION_MAP = {
    'access_ticket_dashboard': _(u"访问工单工作台"),
    'access_ticket_queue': _(u"访问工单队列"),
    'access_ticket_list': _(u"访问工单管理"),
    'send_ticket': _(u"分配工单"),
    'process_ticket': _(u"处理工单"),
    'close_ticket': _(u"关闭工单"),

    'access_account_list': _(u"访问账号管理"),
    'edit_account': _(u"编辑客户账号"),
    'delete_account': _(u"删除客户账号"),
    'access_message_list': _(u"访问消息管理"),
    'create_message': _(u"创建消息"),
    'delete_message': _(u"删除消息"),
    'edit_message': _(u"修改消息"),
    'submit_message': _(u"提交消息"),
    'review_message': _(u"审核消息"),
    'revoke_message': _(u"撤回消息"),
    'access_operation_data': _(u"访问运营数据"),

    'access_exchange_list': _(u"访问转账账单"),
    'access_recharge_list': _(u"访问充值账单"),
    'access_billing_list': _(u"访问计费账单"),
    'create_exchange_record': _(u"转账信息录入"),
    'review_exchange_record': _(u"审核转账信息"),

    'access_system_account': _(u"访问后台账号管理"),
    'access_system_permission': _(u"访问权限管理"),
    'access_system_record': _(u"访问操作日志"),
    'edit_system_account': _(u"修改账号"),
    'forbidden_system_account': _(u"禁用账号"),
    'create_account_group': _(u"新增账号类型"),
    'delete_account_group': _(u"删除账号类型"),
    'edit_account_group': _(u'编辑账号类型'),
    'access_invite_code': _(u"访问邀请码页"),
    'create_invite_code_group': _(u"创建邀请码组"),
    'edit_invite_code_group': _(u"编辑邀请码组"),
    'create_admin_user': _(u"创建管理账户"),
    'access_system_advice': _(u"访问意见和建议"),
}
