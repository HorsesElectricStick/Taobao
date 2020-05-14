"""
selenium模拟登陆淘宝
作者：马电棒
更新时间：2020年5月14日18:17:53
"""
import re,random,time
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

chrome_options = Options()
# 设置UA
chrome_options.add_argument('user-agent="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60"')
# 设置无头浏览器
# chrome_options.add_argument('--headless')
# 设置滚动条
chrome_options.add_argument('--hide-scrollbars')
# 设置最高权限
chrome_options.add_argument('--no-sandbox')
# 设置开发者模式
# chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
chrome_options.add_argument('--disable-gpu')
browser = webdriver.Chrome(chrome_options=chrome_options)
browser.maximize_window()
# 等待条件
wait = WebDriverWait(browser,10)

# 模拟登陆
def login():
    login_url = 'https://login.taobao.com'
    user_name = '可可可可熊熊熊'
    password = 'sseawayss163'
    # fm-login-id
    browser.get(login_url)
    input_user_name = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR,'#fm-login-id'))
    )
    input_password = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR,'#fm-login-password'))
    )
    submit = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,'#login-form > div.fm-btn > button'))
    )
    input_user_name.send_keys(user_name)
    time.sleep(1)
    input_password.send_keys(password)
    time.sleep(1)
    submit.click()
    # login-error > div
    if wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#login-error > div'),'请拖动滑块完成验证')):
        captcha()
    if wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#J_SiteNavLogin > div.site-nav-menu-hd > div.site-nav-user > a'),'可可可可熊熊熊')):
        print('登陆成功')
    else:
        print('登陆失败')
    time.sleep(3)

# 处理滑块验证码
def captcha():
    block = browser.find_element_by_css_selector('#nc_1_n1z')
    ActionChains(browser).click_and_hold(block).perform()
    x = random.randint(100,300)
    ActionChains(browser).move_by_offset(xoffset=x,yoffset=0).perform()
    x = 600-x
    time.sleep(0.5)
    ActionChains(browser).move_by_offset(xoffset=x,yoffset=0).perform()
    ActionChains(browser).release(on_element=block).perform()
    if wait.until(EC.text_to_be_present_in_element(
        (By.CSS_SELECTOR, '#nc_1__scale_text > span > b'), '验证通过')
    ):
        submit = browser.find_element_by_css_selector('#login-form > div.fm-btn > button')
        time.sleep(0.5)
        submit.click()
    else:
        refresh = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#nocaptcha-password > div > span > a')))
        refresh.click()
        captcha()

# 搜索商品
def search():
    try:
        browser.get('https://www.taobao.com')
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#q')))
        search_bottom = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J_TSearchForm > div.search-button > button')))
        input.send_keys('2080ti')
        search_bottom.click()
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.total')))
        return total.text
    except TimeoutException:
        return search()

# 翻页操作
def next_page(page):
    try:
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.form > input')))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        input.clear()
        input.send_keys(page)
        submit.click()

        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > ul > li.item.active > span'),str(page)))
    except TimeoutException:
        next_page(page)

def parse_item():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-itemlist .items .item')))
    html = browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text().split('人')[0],
            'title': item.find('.title').text().strip(),
            'shop': item.find('.shop').text().strip(),
            'location': item.find('.location').text().strip()
        }
        print(product)


def main():
    login()
    total = search()
    print(total)
    total = int(re.compile('(\d+)').search(total).group(1))
    print(total)
    parse_item()
    if total > 1:
        for i in range(2,total+1):
            next_page(i)
            parse_item()
            time.sleep(2)


if __name__ == '__main__':
    main()
