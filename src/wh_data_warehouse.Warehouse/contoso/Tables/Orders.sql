CREATE TABLE [contoso].[Orders] (

	[Order Number] bigint NULL, 
	[Line Number] int NULL, 
	[CustomerKey] int NULL, 
	[StoreKey] int NULL, 
	[ProductKey] int NULL, 
	[Order Date] date NULL, 
	[Delivery Date] date NULL, 
	[Quantity] int NULL, 
	[Unit Price] decimal(19,4) NULL, 
	[Net Price] decimal(19,4) NULL, 
	[Unit Cost] decimal(19,4) NULL, 
	[Currency Code] varchar(8000) NULL
);


GO
ALTER TABLE [contoso].[Orders] ADD CONSTRAINT FK_rel_orders_customer FOREIGN KEY ([CustomerKey]) REFERENCES [contoso].[Customer]([CustomerKey]);
GO
ALTER TABLE [contoso].[Orders] ADD CONSTRAINT FK_rel_orders_date FOREIGN KEY ([Order Date]) REFERENCES [contoso].[Date]([Date]);
GO
ALTER TABLE [contoso].[Orders] ADD CONSTRAINT FK_rel_orders_product FOREIGN KEY ([ProductKey]) REFERENCES [contoso].[Product]([ProductKey]);
GO
ALTER TABLE [contoso].[Orders] ADD CONSTRAINT FK_rel_orders_store FOREIGN KEY ([StoreKey]) REFERENCES [contoso].[Store]([StoreKey]);