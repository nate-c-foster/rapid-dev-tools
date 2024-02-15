"""Read/Write function definitions

This script is where tag read/write functions are defined for the Functional Tag Editor.
Every function must return a function (tag -> tag) where the following dict keys are updated:
{'writePaths':list, 'readValues':list, 'writeValues':list, 'readOnly':list}
See below for examples.

Todo:
	* 

"""
import re

registeredFunctions = [	
	{
	'name':"Path Suffix",
	'description':"Appends suffix path to tag path for read/write, value can be a lambda: tag -> value",
	'functionPath':"tageditor.readwrite.suffixPath",
	'kwargs':{"suffixPath":"","value":"","readOnly":""},
	'dockPaths':{},
	'dropdownPaths':{"readOnly":"Global Components/Functions/Dropdowns/Boolean Value"},
	'order':1,
	'kwargsOrder':{u'readOnly': 3, u'suffixPath': 1, u'value': 2}
	},
	{
	'name':"Tag Parameter",
	'description':"Select a parameter name for read/write, value can be a lambda: tag -> value",
	'functionPath':"tageditor.readwrite.writeParameterValue",
	'kwargs':{"typeId":"","parameter":"","value":"","readOnly":""},
	'dockPaths':{},
	'dropdownPaths':{"typeId":"Global Components/Functions/Dropdowns/Parameter UDT Type Select","parameter":"Global Components/Functions/Dropdowns/Parameter Name Select","readOnly":"Global Components/Functions/Dropdowns/Boolean Value"},
	'order':2,
	'kwargsOrder':{u'readOnly': 4, u'parameter': 2, u'typeId': 1, u'value': 3}
	},
	{
	'name':"Tag Property",
	'description':"Select a property for read/write, value can be a lambda: tag -> value",
	'functionPath':"tageditor.readwrite.writePropertyValue",
	'kwargs':{"property":"","value":"","readOnly":""},
	'dockPaths':{},
	'dropdownPaths':{"property":"Global Components/Functions/Dropdowns/Tag Property","value":"Global Components/Functions/Dropdowns/Tag Property Values","readOnly":"Global Components/Functions/Dropdowns/Boolean Value"},
	'order':3,
	'kwargsOrder':{u'readOnly': 3, u'property': 1, u'value': 2}
	}
]

#*****************************************************************************************************
# Author:         Nate Foster
# Date:           Jan 2023
#*****************************************************************************************************	
def suffixPath(suffixPath, value, readOnly=False):
	"""Appends suffix path to tag path for read/write.
	
	Args:
		suffixPath (str): This is appended to the tag path.
		value (str): The write value. Can be a lambda: tag -> value.
		readOnly (bool): Don't write value if true.
		
	Returns:
		A tag read/write function. (tag -> tag)
	"""

	valueIsLambda = False
	if value.startswith('lambda'):
		f = eval(value)
		valueIsLambda = True


	def tagReadWrite(tag):
	
		prefixPath = str(tag['tagPath'])
		writePath = prefixPath + suffixPath
		tag['writePaths'].append(writePath)
		
		try:
			tag['readValues'].append(system.tag.readBlocking(writePath)[0].value)
		except:
			tag['readValues'].append('')		
		
		if valueIsLambda:
			tag['writeValues'].append(f(tag))
		else:
			tag['writeValues'].append(value)
			
		tag['readOnly'].append(readOnly)
		
		return tag
		
	return tagReadWrite
	
	



#*****************************************************************************************************
# Author:         Nate Foster
# Date:           Jan 2023
#*****************************************************************************************************	
def writePropertyValue(property, value, readOnly=False):
	"""Select a property for read/write.
	
	Args:
		property (str): Property name.
		value (str): The write value. Can be a lambda: tag -> value.
		readOnly (bool): Don't write value if true.
		
	Returns:
		A tag read/write function. (tag -> tag)
	"""

	valueIsLambda = False
	if str(value).startswith('lambda'):
		f = eval(value)
		valueIsLambda = True

	def tagReadWrite(tag):
		prefixPath = str(tag['tagPath'])
		writePath = prefixPath + property
		tag['writePaths'].append(writePath)
			
		try:
			tag['readValues'].append(system.tag.readBlocking(writePath)[0].value)
		except:
			tag['readValues'].append('')		
		
		if valueIsLambda:
			tag['writeValues'].append(f(tag))
		else:
			tag['writeValues'].append(value)
		
		tag['readOnly'].append(readOnly)		
		
		return tag	

	return tagReadWrite
	
	
	

#*****************************************************************************************************
# Author:         Nate Foster
# Date:           Jan 2023
#*****************************************************************************************************	
def writeParameterValue(typeId, parameter, value, readOnly=False):
	"""Select a parameter name for read/write.
	
	Args:
		typeId (str): UDT Type Id.
		parameter (str): Parameter name.
		value (str): The write value. Can be a lambda: tag -> value.
		readOnly (bool): Don't write value if true.
		
	Returns:
		A tag read/write function. (tag -> tag)
	"""

	valueIsLambda = False
	if str(value).startswith('lambda'):
		f = eval(value)
		valueIsLambda = True

	def tagReadWrite(tag):
		prefixPath = str(tag['tagPath'])
		writePath = prefixPath + '/Parameters.' + parameter
		tag['writePaths'].append(writePath)
			
		try:
			tag['readValues'].append(system.tag.readBlocking(writePath)[0].value)
		except:
			tag['readValues'].append('')		
		
		if valueIsLambda:
			tag['writeValues'].append(f(tag))
		else:
			tag['writeValues'].append(value)
			
		tag['readOnly'].append(readOnly)
		
		return tag	

	return tagReadWrite
	
	
	

