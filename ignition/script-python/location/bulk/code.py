
import os



#*****************************************************************************************************
# Author:         Nate Foster
# Date:           Sept 2022
#*****************************************************************************************************	
def createLocation(locationName, locationTypeID, parentLocationID, locationTypeDefinitionID, shortName='', modifiedBy = 'Uknown'):


	dbType = settings.getValue('Location Model', 'modelDBType')
	dbName = settings.getValue('Location Model', 'modelDBName')

	if parentLocationID < 0:
		parentLocationID = None

	queryPath = "Location Model/" + dbType + "/getMaxOrderNumber"
	maxOrderNumber = system.db.runNamedQuery(queryPath, {'parentLocationID': parentLocationID, 'database':dbName})
	if maxOrderNumber is None:
		orderNumber = 1
	else:
		orderNumber = int(maxOrderNumber) + 1
	
	# ------- update model --------------
	params = {
		'ParentLocationID': parentLocationID,
		'LocationTypeID': locationTypeID,
		'Name': locationName,
		'Description': "",
		'LastModifiedBy': modifiedBy,
		'LocationTypeDefinitionID': locationTypeDefinitionID,
		'orderNumber': orderNumber,
		'ShortName':shortName,
		'database':dbName
	}
	
	if parentLocationID:
		query = 'Location Model/' + dbType + '/addLocation'
		system.db.runNamedQuery(query,params)	
	else:
		del params['ParentLocationID']
		query = 'Location Model/' + dbType + '/addLocationToRoot'
		system.db.runNamedQuery(query,params)	
	
	location.model.updateModelTag()


	# ----- create tag -----
	modelTagPath = settings.getValue('Location Model', 'modelTagPath')
	modelDS = system.tag.readBlocking(modelTagPath)[0].value
	for row in range(modelDS.getRowCount()):
		if (not modelDS.getValueAt(row,"parentID") or modelDS.getValueAt(row,"parentID") == parentLocationID) and modelDS.getValueAt(row,"locationName") == locationName:	
			columnNames = modelDS.getColumnNames()
			locationDetails = { columnName : modelDS.getValueAt(row,columnName) for columnName in columnNames }	
		
	createLocationTag(locationDetails)

	# ----- create view import -----
	return getNewViewsForLocation(locationDetails)
	





#*****************************************************************************************************
# Author:         Nate Foster
# Date:           Feb 2023
#*****************************************************************************************************	
def createLocationTag(locationDetails):


	udtPath = locationDetails['udtPath']
	tagPath = locationDetails['tagPath']
	name = locationDetails['locationName']
	
	if '/' in tagPath:
		parentPath = '/'.join(tagPath.split('/')[:-1])
		
	# must be a root tag, hence [tagProvider] is the parent path
	else:
		parentPath = tageditor.util.getProvider(tagPath)


	if not system.tag.exists(tagPath):
		# ---- create location folder -------
		folder={
				'tagType': 	'Folder',
				'name':		name,
				'tags':		[]
			}
		folderResults = system.tag.configure(basePath=parentPath, tags=folder, collisionPolicy = 'm')
	
	
	if not system.tag.exists(tagPath + '/' + name):
		# --- create location UDT instance -------
		tag={
				"name": name,         
				"typeId" : udtPath,
				"tagType" : 'UdtInstance',
			}
		tagResults = system.tag.configure(basePath=tagPath, tags=tag, collisionPolicy = 'm')
		
		
	if location.model.isProcess(locationDetails) and not system.tag.exists(tagPath + '/Alarming'):
		# ---- create Alarming folder -------
		folder={
				'tagType': 	'Folder',
				'name':		'Alarming',
				'tags':		[]
			}
		folderResults = system.tag.configure(basePath=tagPath, tags=folder, collisionPolicy = 'm')

	if location.model.isProcess(locationDetails) and not system.tag.exists(tagPath + '/Control'):
		# ---- create Alarming folder -------
		folder={
				'tagType': 	'Folder',
				'name':		'Control',
				'tags':		[]
			}
		folderResults = system.tag.configure(basePath=tagPath, tags=folder, collisionPolicy = 'm')


#*****************************************************************************************************
# Author:         Nate Foster
# Date:           Jan 2024
#*****************************************************************************************************	
def createLocationTagsFromModel():

	modelDS = system.tag.readBlocking(settings.getValue("Location Model", "modelTagPath"))[0].value

	for row in range(modelDS.getRowCount()):
		locationID = modelDS.getValueAt(row,"locationID")
		locationDetails = location.model.getLocationDetails(locationID, modelDS)
		locationTypeID = locationDetails['locationTypeID']

		if not location.model.isComponent(locationDetails):
			createLocationTag(locationDetails)







