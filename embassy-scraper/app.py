import os
import selenium
import logging
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import chromedriver_autoinstaller
from dotenv import load_dotenv
from datetime import datetime
import requests

# configuration
BASEDIR = os.path.dirname(os.path.realpath(__file__))

# environment variables
load_dotenv(f"{BASEDIR}/.env")

# additional variables
# .env doesn't support chinese characters
SECURITY_QUESTION = "您11岁的时候在哪所学校上学"
SECURITY_ANSWER = "灯市口小学"

if os.name == 'nt':
    chromedriver_autoinstaller.install()

chrome_options = Options()
if os.getenv('HEADLESS') == 'True':
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--window-size={}'.format("1920,1080"))
if os.name != 'nt':  # for docker
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}


class HomePage:
    def __init__(self, driver):
        self.driver = driver

    def click_login(self):
        login_btn = self.driver.find_element_by_id("continueReservation")
        self.driver.execute_script("arguments[0].click()", login_btn)

    def enter_user_id(self, user_id):
        id_input = self.driver.find_element_by_id("recordNumberHuifu")
        id_input.send_keys(user_id)

    def enter_security_question_answer(self, question, answer):
        question_input = self.driver.find_element_by_id("questionIDHuifu")
        options = question_input.find_elements_by_tag_name("option")
        for option in options:
            if question in option.text:
                option.click()
                break
        answer_input = self.driver.find_element_by_id("answerHuifu")
        answer_input.send_keys(answer)

    def confirm_login(self):
        buttons = self.driver.find_elements_by_class_name(
            "ui-button-text-only")
        [btn for btn in buttons if btn.text == "提交"][0].click()


class ReservationPage:
    def __init__(self, driver):
        self.driver = driver

    def click_proceed(self):
        proceed_btn = self.driver.find_element_by_id("myButton")
        proceed_btn.click()

    def click_confirm(self):
        buttons = self.driver.find_elements_by_class_name(
            "ui-button-text-only")
        confirm_btn = [btn for btn in buttons if btn.text == "确认"][0]
        confirm_btn.click()

    def click_dropdown(self):  # choose dropdown option
        select_input = self.driver.find_element_by_id("address")
        options = select_input.find_elements_by_tag_name("option")
        for option in options:
            if "多伦多不见面办理" in option.text:
                option.click()
                break

    def get_reservation_info(self):  # for current month
        titles = self.driver.find_elements_by_class_name("fc-event-title")
        info = [title.text.strip() for title in titles if title.text.strip()]
        return info

    def go_to_next_month(self):
        next_btn = self.driver.find_element_by_class_name("fc-button-next")
        next_btn.click()


def check_reservations():
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(3)
    driver.get(os.getenv('EMBASSY_URL'))

    # login
    home_page = HomePage(driver)
    home_page.click_login()
    home_page.enter_user_id(os.getenv("USER_ID"))
    home_page.enter_security_question_answer(
        SECURITY_QUESTION, SECURITY_ANSWER)
    home_page.confirm_login()

    # view reservation options
    reservation_page = ReservationPage(driver)
    reservation_page.click_proceed()
    time.sleep(5)  # give time for reservation slots to load
    reservation_page.click_confirm()
    reservation_page.click_dropdown()
    month = datetime.now().month
    num_scanned = 0
    info = {}
    while True and num_scanned < 6:
        reservation_info = reservation_page.get_reservation_info()
        info[month] = reservation_info
        if not reservation_info:
            break
        print(reservation_info)
        reservation_page.go_to_next_month()
        month = month + 1 if month < 12 else 1
        num_scanned += 1

    for k, v in info.items():
        for e in v:
            booked, total = e.split('/')
            if booked != total:  # send discord message
                msg = (
                    f"found available reservation for month = {k}, data = {v}. "
                    f"visit {os.getenv('EMBASSY_URL')}"
                )
                requests.post(url=os.getenv("WEBHOOK_URL"), data={"content": msg})
                break


if __name__ == "__main__":

    first_run = True

    while True:
        try:
            print("running embassy bot at {}".format(datetime.now()))
            check_reservations()
        except:
            print("unable to check reservations at {}".format(datetime.now()))

        if first_run:
            msg = "Bot is healthy and running every 5 minutes as of {}".format(datetime.now())
            requests.post(url=os.getenv("WEBHOOK_URL"), data={"content": msg})
            first_run = False

        time.sleep(60*5)
