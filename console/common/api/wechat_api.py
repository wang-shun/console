# encoding: utf-8
import gevent
from gevent import monkey
from gevent.timeout import Timeout

monkey.patch_all()
import urllib2
import json
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from console.common.logger import getLogger


logger = getLogger(__name__)


SEND_MSG_TIMEOUT = 3


class WechatAPI(object):
    def __init__(self, token, encoding_aes_key, corp_id, secrect, agent_id):
        self.token = token
        self.encoding_aes_key = encoding_aes_key
        self.corp_id = corp_id
        self.secrect = secrect
        self.agent_id = agent_id

    # 获取access_token，用于之后的一些主动操作，例如主动给某个用户发送消息
    def get_access_token(self):
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=" + self.corp_id + "&corpsecret=" + self.secrect
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        access_token = json.loads(response.read())["access_token"]
        return access_token

    # to_user_name是一个列表，可以给多个用户发，如果"@all"表示给所有用户发消息
    def send_message(self, to_user_name, title, msg, timeout=None):
        touser = '|'.join(to_user_name) if len(to_user_name) else "test"
        logger.debug("Ticket Send To: %s" % to_user_name)
        logger.debug("Message Title: %s" % title)
        logger.debug("Message Content: %s" % msg)
        logger.debug("===========================")
        logger.debug(type(title))
        logger.debug(type(msg))

        logger.debug(isinstance(title, unicode))
        logger.debug(isinstance(msg, unicode))

        if isinstance(title, unicode):
            title = title.encode("utf-8")

        if isinstance(msg, unicode):
            msg = msg.encode("utf-8")

        logger.debug(type(title))
        logger.debug(type(msg))

        body = {
            'agentid': self.agent_id,
            'touser': touser,
            'msgtype': 'news',
            'news': {
                "articles": [{
                    'title': title,
                    'description': msg
                }]
            },
            'safe': '0'
        }
        logger.debug("The wechat send body content: %s" % body)

        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + self.get_access_token()
        data = json.dumps(body, ensure_ascii=False)
        logger.debug(data)
        req = urllib2.Request(url, data)
        logger.debug(req.__dict__)
        req.add_header('Content-Type', 'application/json')
        _timeout = timeout or SEND_MSG_TIMEOUT
        with gevent.Timeout(_timeout, Timeout):
            response = urllib2.urlopen(req)
            res = response.read()
            logger.debug(res)
            return res

secret = "C-iU0CxqP-p4HlghOwsx-WAVNezpej4dy4uzfK_hbytxaqmoYc8DBeVOeVNc_Qts"
token = "d78qRYadHXqodcIHVG6"
encoding_aes_key = "JggEi7IHuUxjHSU9iBdRlfdsDORUFCrpUBhATVd4DM1"
corp_id = "wxf3a0725934f1b55c"
# 微信平台的微信平台id
agent_id = '14'

wechat_api = WechatAPI(token, encoding_aes_key, corp_id, secret, agent_id)


if __name__ == '__main__':
    # 下面这些是我们微信公众号的配置，不用改，直接用
    secret = "C-iU0CxqP-p4HlghOwsx-WAVNezpej4dy4uzfK_hbytxaqmoYc8DBeVOeVNc_Qts"
    token = "d78qRYadHXqodcIHVG6"
    encoding_aes_key = "JggEi7IHuUxjHSU9iBdRlfdsDORUFCrpUBhATVd4DM1"
    corp_id = "wxf3a0725934f1b55c"
    # 微信平台的报警应用id
    agent_id = '6'
    api = WechatAPI(token, encoding_aes_key, corp_id, secret, agent_id)
    ans = api.send_message(["chenlei256160"], "Test Message")
    print ans