#*****************************************************************************************************
# Author:         Nate Foster
# Date:           Sept 2022
#*****************************************************************************************************		
def getNewViewsForLocation(locationDetails):
	"""Gets all new views for a location.
	
	Args:
		locationDetails (dict): The location details.
		
	Returns:
		Returns a list of views that currently do not exist for a location
	"""

	newViews = []
	
	viewPath = locationDetails['viewPath']
	templatePath = locationDetails['viewTemplatePath']
	locationID = locationDetails['locationID']
	rootTagPath = locationDetails['tagPath']
	parameters = {"LocationID": locationID, "rootTagPath": rootTagPath}
	
	return vieweditor.bulk.createView(viewPath , templatePath, parameters)



#*****************************************************************************************************
# Author:         Nate Foster
# Date:           Sept 2022
#*****************************************************************************************************	
def getNewViewsFromModel():
	"""Gets all new views for the model.
	
	Returns:
		Returns a list of views that currently do not exist for the model
	"""
	newViews = []
	modelDS = system.tag.readBlocking(settings.getValue("Location Model", "modelTagPath"))[0].value

	for row in range(modelDS.getRowCount()):
		locationID = modelDS.getValueAt(row,"locationID")
		locationDetails = location.model.getLocationDetails(locationID, modelDS)
		locationTypeID = locationDetails['locationTypeID']

		if not location.model.isComponent(locationDetails):
			newViews = newViews + getNewViewsForLocation(locationDetails)

	return newViews




#*****************************************************************************************************
# Author:         Nate Foster
# Date:           Dec 2022
#*****************************************************************************************************	
def bulkCreateLocations(jsonData):

	viewImports = []
	
	dbType = settings.getValue('Location Model', 'modelDBType')
	dbName = settings.getValue('Location Model', 'modelDBName')
	
	for row in jsonData:
		parentPath = row['ParentLocationPath']
		name = row['Name']
		shortName = row['ShortName']
		locationType = row['Type']
		definition = row['Definition']
		createTags = row['CreateTags']
		createViews = row['CreateViews']


		# Does parent location exist
		parentLocationID = location.model.getLocationID(parentPath)
		if parentLocationID < 0:
			raise Exception ("Error: Parent Location Path (" + parentPath + ") Does Not Exist")


		# get locationTypeID
		results = system.db.runNamedQuery("Location Model/" + dbType + "/getLocationTypes", {'database':dbName})
		locationTypeID = -1
		for row in range(results.getRowCount()):
			if locationType == results.getValueAt(row,"Name"):
				locationTypeID = results.getValueAt(row, "LocationTypeID")
		if locationTypeID < 0:
			raise Exception( "Error: Location Type (" + locationType + ") is defined multiple times in LocationType" )

		# get locationTypeDefinitionID
		results = system.db.runNamedQuery("Location Model/" + dbType + "/getLocationTypeDefinitions",{"LocationTypeID": locationTypeID, 'database':dbName})
		locationTypeDefinitionID = -1
		for row in range(results.getRowCount()):
			if definition == results.getValueAt(row,"Name"):
				locationTypeDefinitionID = results.getValueAt(row, "LocationTypeDefinitionID")
		if locationTypeDefinitionID < 0:
			raise Exception( "Error: Location Type (" + definition + ") is defined multiple times in LocationType" )
	


		viewImports = viewImports + createLocation(name,
													locationTypeID, 
													parentLocationID,
													locationTypeDefinitionID, 
													shortName= shortName, 
													modifiedBy = 'Bulk Config')
			
	if viewImports:
		vieweditor.util.generateViewImport(viewImports)

		


#*****************************************************************************************************
#
# Author:         Nate Foster
# Date:           Jan 2023
# Description: Edit multiple locations.
# 
#
# tableDS - Headers(Path, shortName, Description, Latitude, Longitude)
#
#*****************************************************************************************************	
def bulkEditLocations(jsonData):

	jsonData
	dbType = settings.getValue('Location Model', 'modelDBType')
	dbName = settings.getValue('Location Model', 'modelDBName')

	for row in jsonData:
		path = row["Path"]
		LocationID = location.model.getLocationID(path)
		if LocationID > 0:
			system.db.runPrepUpdate("UPDATE core.Location SET shortName = ?, Description = ?, Latitude = ?, Longitude = ?   WHERE LocationID = ?", [row["shortName"],row["Description"],row["Latitude"],row["Longitude"],LocationID], dbName)







