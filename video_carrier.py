"""
    从YouTube下载视频，并进行处理，上传至Bilibili
    作者：自动工具哥

    注意安装项目依赖:
        ffmpeg https://ffmpeg.org/
        ImageMagick https://imagemagick.org/

    三方库安装:
    pip install youtube-dl ffmpeg-python pysrt moviepy
"""
import requests
import json

import youtube_dl
import ffmpeg

import xf_mt
import xf_lfasr
import pysrt
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip

# 科大讯飞平台的 appid
XF_APP_ID = ''
# 科大讯飞语音转写的 SecretKey
XF_LFASR_SECRET_KEY = ''
# 科大讯飞机器翻译 APISecret、APIKey
XF_MT_API_SECRET = ''
XF_MT_API_KEY = ''


def gen_url(video_id):
    return 'https://www.youtube.com/watch?v=' + video_id


def video_info(video_id, proxy=None):
    """
    获取YouTube上视频的信息
    :param video_id: 视频ID
    :param proxy: 代理服务器地址，可选
    :return: 视频信息
    """
    params = {'proxy': proxy} if proxy else {}
    return youtube_dl.YoutubeDL(params).extract_info(gen_url(video_id), download=False)


def download_video(video_id, proxy=None):
    """
    下载视频到本地
    :param video_id: Video ID
    :param proxy: 代理服务器地址，可选
    :return: 无
    """
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'videos/%(id)s.%(ext)s'
    }
    if proxy:
        ydl_opts['proxy'] = proxy

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([gen_url(video_id)])


def file_name(file):
    return file[:file.rindex('.')]


def file_path(file):
    return 'videos/' + file


def speech_to_text(file, duration):
    """
    调用讯飞语音转写API完成语音识别成为文本
    :param file: 语音文件相名
    :param duration: 音频时长，单位毫秒
    :return: 识别结果
    """
    api = xf_lfasr.RequestApi(
        appid=XF_APP_ID,
        secret_key=XF_LFASR_SECRET_KEY,
        upload_file_path=file_path(file)
    )
    return api.recognize(duration)


def translate(text, from_lang='en', to_lang='cn'):
    """
    翻译
    :param text: 待翻译文本列表
    :param from_lang: 原语言
    :param to_lang: 目标语言
    :return: 无
    """
    for item in text:
        item['text'] = xf_mt.translate(
            XF_APP_ID, XF_MT_API_SECRET, XF_MT_API_KEY, item['text'], from_lang, to_lang)


def text_to_srt(text, file):
    """
    讯飞识别完的文本转为字幕文件(srt)
    :param text: 文本(携带每一句文本的开始和结束时间)
    :param file: srt文件名
    :return:
    """
    sub_titles = []
    for i, item in enumerate(text):
        sub_titles.append(pysrt.SubRipItem(
            i,
            pysrt.SubRipTime(milliseconds=int(item['begin_at'])),
            pysrt.SubRipTime(milliseconds=int(item['end_at'])),
            item['text']
        ))
    subtitle_file = pysrt.SubRipFile(sub_titles)
    subtitle_file.save(file_path(file), encoding='utf-8')


def write_srt_to_video(video_file, srt_file):
    """
    字幕文件写入到视频中进行显示
    :param video_file: 视频文件名
    :param srt_file: 字母文件名
    :return: 结果文件名
    """
    input_video = VideoFileClip(file_path(video_file))
    sub_titles = SubtitlesClip(
        file_path(srt_file),
        lambda txt: TextClip(
            txt, font='PingFang.ttc', fontsize=50, color='white', stroke_color='black',
            stroke_width=0.5, method='caption', align='South',
            size=(input_video.size[0] * 0.98, input_video.size[1] * 0.99))
    )
    final_video = CompositeVideoClip(
        [input_video, sub_titles.set_position((0.01, 0), relative=True)]
    ).set_duration(input_video.duration)
    out_file = file_name(video_file) + '_srt.mp4'
    # threads为FFmpeg处理视频时可用的线程数，根据机器的核心数进行配置
    final_video.write_videofile(file_path(out_file), audio=False, threads=8)
    return out_file


