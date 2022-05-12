import json
from jmespath import search
import requests
from Kroger_Auth import *
from KrogerProduct import Product
from KrogerLocation import Location

API_URL = 'https://api.kroger.com/v1'

param_map = {
    'brand': 'filter.brand',
    'chain': 'filter.chain',
    'fulfillment': 'filter.fulfillment',
    'limit': 'filter.limit',
    'location_Id': 'filter.locationId',
    'product_Id': 'filter.productId',
    'term': 'filter.term',
    'within_miles': 'filter.radiusInMiles',
    'zipcode': 'filter.zipCode.near',
}

class KrogerClient:

    def __init__(self, encoded_client_token):
        self.token = get_client_access_token(encoded_client_token)

    def make_get_request(self, endpoint, params=None):
        url = API_URL + endpoint
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}',
        }

        response = requests.get(url, headers=headers, params = params)
        return json.loads(response.text)
    
    
    #for product search to return price location_id must not be None
    def search_products(self, term=None, location_Id=None, product_Id=None, brand=None, fulfillment=None, limit = 10):

        params = get_mapped_params(locals())
        #print(params)
        endpoint = '/products'
    
        results = self.make_get_request(endpoint, params=params)
        data = results.get('data')
        #create product class
        return [Product.from_json(product) for product in data]
    
    def get_locations(self, zipcode, within_miles=None, limit=10):
        params = get_mapped_params(locals())
        endpoint = '/locations'

        results = self.make_get_request(endpoint, params=params)
        data = results.get('data')
        #create locations class
        return [Location.from_json(location) for location in data]

def get_mapped_params(params):
        """ Maps a dictionary of parameters (ignore self) to the api's expected key value """
        return { param_map[key] : value for key, value in params.items() if key != 'self'}

if __name__ == '__main__':

    client = KrogerClient(client_key_secret_enc)

    loc = client.get_locations('91325')

    id = '70300646'

    product = client.search_products("cage free eggs", id)

    print(product)


    



    

