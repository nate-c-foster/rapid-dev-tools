UPDATE core.Location 
SET LocationTypeID = :LocationTypeID, Name = :Name, Description = :Description, LastModifiedBy = :LastModifiedBy, LastModifiedOn = getDate(),LocationTypeDefinitionID = :LocationTypeDefinitionID, shortName = :ShortName, ScadaView = :ScadaView
WHERE LocationID = :LocationID