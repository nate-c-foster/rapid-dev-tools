SELECT l.LocationID, l.parentLocationId, l.Name, l.Description, l.Latitude, l.Longitude, l.orderNumber, l.shortName, l.locationTypeID, lt.Name AS locationType, l.LastModifiedOn, l.LastModifiedBy, lt.Icon, ltd.LocationTypeDefinitionID, ltd.Name AS locationTypeDefinition, ltd.UDTPath, ltd.IgnitionTemplatePath
FROM core.Location l
INNER JOIN core.LocationType lt ON l.LocationTypeID = lt.LocationTypeID
INNER JOIN core.LocationTypeDefinition ltd ON l.LocationTypeDefinitionID = ltd.LocationTypeDefinitionID
WHERE l.isActive = 1