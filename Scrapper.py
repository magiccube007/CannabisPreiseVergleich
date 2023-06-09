from bs4 import BeautifulSoup
from configparser import ConfigParser
import re
import pandas as pd
import abc
import os
import requests

config = ConfigParser()
config.read('config.ini')

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
    

class GruenhornApotheke(Apotheke):
    
    url_login = "https://www.gruenhorn.de/preise/"

    def __init__(self):
        self.NAME = 'GruenhornApotheke.csv'
        self.active = config['GRUENHORNAPOTHEKE']['ACTIVE']
        

    def getHTML(self):
        response = requests.get(self.url_login)
        response.raise_for_status()
        return response.content
    
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

    ABCAPOTHEKE_USERNAME = config['ABCAPOTHEKE']['USERNAME']
    ABCAPOTHEKE_PASSWORD = config['ABCAPOTHEKE']['PASSWORT']

    def __init__(self):
        self.NAME = 'AbcApotheke.csv'
        self.active = config['ABCAPOTHEKE']['ACTIVE']

    def getHTML(self):

        data = [
            ('afurd_field_nonce', '300054e3e0'),
            ('_wp_http_referer', '/my-account'),
            ('pre_page', 'https://abc-cannabis.de/'),
            ('username', self.ABCAPOTHEKE_USERNAME),
            ('password', self.ABCAPOTHEKE_PASSWORD),
            ('woocommerce-login-nonce', '49dd00f515'),
            ('_wp_http_referer', '/my-account'),
            ('login', 'Anmelden'),
        ]
        with requests.session() as s:
            s.post(self.url_login, data=data)
            response_inventory = s.get(self.url_data)
        return response_inventory.content
    
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

    HELIOSAPOTHEKE_USERNAME = config['HELIOSAPOTHEKE']['USERNAME']
    HELIOSAPOTHEKE_PASSWORD = config['HELIOSAPOTHEKE']['PASSWORT']

    def __init__(self):
        self.NAME = 'HeliosApotheke.csv'
        self.active = config['HELIOSAPOTHEKE']['ACTIVE']
    
    def getHTML(self):
        html = ""
        return html
    
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
    BROKKOLI_PASSWORD = config['BROKKOLIAPOTHEKE']['PASSWORT']

    def __init__(self):
        self.NAME = '420BrokkoliApotheke.csv'
        self.active = config['BROKKOLIAPOTHEKE']['ACTIVE']
    def getHTML(self):
        data = {
            'Passwort': self.BROKKOLI_PASSWORD,
            'email-confirm': '',
        }
        with requests.session() as s:
            s.post(self.URL_LOGIN, data=data)
            response = s.get(self.URL_LOGIN)
        return response.content
    
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

    CANFLOS_PASSWORD = config['CANFLOSAPOTHEKE']['PASSWORT']
    URL_LOGIN = "https://cannflos-apo.de/wp-login.php?action=postpass"
    URL_PRICE = "https://cannflos-apo.de/preise/"

    def __init__(self):
        self.NAME = 'CannflosApotheke.csv'
        self.active = config['CANFLOSAPOTHEKE']['ACTIVE']

    def getHTML(self):
        data = {
            'post_password': self.CANFLOS_PASSWORD,
            'Submit': 'Absenden',
        }
        
        with requests.session() as s:
            s.post(self.URL_LOGIN, data=data)
            response = s.get(self.URL_PRICE)
        return response.content

    def getItems(self, htlm):
        items = []
        soup = BeautifulSoup(htlm, 'html.parser')
        list_element = soup.find_all('tr', {'id': lambda value: value and 'table_16_row_' in value})
        for li in list_element:
            item_values = li.find_all('td', {'style': ''})
            name = item_values[1].text.strip()
            stock = item_values[9].text.strip()
            price = item_values[11].text.strip().replace(',','.')
            if not 'nicht' in stock:
                items.append({'name': name, 'price': price})
            
        return items

class GrueneblueteApotheke(Apotheke):

    GRUENEBLUETE_PASSWORD = config['GRUENEBLUETEAPOTHEKE']['PASSWORT']
    URL_LOGIN = "https://gruenebluete.de/wp-login.php?action=postpass"
    URL_LIST = "https://gruenebluete.de/produkt-preisliste/"

    def __init__(self):
        self.NAME = 'GrueneblueteApotheke.csv'
        self.active = config['GRUENEBLUETEAPOTHEKE']['ACTIVE']
    
    def getHTML(self):
        data = {
            'post_password': self.GRUENEBLUETE_PASSWORD,
            'Submit': 'Senden',
        }
        
        with requests.session() as s:
            s.post(self.URL_LOGIN, data=data)
            response = s.get(self.URL_LIST)
        return response.content
        

    def getItems(self, htlm):
        items = []
        soup = BeautifulSoup(htlm, 'html.parser')
        list_element = soup.find_all('tr', {'id': lambda value: value and 'table_3_row_' in value})
        for li in list_element:
            item_values = li.find_all('td', {'style': ''})
            typ = item_values[0].text.strip()
            name = item_values[1].text.strip().replace(',','.')
            stock = item_values[8].text.strip()
            price = item_values[9].text.strip().replace('.','')
            if not 'Auf' in stock and typ != 'Extrakt':
                price = price[:-2] + "." + price[-2:]
                items.append({'name': name, 'price': price})
        return items
    
