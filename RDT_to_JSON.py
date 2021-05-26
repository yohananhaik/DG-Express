import pymssql  
import configparser
import json
import pyodbc
import os


config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)) ,'settings.ini'))

mssql_credentials =  {k:v for k, v in config['mssql'].items()}

conn = pymssql.connect(server=mssql_credentials.get('server'), 
                      user=mssql_credentials.get('username'), 
                      password=mssql_credentials.get('password'), 
                      database=mssql_credentials.get('database'))
cur = conn.cursor()
groups_set = set()
products = {"products":[]}

def get_type_name(code):
  query = "select ItemTypeName from ItemMainAndStoreView where BarcodeNumber ='{}'".format(code)
  cur.execute(query)
  return cur.fetchone()[0]

def get_sku_from_parent(parent):
      query = """SELECT DISTINCT I.BarcodeNumber [UPC] FROM ItemMainAndStoreView I 
                  WHERE I.LinkNo IN (SELECT ItemID FROM ItemMainAndStoreView WHERE BarcodeNumber = '{}') 
                  ORDER BY BarcodeNumber""".format(parent)
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
      sku.extend(get_sku_from_parent(parents))
      return sku

# def build_variant(variant):
#       # type,name,price,UPC,onhand, weight,colorfireld,color,sizefield,size
#       type_name,name,price,sku,onHand,weight,color_field,color,size_field,size = variant

#       return build_variants_value()


def get_variants(sku):
      variants=[]
      variants_codes = get_sku_from_parent(sku)
      query = """select distinct 
            I.ItemTypeName
            ,I.[Name]
            ,I.Price
            ,I.BarcodeNumber [UPC]
            ,I.OnHand
            ,I.CustomField4 [colorfield]
            ,I.Matrix1 [color]
            ,I.CustomField2 [sizefield]
            ,I.Matrix2 [size]
            from 
            ItemMainAndStoreView I 
            where I.BarcodeNumber in {}
            order by BarcodeNumber""".format(str(variants_codes).replace('[','(').replace(']',')'))
      cur.execute(query)
      for row in cur:
            # name, price,sku,onHand,color_field,color,size_field,size
            print (*row)
            variants.append(build_variants_value(*row[1:]))
      return variants

def build_product_information(code):
      query = """select distinct 
            I.ItemTypeName,
            ItemGroupName = STUFF((
                        SELECT distinct ',' + G.ItemGroupName
                        FROM itemgroup G
            JOIN ItemtoGroup IG ON G.ItemGroupID = IG.ItemGroupID
                        WHERE I.ItemStoreID = IG.ItemStoreID
                        FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(500)'), 1, 1, '')
            ,I.[Name]
            ,I.Brand
            ,I.Price
            ,I.BarcodeNumber [UPC]
            ,I.OnHand
            ,I.Customfield1 [weight]
            ,I.CustomField4 [colorfield]
            ,I.Matrix1 [color]
            ,I.CustomField2 [sizefield]
            ,I.Matrix2 [size]
            from 
            ItemMainAndStoreView I 
            where I.BarcodeNumber = '{}'
            order by BarcodeNumber""".format(code)
      cur.execute(query)
      build_product(cur.fetchall()[0])

def build_variants_value(name, price,sku,onHand,color_field,color,size_field,size):
      var_options = {"Style":"-","Size":"-","Color":"-"}
      if color_field in ['Package','Neck']:
            var_options["Style"] = color
      elif size_field in ['Package','Neck']:
            var_options["Style"] = size   
                    
      var_options[color_field if color_field else "Color"] = color
      var_options[size_field if size_field else "Size"] = size
      
      return {
            "title":name,
            "price":str(price),
            "sku": str(sku),
            "barcode" :str(sku),
            "inventory_quantity":int(onHand),
            "option1":var_options.get("Style"),
            "option2":var_options.get("Size"),
            "option3":var_options.get("Color"),
            "tracked":True
      }

def build_product(row):
      type_name,groups,name,brand, price,sku, onHand,weight,color_field,color,size_field,size = row

      if type_name == "Parent":
            variants = get_variants(sku)
      elif type_name == "SKU":
            variants = build_variants_value(name, price,sku,onHand,color_field,color,size_field,size)

      options = [{"name":"Style"},{"name": "Size"},{"name":"Color"}]
     
      product ={
            "product": {
            "title": name,
            "vendor": brand,
            "tags": groups,
            "weight":weight,
            "options": options,
            "variants": variants,
            "status": "draft"
            }
            }
      products["products"].append(product)
      groups_set.update(groups.split(','))


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
      codes = mssql_credentials.get('sku').split(',')
      for code in codes:
            build_product_information(code)
      
      json_groups = {"groups":list(groups_set)}
      
      data = {**products,**json_groups}

      with open(mssql_credentials.get('json_name'),'w') as file:
            json.dump(data,file)


main()