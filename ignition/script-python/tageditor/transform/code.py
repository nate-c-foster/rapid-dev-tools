"""Transform function definitions

This script is where tag config transform functions are defined for the Functional Tag Editor.
Every function must return a function (tag -> tag) where the following dict keys are updated:
{'tagConfig':JSON, 'currentValues':list, 'updatedValues':list}
Note: For efficiency reasons "tagConfig" will be empty list until a transformation is performed.
See below for examples.

Todo:
	* 

"""


# -------------------   Utility Functions that can be accessed by lambdas     --------------------------------------------------------------------------------------------


# pyObj to jsonStr
def encode(pyObj):
	return system.util.jsonEncode(pyObj)

# jsonStr to pyObj
def decode(jsonStr):
	return system.util.jsonDecode(jsonStr)

def _updateComponent(jsonObj, keypath, value):
	return util.json.updateValueAtKeypath(jsonObj, keypath.split('.'), system.util.jsonDecode(value))

def _insertComponent(jsonObj, keypath, value):
	return util.json.insertValueAtKeypath(jsonObj, keypath.split('.'), system.util.jsonDecode(value))

def _removeComponent(jsonObj, keypath):
	return util.json.removeItemAtKeypath(jsonObj, keypath.split('.'))

def _getComponent(jsonObj, keypath):
	return util.json.getValueAtKeypath(jsonObj, keypath.split('.'))






#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Jan 2023
#*****************************************************************************************************	
def updateConfigValue(keyPath, value):
	"""Update a configuration value at the given key path.
	
	Args:
		keyPath (str): Path seperated by '.': For example: tags.0.tags.0.tags.0.formatString
		value (str): The new value. Can be a JSON or a lambda:tag->value
		
	Returns:
		A tag transform function. (tag -> tag)
	"""

	valueIsLambda = False
	if value.startswith('lambda'):
			f = eval(value)
			valueIsLambda = True

	def tagTransform(tag):
	
	
		if tag['tagConfig']:
			tagConfig = system.util.jsonDecode(tag['tagConfig'])
		else:
			tagConfig = tageditor.util.getTagConfigObj(tag['tagPath'])
			
		try:
			tag['currentValues'].append(_getComponent(tagConfig, keyPath))
		except:
			tag['currentValues'].append('query error')	
			
		if valueIsLambda:
			lambdaValue = f(tag)
			tag['updatedValues'].append(value)
			util.json.updateValueAtKeypath(tagConfig, keyPath.split('.'), lambdaValue)
		else:
			tag['updatedValues'].append(value)
			util.json.updateValueAtKeypath(tagConfig, keyPath.split('.'), value)
		
		tag["tagConfig"] = system.util.jsonEncode(tagConfig)
				
		return tag
		
		
	return tagTransform




#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Jan 2023
#*****************************************************************************************************	
def insertConfigValue(keyPath, value):
	"""Insert a new configuration value at the given key path. Useful for inserting into a list.
	
	Args:
		keyPath (str): Path seperated by '.': For example: tags.0.tags.0.tags
		value (str): The new value. Can be a JSON or a lambda:tag->value
		
	Returns:
		A tag transform function. (tag -> tag)
	"""

	valueIsLambda = False
	if value.startswith('lambda'):
			f = eval(value)
			valueIsLambda = True
			
	def tagTransform(tag):
	
		if tag['tagConfig']:
			tagConfig = system.util.jsonDecode(tag['tagConfig'])
		else:
			tagConfig = tageditor.util.getTagConfigObj(tag['tagPath'])
			
		try:
			tag['currentValues'].append(_getComponent(tagConfig, keyPath))
		except:
			tag['currentValues'].append('query error')	

		if valueIsLambda:
			util.json.insertValueAtKeypath(tagConfig, keyPath.split('.'), f(tag))
		else:
			util.json.insertValueAtKeypath(tagConfig, keyPath.split('.'), value)
		
		tag["tagConfig"] = system.util.jsonEncode(tagConfig)
				
		return tag
		
		
	return tagTransform
	
	
#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Jan 2023
#*****************************************************************************************************	
def removeConfigItem(keyPath):
	"""Insert a new configuration value at the given key path. Useful for inserting into a list.
	
	Args:
		keyPath (str): Path seperated by '.': For example: tags.0.tags.0.tags
		
	Returns:
		A tag transform function. (tag -> tag)
	"""

		
	def tagTransform(tag):
	
		if tag['tagConfig']:
			tagConfig = system.util.jsonDecode(tag['tagConfig'])
		else:
			tagConfig = tageditor.util.getTagConfigObj(tag['tagPath'])
			
		try:
			tag['currentValues'].append(_getComponent(tagConfig, keyPath))
		except:
			tag['currentValues'].append('query error')	

		util.json.removeItemAtKeypath(tagConfig, keyPath.split('.'))
		
		tag["tagConfig"] = system.util.jsonEncode(tagConfig)
				
		return tag
		
		
	return tagTransform

#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Jan 2023
#*****************************************************************************************************	
def getConfigValue(keyPath):
	"""Gets value at a given key path.
	
	Args:
		keyPath (str): Path seperated by '.': For example: tags.0.tags.0.tags
		
	Returns:
		A tag transform function. (tag -> tag)
	"""

	def tagTransform(tag):

		if tag['tagConfig']:
			tagConfig = system.util.jsonDecode(tag['tagConfig'])
		else:
			tagConfig = tageditor.util.getTagConfigObj(tag['tagPath'])

		tag['currentValues'].append(util.json.getValueAtKeypath(tagConfig, keyPath.split('.')))
		
		return tag
		
		
	return tagTransform
	
	
	
	
	
	
	
	
	

	
