import Scrapper
import pandas as pd
import os

class Matches():

    def __init__(self):
        self.df = pd.read_csv('matchnames.csv',index_col='ID')
    
    def updateMatches(self):
        self.df = pd.read_csv('matchnames.csv',index_col='ID')
    #Normales Search
    def search(self,query): 
        result = []
        for i in self.searchIndexes(query):
            result.append({'Index': str(i), 'Names': str(self.getIndex(i))})
        return result
    
    #Benutzt normales Search und Formatiert zu Telegram-Format
    def searchToString(self,query): 
        return self.format_items(self.search(query))
    
    #Sucht nach einem Key-Word und gibt eine Liste von Indexen zurücken für die Sorten die das Key-Word enthalten
    def searchIndexes(self, query):
        query_lower = query.lower()
        matches = self.df[self.df.apply(lambda row: query_lower in ' '.join(row.values.astype(str)).lower(), axis=1)].index.tolist()
        return matches
    
    #names ist eine Liste mit Namen wie z.B. 
    #[{'Apotheke': 'GruenhornApotheke', 'Name': 'Pedanios 22/1 DNK'}, {'Apotheke': 'AbcApotheke', 'Name': 'Pedanios 22/1'}, 
    #{'Apotheke': 'HeliosApotheke', 'Name': 'Pedanios 22/1 DNK – Ghost Train Haze'}]    
        
    def getIndex(self,index):
        names= []
        for col in self.df.columns.tolist():
            item = self.df.loc[index, col]
            names.append({'Apotheke': str(col), 'Name': str(item)})
        return names
    
    #result ist eine Liste aus IDs und Listen von getIndex z.B.
    #[{'Index': '3', 'Names': "[{'Apotheke': 'GruenhornApotheke', 'Name': '420 Evolution 27/1 CA ICC'}, {'Apotheke': 'AbcApotheke', 'Name': '420 EVOLUTION ICC 27/1'}, 
    #{'Apotheke': 'HeliosApotheke', 'Name': '420 Evolution 27/1 CA ICC – Ice Cream Cake x Kush Mints'}]"}]
    def getIndexToStringNamesOnly(self,index):
        result = []
        result.append({'Index': str(index), 'Names': str(self.getIndex(index))})
        return self.format_items(result)
    
    #Macht das selbe wie getIndex to String, blos mit allen IDs
    def printAllStrains(self):
        result = []
        for i in self.getAllIDs():
            result.append({'Index': str(i), 'Names': str(self.getIndex(i))})
        return self.format_items(result)
    
    #Gibt alle IDs zurück
    def getAllIDs(self):
        return self.df.index.tolist()
    
    #Gibt die Spaltennamen zurück
    def getColoumns(self):
        return self.df.columns.tolist()
    
    #Formatiert die outputs für Telegramm
    def format_items(self, items):
        formatted_str = ""
        for item in items:
            index = item['Index']
            names = item['Names']
            names_list = eval(names)
            formatted_str += f"<b>Sorten ID</b>: {index}\n"
            formatted_str += "<b>Namen:</b> "
            unique_names = set()
            for name_dict in names_list:
                name = name_dict['Name']
                if name != 'nan' and name not in unique_names:
                    unique_names.add(name)
                    formatted_str += f"{name}, "
            formatted_str = formatted_str.rstrip(", ") + "\n\n"
        return formatted_str

class Apotheke():
    def __init__(self,file_name):
        file_name += '.csv'
        self.file_name = file_name
        self.df = pd.read_csv(os.path.join('data/',file_name), index_col='name')
        
    #Gibt den Preis eines bestimmten Produkts einer Apotheke zurück
    def getPrice(self,name):
        try:
            price = self.df.loc[name, 'price']
            return str(price)
        except KeyError:
            return 'None'
        
    
    def updateDataframe(self):
        self.df = pd.read_csv(os.path.join('data/'+self.file_name), index_col='name')
    
    #Gibt den Namen der Apotheke zurück
    def getName(self):
        return str(self.file_name).replace('.csv', '')

