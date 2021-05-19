import requests
import configparser
import json

config = configparser.ConfigParser()
config.read('settings.ini')

shopify_credentials = {k:v for k, v in config['shopify'].items()}


url = "https://{}:{}@{}.myshopify.com/admin/api/2021-04/".format(
        shopify_credentials.get('api_key'),
        shopify_credentials.get('api_password'),
        shopify_credentials.get('store_name'),
        )

def get_all_products():
    products = url + "products.json"

    response = requests.request("GET", products)

    return response.text

def create_new_product(product):
    new_product_url = url+ "products.json"

    payload= json.dumps(product)
    headers = {
    'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", new_product_url, headers=headers, data=payload)



def main():
    with open(config['mssql']['json_name'] ,'r') as file:
        items = json.load(file)
        for product in items["products"]:
            create_new_product(product)

main()