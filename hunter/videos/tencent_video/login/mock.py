# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/9/2 20:09
# @Version     : Python 3.8.5
import atexit
import json
import random
import time
from contextlib import suppress
from pathlib import Path
from threading import Lock

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from utils import LogManager, RequestManager
from videos import account
from videos.tencent_video.login.captcha import Captcha

logger = LogManager('tencent_video_login').file()


class QQLogin(object):
    _lock = Lock()
    _executable_path = r'/usr/bin/chromedriver'
    image_path = Path(__file__).parent / 'tencent_video_captcha'
    image_path.mkdir(parents=True, exist_ok=True)

    def __init__(self,
                 username: str = account.TencentVideo.username,
                 password: str = account.TencentVideo.password,
                 timeout: float = 60
                 ):
        self._username = username
        self._password = password
        self.index_url = 'https://graph.qq.com/oauth2.0/show?redirect_uri=https%3A%2F%2Faccess.video.qq.com%2Fuser%2Fauth_login%3Fvappid%3D11059694%26vsecret%3Dfdf61a6be0aad57132bc5cdf78ac30145b6cd2c1470b0cfe%26raw%3D1%26type%3Dqq%26appid%3D101483052&which=Login&display=pc&response_type=code&client_id=101483052'
        self.timeout = timeout

    def close(self):
        logger.info('关闭WebDriver')
        self.driver.quit()

    def _create(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--start-maximized')
        self.driver = webdriver.Chrome(executable_path=self._executable_path, options=options)
        self.wait = WebDriverWait(self.driver, self.timeout)
        self.driver.get(self.index_url)
        logger.info('打开腾讯视频网站')
        atexit.register(self.close)

    def _before_login(self):
        self.wait.until(expected_conditions.frame_to_be_available_and_switch_to_it((By.ID, 'ptlogin_iframe')))
        logger.info('进入登陆界面')
        time.sleep(1)

    def login(self):
        with self._lock:
            self._create()
            self._before_login()

            is_success = False
            try:
                self.wait.until(expected_conditions.element_to_be_clickable((By.ID, 'switcher_plogin'))).click()
                logger.info('点击帐号密码登录链接')

                self.wait.until(expected_conditions.visibility_of_element_located((By.ID, 'u'))).send_keys(
                    self._username)
                logger.info(f'输入用户账号: {self._username}')
                time.sleep(1)
                self.wait.until(expected_conditions.visibility_of_element_located((By.ID, 'p'))).send_keys(
                    self._password)
                logger.info(f'输入用户密码: {self._password}')
                time.sleep(1)

                self.wait.until(expected_conditions.element_to_be_clickable((By.ID, 'login_button'))).click()
                logger.info('点击授权并登陆按钮')

                self._captcha()
                time.sleep(10)

                cookies = self.driver.get_cookies()
                cookie_list = []
                for cookie in cookies:
                    k = cookie['name']
                    v = cookie['value'].encode('unicode-escape').decode('utf-8')
                    cookie_list.append(f'{k}={v}')
                cookies = '; '.join(cookie_list)
                logger.info(f'cookies: {cookies}')
                is_success = self._is_success(cookies)
            except Exception as e:
                logger.exception(f'运行时错误: {e}')
            logger.info(f'登录状态: {is_success}')
            if not is_success:
                logger.warning('休眠 30 分钟')
                time.sleep(30 * 60)
            return is_success, cookies

    def _captcha(self):
        try:
            self.wait.until(expected_conditions.frame_to_be_available_and_switch_to_it((By.ID, 'tcaptcha_iframe')))
            logger.info('进入滑动验证码界面')
        except exceptions.TimeoutException:
            logger.info('未出现验证码')
        except Exception as e:
            logger.exception(e)
            logger.info('登陆流程异常')
        else:
            cur_time = int(time.time())
            self.wait.until(expected_conditions.visibility_of_element_located((By.ID, 'slideBg')))
            captcha_url = self.driver.find_element_by_id('slideBg').get_attribute('src')
            print(f'captcha_url: {captcha_url}')
            captcha_file = self.image_path / f'{cur_time}_captcha.png'
            self._download(captcha_url, captcha_file)
            block_url = self.driver.find_element_by_id('slideBlock').get_attribute('src')
            block_file = self.image_path / f'{cur_time}_block.png'
            self._download(block_url, block_file)
            time.sleep(3)

            distance = Captcha().get_distance(block_file, captcha_file)
            traces = self._fibonacci_trace(distance)
            self._move(traces)

    def _move(self, traces: list):
        logger.info(f'开始滑动: {traces}')
        slider = self.driver.find_element_by_id("tcaptcha_drag_button")
        ActionChains(self.driver).click_and_hold(slider).perform()

        for x in traces:
            ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=random.randint(-2, 3)).perform()
            time.sleep(.2)
        time.sleep(random.random())
        ActionChains(self.driver).release().perform()
        time.sleep(3)

    @staticmethod
    def _fibonacci_trace(distance: int) -> list:
        print(f'distance: {distance}')
        a, b = 1, 1
        fibonacci = [1]
        while sum(fibonacci) < distance:
            a, b = b, a + b
            fibonacci.append(a)
        fibonacci.append(distance - sum(fibonacci))
        return fibonacci

    @staticmethod
    def _download(url: str, filename: str):
        if not url.startswith('http'):
            url = f'https://t.captcha.qq.com{url}'
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36"
        }
        resp_bytes = RequestManager().request('get', url, headers=headers).content
        with open(filename, 'wb') as fw:
            fw.write(resp_bytes)

    @staticmethod
    def _is_success(cookie: str):
        rm = RequestManager()
        rm.add_cookies(cookie)
        cookiedict = rm.cookiedict
        qq_openid = cookiedict['vqq_openid']
        qq_access_token = cookiedict['vqq_access_token']
        qq_client_id = cookiedict['vqq_appid']
        success = False
        url = (
            f'https://vip.video.qq.com/fcgi-bin/svip_comm_cgi?svr_name=svipupdate&cmd=5633&callback=jQuery&TvReqType=1'
            f'&OpenId={qq_openid}'
            f'&AccessToken={qq_access_token}'
            f'&Appid={qq_client_id}')
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "cookie": cookie,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36"
        }
        with suppress(Exception):
            resp_str = RequestManager().request('get', url, headers=headers).text
            logger.info(f'验证接口返回数据: {resp_str}')
            resp_dict = json.loads(resp_str[7:-2])
            if (resp_dict.get('result') or {}).get('code') == 0:
                success = True
        return success


if __name__ == '__main__':
    r = QQLogin().login()
    print(json.dumps(r))
