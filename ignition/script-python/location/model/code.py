"""Functions for working with the location model

"""

import os


#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Feb 2023
#*****************************************************************************************************	
def updateModelTag():
	"""Updates model tag.
	
	Queries location tables to update model tag.
	"""
	
	dbType = settings.getValue('Location Model', 'modelDBType')
	dbName = settings.getValue('Location Model', 'modelDBName')
	queryPath = "Location Model/" + dbType + "/getModel"
	print 'queryPath: ', queryPath
	print 'params: ', {'database':dbName}
	model = system.db.runNamedQuery(queryPath, {'database':dbName})

	headers = [	
				"locationName",
				"locationID",
				"orderNumber",
				"shortName",
				"description",			
				"icon",		
				"parentID",
				"childrenCount",
				"childrenIDs",
				"locationIDPath",
				"locationPath",				
				"tagPath",
				"viewPath",
				"treePath",
				"locationType",
				"locationTypeID",
				"locationTypeDefinition",
				"locationTypeDefinitionID",
				"udtPath",
				"viewTemplatePath",
				"scadaView",
				"lastModifiedBy",
				"lastModifiedOn"
				]
				
	data = []
	for row in range(model.getRowCount()):
		
		locationID = model.getValueAt(row,"LocationID")
		locationIDPath = getLocationIDPath(locationID)
		locationPath = getLocationPath(locationID)
		tagPath = settings.getValue('Location Model', 'tagPathPrefix') + locationPath
		viewPath = settings.getValue('Location Model', 'viewPathPrefix') + locationPath
			
			
		# ------ Find all children and sort  ----------------------------------
		queryPath = "Location Model/" + dbType + "/getChildren"
		children = system.db.runNamedQuery(queryPath, {'LocationID': locationID, 'database':dbName})
		childrenCount = children.getRowCount()
		childrenIDs = []
		childrenIDsSorted = ""	
		if childrenCount > 0:
			childOrder = {}
			childName = {}
			for r in range(children.getRowCount()):
				childID = str(children.getValueAt(r,"LocationID"))
				childrenIDs.append(childID)
				childOrder[childID] = children.getValueAt(r,"orderNumber")
				childName[childID] = children.getValueAt(r,"Name")	
				
			childrenIDs.sort(key = lambda ID : childOrder[ID] if childOrder[ID] else childName[ID])
			childrenIDsSorted = ','.join(childrenIDs)
				
				
		rowData = [ 	
						model.getValueAt(row,"Name"),
						locationID,
						model.getValueAt(row,"orderNumber"),
						model.getValueAt(row,"shortName"),
						model.getValueAt(row,"description"),
						model.getValueAt(row,"icon"),
						model.getValueAt(row,"ParentLocationID"),	
						childrenCount,
						childrenIDsSorted,	
						locationIDPath,					
						locationPath,
						tagPath,
						viewPath,
						"",
						model.getValueAt(row,"locationType"),
						model.getValueAt(row,"LocationTypeID"),
						model.getValueAt(row,"locationTypeDefinition"),
						model.getValueAt(row,"LocationTypeDefinitionID"),						
						model.getValueAt(row,"UDTPath"),
						model.getValueAt(row,"IgnitionTemplatePath"),	
						model.getValueAt(row, "ScadaView"),									
						model.getValueAt(row,"LastModifiedBy"),
						model.getValueAt(row,"LastModifiedOn")
					]
					
		data.append(rowData)


	modelDS = system.dataset.toDataSet(headers, data)
	
	
	# ---------  add tree paths to each location  -----------------------
	for row in range(modelDS.getRowCount()):
		locationID = modelDS.getValueAt(row, "LocationID")
		treePath = getTreePath(locationID, modelDS)
		modelDS = system.dataset.setValue(modelDS, row, "treePath", treePath)
	
	
	system.tag.writeBlocking(settings.getValue('Location Model', 'modelTagPath'), modelDS)






