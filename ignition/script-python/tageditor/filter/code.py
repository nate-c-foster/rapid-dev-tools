"""Filter function definitions

This script is where tag filter functions are defined for the Functional Tag Editor.
Every function must return a function (tag -> bool) where a tag is a dict with keys 
{'tagPath':str, 'tagType':str, 'tagConfig':str}.
See below for examples.

Todo:
	* 

"""


import re


registeredFunctions = [	
	{
	'name':"Tag Path",
	'description':"Filter by tag path, uses Python regex.",
	'functionPath':"tageditor.filter.tagPathFilter",
	'kwargs':{"pathFilter":""},
	'dockPaths':{},
	'dropdownPaths':{},
	'order':1,
	'kwargsOrder':{u'pathFilter': 1}
	},
	{
	'name':"Tag Property Value",
	'description':"Filter by value given a tag property. Uses tag read and Python regex.",
	'functionPath':"tageditor.filter.tagReadPropertyFilter",
	'kwargs':{"property":"","valueFilter":""},
	'dockPaths':{},
	'dropdownPaths':{"property": "Global Components/Functions/Dropdowns/Tag Property", "valueFilter": "Global Components/Functions/Dropdowns/Tag Property Values"},
	'order':2,
	'kwargsOrder':{u'valueFilter': 2, u'property': 1}
	},
	{
	'name':"Tag Parameter",
	'description':"Filter by value of a tag parameter. Uses tag read and Python regex.",
	'functionPath':"tageditor.filter.tagParameterFilter",
	'kwargs':{"typeId":"","parameter":"","valueFilter":""},
	'dockPaths':{},
	'dropdownPaths':{"typeId":"Global Components/Functions/Dropdowns/Parameter UDT Type Select","parameter":"Global Components/Functions/Dropdowns/Parameter Name Select","readOnly":"Global Components/Functions/Dropdowns/Boolean Value"},
	'order':3,
	'kwargsOrder':{u'valueFilter': 3, u'parameter': 2, u'typeId': 1}
	},
	{
	'name':"Path Suffix",
	'description':"Filter by value given a tag suffix. Uses tag read and Python regex.",
	'functionPath':"tageditor.filter.tagReadSuffixFilter",
	'kwargs':{"suffixPath":"","valueFilter":""},
	'dockPaths':{},
	'dropdownPaths':{},
	'order':4,
	'kwargsOrder':{u'valueFilter': 2, u'suffixPath': 1}
	},
	{
	'name':"Tag Config Value",
	'description':"Filters tag config value at a given key path, uses Python regex.",
	'functionPath':"tageditor.filter.keyPathValueFilter",
	'kwargs':{"keyPath":"","valueFilter":""},
	'dockPaths':{},
	'dropdownPaths':{},
	'order':5,
	'kwargsOrder':{u'valueFilter': 2, u'keyPath': 1}
	},
	{
	'name':"Parent UDT",
	'description':"Filter by parent UDT. Useful for atomic tags.",
	'functionPath':"tageditor.filter.ancestorUdtFilter",
	'kwargs':{"typeId":""},
	'dockPaths':{},
	'dropdownPaths':{"typeId": "Global Components/Functions/Dropdowns/UDT Type Id"},
	'order':6,
	'kwargsOrder':{u'typeId': 1}
	}
]

#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Jan 2023
#*****************************************************************************************************		
def tagPathFilter(pathFilter):
	"""Tag path filter. Uses Python regex.
	
	Args:
		pathFilter (str): Path filter
		
	Returns:
		A tag filter function. (tag -> bool)
	"""

	def tagFilter(tag):

		if re.search(pathFilter, str(tag["tagPath"])):
			return True
		else:
			return False
	
	return tagFilter
	



