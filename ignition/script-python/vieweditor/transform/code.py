"""Transform function definitions

This script is where view transform functions are defined for the Functional View Editor.
Every function must return a function (view -> view) where the following dict keys are updated:
{'viewJSON':JSON, 'currentValues':list, 'updatedValues':list}


Todo:
	* 

"""


# -------------  Lambda helper functions -------------------------------------------

def _updateComponent(jsonObj, keyPath, value):
	return util.json.updateValueAtKeypath(jsonObj, keyPath.split('.'), system.util.jsonDecode(value))

def _insertComponent(jsonObj, keyPath, value):
	return util.json.insertValueAtKeypath(jsonObj, keyPath.split('.'), system.util.jsonDecode(value))

def _getComponent(jsonObj, keyPath):
	return util.json.getValueAtKeypath(jsonObj, keyPath.split('.'))






#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Sept 2022
#*****************************************************************************************************	
def insertComponent(keyPath, jsonString):
	"""Insert a view JSON subcomponent. Useful for inserting into a list.
	
	Args:
		keyPath (str): Path seperated by '.': For example: tags.0.tags.0.tags
		jsonString (str): The new value. Can be a JSON or a lambda:view->value
		
	Returns:
		A view transform function. (view -> view)
	"""
	
	valueIsLambda = False
	if jsonString.startswith('lambda'):
		f = eval(jsonString)
		valueIsLambda = True

	def viewTransform(view):
	
		viewJSONobj = dict(system.util.jsonDecode(view["viewJSON"]))
		
	
		
		if valueIsLambda:
			viewJSONobj = util.json.insertValueAtKeypath(viewJSONobj, keyPath.split('.'), f(view))	
		else:
			viewJSONobj = util.json.insertValueAtKeypath(viewJSONobj, keyPath.split('.'), system.util.jsonDecode(jsonString))	
		view["viewJSON"] = system.util.jsonEncode(viewJSONobj)
				
		return view
		
		
	return viewTransform


#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Sept 2022
#*****************************************************************************************************	
def updateComponent(keyPath, jsonString):
	"""Update a view JSON subocomponent with a new JSON subcomponent. 
	
	Args:
		keyPath (str): Path seperated by '.': For example: tags.0.tags.0.tags.0.formatString
		jsonString (str): The new value. Can be a JSON or a lambda:view->value
		
	Returns:
		A view transform function. (view -> view)
	"""

	valueIsLambda = False
	if jsonString.startswith('lambda'):
		f = eval(jsonString)
		valueIsLambda = True

	def viewTransform(view):
	
		viewJSONobj = dict(system.util.jsonDecode(view["viewJSON"]))
		
		
		try:
			view['currentValues'].append(_getComponent(viewJSONobj, keyPath))
		except:
			view['currentValues'].append('query error')		
		
		if valueIsLambda:
			value = f(view)
			view['updatedValues'].append(value)
			viewJSONobj = util.json.updateValueAtKeypath(viewJSONobj, keyPath.split('.'), value)	
		else:
			view['updatedValues'].append(jsonString)
			viewJSONobj = util.json.updateValueAtKeypath(viewJSONobj, keyPath.split('.'), system.util.jsonDecode(jsonString))
		view["viewJSON"] = system.util.jsonEncode(viewJSONobj)
				
		return view
		
		
	return viewTransform


#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Sept 2022
#*****************************************************************************************************	
def updateViewParams(params):
	"""Update View Parameters.
	
	Args:
		params (str): Example {"LocationID":71}
		
	Returns:
		A view transfrom function. (view -> view)
	"""

	if not isinstance(params,dict):
		params = system.util.jsonDecode(params)

	def viewTransform(view):
	
		viewJSONdict = dict(system.util.jsonDecode(view["viewJSON"]))
		
		
		for key in params.keys():
			if key in viewJSONdict["params"]:
				viewJSONdict["params"][key] = params[key]
				
		view["viewJSON"] = system.util.jsonEncode(viewJSONdict)
				
		return view
		
		
	return viewTransform
	
	
	
