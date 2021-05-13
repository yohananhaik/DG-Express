import pymssql  
import configparser
import json

config = configparser.ConfigParser()
config.read('settings.ini')

mssql_credentials =  {k:v for k, v in config['mssql'].items()}

conn = pymssql.connect("""server='{}', user='{}', password='{}', database='{}''""".format(
        mssql_credentials.get('server'),
        mssql_credentials.get('username'),
        mssql_credentials.get('password'),
        mssql_credentials.get('database'),
))
cur = conn.cursor()

query = """SELECT (TOP 10)
	IP.Name as Title,
	IV.Description,
	IP.Price as Price,
	IV.UPC as Sku,
	IP.BarcodeNumber as Barcode,
	IP.OnHand as Quantity,
	IP.Brand as Vendor,
	IP.Groups as Type,
	IV.size as Size
  FROM RDT.dbo.ItemViewBasic IP
  JOIN RDT.dbo.FullItemNames FN
  ON FN.ItemID = IP.ItemID
  JOIN RDT.db].ItemInfoView IV
  on IV.ItemStoreID = FN.ItemStoreID"""

cur.execute(query)

for row in cur:
      print(row)