

THEMES_RELATIVE_PATH = '/Ignition/data/modules/com.inductiveautomation.perspective/themes'
ICONS_RELATIVE_PATH = '/Ignition/data/modules/com.inductiveautomation.perspective/icons'




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