def process_video(file, **opts):
    """
    视频处理方法
    :param file: 视频文件名
    :param opts: 选项参数，解释如下
        lang
            视频语言，cn 或 en
        translate
            要翻译成的目标语言
        ratio
            视频播放速度比率，0.5表示播放速度加倍，2表示播放速度减半，可以自行设置其他值

    :return: 无
    """
    if len(opts) == 0:
        return

    name = file_name(file)
    video = ffmpeg.input(file_path(file))
    video_stream = video.video
    audio_stream = video.audio

    # 抽取音频
    ori_audio = name + '_audio.wav'
    ffmpeg.output(audio_stream, file_path(ori_audio)).run()

    # 抽取视频
    ori_video = name + '_video.mp4'
    ffmpeg.output(video_stream, file_path(ori_video)).run()

    # 音频提取文本(并翻译，如果需要的话)
    duration_ms = int(float(ffmpeg.probe(file_path(ori_audio))['streams'][0]['duration']) * 1000)
    text_result = speech_to_text(ori_audio, duration_ms)
    if opts.get('lang', 0) and opts.get('translate', 0):
        translate(text_result, opts['lang'], opts['translate'])

    # 文本转字幕
    srt_file = name + '.srt'
    text_to_srt(text_result, srt_file)

    # 字幕写入视频文件
    srt_video = write_srt_to_video(ori_video, srt_file)

    video_stream = ffmpeg.input(file_path(srt_video)).video
    if opts['ratio']:
        # 改变视频播放速度
        video_stream = ffmpeg.filter(video_stream, "setpts", str(opts['ratio']) + "*PTS")
        # 改变音频播放速度
        audio_stream = ffmpeg.filter(audio_stream, "atempo", 1 / opts['ratio'])

    # 合并音频和视频并输出
    output = ffmpeg.concat(video_stream, audio_stream, v=1, a=1)
    final_name = name + '_result.mp4'
    ffmpeg.output(output, file_path(final_name)).run()
    return final_name


def upload_to_bilibili(file, title, desc, tags):
    """
    上传视频到Bilibili，由于没有拿到 AccessToken 和 AppKey，此函数没做测试
    Bilibili开放平台地址 https://openhome.bilibili.com/

    :param file: 待上传视频名
    :param title:
    :param desc:
    :param tags:
    :return:
    """
    url = "https://api.bilibili.com/x/video/dm/create"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Your User-Agent",
        "access_token": "Bilibili开放平台 AccessToken",
        "appkey": "Bilibili开放平台 AppKey"
    }
    data = {
        "dmid": "0",
        "pid": "0",
        "cid": "0",
        "title": title,
        "desc": desc,
        "tag": ','.join(tags)
    }

    with open(file_path(file), "rb") as f:
        files = {"file": f}
        response = requests.post(url, headers=headers, data=json.dumps(data), files=files)
        print(response.json())


if __name__ == '__main__':
    # 要下载的YouTube视频的ID，在YouTube播放界面上，复制地址中的参数
    # 例如 https://www.youtube.com/watch?v=owlHiqL3nAI，则video_id = 'owlHiqL3nAI'
    video_id = 'DOa-d1G2clM'

    # 代理服务器地址
    proxy_url = 'socks5://127.0.0.1:1080/'

    # 从YouTube下载视频到本地
    download_video(video_id, proxy_url)

    # 视频处理
    info = video_info(video_id, proxy_url)
    video_file = info['id'] + '.' + info['ext']
    result_file = process_video(video_file, lang='en', translate='cn', ratio=0.8)

    # 上传视频到Bilibili
    # upload_to_bilibili(result_file, '标题', '视频描述', ['标签1', '标签2'])
