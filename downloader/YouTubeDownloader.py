import yt_dlp

from downloader.Downloader import Downloader


class YouTubeDownloader(Downloader):
    def __init__(self, video_id, proxy=None):
        super().__init__('YouTube', video_id, proxy)
        self.url = 'https://www.youtube.com/watch?v=' + video_id

    def video_info(self):
        params = {'proxy': self.proxy} if self.proxy else {}
        return yt_dlp.YoutubeDL(params).extract_info(self.url, download=False)

    def download(self):
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': 'videos/%(id)s.%(ext)s'
        }
        if self.proxy:
            ydl_opts['proxy'] = self.proxy
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])

        info = self.video_info()
        return {'title': info['title'], 'file': f"{info['id']}.{info['ext']}"}


if __name__ == "__main__":
    d = YouTubeDownloader('bWM633v77-I', 'socks5://127.0.0.1:1080/')
    rs = d.download()
    print(rs)
