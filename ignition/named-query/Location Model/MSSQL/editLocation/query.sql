UPDATE core.Location 
SET LocationTypeID = :LocationTypeID, Name = :Name, Description = :Description, LastModifiedBy = :LastModifiedBy, LastModifiedOn = getDate(),LocationTypeDefinitionID = :LocationTypeDefinitionID, shortName = :ShortName
WHERE LocationID = :LocationID