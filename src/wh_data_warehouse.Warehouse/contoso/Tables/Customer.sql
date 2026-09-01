CREATE TABLE [contoso].[Customer] (

	[CustomerKey] int NOT NULL, 
	[Gender] varchar(8000) NULL, 
	[Name] varchar(8000) NULL, 
	[Address] varchar(8000) NULL, 
	[City] varchar(8000) NULL, 
	[State Code] varchar(8000) NULL, 
	[State] varchar(8000) NULL, 
	[Zip Code] varchar(8000) NULL, 
	[Country Code] varchar(8000) NULL, 
	[Country] varchar(8000) NULL, 
	[Continent] varchar(8000) NULL, 
	[Birthday] date NULL, 
	[Age] int NULL
);


GO
ALTER TABLE [contoso].[Customer] ADD CONSTRAINT PK_Customer primary key NONCLUSTERED ([CustomerKey]);