#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Feb 2023
#*****************************************************************************************************	
def updateModelTree(modelDS, expanded=True, filterFunction=lambda x : True, transformFunction=lambda x : x):
	"""Update the location model tree.
	
	Args:
		modelDS (Dataset): The location model dataset.
		expanded (bool): All tree items are expanded if True.
		filterFunction (function): A function that takes locationDetails and returns a bool.
		transformFunction function): A function that takes a tree node and returns an updated tree node.
	
	Returns:
		A dict where key 'items' is a list of tree items.
	"""
	
	def buildTree(locationID, modelDS, expanded, filterFunction, transformFunction):
	
		try:
			locationDetails = getLocationDetails(locationID, modelDS)
		except:
			return []

		locationName = locationDetails['locationName']
		shortName = locationDetails['shortName']
		if shortName:
			name = shortName
		else:
			name = locationName
		
		
		items = []
		keepMe = False # Keep this subtree if true. Used for filtering.
		
		# recursively build all child subtrees
		if locationDetails['childrenCount'] > 0:
			childrenIDs = map(int, locationDetails['childrenIDs'].split(','))
			for childID in childrenIDs:
				subTree = buildTree(childID, modelDS, expanded, filterFunction, transformFunction)
				if subTree['keepMe']:
					keepMe = True
					items = items + subTree['items']
	
		# base case
		if filterFunction(locationDetails) or keepMe:
			return {"keepMe": True, "items":[transformFunction({"label":name, "data":locationDetails, "expanded":expanded, "items":items})]}
		else:
			return {"keepMe": False, "items":[transformFunction({"label":name, "data":locationDetails, "expanded":expanded, "items":items})]}


	# this was rewritten to allow for multiple roots
	rootIDs = []
	for row in range(modelDS.getRowCount()):
		parentID = modelDS.getValueAt(row, "parentID")
		if parentID == None:
			rootIDs.append(modelDS.getValueAt(row,"locationID"))
			
	trees = []
	for locationID in rootIDs:
		trees = trees + buildTree(locationID, modelDS, expanded, filterFunction, transformFunction)['items']

	trees.sort(key=lambda x : x['data']['orderNumber'])
	return trees










#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Feb 2023
#*****************************************************************************************************	
def getLocationDetails(locationID, modelDS):
	"""
	Get the location details for the given locationID.
	
	Args: 
		locationID (int): The location ID.
		modelDS (Dataset): The location model dataset.
	
	Returns:
		A dictionary containing the location details.
		
	"""
	
	locationDetails = {}
	
	for row in range(modelDS.getRowCount()):
	
			if modelDS.getValueAt(row,"locationID") == locationID:	
				columnNames = modelDS.getColumnNames()
				locationDetails = { columnName : modelDS.getValueAt(row,columnName) for columnName in columnNames }	
	
	return locationDetails



#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           March 2023
#*****************************************************************************************************	
def getTreePath(locationID, modelDS):
	"""Get the Perspective tree path for a location.
	
	Args:
		locationID (int): The location ID.
		modelDS (Dataset): The location model dataset.
	
	Returns:
		An index path used for Perspective trees. For example '0/0/1/2'
	"""

	parentID = getLocationDetails(locationID, modelDS)['parentID']
	if parentID:
		if getLocationDetails(parentID, modelDS):
			siblingIDs = getLocationDetails(parentID, modelDS)['childrenIDs'].split(',')
			
			index = 0
			if siblingIDs:
				for i, siblingID in enumerate(siblingIDs):
					if int(siblingID) == int(locationID):
						index = i
						
			return getTreePath(parentID, modelDS) + '/' + str(index)
		else:
			return ""
	
	else:
		return "0"




