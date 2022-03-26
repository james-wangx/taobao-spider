import json
from urllib.parse import quote

from pyquery.pyquery import PyQuery as pq
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from setting import *

# 配置文件地址，地址栏搜索about:support
profile_directory = r'C:\Users\18368\AppData\Roaming\Mozilla\Firefox\Profiles\x9hlgi1i.dev-edition-default'
# 加载配置
profile = webdriver.FirefoxProfile(profile_directory)
# 启动浏览器配置
browser = webdriver.Firefox(profile)
# 设置等待时间，10s
wait = WebDriverWait(browser, 10)

RESULT = []  # 爬取结果


def index_page(page):
    """
    执行翻页的操作，如果出错，则重新执行

    :param page: 页码

    :return: 无
    """
    print('正在爬取第{}页'.format(page))
    try:
        url = f'https://s.taobao.com/search?q={quote(PRODUCT)}'
        browser.get(url)
        # 保存爬取到的网页源代码，以对比验证是否正确
        # html=browser.page_source
        # with open('taobao.html','w',encoding='utf-8')as file:
        #     file.write(html)

        if page > 1:
            # 等待class属性为'J_Input'的结点加载出来
            input = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, 'J_Input'))
            )
            # 等待class属性值为'J_Submit'的结点可以被点击
            submit = wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'J_Submit'))
            )
            # 通过JavaScript修改结点的属性值
            browser.execute_script(
                "arguments[0].setAttribute('value','{}');".format(str(page)), input)
            submit.click()
        # 等待网页全部加载完成，使用CSS选择器查找
        wait.until(EC.text_to_be_present_in_element((
            By.CSS_SELECTOR, '#mainsrp-pager li.item.active > span'), str(page)
        ))
        wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, '.m-itemlist .items'
        )))
        get_products()
    except TimeoutException:
        index_page(page)


def get_products():
    """
    筛选商品的图片、价格、成交人数等信息

    :return: 无
    """
    html = browser.page_source
    doc = pq(html)
    # 找到本页商品列表的结点
    items = doc('#mainsrp-itemlist .item').items()
    for item in items:
        product = {
            'image': 'https:' + item.find('.pic .img').attr('data-src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text()[:-3],
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        RESULT.append(product)


def save_to_json():
    """
    将爬取下来的信息以json的形式保存

    :return: 无
    """
    print('\n爬取工作完成，一共{}个商品'.format(len(RESULT)))
    print('开始写入文件taobao_{}.json......'.format(PRODUCT))
    with open('taobao_{}.json'.format(PRODUCT), 'w', encoding='utf-8')as file:
        file.write(json.dumps(RESULT, ensure_ascii=False))


def main():
    """
    遍历每一页

    :return: 无
    """
    for i in range(1, MAX_PAGE + 1):
        index_page(i)
    save_to_json()


if __name__ == '__main__':
    main()
