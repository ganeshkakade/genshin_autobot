from selenium import webdriver
from selenium.webdriver.common.by import By
import pickle
import time
import os

daily_checkin_url = "https://webstatic-sea.mihoyo.com/ys/event/signin-sea-v3/index.html?act_id=e202102251931481"
login_url = "https://genshin.mihoyo.com/en/news"
redeem_code_url = "https://genshin.mihoyo.com/en/gift"
redeem_scraping_url = "https://www.pockettactics.com/genshin-impact/codes"
username = "" # mihoyo genshin username
password = "" # mihoyo genshin password
default_server = "Asia" # "America" "Europe" "Asia" "TW, HK, MO"

dir = os.path.dirname(__file__)
msedgedriver = os.path.join(dir, '../drivers/msedgedriver.exe')
pickle_file_path = os.path.join(dir, 'genshin_mihoyo.pkl')

browser = webdriver.Edge(msedgedriver)
browser.maximize_window()

codes = []

def wait_time(t):
    time.sleep(t)

def load_url(url):
    browser.get(url)
    # wait for url to load
    wait_time(5)

def load_refresh_url(url):
    load_url(url)

    # refresh url to reflect logged in status
    browser.refresh()
    wait_time(5)

def scrap_redeem_codes():
    load_url(redeem_scraping_url)

    code_list = browser.find_elements(By.XPATH, '//*[@id="site_wrap"]/article/div/ul[1]/li')

    for item in code_list:
        code = item.find_element(By.TAG_NAME, 'strong')
        code = code.text.strip()
        codes.append(code)

def accept_cookie_dialogue(elem_xpath):
    dialogue_btn = browser.find_elements(By.XPATH, elem_xpath)
    if dialogue_btn:
        dialogue_btn[0].click()

def load_cookies():
    try:
        with open(pickle_file_path, "rb") as f:
            file = pickle.load(f)
            for cookie in file: 
                browser.add_cookie(cookie)

    except:
        print("file error in load_cookies")

def save_cookies():
    pickle.dump(browser.get_cookies(), open(pickle_file_path, "wb"))

def is_cookies_exists():
    try:
        with open(pickle_file_path, "rb") as f:
            return True

    except:
        print("file error in is_cookies_exists")
        return False

def is_cookies_expired():
    cookies = browser.get_cookies()
    return not any(dict.get("name") == 'cookie_token' for dict in cookies)

def delete_cookie_relogin():
    browser.delete_all_cookies()

    try:
        os.remove(pickle_file_path)
    except:
        print("Error while deleting file ", pickle_file_path)

    auto_login()

def auto_login():
    load_url(login_url)
    accept_cookie_dialogue('//div[@class="mihoyo-cookie-tips__button mihoyo-cookie-tips__button--ys"]')

    login = browser.find_elements(By.XPATH, "//button[@class='login__btn']")
    login[0].click()

    user = browser.find_elements(By.XPATH, '//form[@class="mhy-account-flow-password-login"]/div[1]/div/input')
    user[0].send_keys(username)

    pwd = browser.find_elements(By.XPATH, '//form[@class="mhy-account-flow-password-login"]/div[2]/div/input')
    pwd[0].send_keys(password)

    logged_in = browser.find_elements(By.XPATH, '//form[@class="mhy-account-flow-password-login"]/div[3]/button')
    logged_in[0].click()

    # wait time for log in to complete
    # for now, user will solve the challenge manually
    wait_time(20)
    
    # dump existing loggedin cookies
    save_cookies()

def daily_checkin_process():
    load_refresh_url(daily_checkin_url)
    accept_cookie_dialogue('//button[@class="mihoyo-cookie-tips__button mihoyo-cookie-tips__button--hk4e"]')

    active_item = browser.find_elements(By.XPATH, '//div[@class="components-home-assets-__sign-content_---item---1VLDOZ components-home-assets-__sign-content_---active---36unD3"]')
    
    if active_item:
        active_item[0].click()

    # wait time for checkin completion
    wait_time(5)

def auto_daily_checkin():
    if is_cookies_exists():
        load_url(daily_checkin_url)
        load_cookies() # load cookies for daily_checkin_url

        # no cookies get expired??
        if is_cookies_expired():
            delete_cookie_relogin()

        daily_checkin_process()
    else:
        auto_login()
        daily_checkin_process()

def redeem_process():
    load_url(redeem_code_url)
    accept_cookie_dialogue('//div[@class="mihoyo-cookie-tips__button mihoyo-cookie-tips__button--ys"]')

    # open div dropdown
    select = browser.find_elements(By.XPATH, '//div[@id="cdkey__region"]')
    select[0].click()

    select_options = browser.find_elements(By.XPATH, '//div[@class="cdkey-select__option"]')

    for option in select_options:
        if option.text == default_server:
            # select server from option
            option.click()
            break
    
    redeem = browser.find_elements(By.XPATH, '//input[@id="cdkey__code"]')
    submit =  browser.find_elements(By.XPATH, '//button[@class="cdkey-form__submit"]')

    for code in codes:
        redeem[0].clear()
        redeem[0].send_keys(code)

        # wait for redeem start
        wait_time(1)
        submit[0].click()

        # wait for redeem completion
        wait_time(5)

def auto_redeem_code():
    scrap_redeem_codes()
   
    if is_cookies_exists():
        load_url(redeem_code_url)
        load_cookies() # load cookies for redeem_code_url
        
        # no cookies get expired??
        if is_cookies_expired():
            delete_cookie_relogin()

        redeem_process()
    else:
        auto_login()
        redeem_process()

if __name__ == "__main__":
    auto_redeem_code()
    auto_daily_checkin()
    
    browser.quit()