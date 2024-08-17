SELECT LocationID, Name
FROM Location
WHERE ParentLocationID IN (
	SELECT LocationID
	FROM Location
	WHERE Name = :Name)