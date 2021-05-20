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
groups = set()
products = {"products":[]}

def get_type_name(code):
  query = "select ItemTypeName from ItemMainAndStoreView where BarcodeNumber ='{}'".format(code)
  cur.execute(query)
  return cur.fetchone()[0]

def get_sku_from_parents(parents):
      query = """SELECT DISTINCT I.BarcodeNumber [UPC] FROM ItemMainAndStoreView I 
                  WHERE I.LinkNo IN (SELECT ItemID FROM ItemMainAndStoreView WHERE BarcodeNumber IN {}) 
                  ORDER BY BarcodeNumber""".format(str(parents).replace('[','(').replace(']',')'))
      cur.execute(query)
      skus = [sku[0] for sku in cur.fetchall()]
      return skus

def get_barcode_numbers():
      codes = mssql_credentials.get('sku').split(',')
      parents=[]
      sku=[]
      for code in codes:
            type_name = get_type_name(code)
            if type_name == 'Parent':
                  parents.append(code)
            elif type_name == 'SKU':
                  sku.append(code)
      sku.extend(get_sku_from_parents(parents))
      return sku


def select_rows(row_num=0):
  barcodes = get_barcode_numbers()
  # query = "SELECT {} Name,Description,Brand, Price,BarcodeNumber, OnHand,Size,'' as Color,'' as Weight,Groups FROM dbo.ItemMainAndStoreView ;".format("TOP "+str(row_num) if row_num>0 else "*")
  query = """select distinct 
        ItemGroupName = STUFF((
                  SELECT distinct ',' + G.ItemGroupName
                  FROM itemgroup G
        JOIN ItemtoGroup IG ON G.ItemGroupID = IG.ItemGroupID
                  WHERE I.ItemStoreID = IG.ItemStoreID
                  FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(500)'), 1, 1, '')
        ,I.[Name]
        ,I.[Description]
        ,I.Brand
        ,I.Price
        ,I.BarcodeNumber [UPC]
        ,I.OnHand
        ,NULL [Color]
        ,NULL [weight]
        ,I.Matrix2 [size] 
        from 
        ItemMainAndStoreView I 
        where I.BarcodeNumber in {}
        order by BarcodeNumber""".format(str(barcodes).replace('[','(').replace(']',')'))
  cur.execute(query)
  return cur



def create_product_object(row):
  groups,name,description,brand, price,sku, onHand,color,weight,size = row
  options = []
  if size:
        options.append({"name": "Size","values": size })
  if color:
        options.append({"name": "Color","values": color })
  product ={
        "product": {
          "title": name,
          "body_html": description,
          "vendor": brand,
          "product_type": groups,
          "weight":weight,

          "variants": [
            {
              "title":name,
              "price":str(price),
              "sku": str(sku),
              "barcode" :str(sku),
              "inventory_quantity":int(onHand),
              "option1":size,
              "option2":color,
              "tracked":True
            }],
            "options": options,
          "status": "draft"
        }
      }
  products["products"].append(product)

def get_all_groups(barcodes):
      query="""select distinct 
            ItemGroupName = STUFF((
                      SELECT distinct ',' + G.ItemGroupName
                      FROM itemgroup G
            JOIN ItemtoGroup IG ON G.ItemGroupID = IG.ItemGroupID
                      WHERE I.ItemStoreID = IG.ItemStoreID
                      FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(500)'), 1, 1, '')
            from 
            ItemMainAndStoreView I 
            where I.BarcodeNumber in {}""".format(str(barcodes).replace('[','(').replace(']',')'))
      cur.execute(query)
      return cur.fetchone()[0]

def main():
  cur = select_rows()
  for row in cur:
    create_product_object(row)
    groups.update(row[0].split(','))
  
  json_groups = {"groups":list(groups)}
  
  data = {**products,**json_groups}

  with open(mssql_credentials.get('json_name'),'w') as file:
    json.dump(data,file)


main()