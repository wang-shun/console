# _*_ coding: utf-8 _*_

from django.utils.translation import ugettext as _

from console.common import serializers


# GET请求
class BaseGetRequestSerializer(serializers.Serializer):
    # 请求地址填充
    jumper_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"请求IP"))
    )


class CreateJumperSerializer(serializers.Serializer):

    # 用户
    owner = serializers.CharField(
        required=True,
        max_length=30,
        error_messages=serializers.CommonErrorMessages(_(u"用户"))
    )

    # zone
    zone = serializers.ChoiceField(
        required=True,
        choices=["dev", "test", "prod"],
        error_messages=serializers.CommonErrorMessages(_(u"区域"))
    )

    # 硬盘相关
    # 硬盘名称
    disk_name = serializers.CharField(
        required=False,
        default="disk_for_jumper",
        max_length=60,
        error_messages=serializers.CommonErrorMessages(_(u"硬盘名称"))
    )

    # 硬盘数量
    disk_count = serializers.IntegerField(
        required=False,
        max_value=999,
        min_value=1,
        default=1,
        error_messages=serializers.CommonErrorMessages(_(u"硬盘数量"))
    )

    # 公网IP相关
    # 公网IP类型： virtual／public
    pub_ip_type = serializers.CharField(
        required=False,
        default="virtual",
        error_messages=serializers.CommonErrorMessages(_(u"公网IP类型"))
    )

    # IP带宽
    pub_ip_bandwidth = serializers.IntegerField(
        required=False,
        default=1,
        min_value=1,
        error_messages=serializers.CommonErrorMessages(_(u"IP带宽"))
    )

    # IP计费方式
    pub_ip_billing_mode = serializers.CharField(
        required=False,
        default="BW",
        error_messages=serializers.CommonErrorMessages(_(u"IP计费方式"))
    )

    # IP名称
    pub_ip_name = serializers.CharField(
        required=False,
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u"IP名称"))
    )

    # IP付费方式
    pub_ip_charge_mode = serializers.CharField(
        required=False,
        max_length=100,
        default="pay_on_time",
        error_messages=serializers.CommonErrorMessages(_(u"IP付费方式"))
    )

    # IP计费时长
    pub_ip_package_size = serializers.IntegerField(
        required=False,
        default=0,
        error_messages=serializers.CommonErrorMessages(_(u"IP计费时长"))
    )

    # IP数量
    pub_ip_count = serializers.IntegerField(
        required=False,
        default=1,
        error_messages=serializers.CommonErrorMessages(_(u"IP数量"))
    )

    # 网络相关
    # 内网子网选择(去除了)
    pri_sub_nets = serializers.ListField(
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"内网子网"))
    )

    # 堡垒机基础信息相关
    # 堡垒机名称
    jumper_name = serializers.CharField(
        required=True,
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机名称"))
    )

    # 镜像ID
    image_type = serializers.ChoiceField(
        required=True,
        choices=["jumper"],
        error_messages=serializers.CommonErrorMessages(_(u"镜像类型"))
    )

    # 堡垒机类型ID
    jumper_type_id = serializers.ChoiceField(
        required=True,
        choices=["c1m2d20", "c2m4d20"],
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机基础配置ID"))
    )

    # 堡垒机安全组
    security_groups = serializers.ListField(
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机安全组"))
    )

    # 堡垒机登录模式
    login_mode = serializers.CharField(
        required=False,
        default="PWD",
        error_messages=serializers.CommonErrorMessages(_(u"登录方式"))
    )

    # 堡垒机密码
    login_password = serializers.CharField(
        required=False,
        default="1q2w3e",
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机密码"))
    )

    # 堡垒机密钥
    login_keypair = serializers.CharField(
        required=False,
        default="",
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机密钥"))
    )

    # 是否使用基础网络
    use_basenet = serializers.BooleanField(
        required=False,
        default=False,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机是否使用基础网络"))
    )

    # 堡垒机付费方式
    jumper_charge_mode = serializers.CharField(
        required=False,
        default="pay_on_time",
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机付费方式"))
    )

    # 堡垒机包月时长
    jumper_package_size = serializers.IntegerField(
        required=False,
        default=0,
        error_messages=serializers.CommonErrorMessages(_(u"包月时长"))
    )

    # 堡垒机数量
    jumper_count = serializers.IntegerField(
        required=False,
        default=1,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机数量"))
    )

    # 堡垒机所属集群
    availability_zone = serializers.CharField(
        required=True,
        max_length=200,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机所属集群"))
    )


class ListJumperInfoSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"用户"))
    )

    zone = serializers.ChoiceField(
        required=True,
        choices=["dev", "test", "prod"],
        error_messages=serializers.CommonErrorMessages(_(u"区域"))
    )


class BindJumperPubIpSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True,
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u"用户"))
    )

    zone = serializers.ChoiceField(
        required=True,
        choices=["dev", "test", "prod"],
        error_messages=serializers.CommonErrorMessages(_(u"区域"))
    )

    jumper_id = serializers.CharField(
        required=True,
        max_length=200,
        error_messages=serializers.CommonErrorMessages(_(u"主机ID"))
    )

    ip_id = serializers.CharField(
        required=True,
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u"IP_ID"))
    )

    # TODO: 二期需修改
    pub_ip_type = serializers.CharField(
        required=False,
        max_length=100,
        default="virtual",
        error_messages=serializers.CommonErrorMessages(_(u"IP类型"))
    )


class DeleteJumperSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"用户"))
    )

    zone = serializers.ChoiceField(
        required=True,
        choices=["dev", "test", "prod"],
        error_messages=serializers.CommonErrorMessages(_(u"区域"))
    )

    jumpers_id = serializers.ListField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机ID"))
    )

    isSuperUser = serializers.BooleanField(
        required=False,
        default=False
    )


class DropJumperSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_('用户'))
    )

    zone = serializers.ChoiceField(
        required=True,
        choices=['dev', 'test', 'prod'],
        error_messages=serializers.CommonErrorMessages(_('区域'))
    )

    jumper_ids = serializers.ListField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_('堡垒机ID'))
    )

    isSuperUser = serializers.BooleanField(
        required=False,
        default=False
    )


class ListJumperJoinableHostSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"用户ID"))
    )

    zone = serializers.ChoiceField(
        required=True,
        choices=["dev", "test", "prod"],
        error_messages=serializers.CommonErrorMessages(_(u"区域"))
    )


class ListJumperJoinedHostSerializer(serializers.Serializer):
    jumper_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机IP"))
    )


# 新建主机
class NewHostSerializer(serializers.Serializer):
    # 所有者
    owner = serializers.CharField(
        required=True,
        max_length=30,
        error_messages=serializers.CommonErrorMessages(_(u"用户"))
    )

    # zone
    zone = serializers.ChoiceField(
        required=True,
        choices=["dev", "test", "prod"],
        error_messages=serializers.CommonErrorMessages(_(u"区域"))
    )

    # 堡垒机IP
    jumper_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机IP"))
    )
    # 主机ID
    instance_id = serializers.CharField(
        required=True,
        max_length=30,
        error_messages=serializers.CommonErrorMessages(_(u"主机ID"))
    )

    # 主机名
    instance_name = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"主机名称"))
    )

    # 子网ID
    # net_id = serializers.ListField(
    #     required=True,
    #     error_messages=serializers.CommonErrorMessages(_(u"子网ID"))
    # )

    # rdp端口
    rdp_port = serializers.IntegerField(
        required=True,
        max_value=65536,
        error_messages=serializers.CommonErrorMessages(_(u"rdp端口号"))
    )

    # ssh端口
    ssh_port = serializers.IntegerField(
        required=True,
        max_value=65536,
        error_messages=serializers.CommonErrorMessages(_(u"ssh端口号"))
    )

    # rdp键盘记录
    enable_keyboard_record = serializers.BooleanField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"是否启用rdp键盘记录"))
    )

    # rdp打印机／驱动器映射
    enable_disk_redirection = serializers.BooleanField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"是否启用rdp打印机／驱动器映射"))
    )

    # rdp剪切板
    enable_clipboard = serializers.BooleanField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"是否启用rdp剪切板"))
    )


