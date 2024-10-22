

	
def getTagConfigStr(tagPath):
		return system.util.jsonEncode(getTagConfigObj(tagPath))
	
def getTagConfigObj(tagPath):
	return sortTagConfigObj(system.util.jsonDecode(system.tag.exportTags(tagPaths = [tagPath])))	

def sortTagConfigObj(tagConfigObj):

	if 'tags' in tagConfigObj.keys():
		tagConfigObj['tags'].sort(key=lambda x : x['name'])
		for i, tag in enumerate(tagConfigObj['tags']):
			tagConfigObj['tags'][i] = sortTagConfigObj(tag)
			
		return tagConfigObj
			
	else:
		return tagConfigObj


	

def getProvider(tagPath):
	return tagPath.split(']')[0] + ']'









#*****************************************************************************************************
# Author:         Nate Foster
# Date:           May 2023
#*****************************************************************************************************	
def getComponentName(tagPath):
	"""Get componet name from tag path
	
	Args:
		tagPath (str): tagPath of UDT instance
	
	Returns:
		component name
	"""

	if system.tag.exists(tagPath + '/Parameters.componentName') and system.tag.readBlocking(tagPath + '/Parameters.componentName')[0].value:
		return system.tag.readBlocking(tagPath + '/Parameters.componentName')[0].value

	elif system.tag.exists(tagPath + '/General/CommonName') and system.tag.readBlocking(tagPath + '/General/CommonName')[0].value:
		return system.tag.readBlocking(tagPath + '/General/CommonName')[0].value
		
	else:
		return system.tag.readBlocking(tagPath + '.name')[0].value



#*****************************************************************************************************
# Author:         Nate Foster
# Date:           May 2023
#*****************************************************************************************************	
def getLocationName(tagPath):
	"""Get location name from tag path
	
	Args:
		tagPath (str): tagPath of UDT instance
	
	Returns:
		location name
	"""

	if system.tag.exists(tagPath + '/Parameters.locationName') and system.tag.readBlocking(tagPath + '/Parameters.locationName')[0].value:
		return system.tag.readBlocking(tagPath + '/Parameters.locationName')[0].value

	elif system.tag.exists(tagPath + '/General/LocationName') and system.tag.readBlocking(tagPath + '/General/LocationName')[0].value:
		return system.tag.readBlocking(tagPath + '/General/LocationName')[0].value
		
	else:
		return tagPath.split('/')[-2]




#*****************************************************************************************************
# Author:         Nate Foster
# Date:           May 2023
#*****************************************************************************************************	
def getType(tagPath):
	"""Get UDT type ID.
	
	Args:
		tagPath (str): tagPath of UDT instance
	
	Returns:
		Type ID with "[SCADA]_type_/" removed.
	"""
	
	
	typeId = system.tag.readBlocking(tagPath + '.typeId')[0].value
	return _stripPrefix(typeId) if typeId else ''




#*****************************************************************************************************
# Author:         Nate Foster
# Date:           May 2023
#*****************************************************************************************************							
def getParentType(tagPath):
	"""Get parent UDT type ID if inherited.
	
	Args:
		tagPath (str): tagPath of UDT instance
	
	Returns:
		Type ID with "[SCADA]_type_/" removed.
	"""

	tagProvider = settings.getValue('Tag Editor', 'tagProvider')
	typePrefix = tagProvider + '_types_/'
	
	
	parentTypeId = getType(typePrefix + getType(tagPath))
	return _stripPrefix(parentTypeId) if parentTypeId else ''
	
	

def _stripPrefix(typeId):

	tagProvider = settings.getValue('Tag Editor', 'tagProvider')
	typePrefix = tagProvider + '_types_/'

	if typeId.startswith(typePrefix):
		return typeId[len(typePrefix):]
	else:
		return typeId









#rootTagPath = '[SCADA]SIM City/'
#typeId = 'User Defined/SIM/AI_AOI'
#removeList = [	'copyConfig',
#				'faceplatePath',
#				'faceplateTabs',
#				'mobileViewOrder',
#				'mobileViewPath',
#				'overview1ViewOrder',
#				'overview1ViewPath',
#				'overview2ViewOrder', 
#				'overview2ViewPath',
#				'symbolPath',
#				'trendIconColor',
#				'trendIconPath',
#				'trendLocationDisplay',
#				'trendPlotNumber',
#				'trendValuePathPrimary',
#				'trendValuePathSecondary'
#				]


def removeCustomProperites(rootTagPath, typeId, removeList):

	results = system.tag.browse(rootTagPath, {'recursive':True, 'tagType': 'UdtInstance', 'typeId': typeId})
	
	for result in results:
		tagPath = str(result['fullPath'])
		parentPath = '/'.join(tagPath.split('/')[:-1])
	
	#	print tagPath
	#	print parentPath	
	
		tagConfig = tageditor.util.getTagConfigObj(tagPath)
	
		updatedConfig = {key:value for key, value in tagConfig.items() if key not in removeList}
		
		tagConfigStr = system.util.jsonEncode(updatedConfig)
		
		system.tag.configure(parentPath, tagConfigStr)








#*****************************************************************************************************
#
# Author:         Nate Foster
# Date:           Jan 2023
# Description: 
#
# Input arguments:
#				(obj)     
#  
#*****************************************************************************************************		
def tagConfigToSerializable(tagConfig):

	
	def serializeJSON(jsonObj):
	
		if isinstance(jsonObj, dict):

			for key in jsonObj.keys():
				if key == 'path':
					del jsonObj[key]
				else:
					jsonObj[key] = serializeJSON(jsonObj[key])
		

			return jsonObj
		
		elif isinstance(jsonObj, list):

			for i in range(len(jsonObj)):
				jsonObj[i] =  serializeJSON(jsonObj[i])


			return jsonObj

   		else:
   		
   			
   			if isinstance(jsonObj, bool):
   				return bool(jsonObj)
   			elif isinstance(jsonObj, long) or isinstance(jsonObj, int):
   				return long(jsonObj)
   			elif isinstance(jsonObj, float):
   				return float(jsonObj)
   			else:
   				return str(jsonObj)

	return serializeJSON(tagConfig)