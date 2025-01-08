import os
import uuid
import time
import random
import urllib
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By  # 导入 By 类
from selenium.webdriver.common.keys import Keys

NameList = ['猫咪血便']  # 只保留一个关键字

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def send_param_to_baidu(name, browser):
    '''
    :param name:    str
    :param browser: webdriver.Chrome
    :return:        将要输入的 关键字 输入百度图片
    '''
    try:
        # 定位搜索框
        input_box = browser.find_element(By.CSS_SELECTOR, 'span.input-container_94h2R input[name="word"]')
        input_box.clear()  # 清空搜索框
        input_box.send_keys(name)  # 输入关键词
        time.sleep(1)

        # 定位搜索按钮并点击
        search_button = browser.find_element(By.CSS_SELECTOR, 'span.submit-btn_ZmEXZ input[type="submit"]')
        search_button.click()
        time.sleep(1)
    except Exception as e:
        print(f"操作搜索框或按钮时出错: {e}")
    return


def mistaken():
    try:
        print('*****出现异常错误，跳过此次循环，爬取无内容*****')
        ######采集代码##########
        print('——————————接下来继续运行——————————')
    except:
        mistaken()

def download_baidu_images(save_path, img_num, browser):
    ''' 此函数应在
    :param save_path: 下载路径 str
    :param img_num:   下载图片数量 int
    :param name:   爬取种类的名字
    :param browser:   webdriver.Chrome
    :return:
    '''
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    ##下面是打开第一张图片，然后在此界面中点击左右切换图片
    # // *[ @ id = "imgid"]/div[1]/ul/li[1]/div/div[2]/a/img
    # 如果这里报错，其中下面这里的定位地址，需要根据百度你爬取的图片的位置进行相应的修改
    img_link = browser.find_element(By.XPATH, '//*[@id="imgid"]/div/ul/li[3]/div/div[2]/a/img')  # 使用 By.XPATH
    img_link.click()

    # 切换窗口
    windows = browser.window_handles
    browser.switch_to.window(windows[-1])  # 切换到图像界面
    # time.sleep(3)
    time.sleep(random.random())
    print(img_num)
    for i in range(img_num):
        img_link_ = browser.find_element(By.XPATH, '//div/img[@class="currentImg"]')  # 使用 By.XPATH
        src_link = img_link_.get_attribute('src')
        print(src_link)
        # 保存图片，使用urlib
        img_name = uuid.uuid4()
        # urllib.request.urlretrieve(src_link, os.path.join(save_path, str(img_name) + '.jpg'))
        # 上述一行代码直接去访问资源会报403错误，排查发现可能是服务器开启了反爬虫，针对这种情况添加headers浏览器头，模拟人工访问网站行为：
        opener = urllib.request.build_opener()
        # 构建请求头列表每次随机选择一个
        ua_list = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.62',
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
                   'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36 SE 2.X MetaSr 1.0'
                   ]
        opener.addheaders = [('User-Agent', random.choice(ua_list))]
        urllib.request.install_opener(opener)

        # 为了不中断程序完整爬取，所以处理爬虫的过程中出现资源请求不到的错误404 或者403的错误，只需要跳过这些错误继续执行
        try:
            urllib.request.urlretrieve(src_link, os.path.join(save_path, str(img_name) + '.jpg'))
        except Exception as e:
            print(e)
            mistaken()

        # 如果网站反爬虫级别特别高的，还需要切换代理ip：使用urllib模块设置代理IP是比较简单的，首先需要创建ProxyHandler对象，其参数为字典类型的代理IP，键名为协议类型（如HTTP或者HTTPS)，值为代理链接。然后利用ProxyHandler对象与buildopener()
        # 方法构建一个新的opener对象，最后再发送网络请求即可。
        # 创建代理IP
        # proxy_handler = urllib.request.ProxyHandler({
        #     'https': '58.220.95.114:10053'
        # })
        # # 创建opener对象
        # opener = urllib.request.build_opener(proxy_handler)

        # 关闭图像界面，并切换到外观界面
        time.sleep(random.random())

        # 点击下一张图片
        browser.find_element(By.XPATH, '//span[@class="img-next"]').click()  # 使用 By.XPATH
        time.sleep(random.random())

    # 关闭当前窗口，并选择之前的窗口
    browser.close()
    #browser.switch_to.window(windows[0])
    #browser.get(r'https://image.baidu.com/')

    return

def main(name, save_root, img_num, is_open_chrome=True):
    '''
    :param name: str 单个关键字
    :param save_root: str 保存路径
    :param img_num: int 下载图片数量
    :param is_open_chrome: 爬虫是否打开浏览器爬取图像 bool default=False
    :return:
    '''
    options = webdriver.ChromeOptions()
    # 设置是否打开浏览器
    if not is_open_chrome:
        options.add_argument('--headless')  # 不打开浏览器
    # else:
    #     prefs = {"profile.managed_default_content_settings.images": 2}  # 禁止图像加载
    #     options.add_experimental_option("prefs", prefs)

    # 欺骗反爬虫，浏览器可以打开，但是没有内容
    options.add_argument("--disable-blink-features=AutomationControlled")
    browser = webdriver.Chrome(options=options)
    browser.maximize_window()
    browser.get(r'https://image.baidu.com/')
    time.sleep(random.random())

    save_path = os.path.join(save_root, name)  # 以关键字作为文件夹名称
    send_param_to_baidu(name, browser)
    download_baidu_images(save_path=save_path, img_num=img_num, browser=browser)
    if len(browser.window_handles) > 0:
        browser.switch_to.window(browser.window_handles[0])
        browser.get(r'https://image.baidu.com/')
        time.sleep(random.random())
    # 全部关闭
    browser.quit()
    return

if __name__ == "__main__":
    main(name=NameList[0], save_root=r'C:\Users\admin\Desktop\poops', img_num=6000)