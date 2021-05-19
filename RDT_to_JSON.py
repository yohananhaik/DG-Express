import pymssql  
import configparser
import json
import pyodbc


config = configparser.ConfigParser()
config.read('settings.ini')

mssql_credentials =  {k:v for k, v in config['mssql'].items()}

conn = pymssql.connect(server=mssql_credentials.get('server'), 
                      user=mssql_credentials.get('username'), 
                      password=mssql_credentials.get('password'), 
                      database=mssql_credentials.get('database'))
cur = conn.cursor()

products = {"products":[]}

def select_rows(row_num=0):
  query = "SELECT {} Name,Description,Brand, Price,BarcodeNumber, OnHand,Size,Groups FROM dbo.ItemMainAndStoreView ;".format("TOP "+str(row_num) if row_num>0 else "*")
  cur.execute(query)
  return cur

def create_product_object(row):
  name,description,brand, price,sku, onHand,size,groups = row
  product ={
        "product": {
          "title": name,
          "body_html": description,
          "vendor": brand,
          "product_type": groups,

          "variants": [
            {
              "title":name,
              "price":str(price),
              "sku": str(sku),
              "barcode" :str(sku),
              "inventory_quantity":int(onHand),
              "tracked":True
            }],
            "options": [] if size and len(size)==0 else [{"name": "Size","values": [str(size)]}],
          "status": "draft"
        }
      }
  products["products"].append(product)

def main():
  cur = select_rows(10)
  for row in cur:
    create_product_object(row)
  with open(mssql_credentials.get('json_name'),'w') as file:
    json.dump(products,file)


main()