




def lookup(dbType, dbName, tableName, lookupValue, lookupType, noMatchValue, lookupColumn, resultColumns):


	if lookupType == int:
		query = "General/" + dbType + "/lookupInt"
		params = { 	"database": dbName,
					"tableName": tableName,
					"lookupValue": lookupValue,
					"lookupColumn": lookupColumn }
					
		results = system.db.runNamedQuery(query, parameters=params)
		
		if results and results.getRowCount() > 0:
			resultValues = {column:results.getValueAt(0,column) for column in resultColumns}
			return resultValues
		
		else:
			return noMatchValue
		
		
	else:
		return noMatchValue