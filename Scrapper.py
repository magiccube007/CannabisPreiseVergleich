from bs4 import BeautifulSoup
from configparser import ConfigParser
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, NoSuchElementException
import time
import pandas as pd
import abc
import os

config = ConfigParser()
config.read('config.ini')

HELIOSAPOTHEKE_USERNAME = config['HELIOSAPOTHEKE']['USERNAME']
HELIOSAPOTHEKE_PASSWORD = config['HELIOSAPOTHEKE']['PASSWORT']
ABCAPOTHEKE_USERNAME = config['ABCAPOTHEKE']['USERNAME']
ABCAPOTHEKE_PASSWORD = config['ABCAPOTHEKE']['PASSWORT']
BROKKOLI_PASSWORD = config['BROKKOLIAPOTHEKE']['PASSWORT']
GRUENHORN_PASSWORD = config['GRUENHORNAPOTHEKE']['PASSWORT']
CANFLOS_PASSWORD = config['CANFLOSAPOTHEKE']['PASSWORT']
CHROME_PATH = config['CHROME']['PATH']
GRUENEBLUETE_PASSWORD = config['GRUENEBLUETEAPOTHEKE']['PASSWORT']
Cannabisapo24_EMAIL = config['CANNABISAPO24APOTHEKE']['USERNAME']
Cannabisapo24_PASSWORD = config['CANNABISAPO24APOTHEKE']['PASSWORT']

class Apotheke(metaclass=abc.ABCMeta):
    
    
    def __init__(self):
        self.NAME = 'ERROR'
        

    def updateData(self):
        if self.active == 'True':
            print('Updating', self.NAME, '...')
            source = self.getHTML()
            print(self.NAME, 'got HTML!')
            items = self.getItems(source)
            print(self.NAME, 'got Prices!')
            self.writeCSV(self.NAME, items)
        else:
            print(self.NAME, 'not active!')
    
    @abc.abstractmethod
    def getHTML(self):
        pass

    @abc.abstractmethod
    def getItems(self,htlm):
        pass

    def writeCSV(self,file_name,items):
        df = pd.DataFrame(items, columns=['name', 'price'])
        df = df.drop_duplicates()
        df.to_csv(os.path.join('data/',file_name), index=False)
    
    def getDriver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument('--no-sandbox')
        if CHROME_PATH == '':
            driver = webdriver.Chrome(options=chrome_options)
        else:
            driver = webdriver.Chrome(executable_path=os.path.join(CHROME_PATH,'chromedriver.exe'),options=chrome_options)
        driver.implicitly_wait(1)
        return driver

class GruenhornApotheke(Apotheke):
    
    url_login = "https://www.gruenhorn.de/preise/"
    url_data = "https://www.gruenhorn.de/preise/?_form=blueten"

    def __init__(self):
        self.NAME = 'GruenhornApotheke.csv'
        self.active = config['GRUENHORNAPOTHEKE']['ACTIVE']
        

    def getHTML(self):
        driver = self.getDriver()
        driver.get(self.url_data)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[2]/span[3]/button').click()
        driver.find_element(By.XPATH, '//*[@id="gh_form_pw"]').send_keys(GRUENHORN_PASSWORD)
        element = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/div/div[2]/div/div[2]/div/div/div/div/form/button')
        driver.execute_script("arguments[0].click();", element)
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        response = driver.find_element(By.XPATH, '//html').get_attribute('outerHTML')
        return response
    
    def getItems(self, htlm):
        soup = BeautifulSoup(htlm, 'html.parser')
        list_element = soup.find_all('div', {'class': 'cms-listing-col col-sm-6 col-lg-4 col-xl-3'})
        items = []
        for li in list_element:
            name = li.find('div', {'class': 'live-bestand-wert'})
            straintype = li.find('span', {'class': 'price-unit-content'})
            price = li.find('span', {'class': 'product-price'})
            stock = li.find('div', {'class': 'live-bestand-wert available'})
            if stock != None and name != None and price != None and straintype != None:
                stock_name = stock.text.strip()
                straintype_name = straintype.text.strip()
                item_name = name.text.strip()
                item_price = price.text.strip().replace(',', '.').replace('€*', '').strip()
                if not 'nicht' in stock_name and 'Gramm' in straintype_name and not 'Cannabis Extrakt' in item_name:
                    items.append({'name': item_name, 'price': item_price})
        return items

