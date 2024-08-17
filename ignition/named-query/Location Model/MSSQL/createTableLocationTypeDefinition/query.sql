
BEGIN


	-- ****************** core Schema ******************
	IF (NOT EXISTS (SELECT name FROM sys.schemas WHERE name=N'core'))
	
	BEGIN
		EXEC('CREATE SCHEMA [core] AUTHORIZATION [dbo]');
	END
	
	
	-- ******************    LocationTypeDefinition     ****************** 
	IF (NOT EXISTS (SELECT * 
	                 FROM INFORMATION_SCHEMA.TABLES 
	                 WHERE TABLE_SCHEMA = 'core' 
	                 AND  TABLE_NAME = 'LocationTypeDefinition'))
	                 
	BEGIN
	
		CREATE TABLE [core].[LocationTypeDefinition](
			[LocationTypeDefinitionID] [int] IDENTITY(1,1) NOT NULL,
			[Name] [nvarchar](50) NOT NULL DEFAULT 'New Name',
			[Description] [nvarchar](max) NULL,
			[UDTPath] [nvarchar](100) NULL,
			[isActive] [int] NULL DEFAULT 1,
			[LastModifiedBy] [nvarchar](50) NULL,
			[LastModifiedOn] [datetime] NULL,
			[LocationTypeID] [int] NOT NULL DEFAULT 1,
			[IgnitionTemplatePath] [nvarchar](100) NULL,
			[IgnitionPIDTemplatePath] [nvarchar](max) NULL,
		 	CONSTRAINT [PK_LocationTypeDefinitionID] PRIMARY KEY (LocationTypeDefinitionID),
			CONSTRAINT "FK_LocationTypeDefinition_LocationType" FOREIGN KEY("LocationTypeID") REFERENCES [core].[LocationType] ([LocationTypeID])
		 	);

	END
	 
END