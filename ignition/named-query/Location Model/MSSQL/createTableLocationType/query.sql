
BEGIN


	-- ****************** core Schema ******************
	IF (NOT EXISTS (SELECT name FROM sys.schemas WHERE name=N'core'))
	
	BEGIN
		EXEC('CREATE SCHEMA [core] AUTHORIZATION [dbo]');
	END
	
	
	-- ******************    LocationType      ****************** 
	IF (NOT EXISTS (SELECT * 
	                 FROM INFORMATION_SCHEMA.TABLES 
	                 WHERE TABLE_SCHEMA = 'core' 
	                 AND  TABLE_NAME = 'LocationType'))
	                 
	BEGIN
	
		CREATE TABLE [core].[LocationType](
			[LocationTypeID] [int] IDENTITY(1,1) NOT NULL,
			[Name] [nvarchar](50) NOT NULL DEFAULT 'New Name',
			[Description] [nvarchar](max) NULL,
			[Icon] [nvarchar](50) NULL,
			[isActive] [bit] NULL DEFAULT 1,
			[LastModifiedBy] [nvarchar](50) NULL,
			[LastModifiedOn] [datetime] NULL,
		 CONSTRAINT [PK_LocationTypeID] PRIMARY KEY (LocationTypeID)
		 );

	END
	 
END