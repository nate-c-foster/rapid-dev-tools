


#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Feb 2023
#*****************************************************************************************************	
def bulkCreateTags(jsonData):
	"""Create udt instances in bulk.
	
	Creates multiple UDT instances and updates parameters.
	
	Args:
		jsonData (dict): A dictionary with keys {'ParentTagPath','Name','Type','Parameters'}
	"""

	for row in jsonData:
		parentPath = row['ParentTagPath']
		name = row['Name']
		udtType = row['Type']
		parameters = row['Parameters']
		
		createTag(parentPath, name, udtType, parameters)

					
					
def createTag(parentPath, name, udtType, parameters):
	"""Create udt instance.
	
	Creates UDT instance and updates parameters.
	
	Args:
		parentPath (str): Parent tag path.
		name (str): Name of new tag.
		udtType (str): UDT type ID.
		parameters (dict): Dict with keys as parameter names.
	"""
	
	# ----- Create UDT instance -----------------
	typeId = udtType
	tagConfig = {
			"name": name,         
			"typeId" : typeId,
			"tagType" : 'UdtInstance'
		}

	results = str(system.tag.configure(parentPath,tagConfig,collisionPolicy = 'm'))
	print results
	
	# ------ Update Parameters -----------------
	if parameters:
		for parameter in parameters.keys():
			parameterPath = parentPath + "/" + name + "/Parameters." + parameter
			if system.tag.exists(parameterPath) and parameters[parameter]:
				results = system.tag.writeBlocking(parameterPath, parameters[parameter])
				print results



#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Feb 2023
#*****************************************************************************************************	
def bulkMoveTags(jsonData):
	"""Move tags in bulk.
	
	Move multiple tags and update historian.
	
	Args:
		jsonData (dict): A dictionary with keys {'Source','Destination','UpdateHist'}
	"""

	for row in jsonData:
		source = row['Source']
		destination = row['Destination']
		updateHist = row['UpdateHist']
		
		moveTag(source, destination, moveHistorian=updateHist)
					
					
					
#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Nov 2022
# Description: Moves tag and updates historian.
# 
#
#Example - puts folder J00017 within Zone 0 folder
#source = '[SCADA]JBLM/Wastewater System/Lift Stations/LS_G1/J00017'
#destination = '[SCADA]JBLM/Wastewater System/Lift Stations/Zone 0'
#*****************************************************************************************************	
def moveTag(source, destination, moveHistorian=True):

	print 'moving tag ', source, ' to ', destination
	
	if system.tag.exists(source):		
		if moveHistorian:
			moveHist(source, destination)	

		system.tag.move([source], destination)
	else:
		raise Exception("Source path does not exist")
		
		
		
		
#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Nov 2022
# Description: Helper function for moveTag().
# 
#
#Example - puts folder J00017 within Zone 0 folder
#source = '[SCADA]JBLM/Wastewater System/Lift Stations/LS_G1/J00017'
#destination = '[SCADA]JBLM/Wastewater System/Lift Stations/Zone 0'
#*****************************************************************************************************
def moveHist(source, destination):

	# remove tag provider and make all lower case
	histSource = (source.split(']')[-1]).lower()
	histDestination = (destination.split(']')[-1]).lower()
	
	sourceParent = ('/').join(histSource.split('/')[:-1])
	oldPrefix = sourceParent
	
	query = 'TagEditor/' + settings.getValue('Tag Editor','historianDBType') + '/getChildrenTagPaths'
	tags = system.db.runNamedQuery(query, {'parentPath': histSource + '%', 'database':settings.getValue('Tag Editor','historianDBName')})
	
	
	for row in range(tags.getRowCount()):
		oldPath = tags.getValueAt(row,'tagpath')
		newPath = histDestination + oldPath[len(oldPrefix):]
		
		
		query = 'TagEditor/' + settings.getValue('Tag Editor','historianDBType') + '/replaceTagPath'
		numReplaced = system.db.runNamedQuery(query, {'oldPath': oldPath, 'newPath': newPath, 'database':settings.getValue('Tag Editor','historianDBName')})
		if numReplaced > 0:
			print "Old Hist Path: ", oldPath
			print "New Hist Path: ", newPath
			print "Number of Hist Path Replaced: ", numReplaced		
			
			
			
			
			
			
			
			
#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Feb 2023
#*****************************************************************************************************	
def bulkRenameTags(jsonData):
	"""Rename tags in bulk.
	
	Rename multiple tags and update historian.
	
	Args:
		jsonData (dict): A dictionary with keys {'Path','NewName','UpdateHist'}
	"""

	for row in jsonData:
		path = row['Path']
		newName = row['NewName']
		updateHist = row['UpdateHist']
		
		renameTag(path, newName, renameHistorian=updateHist)
			
			
			
			
			
#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Nov 2022
# Description: Renames folder or tag, and updates historian.
# 
#
#Example - renames J00017 to foo
#path = '[SCADA]JBLM/Wastewater System/Lift Stations/LS_G1/J00017'
#newName = 'foo'
#*****************************************************************************************************
def renameTag(path, newName, renameHistorian=True):
	if system.tag.exists(path):
		
		# if folder contains UDT with same name
		udtPath = path + '/' +  path.split('/')[-1]
		if system.tag.exists(udtPath):
			system.tag.rename(udtPath, newName)
			if renameHistorian:
				renameHist(udtPath, newName)
		
		system.tag.rename(path, newName)
		if renameHistorian:
			renameHist(path, newName)
	
	else:
		raise Exception("Source path: " + str(path) + " does not exist")




#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Nov 2022
# Description: Helper function for renameTag()
# 
#
#Example - renames J00017 to foo
#path = '[SCADA]JBLM/Wastewater System/Lift Stations/LS_G1/J00017'
#newName = 'foo'
#*****************************************************************************************************
def renameHist(path, newName):
	# remove tag provider and make all lower case
	histOldParent = (path.split(']')[-1]).lower()
	histNewParent = '/'.join(histOldParent.split('/')[:-1]) + '/' +  newName.lower()
	
	query = 'TagEditor/' + settings.getValue('Tag Editor','historianDBType') + '/getChildrenTagPaths'
	tags = system.db.runNamedQuery(query, {'parentPath': histOldParent + '%', 'database': settings.getValue('Tag Editor','historianDBName')})
	
	for row in range(tags.getRowCount()):
	
		oldPath = tags.getValueAt(row,'tagpath')
		newPath = histNewParent + oldPath[len(histOldParent):]
		
		query = 'TagEditor/' + settings.getValue('Tag Editor','historianDBType') + '/replaceTagPath'
		numReplaced = system.db.runNamedQuery(query, {'oldPath': oldPath, 'newPath': newPath, 'database': settings.getValue('Tag Editor','historianDBName')})
		if numReplaced > 0:
			print "Old Hist Path: ", oldPath
			print "New Hist Path: ", newPath
			print "Number of Hist Path Replaced: ", numReplaced		
			