class AbcApotheke(Apotheke):

    url_login = "https://abc-cannabis.de/my-account"
    url_data = "https://abc-cannabis.de/livebestand"
    
    def __init__(self):
        self.NAME = 'AbcApotheke.csv'
        self.active = config['ABCAPOTHEKE']['ACTIVE']

    def getHTML(self):
        driver = self.getDriver()
        driver.get(self.url_login)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        driver.find_element(By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowallSelection"]').click()
        driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(ABCAPOTHEKE_USERNAME)
        driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(ABCAPOTHEKE_PASSWORD)
        driver.find_element(By.XPATH, '//*[@id="post-9"]/div/div/div/div/div[1]/div/div/form/p[3]/button').click()
        time.sleep(1)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        driver.get(self.url_data)
        time.sleep(1)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
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
        self.active = config['HELIOSAPOTHEKE']['ACTIVE']
    
    def getHTML(self):
        driver = self.getDriver()
        driver.get(self.url_login)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        driver.find_element(By.XPATH, '//*[@id="user_login"]').send_keys(HELIOSAPOTHEKE_USERNAME)
        driver.find_element(By.XPATH, '//*[@id="user_pass"]').send_keys(HELIOSAPOTHEKE_PASSWORD)
        driver.find_element(By.XPATH, '//*[@id="sso_default_login"]').click()
        time.sleep(1)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        htmls = []
        for i in range(1, 11):
            url_sortiment = "https://helios-cannabis.de/sortiment/page/"+ str(i) +"?lieferbar=auf-lager,bald-verfuegbar"
            driver.get(url_sortiment)
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
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
        self.active = config['BROKKOLIAPOTHEKE']['ACTIVE']
    def getHTML(self):
        driver = self.getDriver()
        driver.get(self.URL_LOGIN)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        driver.find_element(By.XPATH, '//*[@id="Passwort"]').send_keys(BROKKOLI_PASSWORD)
        driver.find_element(By.XPATH, '//*[@id="main-form-container"]/div/div/div[3]/button').click()
        time.sleep(1)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
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
        self.active = config['CANFLOSAPOTHEKE']['ACTIVE']

    def getHTML(self):
        driver = self.getDriver()
        driver.get(self.URL_LOGIN)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="wt-cli-accept-all-btn"]'))).click()
        driver.find_element(By.XPATH, '//*[@id="pwbox-17321"]').send_keys(CANFLOS_PASSWORD)
        driver.find_element(By.XPATH, '/html/body/form/p[2]/input').click()
        time.sleep(1)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)
        html = []
        html.append(driver.find_element(By.XPATH, '//html').get_attribute('outerHTML'))
        for i in range(5):
            try:
                nextPage = '#table_1_next'
                element = driver.find_element(By.CSS_SELECTOR, nextPage)
                driver.execute_script("arguments[0].scrollIntoView();", element)
                time.sleep(1)
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, nextPage))).click()
                wait = WebDriverWait(driver, 10)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(1)
                html.append(driver.find_element(By.XPATH, '//html').get_attribute('outerHTML'))
            except (TimeoutException, ElementNotInteractableException) as e:
                print('Exception!')
                if type(e) == TimeoutException:
                    print('Cannflos-Apotheke:',"TimeoutException was raised")
                elif type(e) == ElementNotInteractableException:
                    print('Cannflos-Apotheke:',"ElementNotInteractableException was raised")
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