class Cannabisapo24Apotheke(Apotheke):
    
    Cannabisapo24_EMAIL = config['CANNABISAPO24APOTHEKE']['USERNAME']
    Cannabisapo24_PASSWORD = config['CANNABISAPO24APOTHEKE']['PASSWORT']
    URL_LOGIN = "https://cannabisapo24.de/account/login"
    BESTAND_URL = 'https://cannabisapo24.de/#live-bestand-cannabis-blueten-und-extrakte'
    
    def __init__(self):
        self.NAME = 'Cannabisapo24Apotheke.csv'
        self.active = config['CANNABISAPO24APOTHEKE']['ACTIVE']

    def getHTML(self):
        data = {
            'form_type': 'customer_login',
            'utf8': '✓',
            'checkout_url': '/pages/confirm-addresses',
            'customer[email]': self.Cannabisapo24_EMAIL,
            'customer[password]': self.Cannabisapo24_PASSWORD,
        }
        with requests.session() as s:
            s.post(self.URL_LOGIN, data=data)
            response = s.get(self.BESTAND_URL)
        return response.content
    
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
    
class CannaliveryApotheke(Apotheke):

    CannaliveryApotheke_USERNAME = config['CANNALIVERYAPOTHEKE']['USERNAME']
    CannaliveryApotheke_PASSWORD = config['CANNALIVERYAPOTHEKE']['PASSWORT']
    URL_LOGIN = "https://www.cannalivery.com/de/mein-konto/"
    URL_PRICES = "https://www.cannalivery.com/de/live-bestand/"

    def __init__(self):
        self.NAME = 'CannaliveryApotheke.csv'
        self.active = config['CANNALIVERYAPOTHEKE']['ACTIVE']

    def getHTML(self):
        data = {
            'username': self.CannaliveryApotheke_USERNAME,
            'password': self.CannaliveryApotheke_PASSWORD,
            'woocommerce-login-nonce': '81b9224a98',
            '_wp_http_referer': '/de/mein-konto/',
            'login': 'Anmelden',
        }

        with requests.session() as s:
            s.post(self.URL_LOGIN, data=data)
            response = s.get(self.URL_PRICES)
        return str(response.content)
    def getItems(self, htlm):
        items = []
        soup = BeautifulSoup(htlm, 'html.parser')
        list_element = soup.find_all('tr', {'data-wcpt-variation-id': lambda value: value})
        for element in list_element:
            price = element.get('\\ndata-wcpt-price')
            name = element.find('a').text.strip().replace(',','.')
            stock = element.get('\\ndata-wcpt-stock')
            if float(stock) > 0.00:
                items.append({'name': name, 'price': price})
        return items
    
class JirooApotheke(Apotheke):

    JirooApotheke_USERNAME = config['JIROOAPOTHEKE']['USERNAME']
    JirooApotheke_PASSWORD = config['JIROOAPOTHEKE']['PASSWORT']
    URL_LOGIN = "https://jiroo.de/"
    URL_PRICES = "https://jiroo.de/cannabis-preise/"

    def __init__(self):
        self.NAME = 'JirooApotheke.csv'
        self.active = config['JIROOAPOTHEKE']['ACTIVE']

    def getHTML(self):
        data = {
            'username': self.JirooApotheke_USERNAME,
            'password': self.JirooApotheke_PASSWORD,
            'woocommerce-login-nonce': '20cb387ccb',
            '_wp_http_referer': '/',
            'login': 'Anmelden',
        }
        headers = {
            'authority': 'jiroo.de',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://jiroo.de',
            'referer': 'https://jiroo.de/',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        }
        with requests.session() as s:
            s.post(self.URL_LOGIN, data=data, headers=headers)
            response = s.get(self.URL_PRICES, headers=headers)
        return response.content

    def getItems(self, htlm):
        items = []
        soup = BeautifulSoup(htlm, 'html.parser')
        list_elementents = soup.find('tbody')
        list_element = list_elementents.find_all('tr')
        for element in list_element:
            name = element.find('a').text.strip().replace(',','.')
            price = element.find_all('td')[4].text.strip().replace(',','.').replace('€','').strip()
            if name != '' and price != '':
                items.append({'name': name, 'price': price})
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
        apotheken_list.append(CannaliveryApotheke())
        apotheken_list.append(JirooApotheke())
        self.apotheken = apotheken_list
    
    def getApotheken(self):
        return self.apotheken
    
    def updateAll(self):
        for apo in self.apotheken:
            apo.updateData()
