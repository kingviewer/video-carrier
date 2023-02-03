import requests
import re
import json
import random
import string
from downloader.Downloader import Downloader


def rand_str(length: int):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for x in range(length))


class DouYinDownloader(Downloader):
    def __init__(self, video_id):
        super().__init__('DouYin', video_id, None)

    def download(self):
        r = requests.get('https://v.douyin.com/' + self.video_id)
        key = re.findall(r'video/(\d+)?', str(r.url))[0]
        jx_url = f'https://www.iesdouyin.com/aweme/v1/web/aweme/detail/?aweme_id={key}&aid=1128&version_name=23.5.0&device_platform=android&os_version=2333'
        headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66',
            'Cookie': 'msToken=%s' % rand_str(107)
        }
        js = json.loads(requests.get(url=jx_url, headers=headers).text)
        video_url = js['aweme_detail']['video']['play_addr']['url_list'][0]
        req = requests.get(url=video_url, headers=headers)
        with open(f"videos/{self.video_id}.mp4", 'wb') as f:
            f.write(req.content)
        return {'title': js['aweme_detail']['desc'], 'file': f"{self.video_id}.mp4"}
