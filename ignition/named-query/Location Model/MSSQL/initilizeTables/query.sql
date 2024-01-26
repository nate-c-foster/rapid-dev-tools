
IF ( :version = 'Water_1.3' )
BEGIN

	-- Remove tables if they alread exist
	IF (EXISTS (SELECT * 
	                 FROM INFORMATION_SCHEMA.TABLES 
	                 WHERE TABLE_SCHEMA = 'core' 
	                 AND  TABLE_NAME = 'Location'))
	                 
	BEGIN
	DROP TABLE core.Location
	END
	
	IF (EXISTS (SELECT * 
	                 FROM INFORMATION_SCHEMA.TABLES 
	                 WHERE TABLE_SCHEMA = 'core' 
	                 AND  TABLE_NAME = 'LocationTypeDefinition'))
	                 
	BEGIN
	DROP TABLE core.LocationTypeDefinition
	END
	
	
	IF (EXISTS (SELECT * 
	                 FROM INFORMATION_SCHEMA.TABLES 
	                 WHERE TABLE_SCHEMA = 'core' 
	                 AND  TABLE_NAME = 'LocationType'))
	                 
	BEGIN
	DROP TABLE core.LocationType
	END
	
	-- Create new tables

	CREATE TABLE [core].[Location](
		[LocationID] [int] IDENTITY(60,1) NOT NULL,
		[ParentLocationID] [int] NULL,
		[LocationTypeID] [int] NULL,
		[Name] [nvarchar](50) NOT NULL,
		[Description] [nvarchar](max) NULL,
		[isActive] [bit] NULL,
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
		[ScadaView] [varchar](max) NULL,
		[shortName] [nvarchar](50) NULL,
	 CONSTRAINT [PK_Location] PRIMARY KEY (LocationID)
	 );
 
	CREATE TABLE [core].[LocationTypeDefinition](
		[LocationTypeDefinitionID] [int] IDENTITY(1,1) NOT NULL,
		[Name] [nvarchar](50) NOT NULL,
		[Description] [nvarchar](max) NULL,
		[UDTPath] [nvarchar](100) NULL,
		[isActive] [int] NULL,
		[LastModifiedBy] [nvarchar](50) NULL,
		[LastModifiedOn] [datetime] NULL,
		[LocationTypeID] [int] NOT NULL,
		[IgnitionTemplatePath] [nvarchar](100) NULL,
		[IgnitionPIDTemplatePath] [nvarchar](max) NULL,
	 	CONSTRAINT [PK_LocationTypeDefinitionID] PRIMARY KEY (LocationTypeDefinitionID)
	 	);

	CREATE TABLE [core].[LocationType](
		[LocationTypeID] [int] IDENTITY(1,1) NOT NULL,
		[Name] [nvarchar](50) NOT NULL,
		[Description] [nvarchar](max) NULL,
		[Icon] [nvarchar](50) NULL,
		[isActive] [bit] NULL,
		[LastModifiedBy] [nvarchar](50) NULL,
		[LastModifiedOn] [datetime] NULL,
	 CONSTRAINT [PK_LocationTypeID] PRIMARY KEY (LocationTypeID)
	 );
	 	
	 	
	-- Add data
	INSERT INTO core.Location (ParentLocationID, Name, Description, isActive, LastModifiedBy, LastModifiedOn, LocationTypeID, LocationTypeDefinitionID, orderNumber)
	VALUES
	(NULL, N'State', N'Example Root Location', 1, N'Project Initializer', getDate(), 2, 2, 1);
	
	
	SET IDENTITY_INSERT [core].[LocationTypeDefinition] ON 
	INSERT [core].[LocationTypeDefinition] ([LocationTypeDefinitionID], [Name], [Description], [UDTPath], [isActive], [LastModifiedBy], [LastModifiedOn], [LocationTypeID], [IgnitionTemplatePath], [IgnitionPIDTemplatePath]) VALUES (1, N'Enterprise', N'Root level of hierarchy', N'[SCADA]_types_/Location Types/Enterprise', 1, N'Project Initializer', getDate(), 1, N'Templates/Types/Enterprise Metrics', N'')
	INSERT [core].[LocationTypeDefinition] ([LocationTypeDefinitionID], [Name], [Description], [UDTPath], [isActive], [LastModifiedBy], [LastModifiedOn], [LocationTypeID], [IgnitionTemplatePath], [IgnitionPIDTemplatePath]) VALUES (2, N'State', N'State entity of model', N'[SCADA]_types_/Location Types/State', 1, N'Project Initializer', getDate(), 2, N'SCADA/AWS Templates/View Templates/Higher Level Location', N'')
	INSERT [core].[LocationTypeDefinition] ([LocationTypeDefinitionID], [Name], [Description], [UDTPath], [isActive], [LastModifiedBy], [LastModifiedOn], [LocationTypeID], [IgnitionTemplatePath], [IgnitionPIDTemplatePath]) VALUES (3, N'Water System', N'Water entity of system', N'[SCADA]_types_/Location Types/Water System', 1, N'Project Initializer', getDate(), 3, N'SCADA/AWS Templates/View Templates/Higher Level Location', N'')
	INSERT [core].[LocationTypeDefinition] ([LocationTypeDefinitionID], [Name], [Description], [UDTPath], [isActive], [LastModifiedBy], [LastModifiedOn], [LocationTypeID], [IgnitionTemplatePath], [IgnitionPIDTemplatePath]) VALUES (4, N'Waste Water System', N'Waste Water entity of system', N'[SCADA]_types_/Location Types/Wastewater System', 1, N'Project Initializer', getDate(), 4, N'SCADA/AWS Templates/View Templates/Higher Level Location', N'')
	INSERT [core].[LocationTypeDefinition] ([LocationTypeDefinitionID], [Name], [Description], [UDTPath], [isActive], [LastModifiedBy], [LastModifiedOn], [LocationTypeID], [IgnitionTemplatePath], [IgnitionPIDTemplatePath]) VALUES (5, N'Ground Water Plant', N'Ground Water entity ', N'[SCADA]_types_/Site/Ground Water Plant', 1, N'Project Initializer', getDate(), 5, N'SCADA/AWS Templates/View Templates/Higher Level Location', N'')
	INSERT [core].[LocationTypeDefinition] ([LocationTypeDefinitionID], [Name], [Description], [UDTPath], [isActive], [LastModifiedBy], [LastModifiedOn], [LocationTypeID], [IgnitionTemplatePath], [IgnitionPIDTemplatePath]) VALUES (6, N'Surface Water Plant', N'Surface Water entity', N'[SCADA]_types_/Site/Surface Water Plant', 1, N'Project Initializer', getDate(), 5, N'SCADA/AWS Templates/View Templates/Higher Level Location', N'')
	INSERT [core].[LocationTypeDefinition] ([LocationTypeDefinitionID], [Name], [Description], [UDTPath], [isActive], [LastModifiedBy], [LastModifiedOn], [LocationTypeID], [IgnitionTemplatePath], [IgnitionPIDTemplatePath]) VALUES (7, N'General Process', N'Process entity', N'[SCADA]_types_/Processes/General Process', 1, N'Project Initializer', getDate(), 6, N'SCADA/Templates/View/Process', N'')
	INSERT [core].[LocationTypeDefinition] ([LocationTypeDefinitionID], [Name], [Description], [UDTPath], [isActive], [LastModifiedBy], [LastModifiedOn], [LocationTypeID], [IgnitionTemplatePath], [IgnitionPIDTemplatePath]) VALUES (8, N'General Process Stage', N'Process Stage entity', N'[SCADA]_types_/Process Stage/General Process Stage', 1, N'Project Initializer', getDate(), 8, N'SCADA/AWS Templates/View Templates/Higher Level Location', N'')
	INSERT [core].[LocationTypeDefinition] ([LocationTypeDefinitionID], [Name], [Description], [UDTPath], [isActive], [LastModifiedBy], [LastModifiedOn], [LocationTypeID], [IgnitionTemplatePath], [IgnitionPIDTemplatePath]) VALUES (17, N'Military Base', N'Military Base', N'[SCADA]_types_/Location Types/Military Base', 1, N'Project Initializer', getDate(), 9, N'SCADA/AWS Templates/View Templates/Higher Level Location', N'')
	INSERT [core].[LocationTypeDefinition] ([LocationTypeDefinitionID], [Name], [Description], [UDTPath], [isActive], [LastModifiedBy], [LastModifiedOn], [LocationTypeID], [IgnitionTemplatePath], [IgnitionPIDTemplatePath]) VALUES (19, N'Wastewater Remote Sites', N'Lift Stations ...', N'[SCADA]_types_/Site/Wastewater Remote Sites', 1, N'Project Initializer', getDate(), 5, N'SCADA/AWS Templates/View Templates/Higher Level Location', N'')
	INSERT [core].[LocationTypeDefinition] ([LocationTypeDefinitionID], [Name], [Description], [UDTPath], [isActive], [LastModifiedBy], [LastModifiedOn], [LocationTypeID], [IgnitionTemplatePath], [IgnitionPIDTemplatePath]) VALUES (2025, N'General Water System', N'Container of Water Systems', N'[SCADA]_types_/Location Types/General Water System', 1, N'Project Initializer', getDate(), 10, N'SCADA/AWS Templates/View Templates/Higher Level Location', N'')
	INSERT [core].[LocationTypeDefinition] ([LocationTypeDefinitionID], [Name], [Description], [UDTPath], [isActive], [LastModifiedBy], [LastModifiedOn], [LocationTypeID], [IgnitionTemplatePath], [IgnitionPIDTemplatePath]) VALUES (2026, N'Wastewater Plant', N'Wastewater Treatment Plant', N'[SCADA]_types_/Site/Wastewater Plant', 1, N'Project Initializer', getDate(), 5, N'SCADA/AWS Templates/View Templates/Higher Level Location', N'')
	SET IDENTITY_INSERT [core].[LocationTypeDefinition] OFF
	
	
	SET IDENTITY_INSERT [core].[LocationType] ON 
	INSERT [core].[LocationType] ([LocationTypeID], [Name], [Description], [Icon], [isActive], [LastModifiedBy], [LastModifiedOn]) VALUES (1, N'Enterprise', N'Enterprise level', N'material/apartment', 1, N'Project Initializer', getDate())
	INSERT [core].[LocationType] ([LocationTypeID], [Name], [Description], [Icon], [isActive], [LastModifiedBy], [LastModifiedOn]) VALUES (2, N'State', N'State of system location', N'material/location_city', 1, N'Project Initializer', getDate())
	INSERT [core].[LocationType] ([LocationTypeID], [Name], [Description], [Icon], [isActive], [LastModifiedBy], [LastModifiedOn]) VALUES (3, N'Water System', N'Water System within a state', N'flexware/water', 1, N'Project Initializer', getDate())
	INSERT [core].[LocationType] ([LocationTypeID], [Name], [Description], [Icon], [isActive], [LastModifiedBy], [LastModifiedOn]) VALUES (4, N'Wastewater System', N'Wastewaster system within a state', N'flexware/waste_water', 1, N'Project Initializer', getDate())
	INSERT [core].[LocationType] ([LocationTypeID], [Name], [Description], [Icon], [isActive], [LastModifiedBy], [LastModifiedOn]) VALUES (5, N'Site', N'Site within system', N'flexware/water', 1, N'Project Initializer', getDate())
	INSERT [core].[LocationType] ([LocationTypeID], [Name], [Description], [Icon], [isActive], [LastModifiedBy], [LastModifiedOn]) VALUES (6, N'Process', N'Process within a site', N'flexware/process', 1, N'Project Initializer', getDate())
	INSERT [core].[LocationType] ([LocationTypeID], [Name], [Description], [Icon], [isActive], [LastModifiedBy], [LastModifiedOn]) VALUES (7, N'Component', N'Component within a process', N'material/settings', 1, N'Project Initializer', getDate())
	INSERT [core].[LocationType] ([LocationTypeID], [Name], [Description], [Icon], [isActive], [LastModifiedBy], [LastModifiedOn]) VALUES (8, N'Process Stage', N'Process Stage', N'flexware/process_group', 1, N'Project Initializer', getDate())
	INSERT [core].[LocationType] ([LocationTypeID], [Name], [Description], [Icon], [isActive], [LastModifiedBy], [LastModifiedOn]) VALUES (9, N'Military Base', N'Military Service Site', N'', 1, N'Project Initializer', getDate())
	INSERT [core].[LocationType] ([LocationTypeID], [Name], [Description], [Icon], [isActive], [LastModifiedBy], [LastModifiedOn]) VALUES (10, N'General Water System', N'Container of Water Systems', N'', 1, N'Project Initializer', getDate())
	SET IDENTITY_INSERT [core].[LocationType] OFF
	
	

	-- add foreign key contraints
	ALTER TABLE [core].[Location]  WITH CHECK ADD  CONSTRAINT [FK_Location_LocationType] FOREIGN KEY([LocationTypeID])
	REFERENCES [core].[LocationType] ([LocationTypeID])
	ON DELETE CASCADE
	
	ALTER TABLE [core].[Location] CHECK CONSTRAINT [FK_Location_LocationType]

	ALTER TABLE [core].[LocationTypeDefinition]  WITH CHECK ADD  CONSTRAINT [FK_LocationType_LocationTypeDefinition] FOREIGN KEY([LocationTypeID])
	REFERENCES [core].[LocationType] ([LocationTypeID])
	ON DELETE CASCADE

	ALTER TABLE [core].[LocationTypeDefinition] CHECK CONSTRAINT [FK_LocationType_LocationTypeDefinition]

END	

