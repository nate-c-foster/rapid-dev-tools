SELECT LocationID, orderNumber, Name
FROM Location
WHERE ParentLocationID = :LocationID and isActive = 1