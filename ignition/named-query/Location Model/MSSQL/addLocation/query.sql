INSERT INTO core.Location 
(ParentLocationID, LocationTypeID, Name, Description, IsActive, LastModifiedBy, LastModifiedOn,LocationTypeDefinitionID,orderNumber,shortName) 
VALUES (:ParentLocationID,:LocationTypeID,:Name,:Description,1,:LastModifiedBy,GETDATE(),:LocationTypeDefinitionID,:orderNumber,:ShortName)