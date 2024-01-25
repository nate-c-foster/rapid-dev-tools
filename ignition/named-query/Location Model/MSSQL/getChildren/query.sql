SELECT LocationID, orderNumber, Name
FROM core.Location
WHERE ParentLocationID = :LocationID and isActive = 1