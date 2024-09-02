from robocorp.tasks import task
import calendar
import time
import pandas as pd
from datetime import date, datetime, timedelta
import os
import requests
import shutil

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
    path_images = "./Images_downloaded"
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
        "LIVE BLOGS": True,
        "PHOTO GALLERIES": False,
        "STORIES": True,
        "SUBSECTIONS": False,
        "VIDEOS":False
    }
    path_report_df = "./Report.xlsx"
    path_db_states_df = "./States.xlsx"

    # Open Edge Browser and Objects
    object_browser_flow = CreateBrowserDriverFlow(news_url, 20,0)
    object_browser_flow.status_webpage()

    

    dictionary_date = converter_dic_of_date(number_months)


    # Create Dataframes to report with news information and DB to manage flow states
    columns_report_df = [
        "title",
        "date",
        "description",
        "picture_filename_downloaded"
        ]
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
            db_states_df = partial_update_dataframe(
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

        if(object_browser_flow.state ==0):
            flag_state_0 = object_browser_flow.flow_search(dictionary_category,search_phrase)
            if(flag_state_0):
                object_browser_flow.state = 1
                db_states_df = partial_update_dataframe(
                    db_states_df,path_db_states_df,[0],[0],
                    [object_browser_flow.state])

        elif(object_browser_flow.state == 1):
            flag_state_1 = object_browser_flow.extract_news_information(report_df,path_report_df,path_images,dictionary_date)
            if(flag_state_1):
                object_browser_flow.state = 100
                db_states_df = partial_update_dataframe(
                    db_states_df,path_db_states_df,[0],[0],
                    [object_browser_flow.state])
    
    print("==== Finished the processes ====")



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
        dictionary_date (dict): Dictionary of dates range.

    Returns:
        flag_date (boolean): True if news date is into dates dictionary, False isn't.
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



def partial_update_dataframe(dataframe,path,rows_index_list, columns_index_list,data_list):
    
    dataframe.iloc[rows_index_list,columns_index_list] = data_list
    dataframe.to_excel(path,index=False)
    return dataframe

class CreateBrowserDriverFlow:
    """Class to create a Browser driver"""

    def __init__(self, url, timeout_web, state):
        self.state = state
        self.flow_search_flag = False
        self.flow_extract_flag = False
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

    def borrar_contenido_carpeta(path_folder):
        # Verifica si la path_folder existe
        if not os.path.exists(path_folder):
            print(f"La path_folder {path_folder} no existe.")
            return

        # Recorre todos los archivos y carpetas dentro de la path_folder especificada
        for filename in os.listdir(path_folder):
            file_path = os.path.join(path_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Borra el archivo o enlace simbólico
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Borra la path_folder y todo su contenido
            except Exception as e:
                print(f"No se pudo borrar {file_path}. Razón: {e}")

        print(f"Todo el contenido de la path_folder {path_folder} ha sido borrado.")

    def extract_news_information(self, dataframe_report,path_report_df,path_images,dictionary_date):
        """extract_news_information: Extract information from news listed that which one follow the rules.

        Args:
            dataframe_report (dataframe): Datframe report, where we will save the news information.
            path_report_df (str): Path where we will save report in Excel format.
            path_images (str): Path where we will save news images.
        """
        self.flow_extract_flag = False
        flag_flow = True

        def first_save_dataframe(data_row):
            # Save information in Dataframe and save this in a excel.
            dataframe_report .loc[dataframe_report.shape[0]] = data_row
            dataframe_report.to_excel(path_report_df,index=False)

        def last_save_dataframe(data_row):
            # Save information in Dataframe and save this in a excel.
            dataframe_report.loc[dataframe_report.index[-1]] = data_row            
            dataframe_report.to_excel(path_report_df,index=False)
    
        self.key_escape_message()

        image_counter = 1
        original_windows = self.driver.current_window_handle
        while(flag_flow):

            windows_number = len(self.driver.window_handles)
            windows_opened = self.driver.window_handles
            if(windows_number > 1):
                self.driver.switch_to.window(windows_opened[1])
                self.driver.close() # Close New Borwser Tab
                self.driver.switch_to.window(original_windows)

            div_2 = self.driver.find_element(By.CLASS_NAME,"SearchResultsModule-results")
            news_divs_list_elements = div_2.find_elements(By.CLASS_NAME,"PageList-items-item")
            for new_div_element in news_divs_list_elements:
                try:
                    self.key_escape_message()

                    title = ""
                    description = ""
                    new_date = ""
                    picture_filename_downloaded = ""
                    data_row = [title,new_date,description,picture_filename_downloaded]

                    # Extract Title
                    div_title = new_div_element.find_element(By.CLASS_NAME,"PagePromo-title")
                    title = str(div_title.find_element(By.TAG_NAME,"span").text).strip()
                    data_row = [title,new_date,description,picture_filename_downloaded]
                    first_save_dataframe(data_row)

                    # Open new in new browser tab to extract Date                    
                    a_link_title = div_title.find_element(By.TAG_NAME,"a")
                    WebDriverWait(self.driver,5).until(EC.element_to_be_clickable(a_link_title))
                    a_link_title.send_keys(Keys.CONTROL + Keys.RETURN)
                    original_windows = self.driver.current_window_handle
                    for i in range(1,20): 
                        time.sleep(0.5)
                        windows_opened = self.driver.window_handles
                        windows_number = len(self.driver.window_handles)
                        if(windows_number > 1):
                            self.driver.switch_to.window(windows_opened[1])
                            break
                    if(windows_number > 1):
                        try:
                            main_div_new_browser_tab = self.driver.find_element(By.CLASS_NAME,"Page-content")
                            bsp_element = main_div_new_browser_tab.find_element(By.TAG_NAME,"bsp-timestamp")
                            new_date = str(bsp_element.find_element(By.TAG_NAME,"span").text).strip()
                            list_date_text = new_date.split(',')
                            date_text_1 = str(list_date_text[1] + ',' + list_date_text[2]).strip()
                            if(verify_dictionary_date(date_text_1, dictionary_date)):
                                data_row = [title,new_date,description,picture_filename_downloaded]
                                last_save_dataframe(data_row)
                            else: 
                                flag_flow = False
                                break
                        except:                            
                            print("Exception to try extracting date information, posibly this new doesn't have date.")
                        self.driver.close() # Close New Borwser Tab
                        self.driver.switch_to.window(original_windows)

                    # Extract Description
                    description = str(new_div_element.find_element(By.TAG_NAME,"span").text).strip()
                    data_row = [title,new_date,description,picture_filename_downloaded]
                    last_save_dataframe(data_row)

                    # Donwload image and save the picture file name
                    try:
                        list_divs = new_div_element.find_elements(By.TAG_NAME,"div")
                        div_data = ""
                        for div_1 in list_divs:
                            print(f"{div_1.get_attribute('class')}")
                            if(div_1.get_attribute('class') == "PagePromo"):
                                div_data = div_1
                                break
                        image_element = div_data.find_element(By.TAG_NAME,"img")
                        image_url = image_element.get_attribute('src')
                        image_data = requests.get(image_url).content
                        # Download the image
                        os.makedirs(os.path.dirname(path_images), exist_ok=True)
                        self.borrar_contenido_carpeta(path_images)
                        with open(path_images + f"image_{image_counter}",'wb') as file:
                            file.write(image_data)
                        picture_filename_downloaded = f"image_{image_counter}"
                        data_row = [title,new_date,description,picture_filename_downloaded]
                        last_save_dataframe(data_row)
                        image_counter += 1
                    except:
                        print("The new doesn't have image.")

                except Exception as e: # Exception For
                    print(f"Exception, {e},{e.args},{e.__cause__}")
            
        self.flow_extract_flag = True

    def key_escape_message(self):
        tipo_elemento = "TAG_NAME"
        nombre_elemento = "a"
        diccionario_atributos = {
            "title":"Close",
            "class":"fancybox-item fancybox-close"
        }

        for i in range(4,9):
            try:
                raiz_xpath = f'/html/body/div[{i}]'
                element_x_donate = self.find_element_attribute_text(raiz_xpath,tipo_elemento,nombre_elemento,diccionario_atributos,texto_buscar="",busca_texto=False)                
                if(not isinstance(element_x_donate,str)):
                    ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                    break
            except: pass
        
    def flow_search(self,dictionary_category,search_phrase):
        """flow_search: Function to execute the searching about phrase.

        Args:
            dictionary_category (dict): Dictionary of categories filters.
            search_phrase (str): Phrase to search.
        Returns:
            flow_search_flag (boolean): True execute correctly the process, False doen't.
        """

        try:
            self.key_escape_message()
            WebDriverWait(self.driver,5).until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME,"SearchOverlay-search-button")
                )
            ).click() # serching button
            element_box_input_phrase = WebDriverWait(self.driver,5).until(EC.element_to_be_clickable(
                (By.CLASS_NAME,"SearchOverlay-search-input")
            ))
            element_box_input_phrase.clear()
            element_box_input_phrase.send_keys(search_phrase)            
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            self.key_escape_message()
            sort_by_element = Select(WebDriverWait(self.driver,5).until(EC.element_to_be_clickable(
               (By.CLASS_NAME,"Select-input")
            )))
            sort_by_element.select_by_value("3") # Newest
            self.key_escape_message()
            element_div_categories_filter = WebDriverWait(self.driver,5).until(EC.presence_of_element_located(
                (By.CLASS_NAME,"SearchResultsModule-filters-content")
            ))
            li_filter_elements = element_div_categories_filter.find_elements(By.TAG_NAME,"li")

            for li_element in li_filter_elements:
                filter_text = str(li_element.find_element(By.TAG_NAME,"span").text).strip()
                filter_input_element = li_element.find_element(By.TAG_NAME,"input")
                if(filter_text in dictionary_category):
                    if(dictionary_category[filter_text]):
                        filter_input_element.click()
                else:
                    print("Doesnt exist this filter in dictionary_category")
                self.key_escape_message()            

            WebDriverWait(self.driver,5).until(EC.presence_of_element_located(
                (By.CLASS_NAME,"SearchFilter-seeAll-button")
            )).click() # Button SEE ALL
            self.key_escape_message()

            self.flow_search_flag = True

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
        
    def find_element_attribute_text(self, raiz_xpath,tipo_elemento,nombre_elemento,diccionario_atributos={},texto_buscar="",busca_texto=False):
        """check_exists_by_class: Validate if the element by Tag Name
        exists using Selenium."""
        try:
            lista_elementos = []
            elemento_buscado = ""
            def filtrar_Atributos(lista_elementos_1,diccionario_atributos_1):
                lista_elementos_filtrado = []
                if(len(diccionario_atributos_1) == 0):
                    lista_elementos_filtrado = lista_elementos_1
                else:
                    for elemento in lista_elementos_1:
                        conteo_atributos = 0
                        for name_atributo,value in diccionario_atributos.items():
                            valor_atributo = elemento.get_attribute(name_atributo)
                            if(str(value) in str(valor_atributo)):
                                conteo_atributos +=1
                        if(conteo_atributos == len(diccionario_atributos_1)):
                            lista_elementos_filtrado.append(elemento)
                return lista_elementos_filtrado
            
            raiz_elemento = self.driver.find_element(By.XPATH, raiz_xpath)
            if(tipo_elemento == "TAG_NAME"): 
                lista_elementos = raiz_elemento.find_elements(By.TAG_NAME,nombre_elemento)
            elif(tipo_elemento == "CLASS_NAME"):
                lista_elementos = raiz_elemento.find_elements(By.CLASS_NAME,nombre_elemento)
            elif(tipo_elemento == "XPATH"):
                lista_elementos = raiz_elemento.find_elements(By.XPATH,nombre_elemento)
            elif(tipo_elemento == "ID"):
                lista_elementos = raiz_elemento.find_elements(By.ID,nombre_elemento)
            
            lista_elementos = filtrar_Atributos(lista_elementos,diccionario_atributos)
            if(busca_texto):
                for elemento in lista_elementos:
                    if(texto_buscar in elemento.text):
                        elemento_buscado = elemento
                        print(f"Encontro el elemento tipo {tipo_elemento} con nombre {nombre_elemento} '{texto_buscar}'")
                        break
            elif (len(lista_elementos)>0 and len(lista_elementos) < 2):
                elemento_buscado = lista_elementos[0]
        except Exception as e:
            print(f"Exception, {e},{e.args},{e.__cause__}")
        
        finally:
            return elemento_buscado
