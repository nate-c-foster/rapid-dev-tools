SELECT LocationID, orderNumber, Name
FROM Location
WHERE ParentLocationID IS NULL  and isActive = 1