#*****************************************************************************************************
#
# Author:         Nate Foster
# Date:           Nov 2022
# Description: Move multiple locations.
# 
#
# tableDS - Headers(Source, Destination, Update Model, Update Tags, Update Hist, Update Views)
#
#*****************************************************************************************************	
def bulkMoveLocations(jsonData):

	viewImports = []
	
	for row in jsonData:
		source = row['Source']
		destination = row['Destination']
		moveTags = row['UpdateTags']
		moveHist = row['UpdateHist']
		moveViews = row['UpdateViews']

		
		moveLocation(source, destination)
		
		if moveTags:
			tagPrefix = settings.getValue('Location Model', 'tagPathPrefix')
			tageditor.bulk.moveTag(tagPrefix + source, tagPrefix + destination, moveHist)
			
		if moveViews:
			viewPrefix = settings.getValue('Location Model', 'viewPathPrefix')
			newViews = vieweditor.bulk.moveView(viewPrefix + source, viewPrefix + destination)
			viewImports = viewImports + newViews
	

	print 'generating view import'
	if viewImports:
		vieweditor.util.generateViewImport(viewImports)




#*****************************************************************************************************
#
# Author:         Nate Foster
# Date:           Nov 2022
# Description: Move location.
# 
#
#Example 1 - puts location J00017 within Zone 0
#source = 'JBLM/Wastewater System/Lift Stations/LS_G1/J00017'
#destination = 'JBLM/Wastewater System/Lift Stations/Zone 0'
#
#*****************************************************************************************************	
def moveLocation(source, destination):

	print 'moving location ', source, ' to ', destination

	dbType = settings.getValue('Location Model', 'modelDBType')
	dbName = settings.getValue('Location Model', 'modelDBName')
	
	locationID = location.model.getLocationID(source)
	
	if locationID > 0: 
		
		
		# Destination is not a root location
		if destination:

			parentID = location.model.getLocationID(destination)
	
			if parentID > 0:
			
				query = 'Location Model/' + dbType  + '/getMaxOrderNumber'
				maxOrder = system.db.runNamedQuery(query, {'parentLocationID':parentID, 'database':dbName})
				if maxOrder:
					newOrder = maxOrder + 1
				else:
					newOrder = 1
				
				query = 'Location Model/' + dbType  + '/updateOrderNumber'
				results = system.db.runNamedQuery(query, {'locationID':locationID, 'orderNumber':newOrder, 'database':dbName})
								
				query = 'Location Model/' + dbType  + '/changeParentID'
				system.db.runNamedQuery(query, {'newParentLocationID':parentID, 'LocationID': locationID, 'database':dbName})
			
				location.model.updateModelTag()

				
			else:
				raise Exception("Destination path location ID does not exists")
					
		# Destination is a root location
		else:
		
			query = 'Location Model/' + dbType  + '/getMaxOrderNumberRoots'
			maxOrder = system.db.runNamedQuery(query, {'database':dbName})
			if maxOrder:
				newOrder = maxOrder + 1
			else:
				newOrder = 1
			
			query = 'Location Model/' + dbType  + '/updateOrderNumber'
			results = system.db.runNamedQuery(query, {'locationID':locationID, 'orderNumber':newOrder, 'database':dbName})
		
			query = 'Location Model/' + dbType  + '/changeParentIDtoNULL'
			system.db.runNamedQuery(query, {'LocationID': locationID})

	else:
		raise Exception("Error: Source path location ID does not exists")




#*****************************************************************************************************
#
# Author:         Nate Foster
# Date:           Nov 2022
# Description: Move multiple locations.
# 
#
# tableDS - Headers(Path, New Name, Update Model, Update Tags, Update Hist, Update Views)
#
#*****************************************************************************************************	
def bulkRenameLocations(jsonData):

	viewImports = []
	
	dbType = settings.getValue('Location Model', 'modelDBType')
	dbName = settings.getValue('Location Model', 'modelDBName')
	
	for row in jsonData:
		path = row['Path']
		newName = row['NewName']
		renameTags = row['UpdateTags']
		renameHist = row['UpdateHist']
		renameViews = row['UpdateViews']

		locationID = location.model.getLocationID(path)
		if locationID > 0:
			system.db.runPrepUpdate("UPDATE core.Location SET Name = ? WHERE LocationID = ?", [newName, locationID], dbName)
		else:
			raise Exception("Couldn't find location: " + path)

		if renameTags:
			tagPrefix = settings.getValue('Location Model', 'tagPathPrefix')
			tageditor.bulk.renameTag(tagPrefix + path, newName, renameHist)

		if renameViews:
			viewPrefix = settings.getValue('Location Model', 'viewPathPrefix')
			newViews = vieweditor.bulk.renameView(viewPrefix + path, newName)
			viewImports = viewImports + newViews

	if viewImports:
		vieweditor.util.generateViewImport(viewImports)





