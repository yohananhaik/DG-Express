import requests
import configparser
import json
import os

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)) ,'settings.ini'))

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
    if get_product_id_by_title(product["product"]["title"]) ==0:
        new_product_url = url+ "products.json"

        payload= json.dumps(product)
        headers = {
        'Content-Type': 'application/json'
        }
        
        response = requests.request("POST", new_product_url, headers=headers, data=payload)
        return(response.json())

def add_product_to_custom_collection(product_id, collection_id):
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

def remove_item_from_custom_collection(product_name):
    product_id = get_product_id_by_title(product_name)
    del_url = url+"collects/{}.json".format(product_id)
    payload = ""
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("DELETE", url, headers=headers, data=payload)

def is_collection_exist(collection_name,type):
    retrieve_url = url+"{}_collections.json?title={}".format(type,collection_name)
    payload={}
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("GET", retrieve_url, headers=headers, data=payload)
    collections = response.json()
    if len(collections['{}_collections'.format(type)])>0:
        for collection in collections['{}_collections'.format(type)]:
            if collection['title']==collection_name:
                return collection['id']
    return 0

def create_new_collection(collection_name,type):
    collection_id =  is_collection_exist(collection_name,type)
    if collection_id:
        return collection_id
    else:
        collection_url =url+ "{}_collections.json".format(type)
        if type == 'custom':
            payload = json.dumps({
            "{}_collection".format(type): {
                "title": collection_name
            }})
        elif type == 'smart':
            payload = json.dumps({
            "{}_collection".format(type): {
                "title": collection_name,
                "rules":[{
                        "column": "tag",
                        "relation": "equals",
                        "condition": collection_name
                    }]
            }})
        headers = {
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", collection_url, headers=headers, data=payload)
        res =response.json()['{}_collection'.format(type)]
        return res['id']

def update_smart_collections(groups):
    for category in groups:
        create_new_collection(category,'smart')

def get_product_id_by_title(product_title):
    retrieve_url = url+"products.json".format(product_title)
    payload={}
    headers = {
    'Content-Type': 'application/json'
    }
    params = {'title':product_title}
    response = requests.request("GET", retrieve_url, headers=headers, data=payload,params=params)
    res = response.json()
    if len(res['products'])>0:
        return response.json()['products'][0]['id']
    return 0

def main():
    with open(config['mssql']['json_name'] ,'r') as file:
        items = json.load(file)
        update_smart_collections(items["groups"])
        for product in items["products"]:
            response = create_new_product(product)
            print(response)

main()