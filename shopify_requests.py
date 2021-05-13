import requests
import configparser
import json

config = configparser.ConfigParser()
config.read('settings.ini')

shopify_credentials = {k:v for k, v in config['shopify'].items()}


url = "https://{}:{}@{}.myshopify.com/admin/api/2021-04/products.json".format(
        shopify_credentials.get('api_key'),
        shopify_credentials.get('api_password'),
        shopify_credentials.get('store_name'),
        )

def get_all_products():
    products = url + "products.json"

    response = requests.request("GET", products)

    return response.text

def create_new_product():
    new_product_url = url+ "products.json"


    with open('sample.product.json') as f:
        new_product_json = json.load(f)


    payload= json.dumps(new_product_json)
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json


print(create_new_product())