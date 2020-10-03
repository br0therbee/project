# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/9/14 0:52
# @Version     : Python 3.8.5
import time

from public import RabbitMQQueue
from utils import RabbitMQConsumer, MongoDBManager, m3u8_download, remove_special_characters, LogManager
from hunter.videos import DownloadStatus, DownloadType, get_storage_path, get_provider, Provider
from hunter.videos.tencent_video.tencent_video_service import TencentVideoService

video_db = MongoDBManager().video
logger = LogManager('video_download').file()


def _video_download(provider, filter, download_type, params):
    logger.info(f'开始下载: {provider=}, {filter=}, {download_type=}')
    col = video_db.get_collection(provider)
    col.update_one(
        filter=filter,
        update={"$set": {
            'download.status': DownloadStatus.downloading,
            'download.reason': '',
            'time': time.strftime('%Y-%m-%d %H:%M:%S')
        }}
    )
    record = col.find_one(filter)

    is_success = False
    failures = []
    status = DownloadStatus.failure
    try:
        if download_type == DownloadType.HLS:
            filename = f"{remove_special_characters(record['name'])}_{record['video_id']}.{download_type}"
            filepath = get_storage_path(provider) / filename
            logger.info(f'下载路径: {filepath}')
            for param in params:
                is_success, failures = m3u8_download(filepath, **param, chunk_size=1024)
                if is_success:
                    break
        else:
            raise ValueError('暂不支持其他下载类型')
        if is_success:
            status = DownloadStatus.success
            reason = ''
            logger.info(f'下载成功: {provider=}, {filter=}, {download_type=}')
        else:
            status = DownloadStatus.failure
            reason = f'未下载链接个数: {len(failures)}'
            logger.info(f'下载失败: {reason=}, {provider=}, {filter=}, {download_type=}')
        col.update_one(
            filter=filter,
            update={"$set": {
                'download.status': status,
                'download.reason': reason,
                'time': time.strftime('%Y-%m-%d %H:%M:%S')
            }}
        )

    except Exception as e:
        if e.args:
            reason = e.args[0]
        else:
            reason = '运行错误'
        logger.info(f'下载失败: {reason=}, {provider=}, {filter=}, {download_type=}')
        col.update_one(
            filter=filter,
            update={"$set": {
                'download.status': status,
                'download.reason': reason,
                'time': time.strftime('%Y-%m-%d %H:%M:%S')
            }}
        )
        raise e


def video_download(play_url: str):
    provider = get_provider(play_url)
    if provider == Provider.tencent_video.name:
        tvs = TencentVideoService()
        filter = tvs.get_details(play_url)
        col = video_db.get_collection(provider)
        play_url = col.find_one(filter)['play_url']
        download_params = tvs.download(play_url)
    else:
        logger.error(f'暂不支持的类型: {provider}')
        raise TypeError('暂不支持的类型')
    if download_params:
        _video_download(**download_params)


RabbitMQConsumer(RabbitMQQueue.video_download_name, function=video_download, concurrent_num=5, fps=1,
                 time_periods=[(True, '09:30', '16:00'), (False, '02:00', '05:00')]).start()
