UPDATE Location 
SET LocationTypeID = :LocationTypeID, Name = :Name, Description = :Description, LastModifiedBy = :LastModifiedBy, LastModifiedOn = datetime('now'),LocationTypeDefinitionID = :LocationTypeDefinitionID, shortName = :ShortName, ScadaView = :ScadaView
WHERE LocationID = :LocationID