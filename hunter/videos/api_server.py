# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/9/9 0:10
# @Version     : Python 3.8.5
from flask import Flask, request, jsonify

from public import BackEndPort
from utils import LogManager
from videos import Code, VideoException
from videos.tencent_video.decrypt.get_download_url import DownloadURL

app = Flask('video_api_server')
logger = LogManager('video_api_server').file()


@app.route("/video/tencent_video/get_download_url", methods=["POST"])
def get_download_url():
    """
    @api {get} /video/tencent_video/get_download_url 获取腾讯视频下载地址
    @apiName get_download_url
    @apiVersion 0.0.1
    @apiGroup tencent_video api
    @apiParam {String} play_url 视频播放地址
    @apiSuccessExample {json} 返回示例:
    {
        "code": 10000,
        "data": {
            "play_url": "https://v.qq.com/x/cover/5y07fkhxzj48wcj/g0022cy9bdp.html",
            "download_type": "m3u8",
            "download": [
                {
                    "url": "https://apd.v.smtcdns.com/0325_g0022cy9bdp.321002.ts.m3u8?ver=4",
                    "prefix": "https://apd.v.smtcdns.com/"
                },
                {
                    "url": "https://apd.v.smtcdns.com/vipts.tc.qq.com/0325_g0022cy9bdp.321002.ts.m3u8?ver=4",
                    "prefix": "https://apd.v.smtcdns.com/vipts.tc.qq.com/"
                },
                {
                    "url": "https://apd.v.smtcdns.com/vipts.tc.qq.com/0325_g0022cy9bdp.321002.ts.m3u8?ver=4",
                    "prefix": "https://apd.v.smtcdns.com/vipts.tc.qq.com/"
                },
                {
                    "url": "https://ltsws.qq.com/0325_g0022cy9bdp.321002.ts.m3u8?ver=4",
                    "prefix": "https://ltsws.qq.com/"
                }
            ]
        },
        "message": "插入成功"
    }
    """
    try:
        play_url = request.get_json().get("play_url")
        if not play_url:
            return jsonify({"code": Code.ParameterError, "message": "视频播放链接不能为空"})
        result = DownloadURL(play_url).get()
        return jsonify({
            "code": Code.Success,
            "data": result,
            "message": "成功"
        })
    except VideoException as e:
        logger.exception(f'/video/tencent_video/get_download_url: {e}')
        return jsonify({"code": e.code, "message": e.reason})
    except Exception as e:
        logger.exception(f'/video/tencent_video/get_download_url: {e}')
        return jsonify({"code": Code.SystemError, "message": "内部错误"})


if __name__ == '__main__':
    app.run("0.0.0.0", BackEndPort.video)
