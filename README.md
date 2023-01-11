# 视频搬运

视频搬运工具，从YouTube搬运视频到Bilibili

项目依赖
-------------------
* ffmpeg https://ffmpeg.org/
* ImageMagick https://imagemagick.org/

三方库安装
-------------------
* pip install youtube-dl ffmpeg-python pysrt moviepy

科大讯飞平台API https://www.xfyun.cn/
-------------------
* 创建应用，复制APPID，作为 video_carrier.py 25行 XF_APP_ID 的值
* 语音识别->语音转写，开通，复制 SecretKey，作为 video_carrier.py 27行 XF_LFASR_SECRET_KEY 的值
* 自然语言处理->及其翻译，开通，复制 APISecret， 作为 video_carrier.py 29行 XF_MT_API_SECRET 的值； 复制 APIKey，作为 video_carrier.py 30行 XF_MT_API_KEY 的值

关于科学上网
-------------------
要访问YouTube和ChatGPT的话，需要科学上网。节点最好使用付费节点，一些区域ChatGPT是不允许访问的。我使用的是韩国节点，自建ShadowSocks服务器。

自建服务器
服务器可以使用亚马逊 https://signin.aws.amazon.com/ 的免费服务器；
Shadowsocks服务器部署参考 https://github.com/teddysun/shadowsocks_install

关于ChatGPT账号注册
-------------------
* 注册过程中需要科学上网，账号注册地址 https://openai.com/
* 注册过程中境外手机号问题，可以使用 https://sms-activate.org/ 提供的虚拟号码接收短信。我选择的是印度号码，大概消费1元人民币左右（0.16卢布），可使用支付宝支付