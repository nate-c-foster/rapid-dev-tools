"""Filter function definitions

This script is where tag filter functions are defined for the Functional Tag Editor.
Every function must return a function (tag -> bool) where a tag is a dict with keys 
{'tagPath':str, 'tagType':str, 'tagConfig':str}.
See below for examples.

Todo:
	* 

"""


import re


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
	