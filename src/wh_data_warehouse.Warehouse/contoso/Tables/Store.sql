CREATE TABLE [contoso].[Store] (

	[StoreKey] int NOT NULL, 
	[Store Code] int NULL, 
	[Country] varchar(8000) NULL, 
	[State] varchar(8000) NULL, 
	[Name] varchar(8000) NULL, 
	[Square Meters] int NULL, 
	[Open Date] date NULL, 
	[Close Date] date NULL, 
	[Status] varchar(8000) NULL
);


GO
ALTER TABLE [contoso].[Store] ADD CONSTRAINT PK_Store primary key NONCLUSTERED ([StoreKey]);