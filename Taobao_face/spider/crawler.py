from requests.cookies import cookiejar_from_dict
from requests.exceptions import ReadTimeout
from spider.request import TaobaoRequest
from storage.db import RedisQueue
from json import JSONDecodeError
from storage.mysql import MySQL
from loguru import logger
from setting import *
import requests
import json
import re
import os


class Crawler:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
    }
    queue = RedisQueue()
    mysql = MySQL()

    def get_proxy(self):
        """
        从代理池获取代理

        :return: proxy
        """
        try:
            response = requests.get(PROXY_POOL_URL)
            if response.status_code == 200:
                logger.info('Get Proxy', response.text)
                return response.text
            return None
        except requests.ConnectionError:
            return None

    def get_url(self):
        """
        构造url

        :return: url
        """
        for page in range(MAX_PAGE):
            offset = 6 - page * 3
            detali = 44 * page
            yield f'http://s.taobao.com/search?q={PRODUCT}&bcoffset={offset}&ntoffset={offset}&p4ppushleft=1%2C48&s={detali}'

    def start(self):
        """
        储存全部url，等待调度

        :return: None
        """
        for url in self.get_url():
            taobao_request = TaobaoRequest(url=url, callback=self.parse_detail, headers=self.headers)
            self.queue.add(taobao_request)
            logger.info(f'Add {taobao_request.url} to redis.')

    def parse_detail(self, response):
        """
        解析页面

        :return: 商品信息列表
        """
        # 匹配全部信息
        # match = re.findall(
        #     r'"nid":"(.*?)","category":"(.*?)","pid":"(.*?)","title":"(.*?)","raw_title":"(.*?)","pic_url":"(.*?)",'
        #     r'"detail_url":"(.*?)","view_price":"(.*?)","view_fee":"(.*?)","item_loc":"(.*?)","view_sales":"(.*?)",'
        #     r'"comment_count":"(.*?)","user_id":"(.*?)","nick":"(.*?)"', response.text, re.S)
        # keys = ('nid', 'category', 'pid', 'title', 'raw_title', 'pic_url', 'detail_url', 'view_price',
        #         'view_fee', 'item_loc', 'view_sales', 'comment_count', 'user_id', 'nick')

        # 匹配重要信息
        match = re.findall(
            r'"nid":"(.*?)",.*?,"raw_title":"(.*?)",.*?,"view_price":"(.*?)","view_fee":"(.*?)","item_loc":"(.*?)",'
            r'"view_sales":"(.*?)人付款","comment_count":"(.*?)",.*?,"nick":"(.*?)"', response.text, re.S)
        keys = ('id', 'name', 'price', 'fee', 'location', 'sales', 'comments', 'shop')
        return [dict(zip(keys, value)) for value in match if len(value[4]) < 50]

    def request(self, taobao_request):
        """
        执行请求

        :param taobao_request: 请求
        :return: 响应
        """
        try:
            if taobao_request.need_proxy:
                proxy = self.get_proxy()
                if proxy:
                    proxies = {
                        'http': 'http://' + proxy,
                        'https': 'https://' + proxy
                    }
                    logger.info(f'Get proxy {proxies}')
                    return SESSION.get(url=taobao_request.url, headers=self.headers, timeout=taobao_request.timeout,
                                       proxies=proxies)
            return SESSION.get(url=taobao_request.url, headers=self.headers, timeout=taobao_request.timeout)
        except (ConnectionError, ReadTimeout) as e:
            print(e.args)
            return False

    def error(self, taobao_request):
        """
        错误处理

        :param taobao_request: 请求
        :return: None
        """
        taobao_request.fail_time += 1
        logger.debug(f'Url {taobao_request.url} faile_time + 1, current fail_time: {taobao_request.fail_time}')
        if taobao_request.fail_time < MAX_FAIL_TIME:
            self.queue.add(taobao_request)
        else:
            logger.debug(f'Url {taobao_request.url} delete!')

    def schedule(self):
        """
        调度请求

        :return: None
        """
        while not self.queue.empty():
            taobao_request = self.queue.pop()
            callback = taobao_request.callback
            logger.info(f'Schedule {taobao_request.url}')
            response = self.request(taobao_request)
            if response and response.status_code in VALID_STATUSES:
                results = callback(response)
                if results:
                    for result in results:
                        if isinstance(result, dict):
                            self.mysql.insert(MYSQL_TABLE, result)
                            logger.success(f'successful parse {taobao_request.url}')
                else:
                    self.error(taobao_request)
            else:
                self.error(taobao_request)

    def unqueue_cookies(self):
        """
        反序列化cookies

        :return: cookiejar
        """
        try:
            with open(COOKIES_PATH, 'r', encoding='utf-8') as file:
                cookies_dict = json.load(file)
        except JSONDecodeError as e:
            raise e
        else:
            return cookiejar_from_dict(cookies_dict)

    def run(self):
        """
        开始执行

        :return: None
        """
        self.start()
        self.schedule()


if __name__ == '__main__':
    crawler = Crawler()
    if os.path.exists(COOKIES_PATH):
        SESSION.cookies = crawler.unqueue_cookies()
    crawler.run()
