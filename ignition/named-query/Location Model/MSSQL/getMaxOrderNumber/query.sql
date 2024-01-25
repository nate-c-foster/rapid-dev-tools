SELECT MAX(orderNumber)
FROM core.Location
WHERE ParentLocationID = :parentLocationID and isActive = 1