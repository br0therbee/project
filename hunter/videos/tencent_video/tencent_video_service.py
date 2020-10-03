# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/9/9 8:18
# @Version     : Python 3.8.5
import json
import re
import time
from contextlib import suppress

from public import BackEndPort
from utils import LogManager, MongoDBManager, RequestManager
from videos import VideoDetailData, VideoCategory, BaseVideo, Code, DownloadStatus
from videos.tencent_video import get_cvid

logger = LogManager('video_tencent_video_service').file()

RE_columnInfo = re.compile(r'var COLUMN_INFO = (.*)')
RE_coverInfo = re.compile(r'var COVER_INFO = (.*)')
RE_videoINFO = re.compile(r'var VIDEO_INFO = (.*)')
RE_vid = re.compile(r'vid=(\w+)')

video_col = MongoDBManager().video.get_collection('tencent_video')
# 创建索引
video_col.create_index('video_id', unique=True, background=True)


class Details(object):
    def __init__(self, play_url):
        self.play_url = play_url
        logger.info(self.play_url)
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,"
                      "image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/85.0.4183.83 Safari/537.36"
        }

    def _request(self):
        content = RequestManager().request('get', self.play_url, headers=self.headers).content.decode('utf-8')
        return content

    def parse(self):
        content = self._request()
        cover_info: dict = json.loads(RE_coverInfo.search(content).group(1))
        video_info = json.loads(RE_videoINFO.search(content).group(1))
        vdd = VideoDetailData()
        vdd.category = VideoCategory.movie
        vdd.video_id = cover_info['video_ids'][0]
        vdd.cover_id = cover_info['column_id'] if cover_info['column_id'] != 0 else cover_info['cover_id']
        vdd.play_url = f'https://v.qq.com/x/cover/{vdd.cover_id}/{vdd.video_id}.html'
        vdd.name = cover_info['title']
        vdd.name_en = cover_info.get('title_en') or ''
        vdd.alias = cover_info.get('alias') or []
        vdd.directors = cover_info.get('director') or []
        vdd.actors = cover_info.get('leading_actor') or []
        vdd.score = float(cover_info.get('douban_score') or 0)
        vdd.publish_date = video_info.get('publish_date') or cover_info.get('publish_date') or ''
        vdd.description = cover_info.get('description') or ''
        vdd.area = cover_info.get('area_name') or ''
        vdd.horizontal_pic_url = cover_info.get('horizontal_pic_url') or ''
        vdd.vertical_pic_url = cover_info.get('vertical_pic_url') or ''
        vdd.language = cover_info.get('langue') or ''
        vdd.tags = cover_info.get('sub_genre') or []
        with suppress(ValueError):
            vdd.duration = time.strftime('%H:%M:%S', time.gmtime(int(video_info.get('duration'))))
        if cover_info.get('main_genre'):
            vdd.tags.append(cover_info.get('main_genre'))

        # videos = []
        # if vdd.video_type == VideoType.movie:
        #     vdd.douban_score = cover_info['douban_score']
        #     vdd.title_en = cover_info['title_en']
        #     for element in root.xpath('//ul[@id="_pic_title_list_ul"]//li'):
        #         vdud = VideoDownloadURLData()
        #         vdud.vid = first(element.xpath('@id'))
        #         vdud.cover_id = vdd.cover_id
        #         vdud.play_url = f'https://v.qq.com/x/cover/{vdd.cover_id}/{vdud.vid}.html'
        #         vdud.title = first(element.xpath('@data-title'))
        #         videos.append(vdud)
        # elif vdd.video_type == VideoType.variety:
        #     column_info = json.loads(RE_columnInfo.search(content).group(1))
        #     vdd.directors = column_info['presenter']
        #     vdd.description = column_info['description']
        #
        #     api = (f'https://s.video.qq.com/get_playsource?id={vdd.cover_id}'
        #            f'&plat=2&type=4&data_type=3&range=1-10000&plname=qq&otype=json')
        #     resp_str = RequestManager().request('get', api, headers=self.headers).content.decode('utf-8')[13:-1]
        #     logger.debug(f'综艺: {resp_str}')
        #
        #     resp_dict = json.loads(resp_str)
        #     for video in resp_dict['PlaylistItem']['videoPlayList']:
        #         vdud = VideoDownloadURLData()
        #         vdud.vid = RE_vid.search(video['playUrl']).group(1)
        #         vdud.cover_id = vdd.cover_id
        #         vdud.play_url = f'https://v.qq.com/x/cover/{vdd.cover_id}/{vdud.vid}.html'
        #         vdud.episode_number = video['episode_number']
        #         vdud.title = video['title']
        #         videos.append(vdud)
        # elif vdd.video_type == VideoType.tv:
        #     for index, vid in enumerate(cover_info['video_ids'], start=1):
        #         vdud = VideoDownloadURLData()
        #         vdud.vid = vid
        #         vdud.cover_id = vdd.cover_id
        #         vdud.play_url = f'https://v.qq.com/x/cover/{vdd.cover_id}/{vdud.vid}.html'
        #         vdud.episode_number = str(index)
        #         vdud.title = ''
        #         videos.append(vdud)
        # else:
        #     if vdd.video_type in [VideoType.cartoon, VideoType.child]:
        #         vdd.directors = vdd.directors or cover_info['director_id']
        #         vdd.langue = cover_info['dialogue']
        #     api = (f'https://s.video.qq.com/get_playsource?id={vdd.cover_id}'
        #            f'&plat=2&type=4&data_type=3&range=1-10000&plname=qq&otype=json')
        #     resp_str = RequestManager().request('get', api, headers=self.headers).content.decode('utf-8')[13:-1]
        #     if vdd.video_type == VideoType.cartoon:
        #         flag = '动漫'
        #     elif vdd.video_type == VideoType.child:
        #         flag = '少儿'
        #     elif vdd.video_type == VideoType.doco:
        #         flag = '纪录片'
        #     else:
        #         flag = '其他'
        #     logger.debug(f'{flag}: {resp_str}')
        #
        #     resp_dict = json.loads(resp_str)
        #     for video in resp_dict['PlaylistItem']['videoPlayList']:
        #         vdud = VideoDownloadURLData()
        #         vdud.vid = video['id']
        #         vdud.cover_id = vdd.cover_id
        #         vdud.play_url = f'https://v.qq.com/x/cover/{vdd.cover_id}/{vdud.vid}.html'
        #         vdud.episode_number = video['episode_number']
        #         vdud.title = video['title']
        #         videos.append(vdud)
        return vdd


class TencentVideoService(BaseVideo):

    def get_details(self, play_url: str):
        document = Details(play_url).parse()
        filter = {'video_id': document['video_id']}
        video_col.update_one(
            filter=filter,
            update={'$set': document},
            upsert=True
        )
        logger.info(f'插入数据: {document}')
        return filter

    def download(self, play_url: str):
        api = f'http://127.0.0.1:{BackEndPort.video}/video/tencent_video/get_download_url'
        resp_dict = RequestManager().request('post', api, json={'play_url': play_url}).json()
        cover_id, video_id = get_cvid(play_url)
        code = resp_dict['code']
        message = resp_dict['message']
        logger.info(f'获取下载链接接口返回数据: {resp_dict}')
        if code == Code.Success:
            data = resp_dict['data']
            return data

        elif code in [Code.CookieError, Code.ParseError, Code.NeedPayError]:
            video_col.update_one(
                filter={'video_id': video_id},
                update={'$set': {
                    'download.status': DownloadStatus.failure,
                    'download.reason': message,
                    'time': time.strftime('%Y-%m-%d %H:%M:%S')
                }}
            )
