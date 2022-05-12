import statistics

class ComparePrices:

    def __init__(self, selectedItem, selectedItemPrice, selectedStore, nearbyResults):

        self.item = selectedItem
        self.itemPrice = selectedItemPrice
        self.store = selectedStore
        self.nearby = nearbyResults
        self.priceSum = 0
        self.count = len(nearbyResults.keys())
        

    #returns info on lowest priced item
    def get_min_item(self):

        min_store = self.store
        min_price = self.itemPrice

        for k,v in self.nearby.items():

            if v.price[1] != 0:
                checkPrice = v.price[1]
            else:
                checkPrice = v.price[0]

            if checkPrice < min_price:
                min_price = checkPrice
                min_store = k
    
            self.priceSum += checkPrice
            #self.count+= 1

        return (min_store, min_price)

    #returns mean price
    def get_mean(self):

        return float(self.priceSum/self.count)
    
    #returns list of prices in self.nearby returns list of floats
    def get_price_list(self):

        prices = []

        for k,v in self.nearby.items():

            #if promo price exists we choose that
            if v.price[1] != 0:
                prices.append(float(v.price[1]))
            else:
                prices.append(float(v.price[0]))

        return prices
    
    #returns 
    def get_standard_dev(self):

        prices = self.get_price_list()

        return statistics.stdev(prices)


    def get_mean_str(self, mean):

        string = "The mean price for {}: ${:.2f}".format(self.item.description, mean)
        return string
    
    def get_item_str(self):

        string = 'The Price of {} at selected location: {} - ${}'.format(self.item.description, self.store, self.itemPrice)

        return string
    
    def get_min_item_str(self, radius, min_item_info):

        min_store = min_item_info[0]
        price = min_item_info[1]

        string = 'The Lowest price for {} within {} mile radius: {} - ${}'.format(self.item.description, radius, min_store, price)

        return string

    def get_stdev_str(self, stdev):

        string = 'The standard deviation of prices for {}: {:.2f}'.format(self.item.description, stdev)

        return string
    