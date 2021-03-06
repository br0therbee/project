# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/9/10 22:29
# @Version     : Python 3.8.5
import json
import time
from pathlib import Path
from threading import RLock
from urllib.parse import urlencode

import execjs

from utils import RequestManager, LogManager, ciphers
from hunter.videos import ParseError, CookieError, DownloadType, Provider
from hunter.videos.tencent_video import get_cvid, VideoType
from privacy import get_unid
from hunter.videos.tencent_video.login.mock import QQLogin

logger = LogManager('video_tencent_video_get_download_url').file()
CUR_DIR = Path(__file__).parent
with open(CUR_DIR / 'tencent.js', 'r', encoding='utf-8') as frt:
    EXECJS_TENCENT = execjs.compile(frt.read())


class DownloadURL(object):
    _lock = RLock()
    _cookie_file = CUR_DIR.parent / 'cookie.txt'

    def __init__(self, play_url: str, platform: str = '10201', app_ver: str = '3.5.57', sdtfrom: str = 'v1010'):
        self._cookie = None
        self.session = RequestManager()
        self.session.add_cookies(self.cookie)
        self.auth_refresh()
        self._platform = platform
        self._app_ver = app_ver
        self._sdtfrom = sdtfrom
        self._flowid = f'{ciphers(32)}_{self._platform}'
        self._guid = ciphers(32)
        self.play_url = play_url
        cover_id, video_id = get_cvid(self.play_url)
        self.cid = cover_id
        self.vid = video_id
        logger.info(f'{self.cid=}, {self.vid=}, {self.play_url=}')

    @staticmethod
    def _time33(t):
        i = 5381
        for e in range(len(t)):
            i += (i << 5) + ord(t[e])
        return 2147483647 & i

    def auth_refresh(self):
        params = {
            'vappid': '11059694',
            'vsecret': 'fdf61a6be0aad57132bc5cdf78ac30145b6cd2c1470b0cfe',
            'type': 'qq',
            '_': str(int(time.time() * 1000)),
            'g_tk': '',
            'g_vstk': self._time33(self.session.cookiedict['vqq_vusession']),
            'g_actk': self._time33(self.session.cookiedict['vqq_access_token']),
        }
        api = 'https://access.video.qq.com/user/auth_refresh?'
        headers = {
            "Host": "access.video.qq.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/85.0.4183.121 Safari/537.36",
            "Accept": "*/*",
            "Referer": "https://v.qq.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        cookie_dict: dict = self.session.cookiedict
        resp = self.session.request('get', api, params=params, headers=headers)
        self.session.close()
        self.session = RequestManager()
        self.session.add_cookies(resp.cookies)
        cookie_dict.update(self.session.cookiedict)
        self.session.close()
        self.session = RequestManager()
        self.session.add_cookies(cookie_dict)
        self.cookie = self.session.cookiestr

    @property
    def cookie(self):
        with self._lock, open(self._cookie_file, 'r', encoding='utf-8') as f:
            self._cookie = f.read()
        return self._cookie

    @cookie.setter
    def cookie(self, cookies):
        with self._lock, open(self._cookie_file, 'w', encoding='utf-8') as f:
            f.write(cookies)

    def _get_ckey(self):
        return EXECJS_TENCENT.call('getckey', self._guid, self.vid, int(time.time()), self._platform, self._app_ver)

    def _request(self):
        ckey = self._get_ckey()
        cookie: dict = self.session.cookiedict
        api = 'https://vd.l.qq.com/proxyhttp'
        opid = cookie.get('vqq_openid', '')
        atkn = cookie.get('vqq_access_token', '')
        uid = cookie.get('vqq_vuserid', '')
        tkn = cookie.get('vqq_vusession', '')
        appid = cookie.get('vqq_appid', '')

        cur_time = int(time.time())
        logintoken = {
            "main_login": "qq",
            "openid": opid,
            "appid": appid,
            "access_token": atkn,
            "vuserid": uid,
            "vusession": tkn
        }
        adparam = {
            "ad_type": "LD|KB|PVL",
            "adaptor": "2",
            "appid": appid,
            "appversion": "1.0.150",
            "atkn": atkn,
            "chid": "0",
            "coverid": self.cid,
            "dtype": "1",
            "flowid": self._flowid,
            "from": "0",
            "guid": self._guid,
            "live": "0",
            "lt": "qq",
            "opid": opid,
            "pf": "in",
            "pf_ex": "pc",
            "platform": self._platform,
            "plugin": "1.0.0",
            "pu": "-1",
            "refer": self.play_url,
            "req_type": "1",
            "resp_type": "json",
            "rfid": f'{ciphers(32)}_{cur_time}',
            "tkn": tkn,
            "tpid": "1",
            "ty": "web",
            "uid": uid,
            "url": self.play_url,
            "v": self._app_ver,
            "vid": self.vid
        }
        vinfoparam = {
            "appVer": self._app_ver,
            "cKey": ckey,
            "charge": "1",
            "defaultfmt": "auto",
            "defn": "fhd",
            "defnpayver": "1",
            "defsrc": "2",
            "dlver": "2",
            "drm": "32",
            "dtype": "3",
            "ehost": self.play_url,
            "encryptVer": "9.1",
            "fhdswitch": "0",
            "flowid": self._flowid,
            "guid": self._guid,
            "host": "v.qq.com",
            "isHLS": "1",
            "logintoken": logintoken,
            "otype": "ojson",
            "platform": self._platform,
            "refer": "v.qq.com",
            "sdtfrom": self._sdtfrom,
            "show1080p": "1",
            "spadseg": "3",
            "spau": "1",
            "spaudio": "15",
            "spgzip": "1",
            "sphls": "2",
            "sphttps": "1",
            "spwm": "4",
            "tm": cur_time,
            "unid": get_unid(),
            "vid": self.vid,
        }
        payload = {
            "adparam": urlencode(adparam),
            "buid": "vinfoad",
            "vinfoparam": urlencode(vinfoparam)
        }
        headers = {
            "Host": "vd.l.qq.com",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/85.0.4183.83 Safari/537.36",
            "Content-Type": "text/plain",
            "Origin": "https://v.qq.com",
            "Referer": "https://v.qq.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        resp = self.session.request('post', api, headers=headers, json=payload)
        return resp

    def _get_mp4_url(self, resolution_id, filename, vt):
        ckey = self._get_ckey()
        api = 'https://vd.l.qq.com/proxyhttp'
        cookie: dict = self.session.cookiedict
        opid = cookie.get('vqq_openid', '')
        atkn = cookie.get('vqq_access_token', '')
        uid = cookie.get('vqq_vuserid', '')
        tkn = cookie.get('vqq_vusession', '')
        appid = cookie.get('vqq_appid', '')
        logintoken = {
            "main_login": "qq",
            "openid": opid,
            "appid": appid,
            "access_token": atkn,
            "vuserid": uid,
            "vusession": tkn
        }
        vkeyparam = {
            "appVer": self._app_ver,
            "cKey": ckey,
            "charge": "0",
            "ehost": self.play_url,
            "encryptVer": "9.1",
            "filename": filename,
            "flowid": self._flowid,
            "format": resolution_id,
            "guid": self._guid,
            "linkver": "2",
            "lnk": self.vid,
            "logintoken": logintoken,
            "otype": "ojson",
            "platform": self._platform,
            "refer": self.play_url,
            "sdtfrom": self._sdtfrom,
            "tm": int(time.time()),
            "unid": get_unid(),
            "vid": self.vid,
            "vt": vt
        }
        payload = {
            "buid": "onlyvkey",
            "vkeyparam": urlencode(vkeyparam)
        }
        headers = {
            "Host": "vd.l.qq.com",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/85.0.4183.83 Safari/537.36",
            "Content-Type": "text/plain",
            "Origin": "https://v.qq.com",
            "Referer": "https://v.qq.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        resp_dict = self.session.request('post', api, headers=headers, json=payload).json()
        key = json.loads(resp_dict['vkey'])['key']
        return key

    def get(self):
        resp = self._request()
        try:
            text = resp.content.decode('utf-8')
            logger.debug(f'text: {text}')
            content = json.loads(json.loads(text)['vinfo'])
        except (UnicodeDecodeError, json.decoder.JSONDecodeError, KeyError):
            raise ParseError(resp.text)
        try:
            resolution_id = str(content['fl']['fi'][-1]['id'])
            download_urls = []
            ui = content['vl']['vi'][0]['ul']['ui']
            download_type = DownloadType.HLS if content['dltype'] in VideoType.HLS else DownloadType.MP4
            if content['dltype'] in VideoType.MP4:
                fn = content['vl']['vi'][0].get('fn') or ''
                keyid = content['vl']['vi'][0]['cl']['ci'][0].get('keyid') or ''
                logger.info(f'resolution_id: {resolution_id}, fn: {fn}, keyid: {keyid}')
                if resolution_id not in [*fn.split('.'), *keyid.split('.')]:
                    is_success, cookies = QQLogin().login()
                    if is_success:
                        self.cookie = cookies
                    raise CookieError(self.play_url)
                fc = content['vl']['vi'][0]['cl'].get('fc', 0)
                fn: str = content['vl']['vi'][0]['fn']
                p, n = fn.rsplit('.', 1)
                fns = []
                for i in range(1, fc + 1):
                    fns.append(f'{p}.{i}.{n}')
                fvkey = content['vl']['vi'][0]['fvkey']
                for u in ui[:1]:
                    url = u['url']
                    urls = [f'{url}{fns[0]}?sdtfrom=&guid={self._guid}&vkey={fvkey}']
                    for fn in fns[1:]:
                        key = self._get_mp4_url(resolution_id, fn, u['vt'])
                        urls.append(f'{url}{fn}?sdtfrom=&guid={self._guid}&vkey={key}')
                    download_urls.append({
                        'urls': urls
                    })
            elif content['dltype'] in VideoType.HLS:
                fn = content['vl']['vi'][0].get('fn') or ''
                keyid = content['vl']['vi'][0].get('keyid') or ''
                logger.info(f'resolution_id: {resolution_id}, fn: {fn}, keyid: {keyid}')
                if resolution_id not in [*fn.split('.'), *keyid.split('.')]:
                    is_success, cookies = QQLogin().login()
                    if is_success:
                        self.cookie = cookies
                    raise CookieError(self.play_url)
                for u in ui:
                    url = u['url']
                    hls = u.get('hls') or {}
                    pt = hls.get('pt')
                    if url and hls and pt:
                        download_urls.append({
                            'url': f'{url}{pt}',
                            'prefix': url
                        })
                    elif content['dltype'] == 8:
                        download_urls.append({
                            'url': url,
                            'prefix': url.rsplit('/', 1)[0] + '/'
                        })
            else:
                raise TypeError('only support dltype 1, 3, 8')
        except (KeyError, IndexError, TypeError, AttributeError):
            raise ParseError(content)
        return {
            'provider': Provider.tencent_video.name,
            'filter': {'video_id': self.vid},
            'download_type': download_type,
            'params': download_urls,
        }
