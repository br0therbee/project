# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/10/6 19:29
# @Version     : Python 3.8.5
__all__ = ['Downloader']

from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path

from .. import RequestManager, LogManager, NetworkRequestException

logger = LogManager('mp4_download').file()


class Downloader(object):
    _default_headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/85.0.4183.102 Safari/537.36'
    }

    def __init__(self, thread_num: int = 10, headers: dict = None):
        if thread_num < 1:
            thread_num = 1
        self.executor = ThreadPoolExecutor(max_workers=thread_num)
        self.headers = headers
        self.keys = dict()

    def control(self, filepath: str, urls: list, *, chunk_size: int = 1 * 1024 * 1024, wipe_cache: bool = True):
        dirname = Path(filepath).parent
        filename = Path(filepath).name
        new_dirname = dirname / Path(f"{filename}文件夹")
        new_filepath = new_dirname / filename
        Path(new_filepath).parent.mkdir(parents=True, exist_ok=True)
        logger.info(f'创建文件夹: {new_dirname}')
        failures = self._threads_download(list(zip(range(1, len(urls) + 1), urls)), new_filepath, chunk_size)
        for i in range(5):
            if failures:
                failures = self._threads_download(failures, new_filepath, chunk_size)
        if not failures:
            self._merge_files(new_dirname, filepath, wipe_cache)
        return not bool(failures), failures

    download = control

    def _merge_files(self, dirname, filepath, wipe_cache):
        logger.info(f'合并文件: {dirname} -> {filepath}')
        if Path(filepath).exists():
            Path(filepath).unlink()
            logger.warning(f'删除已存在文件: {filepath}')
        with open(filepath, 'ab') as fwb:
            for filename in sorted(Path(dirname).iterdir()):
                with open(str(filename), 'rb') as fr:
                    fwb.write(fr.read())
                    fwb.flush()
                if wipe_cache:
                    Path(filename).unlink()
                    logger.debug(f'删除文件: {str(filename)}')
        if wipe_cache:
            Path(dirname).rmdir()
            logger.info(f'删除文件夹: {dirname}')

    @staticmethod
    def _get_seed(filepath):
        try:
            with open(filepath, mode='rb') as fr:
                seed = len(fr.read())
        except FileNotFoundError:
            seed = 0
        return seed

    def _threads_download(self, urls, filepath, chunk_size):
        failures = []
        results = self.executor.map(self._download, urls, [filepath] * len(urls), [chunk_size] * len(urls))
        for result in results:
            if result:
                failures.append(result)
        return failures

    def _download(self, url, filepath: str, chunk_size: int):
        all_files = [str(file) for file in Path(filepath).parent.iterdir()]
        index, url = url
        success_path = f'{filepath}.{index:05}1'
        if success_path in all_files:
            logger.info(f'已存在: {success_path}')
            return
        failure_path = f'{filepath}.{index:05}0'
        try:
            self.__download(url, failure_path, chunk_size)
        except NetworkRequestException as e:
            logger.error(f'下载失败: {url}, {index}, {e}')
            return index, url
        except Exception as e:
            logger.exception(f'下载异常: {url}, {index}, {e}')
            raise e
        else:
            logger.debug(f'下载成功: {url}')
            Path(failure_path).rename(f'{failure_path[:-1]}1')

    def __download(self, url: str, filepath: str, chunk_size: int):
        file_size = self._get_seed(filepath)
        headers = {
            'range': f'bytes={file_size}-',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/85.0.4183.102 Safari/537.36'
        }
        if self.headers:
            headers = self.headers

        with RequestManager() as session:
            resp = session.request('get', url, stream=True, headers=headers)
            if 'Content-Range' in resp.headers:
                content_length = int(resp.headers['Content-Range'].rsplit('/', 1)[-1])
                logger.debug(f'流式传输到: {filepath}, {content_length=:,}  {file_size=:,}')
                if content_length > file_size:
                    with open(filepath, 'ab') as fwb:
                        for chunk in resp.iter_content(chunk_size=chunk_size):
                            if chunk:
                                fwb.write(chunk)
                                fwb.flush()
            else:
                logger.debug(f'下载到: {filepath}')
                with open(filepath, 'wb') as fwb:
                    fwb.write(resp.content)

    def close(self):
        self.executor.shutdown()
        return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
