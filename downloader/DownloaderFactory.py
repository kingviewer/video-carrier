from downloader.YouTubeDownloader import YouTubeDownloader
from downloader.DouYinDownloader import DouYinDownloader


class DownloaderFactory:
    @staticmethod
    def create_downloader(plat, video_id, proxy=None):
        """
        生成下载器
        :param plat: 平台，目前支持 DouYin(抖音)、YouTube(油管)
        :param video_id:
        :param proxy:
        :return: 下载器对象
        """
        if plat.lower() == 'youtube':
            return YouTubeDownloader(video_id, proxy)
        if plat.lower() == 'douyin':
            return DouYinDownloader(video_id)
