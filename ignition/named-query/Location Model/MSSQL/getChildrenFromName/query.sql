SELECT LocationID, Name
FROM core.Location
WHERE ParentLocationID IN (
	SELECT LocationID
	FROM core.Location
	WHERE Name = :Name)