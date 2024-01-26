IF(	(EXISTS (SELECT * 
         FROM INFORMATION_SCHEMA.TABLES 
         WHERE TABLE_SCHEMA = 'core' 
         AND  TABLE_NAME = 'Location'))
	 AND
	(EXISTS (SELECT * 
	         FROM INFORMATION_SCHEMA.TABLES 
	         WHERE TABLE_SCHEMA = 'core' 
	         AND  TABLE_NAME = 'LocationTypeDefinition'))
	AND
	(EXISTS (SELECT * 
	         FROM INFORMATION_SCHEMA.TABLES 
	         WHERE TABLE_SCHEMA = 'core' 
	         AND  TABLE_NAME = 'LocationType'))            
   )
SELECT 1 AS result ELSE SELECT 0 as result
	                 
	     
	                 