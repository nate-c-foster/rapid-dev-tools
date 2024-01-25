#*****************************************************************************************************
#
# Author:         	Nate Foster
# Company:        	A.W. Schultz
# Date:           	Sept 2022
# 
#  Utility functions for creating new views import zip file
#*****************************************************************************************************


import os
import shutil
import re

def getIgnitionViewRootPath():
	installationPathIA = settings.getValue('Global','installationPathIA')
	projectName = settings.getValue('View Editor', 'projectName')
	return installationPathIA + '/Ignition/data/projects/' + projectName + '/com.inductiveautomation.perspective/views'


#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Sept 2022
# Description: Generates view import zip file.
# 
# Input arguments:
#	views		(list of dicts with keys {"viewPath", "viewJSON", "resourceJSON"})
#							
#  
#*****************************************************************************************************
def generateViewImport(views):


	# location on gateway server to save import
	saveDirPath =  settings.getValue('Global','serverTempSaveLocation')


	dateTime = system.date.format(system.date.now(),"yyyy-MM-dd-HHmmss")
	importName = settings.getValue('View Editor','projectName') + "_View_Import_" + dateTime
	importViewRootPath = saveDirPath + '/' + importName + '/' + 'com.inductiveautomation.perspective/views'
	

	for view in views:
		viewPath = view["viewPath"]
		viewJSON = view["viewJSON"]
		resourceJSON = view["resourceJSON"]
		
		
		importViewPath = importViewRootPath + '/' + viewPath
		
		system.file.writeFile(importViewPath + '/view.json', viewJSON)		
		system.file.writeFile(importViewPath + '/resource.json', resourceJSON)		
		

		
	##################### add project.json file  ##########################
	projectJSONObj = {
		  					"title": settings.getValue('View Editor','projectName'),
		  					"description": "",
		  					"parent": settings.getValue('View Editor','parentProjectName'),
		  					"enabled": True,
		  					"inheritable": settings.getValue('View Editor','projectInheritable')
						}
	projectJSONStr = system.util.jsonEncode(projectJSONObj)
	system.file.writeFile(saveDirPath + '/' + importName + '/project.json', projectJSONStr)
		
		
	################ create zip file and delete temp folder  ##############################
	shutil.make_archive(saveDirPath + '/' + importName, 'zip', saveDirPath + '/' + importName)
	shutil.rmtree(saveDirPath + '/' + importName)
	
	
	################ transfer zip file from gateway computer to session computer downloads folder #######
	try:
		importReadBytes = system.file.readFileAsBytes(saveDirPath + '/' + importName + '.zip')
		system.perspective.download(importName+'.zip',importReadBytes)
	except:
		print "Couldn't download HMI import."
		





#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Sept 2022
# Description: returns all views within a root view path
#
# Input arguments:
#	rootViewPath		(string)      
#  
#*****************************************************************************************************		
def getViews(rootViewPath):

	views = []

	ignitionViewRootPath = getIgnitionViewRootPath()
	ignitionViewDirPath = ignitionViewRootPath + '/' + rootViewPath


	for dirpath, dirnames, filenames in os.walk(ignitionViewDirPath):
		
		if 'resource.json' in filenames and 'view.json' in filenames:
		
			viewPath = dirpath.split(ignitionViewRootPath + '/')[-1]
			
			# read template JSON
			try:
				viewJSONStr = system.file.readFileAsString(dirpath + '/view.json')
			except:
				print("Couldn't read path: " + dirpath + '/view.json')
				return

			try:
				resourceJSONStr = system.file.readFileAsString(dirpath + '/resource.json')
			except:
				print("Couldn't read path: " + dirpath + '/resource.json')
				return		
				
				
			view = { 	"viewPath": viewPath,
						"viewJSON": viewJSONStr,
						"resourceJSON": resourceJSONStr
					}
					
			views.append(view)
			
	return views


#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Sept 2022
# Description: filters views
#
# Input arguments:
#	views			(dict)      
#	viewPathFilter 	(string)
#	viewJSONFilter 	(string)
#  
#*****************************************************************************************************		
def filterViews(views, viewPathFilter, viewJSONFilter):

	filteredViews = []

	for view in views:
		if re.search(viewPathFilter, view["viewPath"]) and re.search(viewJSONFilter, view["viewJSON"]):
			filteredViews.append(view)
			
	return filteredViews
	



#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Sept 2022
# Description: Given a folder path, returns all the partial view paths within that folder.
# 
# Input arguments:
#	searchPath		(string)      Windows folder path
#							
#  
#*****************************************************************************************************		
def getSubViewDirPaths(searchPath):

	viewDirPaths = []

	for dirpath, dirnames, filenames in os.walk(searchPath):
		
		if 'resource.json' in filenames and 'view.json' in filenames:
			viewDirPaths.append(dirpath.split(searchPath)[-1])
			
	return viewDirPaths
	
	
	
	
	
	
	

	
	
	
	
#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Jan 2023
# Description: returns an Ignition tree of all views
#
# Input arguments:
#	rootPath		(str)      root view path (example "SCADA/JBLM/Water System/Distribution")
#  
#*****************************************************************************************************		
def buildViewTree(rootPath):

	# order folders before views
	def itemOrder(item):
		if item['items']:
			return 0
		else:
			return 1


	ignitionViewRootPath = getIgnitionViewRootPath()
	rootDirPath = ignitionViewRootPath + "/" + rootPath

	name = rootPath.split('/')[-1]
	data = rootPath
	expanded = False


	dirnames = os.listdir(rootDirPath)
	
	if 'resource.json' in dirnames and 'view.json' in dirnames:
		return [{"label":name, "data":data, "expanded":expanded, "items":[]}]
		
	else:
		items = []
		for dirname in dirnames:
			items = items + buildViewTree(rootPath + '/' + dirname)
			items.sort(key=itemOrder)
			
		return [{"label":name, "data":data, "expanded":expanded, "items":items}]




	
def getViewJSON(viewPath):

	ignitionViewRootPath = getIgnitionViewRootPath()
	ignitionViewDirPath = ignitionViewRootPath + '/' + viewPath
	
	try:
		viewJsonStr = system.file.readFileAsString(ignitionViewDirPath + '/view.json')
	except:
		return []
	
	return viewJsonStr
	
	
		