from requests.utils import dict_from_cookiejar, cookiejar_from_dict
from requests.packages import urllib3
from spider.error import TitleError
from json import JSONDecodeError
from urllib.parse import quote
from loguru import logger
from setting import *
import json
import re
import os

EXCEPTION = (
    JSONDecodeError,
    TitleError,
    Exception,
)


class Login:
    """
    模拟登录并获取cookies
    """

    def __init__(self, ua, loginId, password2):
        """
        初始化用户参数信息和相关url

        :param ua:
        :param loginId:
        :param password2:
        """
        self.ua = ua
        self.loginId = loginId
        self.password2 = password2

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
        }

        # 模拟输入商品后跳转的登录页面
        self.login_url = f'https://login.taobao.com/member/login.jhtml?redirectURL=http%3A%2F%2Fs.taobao.com%2Fsearch%3Fq%3D{quote(PRODUCT)}'
        # 提交表单,获取重定向url
        self.commit_url = 'https://login.taobao.com/newlogin/login.do?appName=taobao&fromSite=0'
        # 默认重定向url
        self.redirect_url = f'https://s.taobao.com/search?q={PRODUCT}'
        urllib3.disable_warnings()

    @property
    def _html(self):
        """
        获取登录页面代码

        :return: self._html
        """
        response = SESSION.get(url=self.login_url, headers=self.headers, verify=False)
        return response.text

    def get_value(self, key):
        """
        根据传入的键得到对应的值

        :param key: 键名
        :return: 键所对应的值
        """
        match = re.search(rf'"{key}":"(.*?)"', self._html)
        return match.group(1)

    def load_cookies(self):
        """
        加载cookies

        :return: bool
        """
        if os.path.exists(COOKIES_PATH):
            try:
                logger.info('加载cookies')
                SESSION.cookies = self.unqueue_cookies()
                self.print_title()
            except EXCEPTION as e:
                logger.error(f'登录失败，原因：{e}')
                os.remove(COOKIES_PATH)
                return False
            else:
                return True
        else:
            return False

    def logged(self):
        """
        模拟登录

        :return: bool
        """
        if self.load_cookies():
            return False
        post_data = {
            'loginId': self.loginId,
            'password2': self.password2,
            'keepLogin': 'false',
            'ua': self.ua,
            # 'umidGetStatusVal': '255',
            # 'screenPixel': '1536x864',
            # 'navlanguage': 'zh-CN',
            'navUserAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
            'navPlatform': 'Win32',
            'appName': 'taobao',
            'appEntrance': 'taobao_pc',
            '_csrf_token': self.get_value('_csrf_token'),
            'umidToken': self.get_value('umidToken'),
            'hsiz': self.get_value('hsiz'),
            'bizParams': None,
            # 'style': 'default',
            'appkey': '00000000',
            'from': 'tb',
            'isMobile': 'false',
            # 'lang': 'zh-CN',
            'returnUrl': self.redirect_url,
            'fromSite': '0'
        }
        headers = {
            'Host': 'login.taobao.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            # 'Accept-Language': 'zh-CN,en-US;q=0.7,en;q=0.3',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://login.taobao.com',
            'Connection': 'keep-alive',
            'Referer': self.login_url,

        }
        try:
            response = SESSION.post(url=self.commit_url, headers=headers, data=post_data, verify=False)
            response.raise_for_status()
        except Exception as e:
            logger.error(f'登录失败，原因：')
            raise e
        self.queue_cookies()
        self.redirect_url = response.json()['content']['data']['redirectUrl']
        return True

    def print_title(self):
        """
        输出重定向页面后的标题，以验证登录

        :return:
        """
        try:
            response = SESSION.get(url=self.redirect_url, headers=self.headers, verify=False)
            response.raise_for_status()
            content = response.text
            # # 有必要时保存第一页代码，便于调试
            # with open('success.html', 'w', encoding='utf-8')as file:
            #     file.write(content)
            match = re.search(r'<title>(.*?)</title>', content, re.S)
            title = match.group(1)
            if title != f'{PRODUCT}_淘宝搜索':
                raise TitleError(f'标题错误，标题:{title}')
        except TitleError as e:
            raise e
        else:
            logger.info(f'网页标题为：{title}')

    def queue_cookies(self):
        """
        序列化cookies

        :return:
        """
        cookies_dict = dict_from_cookiejar(SESSION.cookies)
        with open(COOKIES_PATH, 'w', encoding='utf-8') as file:
            json.dump(cookies_dict, file)
            logger.success('保存cookies文件成功！')

    def unqueue_cookies(self):
        """
        反序列化cookies

        :return:
        """
        try:
            with open(COOKIES_PATH, 'r', encoding='utf-8') as file:
                cookies_dict = json.load(file)
        except JSONDecodeError as e:
            raise e
        else:
            return cookiejar_from_dict(cookies_dict)

    def parse_detail(self):
        """
        解析登录后的页面，方便调试

        :return:
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
            r'"view_sales":"(.*?)人付款","comment_count":"(.*?)",.*?,"nick":"(.*?)"', self.content, re.S)
        keys = ('id', 'name', 'price', 'fee', 'location', 'sales', 'comments', 'shop')
        self.result = [dict(zip(keys, value)) for value in match if len(value[4]) < 50]

    def save_to_json(self):
        """
        保存为json格式，方便调试

        :return:
        """
        with open('../good.json', 'w', encoding='utf-8') as file:
            file.write(json.dumps(self.result, indent=2, ensure_ascii=False))


if __name__ == '__main__':

    # 用户信息参数
    loginId = ''
    ua = ''
    password2 = ''
    login = Login(ua, loginId, password2)
    if login.logged():
        login.print_title()
    login.parse_detail()
    login.save_to_json()
