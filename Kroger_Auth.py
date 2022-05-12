import base64
from os import access
from unicodedata import name
import requests
import simple_cache


# https://stackoverflow.com/questions/29931671/making-an-api-call-in-python-with-an-api-that-requires-a-bearer-token
# https://github.com/jtbricker/python-kroger-client/blob/master/python_kroger_client/auth_service.py

client_id = 'KROGER_API_KEY'
client_secret = 'KROGER_API_SECRET_KEY'
client_key_secret = client_id+":"+client_secret
client_key_secret_enc = base64.b64encode(client_key_secret.encode()).decode()

API_URL = 'https://api.kroger.com/v1'

@simple_cache.cache_it("access_token.cache", 1800)
def get_client_access_token(client_key_secret_enc):

    url = API_URL + '/connect/oauth2/token'

    headersAuth = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Basic '+ str(client_key_secret_enc)
    }

    data = {
        'grant_type': 'client_credentials',
        'scope': 'product.compact'
    }
    response = requests.post(url, headers=headersAuth, data=data, verify=True)
    j = response.json()
    return j['access_token']
