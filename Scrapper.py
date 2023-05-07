from bs4 import BeautifulSoup
from configparser import ConfigParser
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
import time
import pandas as pd
import abc

config = ConfigParser()
config.read('config.ini')

HELIOSAPOTHEKE_USERNAME = config['HELIOSAPOTHEKE']['USERNAME']
HELIOSAPOTHEKE_PASSWORD = config['HELIOSAPOTHEKE']['PASSWORT']
ABCAPOTHEKE_USERNAME = config['ABCAPOTHEKE']['USERNAME']
ABCAPOTHEKE_PASSWORD = config['ABCAPOTHEKE']['PASSWORT']
BROKKOLI_PASSWORD = config['BROKKOLIAPOTHEKE']['PASSWORT']
GRUENHORN_PASSWORD = config['GRUENHORNAPOTHEKE']['PASSWORT']
CANFLOS_PASSWORD = config['CANFLOSAPOTHEKE']['PASSWORT']

PATH = config['CHROME']['PATH']


class Apotheke(metaclass=abc.ABCMeta):
    
    
    def __init__(self):
        self.NAME = 'ERROR'

    def updateData(self):
        print('Updating', self.NAME, '...')
        source = self.getHTML()
        items = self.getItems(source)
        self.writeCSV(self.NAME, items)
    
    @abc.abstractmethod
    def getHTML(self):
        pass

    @abc.abstractmethod
    def getItems(self,htlm):
        pass

    def writeCSV(self,file_name,items):
        df = pd.DataFrame(items, columns=['name', 'price'])
        df = df.drop_duplicates()
        df.to_csv('data\\'+file_name, index=False)
    
    def getDriver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument("--log-level=3")
        return webdriver.Chrome(PATH, options=chrome_options)

class GruenhornApotheke(Apotheke):
    
    url_login = "https://www.gruenhorn.de/preise/"
    url_data = "https://www.gruenhorn.de/preise/?_form=blueten"

    def __init__(self):
        self.NAME = 'GruenhornApotheke.csv'
        

    def getHTML(self):
        driver = self.getDriver()
        driver.get(self.url_login)
        time.sleep(3)
        driver.find_element(By.XPATH, '//*[@id="tarteaucitronAccept"]').click()
        driver.find_element(By.XPATH, '//*[@id="pwbox-3290"]').send_keys(GRUENHORN_PASSWORD)
        driver.find_element(By.XPATH, '//*[@id="post-3290"]/div/form/p[2]/input').click()
        time.sleep(3)
        driver.get(self.url_data)
        time.sleep(3)
        response = driver.find_element(By.XPATH, '//html').get_attribute('outerHTML')
        return response
    
    def getItems(self, htlm):
        soup = BeautifulSoup(htlm, 'html.parser')
        list_element = soup.find_all('article')
        items = []
        for li in list_element:
            name = li.find('div', {'class': 'lb-name'})
            price = li.find('span', {'class': 'lb-preis'})
            stock = li.find(string=re.compile('nicht'))
            if not stock and name != None and price != None:
                item_name = name.text.strip()
                item_price = price.text.strip().replace('PREIS:', '').replace('€', '').replace('für 1 g', '').replace(',', '.').strip().replace(' für 1g', '')
                items.append({'name': item_name, 'price': item_price})
        return items


