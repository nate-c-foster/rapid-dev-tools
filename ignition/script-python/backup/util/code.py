
import shutil
import os



#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           March 2023
#*****************************************************************************************************	
def createTempDirectory(directoryName):
	"""Creates a temporary directory.
	"""

	tempLocation = settings.getValue('Global','serverTempSaveLocation')
	path = tempLocation + '/' + directoryName

	os.mkdir(path)



#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           March 2023
#*****************************************************************************************************	
def zipTempDirectory(directoryName):
	"""Zip temporary directory.
	"""

	tempLocation = settings.getValue('Global','serverTempSaveLocation')
	path = tempLocation + '/' + directoryName
	format = 'zip'

	shutil.make_archive(path, format, path)
	shutil.rmtree(path)
	
	
#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           March 2023
#*****************************************************************************************************	
def unZipTempFile(fileName):
	"""unzip temporary file.
	"""

	tempLocation = settings.getValue('Global','serverTempSaveLocation')
	path = tempLocation + '/' + fileName



	from zipfile import ZipFile
	
	zipFile = ZipFile(path, 'r')
	zipFile.extractall(path[:-len('.zip')])
	zipFile.close()
	os.remove(path)
	
	
	
#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           March 2023
#*****************************************************************************************************	
def copyToTempDirectory(sourcePath, directoryName):	
	"""Copy file/folder from sourcePath to temporary directoryName
	"""
	tempLocation = settings.getValue('Global','serverTempSaveLocation')
	destinationPath = tempLocation + '/' + directoryName
	
	if os.path.isfile(sourcePath):
		shutil.copy(sourcePath, destinationPath)
	elif os.path.isdir(sourcePath):
		shutil.copytree(sourcePath, destinationPath)
	else:
		print 'Error: Not a file or folder'
	
	
	

#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           March 2023
#*****************************************************************************************************		
def downloadTempFile(fileName):
	"""Transfer temporary file from gateway computer to session computer downloads folder
	"""

	tempLocation = settings.getValue('Global','serverTempSaveLocation')
	path = tempLocation + '/' + fileName

	importReadBytes = system.file.readFileAsBytes(path)
	system.perspective.download(fileName,importReadBytes)
	




#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           March 2023
#*****************************************************************************************************		
def getProjectNames():
	"""Get a list of non-default project names
	"""

	installationPath = settings.getValue('Global', 'installationPathIA')
	projectsPath = installationPath + '/Ignition/data/projects'
	
	dirList = os.listdir(projectsPath)
	
	
	defaultProjects = ['samplequickstart']
	projects = []
	for name in dirList:
		if name not in defaultProjects and '.' not in name:
			projects.append(name)
			
	return projects


#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           March 2023
#*****************************************************************************************************	
def getTagProviders():
	"""Get a list of tag providers.
	"""
	
	tags = system.tag.browse('')
	tagProviders = []
	for tag in tags:
		tagProviders.append(tag['fullPath'])
		
	return tagProviders
		


#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           March 2023
#*****************************************************************************************************			
def getThemeNames():
	"""Get a list of non-default theme names
	"""

	installationPath = settings.getValue('Global','installationPathIA')
	themesPath = installationPath + '/Ignition/data/modules/com.inductiveautomation.perspective/themes'
	
	dirList = os.listdir(themesPath)
	
	defaultThemes = ['dark','dark-cool','dark-warm','light','light-cool','light-warm','light-cool']
	themes = []
	for name in dirList:
		if name not in defaultThemes and '.' not in name:
			themes.append(name)

	return themes
	

#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           March 2023
#*****************************************************************************************************			
def exportTags(fileName, tagPath):
	"""Export tags
	"""
	filePath = settings.getValue('Global','serverTempSaveLocation') + '/' + fileName
	system.tag.exportTags(filePath, [tagPath], True)	
	










#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           June 2023
#*****************************************************************************************************		
def copyFile(sourcePath,  destinationPath):
	"""Copy file from sourcePath to destinationPath.
	
	Args:
		sourcePath (str): Path to source file. Use '/' not '\\'.
		destinationPath (str): Path to destination file. Use '/' not '\\'.

	"""
	
	fileBytes = system.file.readFileAsBytes(sourcePath)
	system.file.writeFile(destinationPath,fileBytes)
	
	
#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           June 2023
#*****************************************************************************************************	
def copyFolder(sourcePath, destinationPath):
	"""Copy folder from sourcePath to destinationPath.
	
	Args:
		sourcePath (str): Path to source folder. Use '/' not '\\'.
		destinationPath (str): Path to destination folder. Use '/' not '\\'.

	"""

	for dirpath, dirnames, filenames in os.walk(sourcePath):

		for fileName in filenames:
			fileSuffixPath = dirpath[len(sourcePath):].replace('\\','/') + '/' + fileName
			fileSourcePath = sourcePath + fileSuffixPath
			fileDestinationPath = destinationPath +  fileSuffixPath
			copyFile(fileSourcePath, fileDestinationPath)




	
#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           June 2023
#*****************************************************************************************************	
def getResourceNames(resourcePath):
	"""Get all file names in a resource folder.
	
	Args:
		resourcePath (str): Path to directory of a resource type. Example "C:/Program Files/Inductive Automation/Ignition/data/projects/RapidDevToolsCore/resources/themes"

	"""
	
	names = []
	
	if os.path.exists(resourcePath):
		names = [f for f in os.listdir(resourcePath) if os.path.isfile(resourcePath + '/' + f)]
	
	return names
	
	
	
#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           June 2023
#*****************************************************************************************************	
def convertFilenameToLabel(filename, resourceType):
	"""Convert resource filename to a label
	
	foo__name1-name2-name3.type => [foo]name1/name2/name3
	
	Args:
		filename (str): Full filename. 
		resourceType (str) : Examples 'tags', 'tables', 'themes', 'icons'

	"""
	name = filename

	if resourceType == 'tags':
		name = '[' + name.replace('__',']')
		name = name.replace('-','/')
		name = name.split('.')[0]
	
	elif resourceType == 'tables':
		name = '[' + name.replace('__',']')
		if '.csv' in name:
			name = name[:-len('.csv')]
	
	elif resourceType == 'themes':
		if '.css' in name:
			name = name[:-len('.css')]
		
	elif resourceType == 'icons':
		name = name.split('.')[0]

	return name

	
	
