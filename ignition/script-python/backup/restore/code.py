import os

THEMES_RELATIVE_PATH = '/Ignition/data/modules/com.inductiveautomation.perspective/themes'
ICONS_RELATIVE_PATH = '/Ignition/data/modules/com.inductiveautomation.perspective/icons'
DEFAULT_INSTALLATION_PATH = 'C:/Program Files/Inductive Automation'



def restoreTags(resourcesPath, fileName):
	"""Import tags from resources folder.
	
	Args:
		resourcesPath (str): Example: C:/Program Files/Inductive Automation/Ignition/data/projects/rapid-dev-tools/resources
		fileName (str): Example: SCADA__Configuration-RapidDev.json

	"""

	fullTagPath = backup.util.convertFilenameToLabel(fileName, 'tags')
	tagProvider = fullTagPath.split(']')[0][1:]
	tagPath = fullTagPath.split(']')[-1].replace('-','/')
	if '/' in tagPath:
		parentPath = '/'.join(tagPath.split('/')[:-1])
	else:
		parentPath = ''
	
	system.tag.importTags(resourcesPath + '/tags/' + fileName, '[' + tagProvider + ']' + parentPath)




def restoreThemes(installationPath, resourcesPath, themeName):
	"""Import tags from resources folder.
	
	Args:
		installationPath (str): Example: C:/Program Files/Inductive Automation
		resourcesPath (str): Example: C:/Program Files/Inductive Automation/Ignition/data/projects/rapid-dev-tools/resources
		themeName (str): Example: rapid-dev-dark

	"""

	themesPath = installationPath + THEMES_RELATIVE_PATH
	
	fileName = themeName + '.css'
	folderName = themeName
	backup.util.copyFile(resourcesPath + '/themes/' + fileName, themesPath + '/' + fileName)
	backup.util.copyFolder(resourcesPath + '/themes/' + folderName, themesPath + '/' + folderName)
	
	
	
def restoreIcons(installationPath, resourcesPath, fileName):
	"""Import tags from resources folder.
	
	Args:
		installationPath (str): Example: C:/Program Files/Inductive Automation
		resourcesPath (str): Example: C:/Program Files/Inductive Automation/Ignition/data/projects/rapid-dev-tools/resources
		fileName (str): Example: rapid-dev.svg

	"""

	iconsPath = installationPath + ICONS_RELATIVE_PATH
	
	backup.util.copyFile(resourcesPath + '/icons/' + fileName,  iconsPath + '/' + fileName)
	

	
def tagsExist():
	"""Check that RapidDev tags exists
	
	"""

	rootFolderExists =  system.tag.exists(settings.ROOT_PATH + '/RapidDev')
	
	if rootFolderExists:
		globalFolderExists = system.tag.exists(settings.ROOT_PATH + '/RapidDev/Global')
		locationModelFolderExists = system.tag.exists(settings.ROOT_PATH + '/RapidDev/Location Model')
		dbEditorFolderExists = system.tag.exists(settings.ROOT_PATH + '/RapidDev/Database Editor')
		tagEditorFolderExists = system.tag.exists(settings.ROOT_PATH + '/RapidDev/Tag Editor')
		viewEditorFolderExists = system.tag.exists(settings.ROOT_PATH + '/RapidDev/View Editor')
		backupRestoreFolderExists = system.tag.exists(settings.ROOT_PATH + '/RapidDev/Backup Restore')
		if globalFolderExists and locationModelFolderExists and dbEditorFolderExists and tagEditorFolderExists and viewEditorFolderExists and backupRestoreFolderExists:
			return True
		else:
			return False
	else:
		return False
	

def themesExist():
	"""Check that RapidDev themes exists
	
	"""
	
	if tagsExist():
		installationPathIA = settings.getValue("Global", "installationPathIA")
	else:
		installationPathIA = DEFAULT_INSTALLATION_PATH
		
	themesFolderPath = installationPathIA + backup.restore.THEMES_RELATIVE_PATH
	darkThemePath = themesFolderPath + '/rapid-dev-dark'
	lightThemePath = themesFolderPath + '/rapid-dev-light'
	
	if os.path.isfile(darkThemePath + '.css') and os.path.isdir(darkThemePath) and os.path.isfile(lightThemePath + '.css') and os.path.isdir(lightThemePath):
		return True
	else:
		return False

def iconsExist():
	"""Check that RapidDev icons exists
	
	"""
	
	if tagsExist():
		installationPathIA = settings.getValue("Global", "installationPathIA")
	else:
		installationPathIA = DEFAULT_INSTALLATION_PATH

	iconsFolderPath = installationPathIA + backup.restore.ICONS_RELATIVE_PATH
	iconsPath = iconsFolderPath + '/rapid-dev.svg'
	
	if os.path.isfile(iconsPath):
		return True
	else:
		return False
		