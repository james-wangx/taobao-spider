from requests import Request
from setting import *


class TaobaoRequest(Request):
    """
    淘宝请求
    """

    def __init__(self, url, callback, method='GET', headers=None, need_proxy=NEED_PROXY, timeout=TIMEOUT, fail_time=0):
        """

        :param url: url
        :param callback: 回调函数
        :param method: 请求方法
        :param headers: 请求头
        :param need_proxy: 是否需要代理
        :param timeout: 超时时间
        :param fail_time: 请求失败次数
        """
        Request.__init__(self, method, url, headers)
        self.callback = callback
        self.need_proxy = need_proxy
        self.timeout = timeout
        self.fail_time = fail_time
