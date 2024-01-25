
import os



#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Sept 2022
#*****************************************************************************************************	
def createLocation(locationName, locationTypeID, parentLocationID, locationTypeDefinitionID, shortName='', modifiedBy = 'Uknown'):


	if parentLocationID < 0:
		parentLocationID = None

	queryPath = "Location Model/" + settings.getValue('Location Model', 'modelDBType') + "/getMaxOrderNumber"
	maxOrderNumber = system.db.runNamedQuery(queryPath, {'parentLocationID': parentLocationID})
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
		'ShortName':shortName
	}
	
	modelDBType = settings.getValue('Location Model', 'modelDBType')
	query = 'Location Model/' + modelDBType + '/addLocation'
	system.db.runNamedQuery(query,params)	
	
	location.model.updateModelTag()


	# ----- create tag -----
	modelTagPath = settings.getValue('Location Model', 'modelTagPath')
	modelDS = system.tag.readBlocking(modelTagPath)[0].value
	for row in range(modelDS.getRowCount()):
		if modelDS.getValueAt(row,"parentID") == parentLocationID and modelDS.getValueAt(row,"locationName") == locationName:	
			columnNames = modelDS.getColumnNames()
			locationDetails = { columnName : modelDS.getValueAt(row,columnName) for columnName in columnNames }	
		
	createLocationTag(locationDetails)

	# ----- create view import -----
	return getNewViewsForLocation(locationDetails)
	





#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Feb 2023
#*****************************************************************************************************	
def createLocationTag(locationDetails):


	udtPath = locationDetails['udtPath']
	tagPath = locationDetails['tagPath']
	parentPath = '/'.join(tagPath.split('/')[:-1])
	name = locationDetails['locationName']


	# ---- create location folder -------
	folder={
			'tagType': 	'Folder',
			'name':		name,
			'tags':		[]
		}
	folderResults = system.tag.configure(basePath=parentPath, tags=folder, collisionPolicy = 'm')
	
	# --- create location UDT instance -------
	tag={
			"name": name,         
			"typeId" : udtPath,
			"tagType" : 'UdtInstance',
		}
	tagResults = system.tag.configure(basePath=tagPath, tags=tag, collisionPolicy = 'm')



#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
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
	
	ignitionViewRootPath = vieweditor.util.getIgnitionViewRootPath()
		
	viewPath = locationDetails['viewPath']
	templatePath = locationDetails['viewTemplatePath']
			
		
	ignitionViewDirPath = ignitionViewRootPath + '/' + viewPath
	ignitionTemplateDirPath = ignitionViewRootPath + '/' + templatePath
			

	for partialViewPath in vieweditor.util.getSubViewDirPaths(ignitionTemplateDirPath):
			
		ignitionViewPath = ignitionViewDirPath + partialViewPath
		ignitionTemplatePath = ignitionTemplateDirPath + partialViewPath
		viewExists = os.path.exists(ignitionViewPath)
				
		if not viewExists:

			# read template JSON
			try:
				viewJSONStr = system.file.readFileAsString(ignitionTemplatePath + '/view.json')
			except:
				raise Exception("Couldn't read path: " + ignitionTemplatePath + '/view.json')
				

			try:
				resourceJSONStr = system.file.readFileAsString(ignitionTemplatePath + '/resource.json')
			except:
				raise Exception("Couldn't read path: " + ignitionTemplatePath + '/resource.json')
						
			
			
					
			newView = {		"viewPath": ignitionViewPath.split("com.inductiveautomation.perspective/views/")[-1],
							"viewJSON": viewJSONStr,
							"resourceJSON": resourceJSONStr
						}
								
	
								
			# ------------------   Update view params with location details --------------
			rootTagPath = locationDetails['tagPath']
			locationID = locationDetails['locationID']
			params = {"LocationID": locationID, "rootTagPath": rootTagPath}	
			newView = vieweditor.transform.updateViewParams(params)(newView)			
			newViews.append(newView)
			
	return newViews



#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Dec 2022
#*****************************************************************************************************	
def bulkCreateLocations(jsonData):

	viewImports = []
	
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


		modelDBType = settings.getValue("Location Model", "modelDBType")


		# get locationTypeID
		results = system.db.runNamedQuery("Location Model/" + modelDBType + "/getLocationTypes")
		locationTypeID = -1
		for row in range(results.getRowCount()):
			if locationType == results.getValueAt(row,"Name"):
				locationTypeID = results.getValueAt(row, "LocationTypeID")
		if locationTypeID < 0:
			raise Exception( "Error: Location Type (" + locationType + ") is defined multiple times in LocationType" )

		# get locationTypeDefinitionID
		results = system.db.runNamedQuery("Location Model/" + modelDBType + "/getLocationTypeDefinitions",{"LocationTypeID": locationTypeID})
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
# Company:        A.W. Schultz
# Date:           Jan 2023
# Description: Edit multiple locations.
# 
#
# tableDS - Headers(Path, shortName, Description, Latitude, Longitude)
#
#*****************************************************************************************************	
def bulkEditLocations(jsonData):

	jsonData

	for row in jsonData:
		path = row["Path"]
		LocationID = location.model.getLocationID(path)
		if LocationID > 0:
			system.db.runPrepUpdate("UPDATE core.Location SET shortName = ?, Description = ?, Latitude = ?, Longitude = ?   WHERE LocationID = ?", [row["shortName"],row["Description"],row["Latitude"],row["Longitude"],LocationID])







#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
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
# Company:        A.W. Schultz
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

	locationID = location.model.getLocationID(source)
	
	if locationID > 0:
		parentID = location.model.getLocationID(destination)

		if parentID > 0:
		
			query = 'Location Model/' + settings.getValue('Location Model', 'modelDBType')  + '/changeParentID'
			system.db.runNamedQuery(query, {'newParentLocationID':parentID, 'LocationID': locationID})
			
			location.model.updateModelTag()
			return 1
			
		else:
			raise Exception("Destination path location ID does not exists")

	else:
		raise Exception("Error: Source path location ID does not exists")




#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Nov 2022
# Description: Move multiple locations.
# 
#
# tableDS - Headers(Path, New Name, Update Model, Update Tags, Update Hist, Update Views)
#
#*****************************************************************************************************	
def bulkRenameLocations(jsonData):

	viewImports = []
	
	for row in jsonData:
		path = row['Path']
		newName = row['NewName']
		renameTags = row['UpdateTags']
		renameHist = row['UpdateHist']
		renameViews = row['UpdateViews']
		
		

		locationID = location.model.getLocationID(path)
		if locationID > 0:
			system.db.runPrepUpdate("UPDATE core.Location SET Name = ? WHERE LocationID = ?", [newName, locationID], "SCADA")
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





