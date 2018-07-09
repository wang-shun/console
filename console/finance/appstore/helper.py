# _*_ coding: utf-8 _*_
import hashlib
import pymysql
from collections import defaultdict

from console.common.account.helper import AccountService
from console.common.utils import console_response
from console.common.utils import getLogger
# from console.common.api.api_aes import aes_api
from console.common.zones.models import ZoneModel
from console.settings import KAFKA_MQ_HOST, KAFKA_MQ_DB_HOST, KAFKA_MQ_DB_NAME, KAFKA_MQ_DB_PORT, KAFKA_MQ_DB_USER, KAFKA_MQ_DB_PASSWORD
from .models import AppStoreModel, AppUserModel

logger = getLogger(__name__)
KAFKA_MQ_DB_SQL_INSERT = "INSERT INTO sec_user (module_id, name, username, password, user_type, version) " \
                         "VALUES (%(module_id)s, %(name)s, %(username)s, %(password)s, %(user_type)s, %(version)s);"
KAFKA_MQ_DB_SQL_DELETE = "DELETE FROM sec_user WHERE name = %(name)s;"


def md5(pwd):
    """
    md5加密
    :param pwd:
    :return:
    """
    m = hashlib.md5()
    m.update(pwd)
    return m.hexdigest()


def mq_md5(password):
    """
    mq密码加密
    :param password:
    :return:
    """
    md5_pwd = md5(password + "tamboo")
    list_md5_pwd = list(md5_pwd)
    result = list()
    for item in list_md5_pwd:
        if (int(item.encode("hex")) & 0xff) < 16:
            item = 0
        result.append(item)
    return "".join(result)


def mysql_connect(host, db_name, user, password, port=3306, chartset="utf8"):
    """
    数据库连接
    :param host:
    :param db_name:
    :param user:
    :param password:
    :param port:
    :param chartset:
    :return:
    """
    conn = pymysql.connect(host=host, user=user, password=password, db=db_name, charset=chartset, port=port)
    cur = conn.cursor()
    conn.autocommit(1)
    return conn, cur


def mysql_execute(conn, cur, sql, data):
    """
    操作数据库
    :param conn:
    :param cur:
    :param sql:
    :param data:
    :return:
    """
    conn, cur = conn, cur
    try:
        cur.execute(sql, data)
        logger.debug("execute mq database success, data is: %s", data)
        return 0
    except Exception as exc:
        logger.error("execute mq database error, error is %s, sql is %s, data is: %s", exc, sql, data)
        return 1


class AppstoreService(object):

    @classmethod
    def create(cls, app_name, app_publisher, app_version, app_zone):
        """
        创建
        :param app_name:
        :param app_publisher:
        :param app_version:
        :param app_zone:
        :return:
        """
        zone_model = ZoneModel.get_zone_by_name(app_zone)
        try:
            app_momdel = AppStoreModel(app_name=app_name, app_publisher=app_publisher, app_version=app_version, app_zone=zone_model)
            app_momdel.save()
        except Exception as exc:
            logger.error("create get exception: %s", exc)
            return 1, exc
        return 0, None

    @classmethod
    def get_all_apps(cls, owner, zone):
        """
        获取当前zone当前用户下app状态
        :param owner:
        :param zone:
        :return:
        """
        user_model = AccountService.get_by_owner(owner).user
        zone_model = ZoneModel.get_zone_by_name(zone)
        all_app = AppStoreModel.objects.filter(app_zone=zone_model).all()
        app_users = AppUserModel.objects.filter(app_users__in=(user_model, ), app_app__app_zone=zone_model).all()
        apps_installed = list()
        for app in app_users:
            apps_installed.extend(app.app_app.all())
        dict_apps = defaultdict(dict)
        for app in all_app:
            dict_one_app = dict()
            if app in apps_installed:
                dict_one_app["installed"] = True
                app_user = app_users.filter(app_app=app).first()
                dict_one_app["status"] = app_user.app_status
                dict_one_app["version"] = app.app_version
                dict_one_app["publisher"] = app.app_publisher
                if app.app_name == "mq":
                    dict_one_app["mq_host"] = KAFKA_MQ_HOST
                dict_apps[app.app_name] = dict_one_app
                continue
            dict_one_app["installed"] = False
            dict_one_app["status"] = None
            dict_one_app["version"] = app.app_version
            dict_one_app["publisher"] = app.app_publisher
            dict_apps[app.app_name] = dict_one_app
        return dict_apps

    @classmethod
    def install_one_app(cls, app_name, zone, owner, app_status="in_use"):
        """
        安装应用
        :param app_name:
        :param zone:
        :param owner:
        :param app_status:
        :return:
        """
        user_model = AccountService.get_by_owner(owner).user
        zone_model = ZoneModel.get_zone_by_name(zone)
        app = AppStoreModel.objects.get(app_name=app_name, app_zone=zone_model)
        try:
            app_user_model = AppUserModel(app_status=app_status)
            app_user_model.save()
            app_user_model.app_app.add(app)
            app_user_model.app_users.add(user_model)
            app_user_model.save()
        except Exception as exc:
            logger.error("install_one_app get exception: %s", exc)
            return 1
        return 0

    @classmethod
    def change_one_app_status(cls, app_name, zone, owner, app_status):
        """
        修改应用状态
        :param app_name:
        :param zone:
        :param owner:
        :param app_status:
        :return:
        """
        if not app_status:
            return 0
        user_model = AccountService.get_by_owner(owner).user
        zone_model = ZoneModel.get_zone_by_name(zone)
        app = AppStoreModel.objects.filter(app_name=app_name, app_zone=zone_model)
        try:
            app_user_model = AppUserModel.objects.get(app_app=app, app_users=user_model)
            app_user_model.app_status = app_status
            app_user_model.save()
        except Exception as exc:
            logger.error("change_one_app_status get exception: %s", exc)
            return 1
        return 0

    @classmethod
    def uninstall_one_app(cls, app_name, zone, owner):
        """
        卸载应用
        :param app_name:
        :param zone:
        :param owner:
        :return:
        """
        user_model = AccountService.get_by_owner(owner).user
        zone_model = ZoneModel.get_zone_by_name(zone)
        try:
            app = AppStoreModel.objects.filter(app_name=app_name, app_zone=zone_model)
            app_user_model = AppUserModel.objects.get(app_app=app, app_users=user_model)
            app_user_model.delete()
        except Exception as exc:
            logger.error("uninstall_one_app get exception: %s", exc)
            return 1
        return 0


