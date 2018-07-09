# _*_ coding: utf-8 _*_

import json
import requests


POST_WAF_RELEASESEAUTH = "http://%(IP)s/waf/releaseSeAuth?token=%(TOKEN)s"
waf_smc_token = "OpbAG26xIs0HRGVGhsS+FduJYL5LMxo/BKmn41reE1A3Up+F8i+dUXHFfc7zz6Zb"


def base_request(base_url, url_data, content_type="application/json", req_type="get", req_data=None):
    """
    基础请求
    :param base_url: 基础请求地址
    :param url_data: 填充请求地址里的参数
    :param content_type: 数据格式
    :param req_type: 请求方式
    :param req_data: 请求数据（用于post和put）
    :return: 操作成功时，返回(0, 内容)，操作失败时，返回(原始状态码，错误信息)
    """
    req_session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
               "Accept": content_type}
    url = base_url % url_data
    req_session.headers = headers
    if req_type == "get":
        try:
            resp = req_session.get(url=url, verify=False)
            status = resp.status_code
            if status == 200:
                content = json.loads(resp.text, encoding="utf-8")
                return 0, content
            elif status:
                return status, resp.text
            else:
                return status, resp.status
        except Exception as excep:
            return None, excep

    elif req_type == "post":
        try:
            headers["Content-Type"] = content_type
            req_session.headers = headers
            resp = req_session.post(url=url, data=json.dumps(req_data))
            status = resp.status_code
            if status == 200:
                content = resp.text if resp.text else ""
                return 0, content
            elif status:
                content = resp.text if resp.text else ""
                return status, content
            else:
                return status, resp.status
        except Exception as excep:
            return None, excep
    return None, 1


# if __name__ == '__main__':
#     url_data = dict(
#         IP="172.31.3.222",
#         TOKEN=waf_smc_token
#     )
#     req_data = dict(
#         id="-1284349292_49_1536527406",
#         wafStatus=""
#     )
#     base_request(POST_WAF_RELEASESEAUTH, )
