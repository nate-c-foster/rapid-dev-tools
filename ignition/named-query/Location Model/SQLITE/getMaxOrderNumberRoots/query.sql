SELECT MAX(orderNumber)
FROM Location
WHERE ParentLocationID is NULL and isActive = 1