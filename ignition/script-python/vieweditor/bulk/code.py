


import os
import shutil
import re

def getIgnitionViewRootPath():
	installationPathIA = settings.getValue('Global','installationPathIA')
	return installationPathIA + '/Ignition/data/projects/SCADA/com.inductiveautomation.perspective/views'
	
	
#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Feb 2023
#*****************************************************************************************************	
def bulkCreateViews(jsonData):
	"""Create views in bulk.
	
	Creates multiple views and downloads a view import.
	
	Args:
		jsonData (dict): A dictionary with keys {'ViewPath','TemplatePath', 'Parameters'}
	"""


	viewImports = []
	for row in jsonData:
		viewPath = row['ViewPath']
		templatePath = row['TemplatePath']
		parameters = row['Parameters']
		
		viewImports = viewImports + createView(viewPath, templatePath, parameters)
			
	if viewImports:
		vieweditor.util.generateViewImport(viewImports)




#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Sept 2022
#*****************************************************************************************************		
def createView(viewPath , templatePath, parameters):
	"""Create view using a template view.
	
	Creates multiple views and downloads a view import.
	
	Args:
		jsonData (dict): A dictionary with keys {'ViewPath','TemplatePath', Parameters}
	"""

	newViews = []
	
	ignitionViewRootPath = getIgnitionViewRootPath()
		

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
								
	
			
			# ------ Update Parameters -----------------
			if parameters:
				newView = vieweditor.transform.updateViewParams(parameters)(newView)
					
			newViews.append(newView)
			
	return newViews





#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Feb 2023
#*****************************************************************************************************	
def bulkMoveViews(jsonData):
	"""Move views in bulk.
	
	Moves multiple views and downloads a view import.
	
	Args:
		jsonData (dict): A dictionary with keys {'Source','Destination'}
	"""
	
	viewImports = []
	for row in jsonData:
		source = row['Source']
		destination = row['Destination']
		
		viewImports = viewImports + moveView(source,destination)
			
	if viewImports:
		vieweditor.util.generateViewImport(viewImports)
		
		
		
		


#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Nov 2022
# Description: Moves view folder.
# 
#
#Example - puts folder J00017 within Zone 0 folder
#source = 'SCADA/JBLM/Wastewater System/Lift Stations/LS_G1/J00017'
#destination = 'SCADA/JBLM/Wastewater System/Lift Stations/Zone 0'
#*****************************************************************************************************	
def moveView(source, destination):

	print 'moving view ', source, ' to ', destination

	sourceViews = vieweditor.util.getViews(source)
	views = []
	
	
	for view in sourceViews:

		ignitionSourcePath = getIgnitionViewRootPath() + '/' + view["viewPath"]
		
		# read template JSON
		try:
			viewJSONStr = system.file.readFileAsString(ignitionSourcePath + '/view.json')
		except:
			raiseException("Couldn't read path: " + ignitionSourcePath + '/view.json')

		
		try:
			resourceJSONStr = system.file.readFileAsString(ignitionSourcePath + '/resource.json')
		except:
			raiseException("Couldn't read path: " + ignitionSourcePath + '/resource.json')		
					
		view["viewJSON"]= viewJSONStr
		view["resourceJSON"]=resourceJSONStr
		
		sourceViewPath = view["viewPath"]	
		sourceParentPath = ('/').join(source.split('/')[:-1])	
		destinationViewPath = destination + sourceViewPath[len(sourceParentPath):]
		
		view["viewPath"] = destinationViewPath
		
		views.append(view)
	
	
	return views
		
		
		
		
		


#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Feb 2023
#*****************************************************************************************************	
def bulkRenameViews(jsonData):
	"""Rename views in bulk.
	
	Rename multiple views and downloads a view import.
	
	Args:
		jsonData (dict): A dictionary with keys {'Path','NewName'}
	"""
	
	viewImports = []
	for row in jsonData:
		path = row['Path']
		newName = row['NewName']
		
		viewImports = viewImports + renameView(path, newName)
			
	if viewImports:
		vieweditor.util.generateViewImport(viewImports)


		
		
		
#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Nov 2022
# Description: Renames view folder.
# 
#
#Example - renames J00017 to foo
#path = 'SCADA/JBLM/Wastewater System/Lift Stations/LS_G1/J00017'
#newName = 'foo'
#*****************************************************************************************************
def renameView(path, newName):

	sourceViews = vieweditor.util.getViews(path)
	views = []
	
	for view in sourceViews:

		ignitionSourcePath = getIgnitionViewRootPath() + '/' + view["viewPath"]
		
		# read template JSON
		try:
			viewJSONStr = system.file.readFileAsString(ignitionSourcePath + '/view.json')
		except:
			raise Exception("Couldn't read path: " + ignitionSourcePath + '/view.json')
		
		try:
			resourceJSONStr = system.file.readFileAsString(ignitionSourcePath + '/resource.json')
		except:
			raise Exception("Couldn't read path: " + ignitionSourcePath + '/resource.json')	
					
		view["viewJSON"]= viewJSONStr
		view["resourceJSON"]=resourceJSONStr
		
		sourceViewPath = view["viewPath"]
		sourceParentPath = ('/').join(path.split('/')[:-1])
		replacementPath = sourceParentPath + '/' + newName
		view["viewPath"] = sourceViewPath.replace(path, replacementPath)
				
		views.append(view)
		
	return views