#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Feb 2023
#*****************************************************************************************************	
def getChildrenComponents(rootTagPath, checkAlarms = True):
	"""Get all children compents.
	
	Args:
		rootTagPath (str): The parent tag path.
	
	Returns:
		A list of children components where each element is a dictionary with keys {'name','type'}.
	"""

	components = []
	

	results = system.tag.browse(rootTagPath, {"recursive":False, "tagType":"UdtInstance"})
	for result in results:
		if "Component" in str(result['typeId']) or "User Defined" in str(result['typeId']):
			typeId = str(result['typeId'])
			if '_types_/' in typeId:
				typeId = typeId.split('_types_/')[-1]
			components.append({'name':result['name'], 'type':typeId})
			
	components.sort(key = lambda c : c['type'])		
			
			
	# Also look in folders with these names for udt instances:
	if checkAlarms:
		folderFilter = ['Alarming', 'Alarms']	
		folders = system.tag.browse(rootTagPath, {"recursive":False, "tagType":"Folder"})	
		for folder in folders:
			folderPath = folder['fullPath']
			folderName = folder['name']
			if folderName in folderFilter:
				results = system.tag.browse(folderPath, {"recursive":False, "tagType":"UdtInstance"})
				for result in results:
					if "Component" in str(result['typeId'])  or "User Defined" in str(result['typeId']):
						typeId = str(result['typeId'])
						if '_types_/' in typeId:
							typeId = typeId.split('_types_/')[-1]
						components.append({'name':result['name'], 'type':typeId})
					
				
	return components





#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Feb 2023
#*****************************************************************************************************	
def getLocationIDPath(locationID):
	"""Get locationID path to the given location ID.
	
	Returns a path of location IDs seperated with $.
	
	Args:
		locationID (int): The location ID.
	
	Returns:
		A string representing the locationID path.
	"""
	dbType = settings.getValue('Location Model', 'modelDBType')
	dbName = settings.getValue('Location Model', 'modelDBName')
	
	try:	
		parentID = system.db.runPrepQuery("SELECT ParentLocationID FROM core.Location WHERE LocationID = ?", [locationID], dbName).getValueAt(0,0)
	except:
		return str(locationID)
		
	if parentID:	
		return getLocationIDPath(parentID) + '$' + str(locationID)
	else:
		return str(locationID)




#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Feb 2023
#*****************************************************************************************************	
def getLocationPath(locationID):
	"""Gets the location path
	
	Args:
		locationPath (str): Path of location IDs seperated with $.
		rootTagPath (str): The prefix path for all tag paths.
	
	Returns:
		The location path.
	"""
	
	locationIDPath = getLocationIDPath(locationID)
	locationIDs = map(int, locationIDPath.split('$'))
	
	locationPath = ''
	
	# convert locationID path to location path
	for locationID in locationIDs:
		try:	
			name = system.db.runPrepQuery("SELECT Name FROM core.Location WHERE LocationID = ?", [locationID], settings.getValue('Location Model', 'modelDBName')).getValueAt(0,0)
		except:
			return ''
			
		locationPath = locationPath + name + '/'
		
	return locationPath[:-1]





#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Sept 2022
# Description: Given a location path, returns the location ID. Returns -1 if not found.
# 
# Input arguments:
#	locationPath		(string)      
#							
#  
#*****************************************************************************************************	
def getLocationID(locationPath):

	dbType = settings.getValue('Location Model', 'modelDBType')
	dbName = settings.getValue('Location Model', 'modelDBName')
	
	locationNames = locationPath.split('/')
	length = len(locationNames)	
	locationID = -1
	
	if length < 1:
		return -1
	
	elif length == 1:

		query = 'Location Model/' + dbType + '/getRootLocations'
		roots = system.dataset.toPyDataSet(system.db.runNamedQuery(query,{"database": dbName}))
		for root in roots:
			if locationNames[0] == root["Name"]:
				locationID = root["LocationID"]

	else: 
	
		# update locationID as you move down the path
		for n in range(length-1):
		
			query = 'Location Model/' + dbType + '/getChildrenFromName'
			children = system.dataset.toPyDataSet(system.db.runNamedQuery(query,{"Name": locationNames[n], 'database':dbName}))
			locationID = -1
			for child in children:
				if locationNames[n+1] == child["Name"]:
					locationID = child["LocationID"]

				
	return locationID
	

def isProcess(locationDetails):
	locationTypeID = locationDetails['locationTypeID']

	if locationTypeID == 6:
		return True
	else:
		return False


def isComponent(locationDetails):
	locationTypeID = locationDetails['locationTypeID']

	if locationTypeID == 7:
		return True
	else:
		return False
	




