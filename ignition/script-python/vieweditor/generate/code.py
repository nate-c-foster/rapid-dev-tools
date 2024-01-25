"""Generate function definitions

This script is where view generator functions are defined for the Functional View Editor.
Every function must return a list of views where a view is a dict with keys {'viewPath':str, 'viewJSON':str, 'resourceJSON':str}.
See below for examples.


"""

import os




#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Sept 2022
#*****************************************************************************************************		
def getViews(rootViewPath):
	"""Generate all views under a given root view path.
	
	Args:
		rootViewPath (str): Root view path.
		
	Returns:
		List of views where a view is a dict with keys {'viewPath':str, 'viewJSON':str, 'resourceJSON':str}
	"""

	views = []

	ignitionViewRootPath = vieweditor.util.getIgnitionViewRootPath()
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
				
				
			view = { 	"viewPath": viewPath.replace('\\','/'),
						"viewJSON": viewJSONStr,
						"resourceJSON": resourceJSONStr
					}
					
			views.append(view)
			
	return views
	
	
	
	
	
	
	
	
	
	
	

	
	
	