class App():
    #Erstellt die Objekte, insbesondere bei den Apotheken werden alle SpaltenNamen aus der match datei genommen und für diese ein Apotheken Objekt Erzeug
    #Dieses wird in eine Liste apotheken hinzugefügt diese hat den Aufbau {'Apotheke': "ApothekenName", 'ApothekeObject': "ApothekenObject"}
    def __init__(self):
        self.scraper = Scrapper.Scrape()
        self.matches = Matches()
        self.apotheken = []
        for apo in self.matches.getColoumns():
            self.apotheken.append({'Apotheke': apo, 'ApothekeObject': Apotheke(apo)})
        self.savePrices()
        self.prices = pd.read_csv('prices.csv')
    
    #updatet die Preise und die Dataframes der Apotheken, anschließend werden die neuen Preise in prices.csv gespeichert
    def updateAll(self):
        self.scraper.updateAll()
        self.matches.updateMatches()
        for apo in self.apotheken:
            apo['ApothekeObject'].updateDataframe()
        self.savePrices()
        self.prices = pd.read_csv('prices.csv')
    
    #Gitb die Anzahl der geladen Strains pro Apotheke zurück
    def getAmountInDatabase(self):
        result = ''
        for apo in self.apotheken:
            amount = len(apo['ApothekeObject'].df)
            name = apo['Apotheke']
            result += '<b>'+ str(name) +':</b> ' + str(amount) + ' Einträge\n'
        return result

    #holt für einen Index die Preise aus allen Apotheken und speichert diese in einem Objekt
    def getPriceForIndex(self, index):
        item_names = self.matches.getIndex(index)
        preise = []
        for name in item_names:
            apotheke = name['Apotheke']
            strain = name['Name']
            if strain != 'nan':
                for apo in self.apotheken:
                    if apo['Apotheke'] == apotheke:
                        price = apo['ApothekeObject'].getPrice(strain)
                        preise.append({'Apotheke': apotheke, 'Preis': price})
        return {'ID': index, 'Preise': preise}
    
    #Erstellt mit Hilfe von getPriceForIndex eine Liste aus diesen Objekten
    def getPriceForAll(self):
        result = []
        for i in self.matches.getAllIDs():
            result.append(self.getPriceForIndex(i))
        return result
    
    #Speichert mit Hilfe von getPriceForAll alle Preise in prices.csv
    def savePrices(self):
        df = pd.DataFrame(self.getPriceForAll())
        for index, row in df.iterrows():
            prices_dict = row['Preise']
            for price in prices_dict:
                apotheke_name = price['Apotheke']
                apotheke_price = price['Preis']
                df.at[index, apotheke_name] = apotheke_price
        df.drop('Preise', axis=1, inplace=True)
        df.to_csv('prices.csv', index=False)

    #Gibt mit Hilfe von prices.csv die Preise in allen Apotheken für einen bestimmten Index als Dictenoary zurück
    #{'ID': 2.0, 'GruenhornApotheke': 10.99, 'AbcApotheke': 10.58, 'HeliosApotheke': 10.9}
    def getPriceFromFileByIndex(self,index):
        df = self.prices
        coloumns = df.columns.tolist()
        row = df[df['ID'] == index]
        prices_dict = {}
        for apotheke in coloumns:
            price = row[apotheke].iloc[0]
            if pd.isna(price):
                prices_dict[apotheke] = None
            else:
                prices_dict[apotheke] = float(price)
        return prices_dict
    
    #Gibt ID und Namen, als auch preis in allen verfügbaren Apotheken eines bestimmten Index zurück
    def getPriceAndNameByIndexToString(self,index):
        if self.matches.getAllIDs().__contains__(index):
            pharmacy_list = self.matches.getIndex(index)
            price_dict = self.getPriceFromFileByIndex(index)
            output = self.matches.getIndexToStringNamesOnly(index).replace('\n\n', '\n')
            for pharmacy in pharmacy_list:
                if pharmacy["Name"] != 'nan' and price_dict.get(pharmacy['Apotheke']) != None:
                    output += f"<b>{pharmacy['Apotheke']}</b>: {price_dict.get(pharmacy['Apotheke'], 'N/A')}€\n"
            return output.strip()
        else:
            return 'Der gegebene Index war ungültig!'
    
    #Suche mit einem query
    def search(self,query):
        return self.matches.searchToString(query)
    
    #Gibt alle Strains zurück
    def getAllStrains(self):
        return self.matches.printAllStrains()

    #Gibt alle Strains zurück, die bei einer der Apotheken günstiger als ein bestimmter Preis verfügbar sind
    def getBelow(self,amount):
        df = self.prices
        all_columns = df.columns.to_list()
        all_columns.remove('ID')
        mask = df[all_columns] < amount
        indices = df.loc[mask.any(axis=1), 'ID'].tolist()
        result = ''
        for i in indices:
            index = int(i)
            result += self.getPriceAndNameByIndexToString(index) + '\n\n'
        return result
    
    #Best Deal
    def getBestDeal(self, id_list1, id_list2, anzahl1, anzahl2):
        df = self.prices
        all_columns = df.columns.to_list()
        all_columns.remove('ID')
        bestdeal_list = []
        for apo in all_columns:
            valid_ids1 = [id for id in id_list1 if pd.notna(df.loc[df['ID'] == id, apo].values[0])]
            valid_ids2 = [id for id in id_list2 if pd.notna(df.loc[df['ID'] == id, apo].values[0])]
            if not valid_ids1 or not valid_ids2:
                continue
            cheapest_id1 = min(valid_ids1, key=lambda x: df.loc[df['ID'] == x, apo].values[0])
            cheapest_id2 = min(valid_ids2, key=lambda x: df.loc[df['ID'] == x, apo].values[0])
            price1 = df.loc[df['ID'] == cheapest_id1, apo].values[0]
            price2 = df.loc[df['ID'] == cheapest_id2, apo].values[0]
            total = price1 * anzahl1 + price2 * anzahl2 + 2 * 4.26
            bestdeal_dict = {'total': total, 'apotheke': apo, 'Strain1': cheapest_id1, 'Strain2': cheapest_id2}
            bestdeal_list.append(bestdeal_dict)
        if not bestdeal_list:
            return None
        bestdeal_list_sorted = sorted(bestdeal_list, key=lambda x: x['total'])
        result_string_list = ''
        for bestdeal_dict in bestdeal_list_sorted:
            result_string = ('Bestes Angebot bei: <b>'+ str(bestdeal_dict['apotheke']) +'</b>\n'
                'Preis ohne Versandkosten: <b>' + str(round(bestdeal_dict['total'],2)) + '</b>\n'
                + str(self.matches.getIndexToStringNamesOnly(bestdeal_dict['Strain1'])) 
                + str(self.matches.getIndexToStringNamesOnly(bestdeal_dict['Strain2'])))
            result_string_list += result_string + '\n\n'
        return result_string_list
    #Access Control
    def get_allowed_users():
        df = pd.read_csv('allowedusers.csv')
        return set(df['user_id'].astype(str).tolist())
    
    def add_new_user(user_id):
        df = pd.read_csv('allowedusers.csv')
        new_row = {'user_id': user_id}
        df = df._append(new_row, ignore_index=True)
        df.to_csv('allowedusers.csv', index=False)
