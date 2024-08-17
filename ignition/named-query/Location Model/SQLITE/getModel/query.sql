SELECT l.LocationID, l.parentLocationId, l.Name, l.Description, l.Latitude, l.Longitude, l.orderNumber, l.shortName, l.locationTypeID, l.ScadaView, lt.Name AS locationType, l.LastModifiedOn, l.LastModifiedBy, lt.Icon, ltd.LocationTypeDefinitionID, ltd.Name AS locationTypeDefinition, ltd.UDTPath, ltd.IgnitionTemplatePath
FROM Location l
INNER JOIN LocationType lt ON l.LocationTypeID = lt.LocationTypeID
INNER JOIN LocationTypeDefinition ltd ON l.LocationTypeDefinitionID = ltd.LocationTypeDefinitionID
WHERE l.isActive = 1