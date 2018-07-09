# _*_ coding: utf-8 _*_

from console.common import serializers


class SmcBaseSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"用户")
    )

    zone = serializers.ChoiceField(
        required=True,
        choices=["dev", "prod", "test"],
        error_messages=serializers.CommonErrorMessages(u"分区")
    )


class ListWafInfoSerializer(SmcBaseSerializer):
    """
    waf列表
    """
    page_index = serializers.IntegerField(
        required=False,
        default=1
    )

    page_size = serializers.IntegerField(
        default=0,
        required=False
    )


class ListWafNodesSerializer(SmcBaseSerializer):
    """
    waf节点信息
    """
    page_index = serializers.IntegerField(
        required=False
    )

    page_size = serializers.IntegerField(
        default=0,
        required=False
    )


class CreateWafServiceSerializer(SmcBaseSerializer):
    """
    增加站点
    """
    domain = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"站点域名")
    )

    ips = serializers.ListField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"站点回源IP")
    )


class DeleteWafServiceSerializer(SmcBaseSerializer):
    """
    彻底删除站点
    """
    waf_id = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"waf_id")
    )


class WafBaseSerializer(serializers.Serializer):
    """
    每秒查询频率、HTTP连接数、CPU使用率、内存使用率
    请求次数统计、响应时间统计、安全防护日志
    基础防护、HTTP协议防护、防错误信息泄露、WAF规则
    url白名单
    系统信息
    """
    owner = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"用户")
    )

    zone = serializers.ChoiceField(
        required=True,
        choices=["dev", "prod", "test"],
        error_messages=serializers.CommonErrorMessages(u"分区")
    )

    waf_id = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"waf_id")
    )

    smc_ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"smc_ip")
    )

    page_index = serializers.IntegerField(
        default=1,
        required=False
    )

    page_size = serializers.IntegerField(
        default=0,
        required=False
    )


class ListWafAttacklogSerializer(WafBaseSerializer):
    """
    获取攻击日志
    """
    attack_type = serializers.ChoiceField(
        required=False,
        choices=["XSS", "CC", "Acl", "CSRF", "Http-Protocol", "Waf-Rule", "Http-Status",
                 "Scanner", "Collision", "SQL", "Hotlink", "Directory-Traversal", "All"],
        error_messages=serializers.CommonErrorMessages(u"攻击类型")
    )

    process_action = serializers.ChoiceField(
        required=False,
        choices=["pass", "notify", "deny", "captcha", "all"],
        error_messages=serializers.CommonErrorMessages(u"防护动作")
    )


class DescribeWafCookieSerializer(WafBaseSerializer):
    """
    cookie防护列表
    """
    type = serializers.ChoiceField(
        required=True,
        choices=["cookie"],
        error_messages=serializers.CommonErrorMessages(u"查询类型")
    )


class CreateWafCookieSerializer(DescribeWafCookieSerializer):
    """
    新建cookie防护
    """
    url = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"url")
    )

    httponly = serializers.BooleanField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"http_only")
    )

    matchtype = serializers.ChoiceField(
        required=True,
        choices=["equ", "cnt", "regex", "prefix"],
        error_messages=serializers.CommonErrorMessages(u"关系")
    )


class DeleteWafCookieSerializer(DescribeWafCookieSerializer):
    """
    删除cookie防护
    """
    url = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"url")
    )


class DescribeWafSeniorSerializer(WafBaseSerializer):
    """
    高级防护列表、监控列表、记录列表
    """
    type = serializers.ChoiceField(
        required=True,
        choices=["cc", "collision"],
        error_messages=serializers.CommonErrorMessages(u"类型")
    )


class CreateWafSeniorSerializer(DescribeWafSeniorSerializer):
    """
    新建高级防护
    """
    url = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"url")
    )

    time = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"统计时间")
    )

    blocktime = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"阻断时间")
    )

    threshold = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"阈值")
    )

    process_action = serializers.ChoiceField(
        required=True,
        choices=["pass", "notify", "deny", "captcha", "all"],
        error_messages=serializers.CommonErrorMessages(u"防护动作")
    )

    matchtype = serializers.ChoiceField(
        required=True,
        choices=["equ", "cnt", "regex", "prefix"],
        error_messages=serializers.CommonErrorMessages(u"关系")
    )


class DeleteSeniorSerializer(DescribeWafSeniorSerializer):
    """
    删除高级防护规则
    """
    url = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"url")
    )


class DeleteWafSenioripSerializer(DescribeWafSeniorSerializer):
    """
    删除／清除高级防护监控
    """
    ip = serializers.IPAddressField(
        required=False,
        default="all"
    )


class DescribeWafIplistSerializer(WafBaseSerializer):
    """
    黑白名单列表
    """
    type = serializers.ChoiceField(
        required=True,
        choices=["blackip", "whiteip"],
        error_messages=serializers.CommonErrorMessages(u"类型")
    )


class ChangeWafIplistSerializer(DescribeWafIplistSerializer):
    """
    新建IP黑／白名单、删除IP黑/白名单
    """
    ip = serializers.IPAddressField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"IP")
    )


class CreateWafUrllistSerializer(WafBaseSerializer):
    """
    新建url白名单
    """
    matchtype = serializers.ChoiceField(
        required=True,
        choices=["equ", "cnt", "regex", "prefix"],
        error_messages=serializers.CommonErrorMessages(u"关系")
    )

    url = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"url")
    )


class DeleteWafUrllistSerializer(WafBaseSerializer):
    """
    删除url白名单
    """
    url = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"url")
    )