class ChangeJumperHostInfoSerializer(serializers.Serializer):
    jumper_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机IP"))
    )

    host_id = serializers.IntegerField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"主机ID"))
    )

    enable = serializers.BooleanField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"主机状态"))
    )

    # rdp端口
    rdp_port = serializers.IntegerField(
        required=True,
        max_value=65536,
        error_messages=serializers.CommonErrorMessages(_(u"rdp端口号"))
    )

    # ssh端口
    ssh_port = serializers.IntegerField(
        required=True,
        max_value=65536,
        error_messages=serializers.CommonErrorMessages(_(u"ssh端口号"))
    )

    # rdp键盘记录
    enable_keyboard_record = serializers.BooleanField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"是否启用rdp键盘记录"))
    )

    # rdp打印机／驱动器映射
    enable_disk_redirection = serializers.BooleanField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"是否启用rdp打印机／驱动器映射"))
    )

    # rdp剪切板
    enable_clipboard = serializers.BooleanField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"是否启用rdp剪切板"))
    )


class ListHostsSerializer(serializers.Serializer):
    # 堡垒机IP
    jumper_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机IP"))
    )

    # 堡垒机ID
    jumper_id = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机ID"))
    )


class RemoveJumperHostSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"用户"))
    )

    zone = serializers.ChoiceField(
        required=True,
        choices=["dev", "test", "prod"],
        error_messages=serializers.CommonErrorMessages(_(u"区域"))
    )

    jumper_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机IP"))
    )

    host_ids = serializers.ListField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"主机ID"))
    )


# 添加主机账户
class AddHostAccountSerializer(serializers.Serializer):

    # 堡垒机IP
    jumper_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机IP"))
    )

    # 主机ID
    host_id = serializers.IntegerField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"主机ID"))
    )

    # 账户名
    account_name = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"账户名"))
    )

    # 账户密码
    account_password = serializers.CharField(
        required=False,
        default=""
    )

    # 登录方式
    auth_mode = serializers.ChoiceField(
        choices=["autoLogin", "manualLogin"],
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"登录方式"))
    )

    # 用户协议
    protocol = serializers.ChoiceField(
        choices=["RDP", "SSH"],
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"用户协议"))
    )


# 主机账号列表
class ListAllAccountSerializer(serializers.Serializer):
    # jumper_ip
    jumper_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机IP"))
    )

    # host_id
    host_id = serializers.IntegerField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"host id"))
    )


# 修改主机账户
class ChangeJumperAccountInfoSerializer(serializers.Serializer):
    jumper_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机IP"))
    )

    host_id = serializers.IntegerField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"主机ID"))
    )

    account_id = serializers.IntegerField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"账户ID"))
    )

    protocol = serializers.ChoiceField(
        choices=["SSH", "RDP"],
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"协议"))
    )

    auth_mode = serializers.ChoiceField(
        choices=["autoLogin", "manualLogin"],
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"登录方式"))
    )

    account_name = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"用户名"))
    )

    password = serializers.CharField(
        required=False,
        default="",
        error_messages=serializers.CommonErrorMessages(_(u"密码"))
    )


# 移除主机账户
class RemoveJumperHostAccountSerializer(serializers.Serializer):
    jumper_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机IP"))
    )

    host_id = serializers.IntegerField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"主机ID"))
    )

    account_ids = serializers.ListField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"账户ID"))
    )


