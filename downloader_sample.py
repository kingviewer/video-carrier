from downloader.DownloaderFactory import DownloaderFactory

if __name__ == '__main__':
    # 抖音视频下载
    dy_down = DownloaderFactory.create_downloader('DouYin', 'BM4q1TW')
    rs = dy_down.download()
    print(rs)

    # YouTube视频下载
    # yt_down = DownloaderFactory.create_downloader(
    #     'YouTube', 'CxO9L90QvTA', 'socks5://127.0.0.1:1080/'
    # )
    # rs = yt_down.download()
    # print(rs)
