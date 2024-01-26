SELECT LocationID, orderNumber, Name
FROM core.Location
WHERE ParentLocationID IS NULL  and isActive = 1