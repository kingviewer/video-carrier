from downloader.YouTubeDownloader import YouTubeDownloader
from downloader.DouYinDownloader import DouYinDownloader


class DownloaderFactory:
    @staticmethod
    def create_downloader(plat, video_id, proxy=None):
        if plat.lower() == 'youtube':
            return YouTubeDownloader(video_id, proxy)
        if plat.lower() == 'douyin':
            return DouYinDownloader(video_id)
