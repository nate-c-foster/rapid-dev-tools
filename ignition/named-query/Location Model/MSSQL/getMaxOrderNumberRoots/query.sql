SELECT MAX(orderNumber)
FROM core.Location
WHERE ParentLocationID is NULL and isActive = 1