# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import json
import os
import time
import requests
import urllib

lfasr_host = 'https://raasr.xfyun.cn/v2/api'
# 请求的接口名
api_upload = '/upload'
api_get_result = '/getResult'


class RequestApi(object):
    def __init__(self, appid, secret_key, upload_file_path):
        self.appid = appid
        self.secret_key = secret_key
        self.upload_file_path = upload_file_path
        self.ts = str(int(time.time()))
        self.signa = self.get_signa()

    def get_signa(self):
        appid = self.appid
        secret_key = self.secret_key
        m2 = hashlib.md5()
        m2.update((appid + self.ts).encode('utf-8'))
        md5 = m2.hexdigest()
        md5 = bytes(md5, encoding='utf-8')
        # 以secret_key为key, 上面的md5为msg， 使用hashlib.sha1加密结果为signa
        signa = hmac.new(secret_key.encode('utf-8'), md5, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        return signa

    def upload(self, duration, src_lang='cn', translate_lang=None):
        print("上传部分：")
        upload_file_path = self.upload_file_path
        file_len = os.path.getsize(upload_file_path)
        file_name = os.path.basename(upload_file_path)

        param_dict = {}
        param_dict['appId'] = self.appid
        param_dict['signa'] = self.signa
        param_dict['ts'] = self.ts
        param_dict["fileSize"] = file_len
        param_dict["fileName"] = file_name
        param_dict["duration"] = str(duration)
        param_dict["language"] = src_lang
        if translate_lang:
            param_dict["transLanguage"] = translate_lang
            param_dict["transMode"] = '2'
        print("upload参数：", param_dict)
        data = open(upload_file_path, 'rb').read(file_len)

        response = requests.post(url=lfasr_host + api_upload + "?" + urllib.parse.urlencode(param_dict),
                                 headers={"Content-type": "application/json"}, data=data)
        print("upload_url:", response.request.url)
        result = json.loads(response.text)
        print("upload resp:", result)
        return result

    def recognize(self, duration):
        upload_rs = self.upload(duration)
        order_id = upload_rs['content']['orderId']
        rs = self.get_result(order_id)
        return rs

    def parse_result(self, rs):
        result = []
        if not rs:
            return result

        if rs['content'].get('orderResult', 0):
            order_result = json.loads(rs['content']['orderResult'])
            for sentence in order_result['lattice']:
                item = json.loads(sentence['json_1best'])['st']
                result.append({
                    'begin_at': item['bg'],
                    'end_at': item['ed'],
                    'role_id': item['rl'],
                    'text': ' '.join(map(lambda x: x['cw'][0]['w'].strip(), item['rt'][0]['ws']))
                })
        return result

    def get_result(self, order_id):
        param_dict = {
            'appId': self.appid,
            'signa': self.signa,
            'ts': self.ts,
            'orderId': order_id,
            'resultType': 'transfer'
        }

        print("查询结果：")
        print("get result参数：", param_dict)
        # 建议使用回调的方式查询结果，查询接口有请求频率限制
        while True:
            response = requests.post(
                url=lfasr_host + api_get_result + "?" + urllib.parse.urlencode(param_dict),
                headers={"Content-type": "application/json"})
            print("查询中······")
            result = json.loads(response.text)
            if result['content']['orderInfo']['status'] != 3:
                break
            time.sleep(5)
        return self.parse_result(result)
