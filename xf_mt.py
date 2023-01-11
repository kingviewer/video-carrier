"""
    科大讯飞机器翻译

    1.机器翻译2.0，请填写在讯飞开放平台-控制台-对应能力页面获取的APPID、APISecret、APIKey。
    2.目前仅支持中文与其他语种的互译，不包含中文的两个语种之间不能直接翻译。
    3.翻译文本不能超过5000个字符，即汉语不超过15000个字节，英文不超过5000个字节。
    4.此接口调用返回时长上有优化、通过个性化术语资源使用可以做到词语个性化翻译、后面会支持更多的翻译语种。
"""
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import json
import requests


class AssembleHeaderException(Exception):
    def __init__(self, msg):
        self.message = msg


class Url:
    def __init__(self, host, path, schema):
        self.host = host
        self.path = path
        self.schema = schema
        pass


# calculate sha256 and encode to base64
def sha256base64(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    digest = base64.b64encode(sha256.digest()).decode(encoding='utf-8')
    return digest


def parse_url(requset_url):
    stidx = requset_url.index("://")
    host = requset_url[stidx + 3:]
    schema = requset_url[:stidx + 3]
    edidx = host.index("/")
    if edidx <= 0:
        raise AssembleHeaderException("invalid request url:" + requset_url)
    path = host[edidx:]
    host = host[:edidx]
    u = Url(host, path, schema)
    return u


# build websocket auth request url
def assemble_ws_auth_url(requset_url, method="POST", api_key="", api_secret=""):
    u = parse_url(requset_url)
    host = u.host
    path = u.path
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))
    signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha256).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
    authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
        api_key, "hmac-sha256", "host date request-line", signature_sha)
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    values = {
        "host": host,
        "date": date,
        "authorization": authorization
    }

    return requset_url + "?" + urlencode(values)


def translate(appid, api_secret, api_key, text, from_lang='en', to_lang='cn'):
    url = 'https://itrans.xf-yun.com/v1/its'
    body = {
        "header": {
            "app_id": appid,
            "status": 3
        },
        "parameter": {
            "its": {
                "from": from_lang,
                "to": to_lang,
                "result": {}
            }
        },
        "payload": {
            "input_data": {
                "encoding": "utf8",
                "status": 3,
                "text": base64.b64encode(text.encode("utf-8")).decode('utf-8')
            }
        }
    }
    request_url = assemble_ws_auth_url(url, "POST", api_key, api_secret)
    headers = {'content-type': "application/json", 'host': 'itrans.xf-yun.com', 'app_id': appid}
    response = requests.post(request_url, data=json.dumps(body), headers=headers)
    tmp_result = json.loads(response.content.decode())
    result = json.loads(base64.b64decode(tmp_result['payload']['result']['text']).decode())
    print(result)
    return result['trans_result']['dst']
