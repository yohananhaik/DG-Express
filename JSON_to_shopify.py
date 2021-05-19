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
    return(response.json())

def is_collection_exist(collection_name):
    retrieve_url = url+"custom_collections.json?title={}".format(collection_name)
    payload={}
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("GET", retrieve_url, headers=headers, data=payload)
    collections = response.json()
    if len(collections['custom_collections'])>0:
        for collection in collections['custom_collections']:
            if collection['title']==collection_name:
                return collection['id']
    return 0

def create_new_collection(collection_name):
    collection_id =  is_collection_exist(collection_name)
    if collection_id:
        return collection_id
    else:
        collection_url =url+ "custom_collections.json"

        payload = json.dumps({
        "custom_collection": {
            "title": collection_name
        }
        })
        headers = {
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", collection_url, headers=headers, data=payload)
        return response.json()['custom_collection']['id']

def add_product_to_collection(product_id, collection_id):
    collect_url = url+"collects.json"

    payload = json.dumps({
    "collect": {
        "product_id": product_id,
        "collection_id": collection_id
        }
        })
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", collect_url, headers=headers, data=payload)

def remove_item_from_collection(product_name):
    product_id = get_product_id_by_title(product_name)
    del_url = url+"collects/{}.json".format(product_id)
    payload = ""
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("DELETE", url, headers=headers, data=payload)

def get_product_id_by_title(product_title):
    retrieve_url = url+"products.json".format(product_title)
    payload={}
    headers = {
    'Content-Type': 'application/json'
    }
    params = {'title':product_title}
    response = requests.request("GET", retrieve_url, headers=headers, data=payload,params=params)
    return response.json()['products'][0]['id']

def main():
    collection_id = create_new_collection('test_collffhection')
    with open(config['mssql']['json_name'] ,'r') as file:
        items = json.load(file)
        for product in items["products"]:
            response = create_new_product(product)
            product_id = response['product']['id']
            add_product_to_collection(product_id,collection_id)

main()