import os
import uuid
import random
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import io

# 随机 User-Agent 列表
ua_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.62',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36 SE 2.X MetaSr 1.0'
]

def download_and_convert_to_jpg(src_link, save_path, img_name):
    try:
        headers = {"User-Agent": random.choice(ua_list)}
        response = requests.get(src_link, headers=headers)
        if response.status_code == 200:
            # 使用 Pillow 打开图片并转换为 JPG
            img = Image.open(io.BytesIO(response.content))
            jpg_path = os.path.join(save_path, f"{img_name}.jpg")
            img.convert("RGB").save(jpg_path, "JPEG")
            print(f"Image saved and converted: {jpg_path}")
        else:
            print(f"Failed to download image: {response.status_code}")
    except Exception as e:
        print(f"Error downloading or converting image: {e}")

def download_images_from_post(browser, save_path, img_num):
    # 定位所有 parent-comment
    parent_comments = browser.find_elements(By.CLASS_NAME, 'parent-comment')
    img_count = 0

    for comment in parent_comments:
        try:
            # 在 parent-comment 中查找 comment-picture
            comment_picture = comment.find_element(By.CLASS_NAME, 'comment-picture')
            img_element = comment_picture.find_element(By.TAG_NAME, 'img')
            src_link = img_element.get_attribute('src')
            
            if src_link:
                print(f"Found image: {src_link}")
                download_and_convert_to_jpg(src_link, save_path, str(uuid.uuid4()))
                img_count += 1
                if img_count >= img_num:
                    break
        except Exception as e:
            print(f"No image found in this comment or error occurred: {e}")

    return img_count

def main(save_root, img_num, is_open_chrome=True):
    save_path = save_root
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    options = webdriver.ChromeOptions()
    if not is_open_chrome:
        options.add_argument('--headless')

    options.add_argument("--disable-blink-features=AutomationControlled")
    browser = webdriver.Chrome(options=options)
    browser.maximize_window()
    browser.get(r'https://www.xiaohongshu.com/explore')
    time.sleep(30)

    # 搜索关键词
    search_input = browser.find_element(By.XPATH, '//*[@id="search-input"]')
    search_input.send_keys('正常猫咪粪便') 
    search_button = browser.find_element(By.XPATH, '//*[@id="global"]/div[1]/header/div[2]/div')
    search_button.click()
    time.sleep(10)

    # 点击图文按钮
    short_note_button = browser.find_element(By.XPATH, '//*[@id="short_note"]')
    short_note_button.click()
    time.sleep(20)

    # 循环下载多个帖子的图片
    total_img_count = 0
    section_index = 1  # 从第一个帖子开始

    while total_img_count < img_num:
        try:
            # 每10个帖子滚动一次页面
            if section_index % 10 == 0:
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)  # 等待页面加载

            # 获取所有帖子
            posts = browser.find_elements(By.XPATH, '//*[@id="global"]/div[2]/div[2]/div/div[3]/section/div/a[2]')
            
            if section_index > len(posts):
                print("No more posts to process.")
                break

            # 点击当前帖子
            post = posts[section_index - 1]
            post.click()
            time.sleep(5)

            # 下载当前帖子的评论图片
            img_count = download_images_from_post(browser, save_path, img_num - total_img_count)
            total_img_count += img_count

            # 关闭当前帖子界面
            close_button = browser.find_element(By.XPATH, '/html/body/div[6]/div[2]')
            close_button.click()
            time.sleep(2)  # 等待关闭

            # 切换到下一个帖子
            section_index += 1

        except Exception as e:
            print(f"Error navigating to next post or downloading images: {e}")
            section_index += 1
            continue

    # 关闭浏览器
    browser.quit()

if __name__ == "__main__":
    main(save_root=r'C:\Users\admin\Desktop\xhs', img_num=2000)