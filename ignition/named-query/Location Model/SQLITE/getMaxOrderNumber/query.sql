SELECT MAX(orderNumber)
FROM Location
WHERE ParentLocationID = :parentLocationID and isActive = 1