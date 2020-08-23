from os.path import abspath, dirname
from requests import Session

# redis 配置
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PASSWORD = None
REDIS_KEY = 'Taobao'

# mysql 配置
MYSQL_HOST = 'namenode'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = None
MYSQL_DATABASE = 'taobao'
MYSQL_TABLE = 'details'

# 最大请求时间
TIMEOUT = 10
# 项目所在目录
PATH = dirname(abspath(__file__))
# cookies保存路径
COOKIES_PATH = f'{PATH}/storage/taobao_search_cookies.txt'
# 待爬取的商品名
PRODUCT = 'iphone'
# 最大页数
MAX_PAGE = 10
# 全局会话
SESSION = Session()
# 是否需要代理
NEED_PROXY = False
# 最大失败次数
MAX_FAIL_TIME = 10
# 获取代理地址
PROXY_POOL_URL = 'http://127.0.0.1:5555/random'
# 正确的状态代码
VALID_STATUSES = [200]