# 授权用户登录
class AddAuthorizationUserSerializer(serializers.Serializer):
    # 堡垒机IP
    jumper_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机IP"))
    )

    # 主机ID
    host_id = serializers.IntegerField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"主机ID"))
    )

    # 账户ID
    account_id = serializers.IntegerField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"账户ID"))
    )

    account_name = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"用户名"))
    )

    # 协议
    protocol = serializers.ChoiceField(
        choices=["SSH", "RDP"],
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"协议"))
    )

    # 登录模式
    auth_mode = serializers.CharField(
        required=True,
        max_length=50,
        error_messages=serializers.CommonErrorMessages(_(u"登录模式"))
    )

    # 用户s [(username, departmentId, nickname, password, roleName), (username1)]
    user_ids = serializers.ListField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"授权用户列表"))
    )


class AddJumperAuthorizationUserOrDetachSerializer(serializers.Serializer):
    jumper_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机IP"))
    )

    host_id = serializers.IntegerField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"主机ID"))
    )

    data = serializers.ListField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"操作详情"))
    )


# 已授权用户(账户名+登录模式+协议)
class ListAuthorizationUserSerializer(serializers.Serializer):
    # jumper_ip
    jumper_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机IP"))
    )

    # host_id
    host_id = serializers.IntegerField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"主机ID"))
    )


# 某主机所有账户下已授权用户(主机)
class ListUsersOfHostSerializer(serializers.Serializer):
    # jumper_ip
    jumper_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机IP"))
    )

    # host_id
    host_id = serializers.IntegerField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"主机ID"))
    )


# 取消用户授权
class DetachJumperAuthorizationUserSerializer(serializers.Serializer):
    jumper_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机IP"))
    )

    host_id = serializers.IntegerField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"主机ID"))
    )

    user_ids = serializers.ListField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"用户ID"))
    )

    rule_ids = serializers.ListField(
        required=False
    )


# 获取全部历史会话
class ListJumperSessionHistorySerializer(serializers.Serializer):
    jumper_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机IP"))
    )

    host_ip = serializers.IPAddressField(
        required=False
    )

    user_name = serializers.CharField(
        required=False
    )

    protocol = serializers.ChoiceField(
        choices=["RDP", "SSH"],
        required=False
    )


# 获取会话详情
class ShowJumperSessionDetailSerializer(serializers.Serializer):
    jumper_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机IP"))
    )

    session_id = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"会话ID"))
    )


class PlayJumperSessionAddressSerianlizer(serializers.Serializer):
    jumper_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机IP"))
    )

    session_id = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"会话ID"))
    )


class ListJumperSessionEventSerializer(serializers.Serializer):
    jumper_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机IP"))
    )

    content_key = serializers.CharField(
        required=False
    )


class ShowJumperEventDetailSerializer(serializers.Serializer):
    jumper_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"堡垒机IP"))
    )

    event_id = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"事件ID"))
    )


class ShowJumperHostAllSudoSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"用户"))
    )

    zone = serializers.ChoiceField(
        required=True,
        choices=["dev", "test", "prod"],
        error_messages=serializers.CommonErrorMessages(_(u"区域"))
    )

    app_system_id = serializers.IntegerField(
        required=False
    )

    compute_resource = serializers.CharField(
        required=False
    )


class ShowJumperSessionTypeSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"用户"))
    )

    zone = serializers.ChoiceField(
        required=True,
        choices=["dev", "test", "prod"],
        error_messages=serializers.CommonErrorMessages(_(u"区域"))
    )

    app_system_id = serializers.IntegerField(
        required=False
    )

    compute_resource = serializers.CharField(
        required=False
    )


class ListJumperHostEventSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"用户"))
    )

    zone = serializers.ChoiceField(
        required=True,
        choices=["dev", "test", "prod"],
        error_messages=serializers.CommonErrorMessages(_(u"区域"))
    )

    app_system_id = serializers.IntegerField(
        required=False
    )

    compute_resource = serializers.CharField(
        required=False
    )

    time_for_show = serializers.ChoiceField(
        choices=["seven_days", "thirty_days", "ninety_days"],
        required=False
    )

    department_name = serializers.CharField(
        required=False
    )

    event_type = serializers.ChoiceField(
        choices=[""],
        required=False
    )

    user_name = serializers.CharField(
        required=False
    )

    work_id = serializers.IntegerField(
        required=False
    )
