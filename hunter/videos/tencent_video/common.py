# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/9/21 0:53
# @Version     : Python 3.8.5


def get_cvid(play_url: str) -> tuple:
    cover_id, video_id = play_url.rsplit('.', 1)[0].split('/')[-2:]
    return cover_id, video_id


class VideoType(object):
    MP4 = 1,
    HLS = 3, 8
