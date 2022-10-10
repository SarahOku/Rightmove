from ast import IsNot, Return
from attr import NOTHING
from selenium.webdriver import Chrome 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import dplython as dplyr
import uuid

class Scraper:

    def __init__(self, url:str = 'https://www.rightmove.co.uk' ):

        self.driver = Chrome(service = Service(ChromeDriverManager().install()))
        self.driver.get(url)

    def accept_cookies(self, xpath: str = '/html/body/div[1]/div[2]/div[4]/div[2]/div/button'): # used xpath = full path to locate button 
        try:

            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

            element = self.driver.find_element(By.XPATH, xpath)
            self.driver.execute_script("arguments[0].click();", element)  #was not finding the button wrapped in wrapper

        except TimeoutException:
                print('No cookies found')

    def click_find_properties(self): #/html/body/div[3]/div[2]/div/div[1]/div/form/fieldset[2]/div[4]/button
    
        try:           
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="submit"]')))

            element = self.driver.find_element(By.XPATH, '//*[@id="submit"]').click()
            
        except TimeoutException:
            print('')

    def look_for_search_bar(self, xpath: str):
    
        try:
                time.sleep(3)
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

                element = self.driver.find_element(By.XPATH, xpath)
                search_bar_look = element.click()
                #search_bar_look = self.driver.execute_script("arguments[0].click();", element)  

                return element

        except TimeoutException:
                    print('No searchbar found')   #Returns Nothing           
                    return None

    def input_location_to_search_bar(self, text):
        search_bar = self.look_for_search_bar('//*[@id="_3OuiRnbltQyS534SB4ivLV"]/div/div/div/div/input')
        
        if search_bar:
           search_bar.send_keys(text)
           search_bar.send_keys(Keys.ENTER)
           self.click_find_properties()
           
        else:
            raise  Exception('No Searchbar was found')

    def find_result_search_container(self, xpath: str = '//div[@id="l-searchResults"]/div'):
        try:
            return self.driver.find_element(By.XPATH, xpath)
        except:
            print('')
    
    def list_all_prop(self):
        container = self.find_result_search_container()
        list_properties = container.find_elements(By.XPATH, '//a[@class="propertyCard-link property-card-updates"]')

        link_list = []
        
        for property in list_properties:
            link_list.append(property.get_attribute('href'))      
        return link_list

    def collect_prop_data(self):

        link_list = self.list_all_prop()
        id = uuid.uuid4()
        

        property_dict = {    
                        'UUID': id, 
                        'Link':[],
                        'Price':[],
                        'Bedrooms':[],
                        'Sqft':[],
                        'Date Added':[]
        }

        for link in link_list[0:5]:
            
            self.driver.get(link)
            time.sleep(1)
            property_dict['Link'].append(link)

          #  id = range(1,50)
          #  property_dict['ID'].append(id)
            
            try:
                price = self.driver.find_element(By.XPATH,'//div[@class="_1gfnqJ3Vtd1z40MlC0MzXu"]/span')
                property_dict['Price'].append(price.text)
            except NoSuchElementException:
                property_dict['Price'].append('N/A')
            try:
                bedrooms = self.driver.find_element(By.XPATH, '/html/body/div[4]/main/div/div[3]/div/article[2]/div[2]/div[3]/div[2]/div[2]/p')
                property_dict['Bedrooms'].append(bedrooms.text) #/html/body/div[4]/main/div/div[3]/div/article[2]/div[2]/div[3]/div[2]/div[2]/p
            except NoSuchElementException:  
                property_dict['Bedrooms'].append('N/A')
            try:
                sqft = self.driver.find_element(By.XPATH, '//*[@id="root"]/main/div/div[3]/div/article[2]/div[2]/div[4]/div[2]/div[2]/div[1]') 
                property_dict['Sqft'].append(sqft.text)
            except NoSuchElementException:
                property_dict['Sqft'].append('N/A')
            try:
                date_added = self.driver.find_element(By.XPATH, '//*[@id="root"]/main/div/div[3]/div/article[1]/div/div/div[2]/div/div') 
                property_dict['Date Added'].append(date_added.text)
            except NoSuchElementException:
                property_dict['Date Added'].append('N/A')
            
        return property_dict

    def display_data(self):
        data_display = self.collect_prop_data()

       
        df = pd.DataFrame(data_display)
        
        df.insert(0, 'New_ID', range(1, 1 + len(df)))
        #df['uuid'] = uuid.uuid4() -another way of implementing uuid in the dataframe columns 

        return df


if __name__ == '__main__':
    bot = Scraper()
    bot.accept_cookies()
    bot.input_location_to_search_bar('Manchester')
    bot.find_result_search_container()
    bot.collect_prop_data()
    bot.display_data()