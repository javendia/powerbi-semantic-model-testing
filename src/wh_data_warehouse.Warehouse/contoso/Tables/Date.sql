CREATE TABLE [contoso].[Date] (

	[Date] date NOT NULL, 
	[Year] int NULL, 
	[Year Quarter] varchar(8000) NULL, 
	[Year Quarter Number] int NULL, 
	[Quarter] varchar(8000) NULL, 
	[Year Month] varchar(8000) NULL, 
	[Year Month Short] varchar(8000) NULL, 
	[Year Month Number] int NULL, 
	[Month] varchar(8000) NULL, 
	[Month Short] varchar(8000) NULL, 
	[Month Number] int NULL, 
	[Day of Week] varchar(8000) NULL, 
	[Day of Week Short] varchar(8000) NULL, 
	[Day of Week Number] int NULL, 
	[Working Day] bit NULL, 
	[Working Day Number] int NULL
);


GO
ALTER TABLE [contoso].[Date] ADD CONSTRAINT PK_Date primary key NONCLUSTERED ([Date]);