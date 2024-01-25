"""Filter function definitions

This script is where view filter functions are defined for the Functional View Editor.
Every function must return a function (view -> bool) where a view is a dict with keys 
{'viewPath':str, 'viewJSON':str, 'resourceJSON':str}.
See below for examples.

Todo:
	* 

"""


import re




#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Sept 2022
#*****************************************************************************************************		
def viewPathFilter(pathFilter):
	"""View path filter. Uses Python regex.
	
	Args:
		pathFilter (str): Path filter
		
	Returns:
		A view filter function. (view -> bool)
	"""

	def viewFilter(view):

		if re.search(pathFilter, view["viewPath"]):
			return True
		else:
			return False
	

			
	return viewFilter
	

#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Sept 2022
#*****************************************************************************************************		
def viewJSONFilter(viewJSONFilter):
	"""Filter view JSON. Uses Python regex.
	
	Args:
		viewJSONFilter (str): JSON string filter
		
	Returns:
		A view filter function. (view -> bool)
	"""

	def viewFilter(view):

		if re.search(viewJSONFilter, view["viewJSON"]):
			return True
		else:
			return False
	

			
	return viewFilter
	







#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           May 2023
#*****************************************************************************************************	
def keyPathValueFilter(keyPath, valueFilter):
	"""Filter value at a given key path. Uses Python regex.
	
	Args:
		kayPath (str): Path seperated by '.': For example: root.children.0.type
		valueFilter (str): Value filter
		
	Returns:
		A view filter function. (view -> bool)
	"""
	
	# lambda predicate : value -> bool
	valueIsLambda = False
	

	
	if valueFilter and str(valueFilter).startswith('lambda'):
		p = eval(valueFilter)
		valueIsLambda = True
		

	def viewFilter(view):
		viewObj = system.util.jsonDecode(view["viewJSON"])
		
		value = util.json.getValueAtKeypath(viewObj, keyPath.split('.'))
		
		if valueIsLambda:
			return p(value)
		else:
			if value:
				if re.search(valueFilter, str(value)):
					return True
				else:
					return False
			else:
				return False
	
	return viewFilter
	

	
	
	


#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           April 2023
#*****************************************************************************************************		
def containsSubcomponent(componentType, componentFilter):
	"""Filters views that contain a certain perspective component and satisfies a lambda predicate.
	
	Args:
		componentType (str): Perspective component name.
		componentFilter (str): A lambda:component -> bool. If empty, then no component filter is applied.
		
	Returns:
		A view filter function. (view -> bool)
	"""

	# lambda predicate : componentObj -> bool
	if componentFilter.startswith('lambda'):
		componentFilterFunction = eval(componentFilter)
	else:
		componentFilterFunction = lambda x : True

	# ----- Recursive helper function ---------------------
	def typeFilter(jsonObj, componentType, componentFilter):
		
		if isinstance(jsonObj, dict):
			for key in jsonObj.keys():
				if key == 'type':
					try:
						if jsonObj['type'] == componentType and componentFilter(jsonObj):
							return True
					except:
						pass
				elif key == 'root':
					return typeFilter(jsonObj['root'], componentType, componentFilter)
				elif key == 'children':
					if any( [ typeFilter(child, componentType, componentFilter) for child in jsonObj['children'] ] ):
						return True
					else:
						return False
		else:
			return False



	def viewFilter(view):
		viewObj = system.util.jsonDecode(view["viewJSON"])

		if typeFilter(viewObj, componentType, componentFilterFunction):
			return True
		else:
			return False
	
	return viewFilter
	
	
	