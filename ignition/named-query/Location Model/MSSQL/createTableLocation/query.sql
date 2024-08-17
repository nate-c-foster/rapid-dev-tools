
BEGIN


	-- ****************** core Schema ******************
	IF (NOT EXISTS (SELECT name FROM sys.schemas WHERE name=N'core'))
	
	BEGIN
		EXEC('CREATE SCHEMA [core] AUTHORIZATION [dbo]');
	END
	
	
	-- ******************    Location      ****************** 
	IF (NOT EXISTS (SELECT * 
	                 FROM INFORMATION_SCHEMA.TABLES 
	                 WHERE TABLE_SCHEMA = 'core' 
	                 AND  TABLE_NAME = 'Location'))
	                 
	BEGIN
	
		CREATE TABLE [core].[Location](
			[LocationID] [int] IDENTITY(60,1) NOT NULL,
			[ParentLocationID] [int] NULL,
			[LocationTypeID] [int] NULL,
			[Name] [nvarchar](50) NOT NULL DEFAULT 'New Name',
			[Description] [nvarchar](max) NULL,
			[isActive] [bit] NULL DEFAULT 1,
			[LastModifiedBy] [nvarchar](50) NULL,
			[LastModifiedOn] [datetime] NULL,
			[ZoomLevel] [int] NULL,
			[Latitude] [decimal](8, 6) NULL,
			[Longitude] [decimal](8, 6) NULL,
			[MQTTPath] [nvarchar](100) NULL,
			[LocationTypeDefinitionID] [int] NULL,
			[MapCallID] [int] NULL,
			[HmiUrl] [nvarchar](max) NULL,
			[orderNumber] [int] NULL,
			[ScadaView] [bit] NOT NULL DEFAULT 1,
			[shortName] [nvarchar](50) NULL,
		 	CONSTRAINT [PK_Location] PRIMARY KEY (LocationID),
			CONSTRAINT "FK_Location_LocationType" FOREIGN KEY("LocationTypeID") REFERENCES [core].[LocationType] ([LocationTypeID])
		 );
	END
	 
END
