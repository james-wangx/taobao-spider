from os.path import abspath, dirname, join
from requests import Session
from loguru import logger
from environs import Env
import argparse
import sys

env = Env()

# redis 配置
REDIS_HOST = env.str('REDIS_HOST', '127.0.0.1')
REDIS_PORT = env.int('REDIS_HOST', 6379)
REDIS_PASSWORD = env.str('REDIS_PASSWORD', None)
REDIS_KEY = env.str('REDIS_KEY', 'Taobao')

# mysql 配置
MYSQL_HOST = env.str('MYSQL_HOST', 'namenode')
MYSQL_PORT = env.int('MYSQL_PORT', 3306)
MYSQL_USER = env.str('MYSQL_USER', 'root')
MYSQL_PASSWORD = env.str('MYSQL_PASSWORD', None)
MYSQL_DATABASE = env.str('MYSQL_DATABASE', 'taobao')
MYSQL_TABLE = env.str('MYSQL_TABLE', 'details')

# 命令行参数配置
parser = argparse.ArgumentParser(description='爬取商品列表')
parser.add_argument('product', type=str, help='要爬取的商品名')
parser.add_argument('--max_page', type=int, help='爬取的最大页数', default=10)
parser.add_argument('--timeout', type=int, help='最大请求时间', default=10)
parser.add_argument('--need_proxy', type=bool, help='代理开关', default=False)
parser.add_argument('--max_fail_time', type=int, help='最大失败次数', default=10)
args = parser.parse_args()
PRODUCT = env.str('PRODUCT', args.product)
MAX_PAGE = env.int('MAX_PAGE', args.max_page)
TIMEOUT = env.int('TIMEOUT', args.timeout)
NEED_PROXY = env.bool('NEED_PROXY', args.need_proxy)
MAX_FAIL_TIME = env.int('MAX_FAIL_TIME', args.max_fail_time)

# 项目所在目录
ROOT_DIR = dirname(abspath(__file__))
sys.path.append(ROOT_DIR)
# 日志所在目录
LOG_DIR = join(ROOT_DIR, env.str('LOG_DIR', 'logs'))
logger.add(env.str('LOG_RUNTIME_FILE', join(LOG_DIR, 'runtime.log')),
           level='DEBUG',
           rotation='1 week',
           encoding='utf-8',
           retention='20 days')
# cookies保存路径
COOKIES_PATH = env.str('COOKIES_PATH', f'{ROOT_DIR}/storage/taobao_search_cookies.txt')
# 全局会话
SESSION = Session()
# 代理接口
PROXY_POOL_URL = 'http://127.0.0.1:5555/random'
# 正确的状态代码
VALID_STATUSES = [200]