#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Sept 2022
#*****************************************************************************************************					
def viewReplace(templateViewPath):
	"""Replace view with a template view.
	
	Args:
		templateViewPath (str): Path  to template view
		
	Returns:
		A view transform function. (view -> view)
	"""
	
	def viewTransform(view):
		
		ignitionTemplatePath = vieweditor.util.ignitionViewRootPath + '\\' + templateViewPath.replace('/','\\')

		# read template JSON
		try:
			viewJSONStr = system.file.readFileAsString(ignitionTemplatePath + '\\view.json')
		except:
			print("Couldn't read path: " + ignitionTemplatePath + '\\view.json')
			return
		
		try:
			resourceJSONStr = system.file.readFileAsString(ignitionTemplatePath + '\\resource.json')
		except:
			print("Couldn't read path: " + ignitionTemplatePath + '\\resource.json')
			return		
					
					
							
		view["viewJSON"]= viewJSONStr
		view["resourceJSON"]=resourceJSONStr
		
		return view
		
	return viewTransform
	



#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           April 2023
#*****************************************************************************************************					
def forEachComponent(componentType, componentFilter, keypath, updateValue, insertValue):
	"""For each perspective component, apply a transformation function.
	
	Args:
		componentType (str): Perspective component name.
		componentFilter (str): A lambda:component -> bool. If empty, then no component filter is applied.
		keyPath (str): A subpath seperated by '.': For example: props.text
		updateValue (str): The updated Value.
		insertValue (str): Only use if inserting into a list.
		
	Returns:
		A view transform function. (view -> view)
	"""
	
	
	
	# lambda predicate : componentObj -> bool
	if componentFilter.startswith('lambda'):
		componentFilterFunction = eval(componentFilter)
	else:
		componentFilterFunction = lambda x : True
		
	
	# ----- Recursive helper function ---------------------
	def typeTransform(jsonObj, componentType, componentFilter, componentTransform):
		
		if isinstance(jsonObj, dict):
			for key in jsonObj.keys():
				if key == 'type':
				
					try:
						if jsonObj['type'] == componentType and componentFilter(jsonObj):
							jsonObj = componentTransform(jsonObj)
					except:
						print 'typeTransform exception'
						pass
							
				elif key == 'root':
					jsonObj['root'] = typeTransform(jsonObj['root'], componentType, componentFilter, componentTransform)
				elif key == 'children':
					jsonObj['children'] = [ typeTransform(child, componentType, componentFilter, componentTransform) for child in jsonObj['children'] ]
	
		return jsonObj

	# ----- Recursive helper function ---------------------
	def typeQuery(jsonObj, componentType, componentFilter):
	
		values = []
		
		if isinstance(jsonObj, dict):
			for key in jsonObj.keys():
				if key == 'type':
				
					try:
						if jsonObj['type'] == componentType and componentFilter(jsonObj):
							values.append(_getComponent(jsonObj, keypath))
					except:
						print 'typeQuery exception'
						pass
							
				elif key == 'root':
					values = values + typeQuery(jsonObj['root'], componentType, componentFilter)
				elif key == 'children':
					for child in jsonObj['children']:
						values = values + typeQuery(child, componentType, componentFilter)
	
		return values

	
	def viewTransform(view):
		viewJSONobj = system.util.jsonDecode(view["viewJSON"])
		
		try:
			view['currentValues'].append(typeQuery(viewJSONobj, componentType, componentFilterFunction))
		except:
			view['currentValues'].append([])
		
		if updateValue:
		
		
			if updateValue.startswith('lambda'):
				f = eval(updateValue)
				componentTransformFunction = lambda componentObj : _updateComponent(componentObj, keypath, f(view, componentObj))
			else:
				componentTransformFunction = lambda componentObj : _updateComponent(componentObj, keypath, updateValue)
	
		elif insertValue:
			if insertValue.startswith('lambda'):
				f = eval(insertValue)
				componentTransformFunction = lambda componentObj : _insertComponent(componentObj, keypath, f(view, componentObj))
			else:
				componentTransformFunction = lambda componentObj :  _insertComponent(componentObj, keypath, insertValue)
		else:
			componentTransformFunction = lambda x :  x	
		
		
		viewJSONobj = typeTransform(viewJSONobj, componentType, componentFilterFunction, componentTransformFunction)
		
		try:
			view['updatedValues'].append( filter(lambda x : not x == "", typeQuery(viewJSONobj, componentType, lambda x : True)) )
		except:
			view['updatedValues'].append([])
			
		
		
		view["viewJSON"] = system.util.jsonEncode(viewJSONobj)
		return view
		

	return viewTransform
	
	