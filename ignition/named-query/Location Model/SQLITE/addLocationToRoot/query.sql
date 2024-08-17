INSERT INTO Location 
(ParentLocationID, LocationTypeID, Name, Description, IsActive, LastModifiedBy, LastModifiedOn,LocationTypeDefinitionID,orderNumber,shortName) 
VALUES (NULL,:LocationTypeID,:Name,:Description,1,:LastModifiedBy,GETDATE(),:LocationTypeDefinitionID,:orderNumber,:ShortName)