#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Jan 2023
#*****************************************************************************************************		
def tagReadSuffixFilter(suffixPath, valueFilter):
	"""Filter by value given a tag suffix. Uses tag read and Python regex.
	
	Args:
		valueFilter (str): Value Filter
		
	Returns:
		A tag filter function. (tag -> bool)
	"""

	# lambda predicate : value -> bool
	valueIsLambda = False
	if valueFilter.startswith('lambda'):
		p = eval(valueFilter)
		valueIsLambda = True


	def tagFilter(tag):
		
		try:
			value = system.tag.readBlocking(str(tag['tagPath']) + suffixPath)[0].value
			if value == None:
				value = ''
		except:
			return False


		if valueIsLambda:
			try:
				return p(value)
			except:
				return False

		if isinstance(value,int):
			try:
				return int(valueFilter) == int(value)
			except:
				return False
		if isinstance(value,long):
			try:
				return long(valueFilter) == long(value)
			except:
				return False
		if isinstance(value,float):
			try:
				return float(valueFilter) == float(value)
			except:
				return False
		
		if re.search(valueFilter, str(value)):
			return True
		else:
			return False
	
	return tagFilter
	



#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Jan 2023
#*****************************************************************************************************		
def tagParameterFilter(typeId, parameter, valueFilter):
	""""Filter by value given a tag property. Uses tag read and Python regex.
		
	Args:
		typeId (str): UDT type ID
		parameter (str): Tag parameter
		valueFilter (str): Value filter
		
	Returns:
		A tag filter function. (tag -> bool)
	"""
	return tagReadSuffixFilter('/Parameters.' + parameter, valueFilter)




#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Jan 2023
#*****************************************************************************************************		
def tagReadPropertyFilter(property, valueFilter):
	"""Filter by value given a tag property. Uses tag read and Python regex.
	
	Args:
		valueFilter (str): Value Filter
		
	Returns:
		A tag filter function. (tag -> bool)
	"""

	# lambda predicate : value -> bool
	valueIsLambda = False
	if isinstance(valueFilter, str) and valueFilter.startswith('lambda'):
		p = eval(valueFilter)
		valueIsLambda = True


	def tagFilter(tag):



		try:
			value = system.tag.readBlocking(str(tag['tagPath']) + property)[0].value
			if value == None:
				value = ''		
		except:
			return False
		

		if valueIsLambda:
			try:
				return p(value)
			except:
				return False

		if isinstance(value,int):
			try:
				return int(valueFilter) == int(value)
			except:
				return False
		if isinstance(value,long):
			try:
				return long(valueFilter) == long(value)
			except:
				return False
		if isinstance(value,float):
			try:
				return float(valueFilter) == float(value)
			except:
				return False

	
		if re.search(valueFilter, str(value)):
			return True
		else:
			return False

	
	return tagFilter
	
	
	
	

#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Jan 2023
#*****************************************************************************************************		
def ancestorUdtFilter(typeId):
	"""Filter by parent UDT. Useful for atomic tags.
	
	Args:
		typeId (str): UDT Type ID
		
	Returns:
		A tag filter function. (tag -> bool)
	"""

	def tagFilter(tag):

		path = str(tag['tagPath'])
		splitPath = path.split('/')
		pathLength = len(splitPath)
		
		for i in range(pathLength):
			ancestorPath = '/'.join(splitPath[: pathLength - i])
			
			try:
				udtType = system.tag.readBlocking(ancestorPath + ".typeId")[0].value
				if typeId == udtType:
					return True
				
			except:
				return False
				
		return False
	
	return tagFilter










#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Jan 2023
#*****************************************************************************************************		
def keyPathValueFilter(keyPath, valueFilter):
	"""Filters tag config value at a given key path, uses Python regex.
	
	Args:
		valueFilter (str): Value filter
		
	Returns:
		A tag filter function. (tag -> bool)
	"""

	def tagFilter(tag):

		tagConfig = tageditor.util.getTagConfigObj(tag['tagPath'])
		value = util.json.getValueAtKeypath(tagConfig, keyPath.split('.'))
		
		value = str(value)
		
		if value:
			if re.search(valueFilter, str(value)):

				return True
			else:
				return False
		else:
			return False
	
	return tagFilter
	