# describe_app_all, install_app_one, change_app_one_status, uninstall_app_one

def describe_app_all(payload):
    """
    获取应用状态
    :param payload:
    :return:
    """
    owner = payload.get("owner")
    zone = payload.get("zone")
    dict_apps = AppstoreService.get_all_apps(owner, zone)
    if not dict_apps:
        return console_response(code=1)
    ret_set = dict_apps
    return console_response(code=0, ret_set=ret_set)


def install_app_one(payload):
    """
    安装应用
    :param payload:
    :return:
    """
    owner = payload.get("owner")
    zone = payload.get("zone")
    app_name = payload.get("app_name")

    # 在MQ数据库中插入用户信息
    # if app_name == "mq":
    #     account_model = AccountService.get_by_owner(owner)
    #     user_model = account_model.user
    #     name = user_name = user_model.account.email
    #     logger.debug("name is %s", name)
    #     password = aes_api.decrypt(account_model.mot_de_passe)
    #     logger.debug("password is %s", password)
    #     md5_pwd = mq_md5(password)
    #     user_type = "role_user"
    #     version = 0
    #
    #     sql_data = dict(
    #         module_id=1,
    #         name=name,
    #         username=user_name,
    #         password=md5_pwd,
    #         user_type=user_type,
    #         version=version
    #     )
    #
    #     # sql = KAFKA_MQ_DB_SQL_INSERT % sql_data
    #     conn, cur = mysql_connect(KAFKA_MQ_DB_HOST, KAFKA_MQ_DB_NAME, KAFKA_MQ_DB_USER, KAFKA_MQ_DB_PASSWORD,
    #                               port=int(KAFKA_MQ_DB_PORT))
    #     code = mysql_execute(conn, cur, KAFKA_MQ_DB_SQL_INSERT, sql_data)
    #     if code == 1:
    #         return console_response(code=1, msg=u"安装失败")

    # 修改数据库
    install_code = AppstoreService.install_one_app(app_name, zone, owner)
    action_record = dict(app_name=app_name)
    return console_response(code=install_code, action_record=action_record)


def change_app_one_status(payload):
    """
    修改应用状态
    :param payload:
    :return:
    """
    owner = payload.get("owner")
    zone = payload.get("zone")
    app_name = payload.get("app_name")
    action = payload.get("action")
    if action == "stop":
        app_status = "stopped"
    elif action == "start":
        app_status = "in_use"
    else:
        app_status = None
    # 根据应用采取操作
    if app_name == "waf":
        pass
    elif app_name == "mq":
        pass
    elif app_name == "mysql":
        pass
    elif app_name == "oracle":
        pass
    else:
        return console_response(code=1, msg=u"应用名称错误")
    # 修改数据库
    change_code = AppstoreService.change_one_app_status(app_name, zone, owner, app_status)
    action_record = dict(app_name=app_name)
    return console_response(code=change_code, action_record=action_record)


def uninstall_app_one(payload):
    """
    卸载应用
    :param payload:
    :return:
    """
    owner = payload.get("owner")
    zone = payload.get("zone")
    app_name = payload.get("app_name")
    # 根据应用采取操作
    if app_name == "waf":
        pass
    # 删除MQ数据库中的用户信息
    elif app_name == "mq":
        user_model = AccountService.get_by_owner(owner).user
        name = user_model.account.email
        sql_data = dict(
            name=name
        )
        # sql = KAFKA_MQ_DB_SQL_DELETE % sql_data
        conn, cur = mysql_connect(KAFKA_MQ_DB_HOST, KAFKA_MQ_DB_NAME, KAFKA_MQ_DB_USER, KAFKA_MQ_DB_PASSWORD, port=int(KAFKA_MQ_DB_PORT))
        code = mysql_execute(conn, cur, KAFKA_MQ_DB_SQL_DELETE, sql_data)
        if code:
            return console_response(code=1, msg=u"卸载失败")
    elif app_name == "mysql":
        pass
    elif app_name == "oracle":
        pass
    else:
        return console_response(code=1, msg=u"应用名称错误")
    # 数据库操作
    uninstall_code = AppstoreService.uninstall_one_app(app_name, zone, owner)
    action_record = dict(app_name=app_name)
    return console_response(code=uninstall_code, action_record=action_record)

#
# if __name__ == '__main__':
#     print mq_md5("521loveJJ")
