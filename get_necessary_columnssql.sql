SELECT 
	IP.Name as Title,
	IV.Description,
	IP.Price as Price,
	IV.UPC as Sku,
	IP.BarcodeNumber as Barcode,
	IP.OnHand as Quantity,
	IP.Brand as Vendor,
	IP.Groups as Type,
	IV.size as Size
  FROM [RDT].[dbo].ItemViewBasic IP
  JOIN RDT.dbo.FullItemNames FN
  ON FN.ItemID = IP.ItemID
  JOIN [RDT].[dbo].ItemInfoView IV
  on IV.ItemStoreID = FN.ItemStoreID