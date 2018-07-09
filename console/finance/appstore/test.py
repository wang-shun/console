# _*_ coding: utf-8 _*_
import hashlib
import pymysql
import logging


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


KAFKA_MQ_DB_SQL_INSERT = "INSERT INTO sec_user (module_id, name, username, password, user_type, version) VALUES " \
                         "(%(module_id)s, %(name)s, %(username)s, %(password)s, %(user_type)s, %(version)s);"
KAFKA_MQ_DB_SQL_DELETE = "DELETE FROM sec_user WHERE name = %(name)s;"


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


def mysql_insert(conn, cur, sql, data):
    """
    插入数据库
    :param conn:
    :param cur:
    :param sql:
    :param data:
    :return:
    """
    conn, cur = conn, cur
    try:
        cur.execute(sql, data)
        logging.debug("insert mq database success, data is: %s", data)
        return 0
    except Exception as exc:
        logging.error(exc)
        logging.error("insert mq database error, sql is %s, data is: %s", sql, data)
        return 1


KAFKA_MQ_DB_HOST = "172.31.1.60"
KAFKA_MQ_DB_NAME = "tamboo_manager"
KAFKA_MQ_DB_USER = "root"
KAFKA_MQ_DB_PASSWORD = "123456"
KAFKA_MQ_DB_PORT = 3306


def insert_mysql(user_name, password):
    name = user_name
    md5_pwd = mq_md5(password)
    user_type = "role_user"
    version = int(0)

    sql_data = dict(
        module_id=int(1),
        name=name,
        username=user_name,
        password=md5_pwd,
        user_type=user_type,
        version=version
    )

    conn, cur = mysql_connect(KAFKA_MQ_DB_HOST, KAFKA_MQ_DB_NAME, KAFKA_MQ_DB_USER, KAFKA_MQ_DB_PASSWORD, port=KAFKA_MQ_DB_PORT)
    code = mysql_insert(conn, cur, KAFKA_MQ_DB_SQL_INSERT, sql_data)
    if code == 1:
        return 1
    return 0


def delete_mysql(username):
    name = username
    sql_data = dict(
        name=name
    )
    conn, cur = mysql_connect(KAFKA_MQ_DB_HOST, KAFKA_MQ_DB_NAME, KAFKA_MQ_DB_USER, KAFKA_MQ_DB_PASSWORD,
                              port=KAFKA_MQ_DB_PORT)
    code = mysql_insert(conn, cur, KAFKA_MQ_DB_SQL_DELETE, sql_data)
    if code == 1:
        return 1
    return 0


# if __name__ == '__main__':
    # name = "zhangjie"
    # md5_pwd = mq_md5(name)
    # user_type = "role_user"
    # version = 0
    # sql_data = dict(
    #     module_id=1,
    #     name=name,
    #     username=name,
    #     password=md5_pwd,
    #     user_type=user_type,
    #     version=version
    # )
    #
    # print KAFKA_MQ_DB_SQL_INSERT % sql_data
    # print delete_mysql("hello")
