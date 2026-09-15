CREATE TABLE [contoso].[Product] (

	[ProductKey] int NOT NULL, 
	[Product Code] varchar(8000) NULL, 
	[Product Name] varchar(8000) NULL, 
	[Manufacturer] varchar(8000) NULL, 
	[Brand] varchar(8000) NULL, 
	[Color] varchar(8000) NULL, 
	[Weight Unit Measure] varchar(8000) NULL, 
	[Weight] float NULL, 
	[Unit Cost] decimal(19,4) NULL, 
	[Unit Price] decimal(19,4) NULL, 
	[Subcategory Code] int NULL, 
	[Subcategory] varchar(8000) NULL, 
	[Category Code] int NULL, 
	[Category] varchar(8000) NULL
);


GO
ALTER TABLE [contoso].[Product] ADD CONSTRAINT PK_Product primary key NONCLUSTERED ([ProductKey]);