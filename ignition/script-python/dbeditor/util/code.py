#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Dec 2022
# Description: imports a dataset into a database table
#
# Input arguments:
#	dataset			(dataset)      dataset with same header names as the DB table
#	database 		(string)		Example: "SCADA"
#	tableName 		(string)		Example: "core.Location"
# 	primaryKey		(string)		Example: "LocationID"
# 	deleteExtra		(bool)			flag to delete extra rows not in the dataset
#  
#*****************************************************************************************************		
def importDSintoDBtable(dataset, database, tableName, primaryKey, deleteExtra=True):

	jsonData =	util.json.convertDsToJsonObj(dataset)

	dataHeaders = dataset.getColumnNames()
	results = system.db.runQuery("SELECT * FROM " + tableName, database)
	tableHeaders = results.getColumnNames()
	
	for header in dataHeaders:
		if header not in tableHeaders:
			print "Import Error: Header " + str(header) + " not in table"
			return

	
	# get all ids in jsonData
	newIDs = [row[primaryKey] for row in jsonData]

	# get all ids in DB
	results = system.db.runQuery("SELECT " + primaryKey + " FROM " + tableName, database)
	currentIDs = []
	for row in range(results.getRowCount()):
		currentIDs.append(results.getValueAt(row,0))
		
	extraIDs = []
	for ID in currentIDs:
		if ID not in newIDs:
			extraIDs.append(ID)
			
	if deleteExtra:
		# delete all extra rows
		if len(extraIDs) > 0:
			# create a tuple string like (2,5,6)
			IDstringList = "("
			for ID in extraIDs:
				IDstringList = IDstringList + str(ID) + ","
			IDstringList = IDstringList[:-1] + ')'
			
			system.db.runPrepUpdate("DELETE FROM " + tableName + " WHERE " + primaryKey + " IN " + IDstringList, [], database)
	
	
	for row in jsonData:
	
		ID = row[primaryKey]
		results = system.db.runPrepQuery("SELECT * FROM " + tableName + " WHERE " + primaryKey + " = ?", [ID], database)
	
		# ----- update an existing row -------
		if results.getRowCount() > 0:
			setValuesString = ''
			parameters = []
			for i, header in enumerate(dataHeaders):
				if header != primaryKey:
					value = row[header]
					setValuesString = setValuesString + ' ' +  header + ' = ?,'
					parameters.append(value)
					
			setValuesString = setValuesString[:-1]
			parameters.append(ID)
			
			statement = "UPDATE " + tableName + " SET " + setValuesString + " WHERE " + primaryKey + " = ?"
			
#			print statement
#			print parameters
			
			results = system.db.runPrepUpdate(statement, parameters, database)

		
		# ----- insert new row  ------
		else:
		
			parameters = []
			columnsString = '('
			valuesString = '('
			for i, header in enumerate(dataHeaders):
				value = row[header]
				parameters.append(value)
				columnsString = columnsString + ' ' + header + ','
				valuesString = valuesString + ' ?,'
			columnsString = columnsString[:-1] + ')'
			valuesString = valuesString[:-1] + ')'
		
			# need statement1 to insert with a given primary key.
			statement1 = "SET IDENTITY_INSERT " + tableName + " ON; "
			statement2 = "INSERT INTO " + tableName +  " " + columnsString + " VALUES " + valuesString + "; "
			statement3 = "SET IDENTITY_INSERT " + tableName + " OFF; "
			
#			print statement2
#			print parameters
			
			results = system.db.runPrepUpdate(statement1 + statement2 + statement3 , parameters, database)
			
			
			
			
			
#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Nov 2022
#*****************************************************************************************************	
def exportDBtable(dbType, dbName, tableName, fileName='', download=True):
	
	params = { 'database':dbName, 'tableName':tableName }
	queryPath = "General/" +  dbType + "/getTable"
	tableData = system.db.runNamedQuery(queryPath, params)	

	csvData = system.dataset.toCSV(dataset = tableData, showHeaders = True, forExport = True)
	
	if download:
		system.perspective.download(fileName, csvData)
	else:
		return csvData