class AbcApotheke(Apotheke):

    url_login = "https://abc-cannabis.de/my-account"
    url_data = "https://abc-cannabis.de/livebestand"
    
    def __init__(self):
        self.NAME = 'AbcApotheke.csv'

    def getHTML(self):
        driver = self.getDriver()
        driver.get(self.url_login)
        time.sleep(3)
        driver.find_element(By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowallSelection"]').click()
        driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(ABCAPOTHEKE_USERNAME)
        driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(ABCAPOTHEKE_PASSWORD)
        driver.find_element(By.XPATH, '//*[@id="post-9"]/div/div/div/div/div[1]/div/div/form/p[3]/button').click()
        time.sleep(3)
        driver.get(self.url_data)
        time.sleep(3)
        response_inventory = driver.find_element(By.XPATH, '//html').get_attribute('outerHTML')
        return response_inventory
    
    def getItems(self, htlm):
        soup = BeautifulSoup(htlm, 'html.parser')
        list_element = soup.find_all('tr')
        list_element.pop(0)

        items = []
        for li in list_element:
            item_price_item = li.find(string=re.compile('Gramm'))
            if item_price_item :
                item_price = str(item_price_item.split("/")[0]).replace('€', '').strip()
            else:
                item_price = "None".strip()
            item_name = str(li.find('a').text).replace("\n", '').replace('  ', ' ').replace('"', '').strip()
            if(item_name.__contains__('\\')):
                item_name = item_name.split("\\")[0].strip()
            stock = li.find(string=re.compile('Nicht'))
            if not stock:
                items.append({'name': str(item_name), 'price': str(item_price)})
        return items

    
class HeliosApotheke(Apotheke):
    
    url_login = "https://helios-cannabis.de/wp-login.php"

    def __init__(self):
        self.NAME = 'HeliosApotheke.csv'
    
    def getHTML(self):
        driver = self.getDriver()
        driver.get(self.url_login)
        time.sleep(3)
        driver.find_element(By.XPATH, '//*[@id="user_login"]').send_keys(HELIOSAPOTHEKE_USERNAME)
        driver.find_element(By.XPATH, '//*[@id="user_pass"]').send_keys(HELIOSAPOTHEKE_PASSWORD)
        driver.find_element(By.XPATH, '//*[@id="sso_default_login"]').click()
        time.sleep(3)
        htmls = []
        for i in range(1, 11):
            url_sortiment = "https://helios-cannabis.de/sortiment/page/"+ str(i) +"?lieferbar=auf-lager,bald-verfuegbar"
            driver.get(url_sortiment)
            time.sleep(3)
            response_sortiment = driver.find_element(By.XPATH, '//html').get_attribute('outerHTML')
            htmls.append(response_sortiment)
        return htmls
    
    def getItems(self, htlm):
        items = []
        for h in htlm:
            soup = BeautifulSoup(h, 'html.parser')
            list_element = soup.find_all('li', class_='product')
            for li in list_element:
                item_name = li.find('h2').text.strip()
                item_price = li.find('bdi').text.strip().replace('€', '').replace(',', '.').strip()
                items.append({'name': item_name, 'price': item_price})
        return items
    

class BrokkoliApotheke(Apotheke):
    
    URL_LOGIN = "https://live.420brokkoli.de/"

    def __init__(self):
        self.NAME = '420BrokkoliApotheke.csv'
    def getHTML(self):
        driver = self.getDriver()
        driver.get(self.URL_LOGIN)
        time.sleep(3)
        driver.find_element(By.XPATH, '//*[@id="Passwort"]').send_keys(BROKKOLI_PASSWORD)
        driver.find_element(By.XPATH, '//*[@id="main-form-container"]/div/div/div[3]/button').click()
        time.sleep(3)
        html = driver.find_element(By.XPATH, '//html').get_attribute('outerHTML')
        return html
    
    def getItems(self, htlm):
        soup = BeautifulSoup(htlm, 'html.parser')
        list_element = soup.find_all('tr')
        list_element.pop(0)
        items = []
        for li in list_element:
            stock = li.find('td', {'data-label': 'Vorrat'})
            item_name = li.find('td', {'data-label': 'Blüte'})
            item_price = li.find('td', {'data-label': 'Preis (in € / pro g)'})
            if stock != None and item_name != None and item_price != None:
                item_price_str = str(item_price.text).replace(',', '.').strip()
                item_name_str = str(item_name.text).strip()
                stock_str = str(stock.text).strip()
                if not stock_str.__contains__('Nicht'):
                    items.append({'name': item_name_str, 'price': item_price_str})
        return items

class CannflosApotheke(Apotheke):
    URL_LOGIN = "https://cannflos-apo.de/preise/"

    def __init__(self):
        self.NAME = 'CannflosApotheke.csv'

    def getHTML(self):
        driver = self.getDriver()
        driver.get(self.URL_LOGIN)
        time.sleep(3)
        driver.find_element(By.XPATH, '//*[@id="wt-cli-accept-all-btn"]').click()
        driver.find_element(By.XPATH, '//*[@id="pwbox-17321"]').send_keys(CANFLOS_PASSWORD)
        driver.find_element(By.XPATH, '/html/body/form/p[2]/input').click()
        time.sleep(10)
        html = []
        html.append(driver.find_element(By.XPATH, '//html').get_attribute('outerHTML'))
        for i in range(5):
            try:
                nextPage = '//*[@id="table_1_next"]'
                element = driver.find_element(By.XPATH, nextPage)
                driver.execute_script("arguments[0].scrollIntoView();", element)
                WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, nextPage)))
                element.click()
                time.sleep(2)
                html.append(driver.find_element(By.XPATH, '//html').get_attribute('outerHTML'))
            except (TimeoutException, ElementNotInteractableException):
                break
        return list(set(html)) #remove duplicates

    def getItems(self, htlm):
        items = []
        for h in htlm:
            soup = BeautifulSoup(h, 'html.parser')
            list_element = soup.find_all('tr')
            list_element = list_element[3:]
            for li in list_element:
                stock = li.find('td', {'class': 'center column-bestand'})
                name = li.find('td', {'class': 'expand column-name sorting_1'})
                price = li.find('td', {'class': 'numdata float center column-preise'})
                if stock != None and name != None and price != None:
                    stock_str = stock.text.strip()
                    name_str = name.text.strip()
                    price_str = price.text.strip().replace(',', '.')
                    if name_str != '' and price_str != '':
                        if not stock_str.__contains__('nicht'):
                            items.append({'name': name_str, 'price': price_str})
                        
        return items


class Scrape():
    def __init__(self):
        apotheken_list = []
        apotheken_list.append(GruenhornApotheke())
        apotheken_list.append(AbcApotheke())
        apotheken_list.append(HeliosApotheke())
        apotheken_list.append(BrokkoliApotheke())
        apotheken_list.append(CannflosApotheke())
        self.apotheken = apotheken_list
    
    def getApotheken(self):
        return self.apotheken
    
    def updateAll(self):
        for apo in self.apotheken:
            apo.updateData()

