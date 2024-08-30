from robocorp.tasks import task
import calendar
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC


@task
def main_task():
    """main_task: This function executes all flow of our robot, this is
    about searching news"""
    # Variables Definition
    search_phrase = ""
    news_category = ""
    number_months = 0
    news_url = "https://apnews.com/"

    # Open Edge Browser
    browser_object = CreateBrowserDriver(news_url, 20)
    browser_object.status_webpage()

    # Create Dataframes to report with news information and DB to manage flow states
    columns_report_df = ["title","date","description","picture_filename",
                         "count_search_phrases","flag_money","picture_filename_downloaded"]
    columns_DB_states = ["estado","message"]


class CreateBrowserDriver:
    """Class to create a Browser driver"""

    def __init__(self, url, timeout_web):
        self.url = url
        self.timeout_web = timeout_web
        self.edge_options = webdriver.EdgeOptions()
        self.edge_options.add_argument("--incognito")
        self.edge_options.add_argument("no-sandbox")
        self.edge_options.add_argument("--disable-gpu")
        self.edge_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Edge(options=self.edge_options)
        self.driver.set_page_load_timeout(timeout_web)
        self.driver.maximize_window()
        self.driver.get(self.url)

    def status_webpage(self):
        """status_webpage: Function to verify web page status."""
        self.flag_status = True
        while self.flag_status:
            try:
                self.div_button_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "Page-header-stickyWrap")
                    )
                )
                if self.check_exists_by_xpath(
                    '//*[@id="Page-header-trending-zephr"]/div[2]/div[1]/a'
                ):
                    print("The webpage is working.")
                    self.flag_status = False
                else:
                    print("Possibly the webpage isn't working.")
                    self.driver.get(self.url)
                    time.sleep(60)  # wait 1 minute to try again
            except TimeoutException:
                print("Exception, timeout on the web page.")
                time.sleep(60)  # wait 1 minute to try again
            except Exception as e:
                print(f"Unexpected exception: {e}, {e.args}, {e.__cause__}")
                time.sleep(60)  # wait 1 minute to try again

    def check_exists_by_css_selector(self, selector):
        """check_exists_by_css_selector: Validate if the CSS Selector
        element exists using Selenium."""
        try:
            self.driver.find_element(By.CSS_SELECTOR, "{}".format(selector))
        except NoSuchElementException:
            print(f"Element By.CSS_SELECTOR '{selector}' does not exist on the "
                  "webpage.")
            return False
        else:
            print(f"Element By.CSS_SELECTOR '{selector}' exists on the "
                  "webpage.")
            return True

    def check_exists_by_xpath(self, xpath):
        """check_exists_by_xpath: Validate if the Xpath element exists
        using Selenium."""
        try:
            self.driver.find_element(By.XPATH, "{}".format(xpath))
        except NoSuchElementException:
            print(f"Element By.XPATH '{xpath}' does not exist on the webpage.")
            return False
        else:
            print(f"Element By.XPATH '{xpath}' exists on the webpage.")
            return True

    def check_exists_by_name(self, name):
        """check_exists_by_name: Validate if the element with Name exists
        using Selenium."""
        try:
            self.driver.find_element(By.NAME, "{}".format(name))
        except NoSuchElementException:
            print(f"Element By.NAME '{name}' does not exist on the webpage.")
            return False
        else:
            print(f"Element By.NAME '{name}' exists on the webpage.")
            return True

    def check_exists_by_id(self, name_id):
        """check_exists_by_id: Validate if the element with ID exists
        using Selenium."""
        try:
            self.driver.find_element(By.ID, "{}".format(name_id))
        except NoSuchElementException:
            print(f"Element By.ID '{name_id}' does not exist on the webpage.")
            return False
        else:
            print(f"Element By.ID '{name_id}' exists on the webpage.")
            return True

    def check_exists_by_class(self, class_name):
        """check_exists_by_class: Validate if the element by Class Name
        exists using Selenium."""
        try:
            self.driver.find_element(By.CLASS_NAME, "{}".format(class_name))
        except NoSuchElementException:
            print(f"Element By.CLASS_NAME '{class_name}' does not exist on the "
                  "webpage.")
            return False
        else:
            print(f"Element By.CLASS_NAME '{class_name}' exists on the "
                  "webpage.")
            return True
