from spider.request import TaobaoRequest
from pickle import loads, dumps
from redis import StrictRedis
from setting import *


class RedisQueue():
    def __init__(self):
        """
        初始化Redis
        """
        self.db = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

    def add(self, request):
        """
        向队列添加序列化后的Request

        :param request: 请求对象
        :param fail_time: 失败次数
        :return: 添加结果
        """
        if isinstance(request, TaobaoRequest):
            return self.db.rpush(REDIS_KEY, dumps(request))
        return False

    def pop(self):
        """
        取出下一个Request并反序列化

        :return: Request or None
        """
        if self.db.llen(REDIS_KEY):
            return loads(self.db.lpop(REDIS_KEY))
        else:
            return False

    def clear(self):
        self.db.delete(REDIS_KEY)

    def empty(self):
        return self.db.llen(REDIS_KEY) == 0


if __name__ == '__main__':
    db = RedisQueue()
    start_url = 'http://www.baidu.com'
    taobao_request = TaobaoRequest(url=start_url,callback='Hello')
    db.add(taobao_request)
    request = db.pop()
    print(request)
    print(request.need_proxy,request.callback)