class GrueneblueteApotheke(Apotheke):
    URL_LOGIN = "https://gruenebluete.de/produkt-preisliste/"
    def __init__(self):
        self.NAME = 'GrueneblueteApotheke.csv'
        self.active = config['GRUENEBLUETEAPOTHEKE']['ACTIVE']
    
    def getHTML(self):
        driver = self.getDriver()
        driver.get(self.URL_LOGIN)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(50)
        element = driver.find_element(By.CSS_SELECTOR, '#usercentrics-root')
        shadow_root = driver.execute_script('return arguments[0].shadowRoot', element)
        try:
            element = shadow_root.find_element(By.CSS_SELECTOR, 'button[data-testid="uc-accept-all-button"]')
            element.click()
        except NoSuchElementException:
            print("GrueneBluete: Accept Cookies not found!")

        driver.find_element(By.XPATH, '//*[@id="pwbox-836"]').send_keys(GRUENEBLUETE_PASSWORD)
        send = driver.find_element(By.XPATH, '//*[@id="code_block-1366-838"]/div/div/div/div/div/form/div/input[2]')
        driver.execute_script("arguments[0].click();", send)
        time.sleep(1)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)
        html = []
        html.append(driver.find_element(By.XPATH, '//html').get_attribute('outerHTML'))

        for i in range(6):
            try:
                time.sleep(1)
                nextPage = 'a.paginate_button.next#table_1_next'
                wait = WebDriverWait(driver, 10)
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, nextPage)))
                driver.execute_script("arguments[0].scrollIntoView();", element)
                WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, nextPage)))
                driver.execute_script("arguments[0].click();", element)
                time.sleep(1)
                wait = WebDriverWait(driver, 10)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                html.append(driver.find_element(By.XPATH, '//html').get_attribute('outerHTML'))
            except (TimeoutException, ElementNotInteractableException):
                break
        return list(set(html))
        

    def getItems(self, htlm):
        items = []
        for h in htlm:
            soup = BeautifulSoup(h, 'html.parser')
            list_element = soup.find_all('tr')
            list_element.pop(0)
            for li in list_element:
                stock = li.find('td', {'class': 'column-in_stock'})
                name = li.find('td', {'class': 'expand column-product'})
                price = li.find('td', {'class': 'numdata formula column-formula_1'})
                if stock != None and name != None and price != None:
                    stock_str = stock.text.strip()
                    name_str = name.text.strip().replace(',', '.')
                    price_str = price.text.strip().replace(',', '.')
                    if name_str != '' and price_str != '':
                        if price_str != '0.00' and not stock_str.__contains__('Auf'):
                            items.append({'name': name_str, 'price': price_str})
        return items
    
class Cannabisapo24Apotheke(Apotheke):
    URL_LOGIN = "https://cannabisapo24.de/account/"
    BESTAND_URL = 'https://cannabisapo24.de/#live-bestand-cannabis-blueten-und-extrakte'

    def __init__(self):
        self.NAME = 'Cannabisapo24Apotheke.csv'
        self.active = config['CANNABISAPO24APOTHEKE']['ACTIVE']

    def getHTML(self):
        driver = self.getDriver()
        driver.get(self.URL_LOGIN)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(5)
        driver.find_element(By.XPATH, '//*[@id="LoginCustomerEmail"]').send_keys(Cannabisapo24_EMAIL)
        driver.find_element(By.XPATH, '//*[@id="LoginCustomerPassword"]').send_keys(Cannabisapo24_PASSWORD)
        driver.find_element(By.XPATH, '//*[@id="customer_login"]/div[3]/label/input').click()
        driver.find_element(By.XPATH, '//*[@id="customer_login"]/div[4]/input').click()
        time.sleep(5)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        driver.get(self.BESTAND_URL)
        time.sleep(5)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        html = driver.find_element(By.XPATH, '//html').get_attribute('outerHTML')
        return html
    
    def getItems(self, htlm):
        soup = BeautifulSoup(htlm, 'html.parser')
        list_element = soup.find_all('tr')
        list_element = list_element[2:]
        items = []
        for li in list_element:
            td_tag = li.find('td', {'class': 'border-b whitespace-nowrap xl:whitespace-normal py-4 border-white font-bold px-4'})
            a_tag = td_tag.find('a')
            product_name = a_tag.text.strip().replace(',','.')
            price = li.find('div', class_='space-x-2')
            if price is None:
                price_str = ''
            else:
                price_str = price.text.split()[1].replace('€','').replace(',','.')
            stock = li.find('td', {'class': 'hidden sm:table-cell border-b whitespace-nowrap xl:whitespace-normal py-4 border-white px-4'}).text.strip()
            type = li.find('td', {'class': 'hidden get_form'}).text.strip()
            if type == 'Blüten' and not stock.__contains__('nicht'):
                items.append({'name': product_name, 'price': price_str})
        return items


class Scrape():
    def __init__(self):
        apotheken_list = []
        apotheken_list.append(GruenhornApotheke())
        apotheken_list.append(AbcApotheke())
        apotheken_list.append(HeliosApotheke())
        apotheken_list.append(BrokkoliApotheke())
        apotheken_list.append(CannflosApotheke())
        apotheken_list.append(GrueneblueteApotheke())
        apotheken_list.append(Cannabisapo24Apotheke())
        self.apotheken = apotheken_list
    
    def getApotheken(self):
        return self.apotheken
    
    def updateAll(self):
        for apo in self.apotheken:
            apo.updateData()
