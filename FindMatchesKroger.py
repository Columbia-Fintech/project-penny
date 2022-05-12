import pandas as pd
from Kroger_Auth import *
from KrogerClient import *
from fuzzywuzzy import fuzz

class FindMatchesKroger:

    def __init__(self, df, zip):

        self.df = df
        #user inputs zip
        self.zip = zip
        self.selectedStore = None
        self.matches = []
        self.client = KrogerClient(client_key_secret_enc)
        self.abbrev = pd.read_csv("Abbreviations.csv")
        self.web_raw = pd.read_csv("raw_web_joined.csv")

    def findStores(self):

        locations = self.client.get_locations(self.zip)
        return locations
    

    def expand(self, items):

        abbr_dict = {}
        #abbrev = pd.read_csv("Abbreviations.csv")
        #single word dictionary from manually added abbreviations
        for index, row in self.abbrev.iterrows():

            abbr_dict[row["ShortForm"].lower()] = row["LongForm"].lower() 

        web_raw = {}
        #build dictionary from scraped abbreviations (entire names) #new
        for index, row in self.web_raw.iterrows():

            web_raw[row['short'].lower()] = row['long'].lower()

        items_expanded = []
        if len(items) >= 1:
            #replace known abbreviations
            for k in range(len(items)):
                item = items[k].lower()
                #check if entire name in scraped dictionary first -new
                if item in web_raw.keys():
                    items_expanded.append(web_raw[item])
                #if not check if any words in name are in manual abbrev dict
                else: #-new
                    item_list = item.split(" ")
                    for i in range(len(item_list)):
                        if item_list[i] in abbr_dict.keys():
                            item_list[i] = abbr_dict[item_list[i]]
                    item_new = " ".join(item_list)
                    #items[k] = item_new
                    items_expanded.append(item_new)
        
        return items_expanded
        
    def findmatches(self):

        expanded = self.expand(self.df["items"])

        #search products in api:

        for i in expanded:

            products = self.client.search_products(term = i, location_Id=self.selectedStore)

            score = 0
            if products == []:
                best_guess = None
            else:
                best_guess = None
                for j in products:
                    Ratio = fuzz.partial_ratio(i,j.description)
                    if score != max(Ratio, score):
                        score = Ratio
                        best_guess = j
            
            self.matches.append(best_guess)

        #print(matches)

        self.df["matches"] = self.matches

        return self.df

    

    




                

        










