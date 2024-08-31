from robocorp.tasks import task
import calendar
import time
import pandas as pd
from datetime import date, datetime, timedelta

from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert



@task
def main_task():
    """main_task: This function executes all flow of our robot, this is
    about searching news"""

    # Variables Definition
    search_phrase = "Donald Trump"
    number_months = 2
    news_url = "https://apnews.com/"
    dictionary_date = {}
    dictionary_month_to_text = {
        1:"Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec"
    }
    dictionary_category = {
        "LIVE BLOGS": False,
        "PHOTO GALLERIES": False,
        "STORIES": False,
        "SUBSECTIONS": False,
        "VIDEOS":False,
        "ALL": False
    }
    path_report_df = "./Report.xlsx"
    path_db_states_df = "./States.xlsx"

    # Open Edge Browser and Objects
    object_browser_flow = CreateBrowserDriverFlow(news_url, 20,0)
    object_browser_flow.status_webpage()

    object_handle_dataframe = HandleDataframe()

    dictionary_date = converter_dic_of_date(number_months)


    # Create Dataframes to report with news information and DB to manage flow states
    columns_report_df = [
        "title",
        "date",
        "description",
        "picture_filename",
        "count_search_phrases",
        "flag_money",
        "picture_filename_downloaded", 
        "state",
        "message"]
    columns_db_states = [
        "state",
        "message"]
    try:
        report_df = pd.read_excel(path_report_df)
    except:
        report_df = pd.DataFrame(columns=columns_report_df)
    
    try:
        db_states_df = pd.read_excel(path_db_states_df)
        object_browser_flow.state = db_states_df.loc[0,"state"]
        if(object_browser_flow.state == 100): # Reset state to start new flow
            object_browser_flow.state = 0
            db_states_df = object_handle_dataframe.partial_update_dataframe(
                db_states_df,path_db_states_df,[0],[0],[0])

    except:
        object_browser_flow.state = 0
        db_states_df = pd.DataFrame(columns=columns_db_states)
        db_states_df .loc[db_states_df.shape[0]] = [
            object_browser_flow.state,""
            ] 
        db_states_df.to_excel(path_db_states_df,index=False)

    

    # Start the managing of flow state
    while(object_browser_flow.state<100):
        
        # State 0 to search news about phrase and extract relevant 
        # information like title and description. Then put these 
        # in the report.
        if(object_browser_flow.state ==0):
            flag_state_0 = object_browser_flow.flow_search(
                dictionary_category,search_phrase)
            if(flag_state_0):
                object_browser_flow.state = 1
                db_states_df = object_handle_dataframe.partial_update_dataframe(
                    db_states_df,path_db_states_df,[0],[0],
                    [object_browser_flow.state])

        elif(object_browser_flow.state == 1):
            pass
        elif(object_browser_flow.state == 2):
            pass

# Definition of Classes and Funtions

def converter_dic_of_date(number_months):
    """converter_dic_of_date:Create a dictionary with dates of news that include in the report.

    Args:
        number_months (int): Number of months to count.

    Returns:
        months_dictionary (dict): Dictionary with dates to verify news.
    """
    current_date = datetime.now()
    
    # Create dictionary
    months_dictionary = {}
    
    for i in range(number_months + 1):
        # Calculate month and year
        month = (current_date.month - i - 1) % 12 + 1
        year = current_date.year - ((current_date.month - i - 1) // 12)
        
        # Add to dictionary
        months_dictionary[i] = [month, year]
    
    return months_dictionary

def verify_dictionary_date(date_text, dictionary_date):
    """verify_dictionary_date: Verify new's date if it is in date dictionary.

    Args:
        date_text (str): New Date Text. Example: "August 30, 2024"
        dictionary_date (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Converter Date text in a object datetime
    fecha = datetime.strptime(date_text, "%B %d, %Y")

    # Variable to return
    flag_date = False
    

    # Extract month and year from date
    mes = fecha.month
    año = fecha.year
    
    # Verify if the news month and year are in dictionary_date
    for key in dictionary_date:
        if dictionary_date[key] == [mes, año]:
            flag_date = True
            break
    return flag_date

class HandleDataframe():
    """class to manage dataframe"""

    def partial_update_dataframe(self,dataframe,path,rows_index_list, 
                                 columns_index_list,data_list):
        
        dataframe.iloc[rows_index_list,columns_index_list] = data_list
        dataframe.to_excel(path,index=False)
        return dataframe

class CreateBrowserDriverFlow:
    """Class to create a Browser driver"""

    def __init__(self, url, timeout_web, state):
        self.state = state
        self.flow_search_flag = False
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

    def flow_search(self,dictionary_category,search_phrase):
        """flow_search: Function to execute the searching about phrase.

        Args:
            dictionary_category (dict): Dictionary of categories filters.
            search_phrase (str): Phrase to search.
        Returns:
            flow_search_flag (boolean): True execute correctly the process, False doen't.
        """
        try:
            WebDriverWait(self.driver,5).until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME,"SearchOverlay-search-button")
                )
            ).click() # serching button
            element_box_input_phrase = WebDriverWait(self.driver,5).until(EC.element_to_be_clickable(
                By.CLASS_NAME,"SearchOverlay-search-input"
            ))
            element_box_input_phrase.clear()
            element_box_input_phrase.send_keys(search_phrase)

        except Exception as e:
            print(f"Exception, {e},{e.args},{e.__cause__}")
        finally:            
            return self.flow_search_flag
        
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
