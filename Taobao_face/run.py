# ******************************************************************************************************************** #
#                   Reference link:                                                                                    #
#                                                                                                                      #
#                   pig6:https://github.com/pig6/login_taobao                                                          #
#                   Germey:https://github.com/Python3WebSpider/ProxyPool                                               #
#                          https://github.com/Python3WebSpider/Weixin                                                  #
#                                                                                                                      #
#                                                                                   Thanks!                            #
# ******************************************************************************************************************** #

from spider.crawler import Crawler
from spider.login import Login

if __name__ == '__main__':

    # 这三个表单参数在浏览器中复制，可以多次使用，ua和password2分别为加密后的账号和密码
    # 获取过程：
    # 1、清除淘宝网的cookies，访问淘宝网：https://www.taobao.com
    # 2、在搜索栏搜索任意商品，跳转到登录页面
    # 3、点击登陆，用抓包工具或浏览器开发者模式截获url：https://login.taobao.com/newlogin/login.do?appName=taobao&fromSite=0
    # 4、复制此url内的表单信息ua、loginId、password2
    ua = ''
    loginId = ''
    password2 = ''
    login = Login(ua, loginId, password2)
    crawler = Crawler()
    if login.logged():
        login.print_title()
        crawler.run()
    else:
        crawler.run()
