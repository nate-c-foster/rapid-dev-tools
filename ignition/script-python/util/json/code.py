











def toPythonObject(object): 
	if 'append' in dir(object) and 'class' not in dir(object):
		object = list(object)
		object = [toPythonObject(item) for item in object]
	elif 'iteritems' in dir(object):
		object = dict(object)
		object = {key: toPythonObject(value) for key, value in object.items()}
	return object






#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Jan 2023
# Description: Turns JSON string into Perspective tree items
#
# Input arguments:
#	jsonStr			(str)     
#  
#*****************************************************************************************************		
def jsonToTree(jsonStr, expanded = lambda key : True):
	
	jsonObj = system.util.jsonDecode(jsonStr)
	
	return jsonObjToTree(jsonObj, expanded)





#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Jan 2023
# Description: Turns JSON obj into Perspective tree items
#
# Input arguments:
#	jsonStr			(obj)     
#  
#*****************************************************************************************************		
def jsonObjToTree(jsonObj, expanded = lambda key : True):

	items = []

	try:
		p = eval(expanded)
	except:
		return items
	
	def parseJSON(jsonObj, ObjKey, keypath):
	
		if isinstance(jsonObj, dict):
			items = []
			for key in jsonObj.keys():
				items = items + parseJSON(jsonObj[key], key, keypath  + "." + str(key))
				
				
			# ----  add useful labels to list elements instead of just a number 
			if 'name' in jsonObj.keys() and str(ObjKey) != 'meta':
				label = str(ObjKey) + ' - ' + jsonObj['name']
			elif 'meta' in jsonObj.keys() and 'name' in jsonObj['meta'].keys() and str(ObjKey) != 'root':
				label = str(ObjKey) + ' - ' + jsonObj['meta']['name']
			else:
				label = str(ObjKey)
				
			icon = {'path':'rapid-dev/dict', 'color':'var(--green-78)'}
				
			return [{"label":label, "data": keypath, "expanded":p(jsonObj), "items":items, "icon":icon}]
		
		elif isinstance(jsonObj, list):
			items = []
			for i in range(len(jsonObj)):
				items = items + parseJSON(jsonObj[i], i, keypath + "." + str(i))
				
			icon = {'path':'rapid-dev/list', 'color':'var(--orange-78)'}
			return [{"label":str(ObjKey), "data": keypath, "expanded":p(jsonObj), "items":items, "icon":icon}]

   		else:
   			icon = {'path':'material/stop', 'color':'var(--blue-77)'}
   			return [{"label":str(ObjKey) + " : " + str(jsonObj), "data": keypath, "expanded":p(jsonObj), "items":[], "icon":icon}]


	return parseJSON(jsonObj, "", "")








#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           April 2023
# Description: Sets value at keypath
#
# Input arguments:
#	jsonObj			(dict)     
#  	keypath			(list)   example   ["root","children","1","position","basis"]
# 	val				(dict)  JSON object
#*****************************************************************************************************		
def getValueAtKeypath(jsonObj, keypath):

	if len(keypath) > 0:
		try:
			if isinstance(jsonObj, dict):
				if keypath[0] in jsonObj.keys():
					return getValueAtKeypath(jsonObj[keypath[0]], keypath[1:])
					
			elif isinstance(jsonObj, list):
				if int(keypath[0]) < len(jsonObj):
					return getValueAtKeypath(jsonObj[int(keypath[0])], keypath[1:])
					
			return ''
			
		except:
			print 'updateValueAtKeypath exception'
			return ''
			
			
	else:
		return jsonObj
		
		
		


#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           April 2023
# Description: Sets value at keypath
#
# Input arguments:
#	jsonObj			(dict)     
#  	keypath			(list)   example   ["root","children","1","position","basis"]
# 	val				(dict)  JSON object
#*****************************************************************************************************		
def updateValueAtKeypath(jsonObj, keypath, val):

	if len(keypath) > 0:
		try:
			if isinstance(jsonObj, dict):
				if keypath[0] in jsonObj.keys():
					jsonObj[keypath[0]] = updateValueAtKeypath(jsonObj[keypath[0]], keypath[1:], val)
					
			elif isinstance(jsonObj, list):
				if int(keypath[0]) < len(jsonObj):
					jsonObj[int(keypath[0])] = updateValueAtKeypath(jsonObj[int(keypath[0])], keypath[1:], val)
					
			return jsonObj
			
		except:
			print 'updateValueAtKeypath exception'
			return jsonObj
			
			
	else:
		return val





#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           April 2023
# Description: Inserts value at keypath
#
# Input arguments:
#	jsonObj			(dict)     
#  	keypath			(list)   example   ["root","children","1","position","basis"]
# 	val				(dict)  JSON object
#*****************************************************************************************************		
def insertValueAtKeypath(jsonObj, keypath, val):

	if len(keypath) > 1:
		try:
			if isinstance(jsonObj, dict):
				if keypath[0] in jsonObj.keys():
					jsonObj[keypath[0]] = insertValueAtKeypath(jsonObj[keypath[0]], keypath[1:], val)
					
			elif isinstance(jsonObj, list):
				if int(keypath[0]) < len(jsonObj):
					jsonObj[int(keypath[0])] = insertValueAtKeypath(jsonObj[int(keypath[0])], keypath[1:], val)
					
			return jsonObj
			
		except:
			print 'insertValueAtKeypath exception'
			return jsonObj
			
			
	else:
		try:
			if isinstance(jsonObj, dict):
				jsonObj[keypath[0]] =  val
					
			elif isinstance(jsonObj, list):
				jsonObj.insert(int(keypath[0]),  val)
					
			return jsonObj
			
		except:
			print 'insertValueAtKeypath exception'
			return jsonObj
			
			
#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           April 2023
# Description: Remove item at keypath
#
# Input arguments:
#	jsonObj			(dict)     
#  	keypath			(list)   example   ["root","children","1","position","basis"]
#*****************************************************************************************************
def removeItemAtKeypath(jsonObj, keypath):

	if len(keypath) > 1:
		try:
			if isinstance(jsonObj, dict):
				if keypath[0] in jsonObj.keys():
					jsonObj[keypath[0]] = removeItemAtKeypath(jsonObj[keypath[0]], keypath[1:])
					
			elif isinstance(jsonObj, list):
				if int(keypath[0]) < len(jsonObj):
					jsonObj[int(keypath[0])] = removeItemAtKeypath(jsonObj[int(keypath[0])], keypath[1:])
					
			return jsonObj
			
		except:
			print 'removeItemAtKeypath exception'
			return jsonObj
			
			
	else:
		try:
			if isinstance(jsonObj, dict):
				del jsonObj[keypath[0]]
					
			elif isinstance(jsonObj, list):
				del jsonObj[int(keypath[0])]
					
			return jsonObj
			
		except:
			print 'removeItemAtKeypath exception - last item'
			return jsonObj




#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Sep 2022
# Description: Annotates JSON objects with the differences between them
#
# Input arguments:
#	jsonObj1			(dict)
#	jsonObj2			(dict)     
#  	modified			(str)     'add','mod'
#*****************************************************************************************************	
def JSONdiff(JSONobj1, JSONobj2, modified):
	
	
	if isinstance(JSONobj1, dict) and isinstance(JSONobj2, dict):
	
		taggedDict = {}
		for key in JSONobj1.keys():
		
			if key in JSONobj2.keys() and modified != 'add':
			
				if JSONobj1[key] == JSONobj2[key]:
					taggedDict[key] = JSONobj1[key]
				else:
					taggedDict[key + '_mod'] = JSONdiff(JSONobj1[key], JSONobj2[key], 'mod')
	
			else:
			
				taggedDict[key + '_add'] = JSONdiff(JSONobj1[key],JSONobj1[key], 'add')
	
		return taggedDict
	
	elif isinstance(JSONobj1, list) and isinstance(JSONobj2, list):
	
		taggedList = []
		for x in JSONobj1:
			
			if modified == 'add':
				taggedList.append(JSONdiff(x,x,'add'))
			
			else:
			
				if x in JSONobj2:
					taggedList.append(x)
				else:
					match = False
					for y in JSONobj2:
						if isinstance(x,dict) and isinstance(y,dict):
							if 'meta' in x and 'meta' in y:
								if 'name' in x['meta'] and 'name' in y['meta']:
									if x['meta']['name'] == y['meta']['name']:
										taggedList.append(JSONdiff(x,y,'mod'))
										match = True
										break
					if not match:
						taggedList.append(JSONdiff(x,x,'add'))
	
		return taggedList
	
		
	else:
		return JSONobj1
		
		

#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Sep 2022
# Description: Annotates JSON objects with the differences between them
#
# Input arguments:
#	jsonObj1			(dict)
#	jsonObj2			(dict)     
#  	modified			(str)     'add','mod'
#*****************************************************************************************************	
def JSONdiff_V2(JSONobj1, JSONobj2, modified):
	
	if isinstance(JSONobj1, dict) and isinstance(JSONobj2, dict):
	
		taggedDict = {}
		for key in JSONobj1.keys():
		
			if key in JSONobj2.keys() and modified != 'add':
			
				if JSONobj1[key] == JSONobj2[key]:
#				if objEqual(JSONobj1[key], JSONobj2[key]):
		
					taggedDict[key] = JSONobj1[key]
				else:
					taggedDict[key + '_mod'] = JSONdiff_V2(JSONobj1[key], JSONobj2[key], 'mod')
	
			else:
				taggedDict[key + '_add'] = JSONdiff_V2(JSONobj1[key],JSONobj1[key], 'add')
	
		return taggedDict
	
	elif isinstance(JSONobj1, list) and isinstance(JSONobj2, list):
	
		taggedList = []
		for i, value in enumerate(JSONobj1):
			
			if i < len(JSONobj2) and modified != 'add':
			
				if JSONobj1[i] == JSONobj2[i]:		
#				if objEqual(JSONobj1[i], JSONobj2[i]):		
					taggedList.append(JSONdiff_V2(JSONobj1[i], JSONobj2[i],modified))
				else:	
					taggedList.append(JSONdiff_V2(JSONobj1[i], JSONobj2[i],'mod'))				
					
			else:
				taggedList.append(JSONdiff(JSONobj1[i], JSONobj1[i],'add'))
	
	
		return taggedList
	
		
	else:
		return JSONobj1





#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Sep 2022
# Description: Annotates JSON objects with the differences between them
#
# Input arguments:
#	jsonObj1			(dict)
#	jsonObj2			(dict)     
#  	modified			(str)     'add','mod'
#*****************************************************************************************************	
def JSONdiff_V3(JSONobj1, JSONobj2, modified):
	
	if isinstance(JSONobj1, dict) and isinstance(JSONobj2, dict):
	
		taggedDict = {}
		for key in JSONobj1.keys():
		
			if key in JSONobj2.keys() and modified != 'add':
			
				if JSONobj1[key] == JSONobj2[key]:	
					taggedDict[key] = JSONobj1[key]
					
				else:
					taggedDict[key + '_mod'] = JSONdiff_V3(JSONobj1[key], JSONobj2[key], 'mod')
			else:
				taggedDict[key + '_add'] = JSONdiff_V3(JSONobj1[key],JSONobj1[key], 'add')
				
		return taggedDict
	
	elif isinstance(JSONobj1, list) and isinstance(JSONobj2, list):
	
		taggedList = []
		for i, value1 in enumerate(JSONobj1):
			
			if i < len(JSONobj2) and modified != 'add':
			
				for j, value2 in enumerate(JSONobj2):
				
					if value1['name']== value2['name']: # and value1['tagType']==value2['tagType']:
					
						if JSONobj1[i] == JSONobj2[j]:		
		#				if objEqual(JSONobj1[i], JSONobj2[i]):		
							taggedList.append(JSONdiff_V3(JSONobj1[i], JSONobj2[j],modified))
						else:	
							taggedList.append(JSONdiff_V3(JSONobj1[i], JSONobj2[j],'mod'))				
					
			else:
				taggedList.append(JSONdiff(JSONobj1[i], JSONobj1[i],'add'))
	
	
		return taggedList
	
		
	else:
		return JSONobj1



#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Sep 2022
# Description: Annotates JSON objects with the differences between them
#
# Input arguments:
#	jsonObj1			(dict)
#	jsonObj2			(dict)     
#  	modified			(str)     'add','mod'
#*****************************************************************************************************	
def objEqual(JSONobj1, JSONobj2):
	
	
	if isinstance(JSONobj1, dict) and isinstance(JSONobj2, dict):
		equalList = []
		for key in JSONobj1.keys():
				if key in JSONobj2.keys():
					equalList.append( objEqual(JSONobj1[key], JSONobj2[key]) )
		return all(equalList)
						
					
	elif isinstance(JSONobj1, list) and isinstance(JSONobj2, list):
		equalList = []
		for i, value in enumerate(JSONobj1):
			if i < len(JSONobj2):
					equalList.append( objEqual(JSONobj1[i], JSONobj2[i]) )

		return all(equalList)
	
	elif JSONobj1 == JSONobj2:
		return True

	else:
		return False








def convertDsToJsonObj(dataset):

	ret = []

	pyData = system.dataset.toPyDataSet(dataset)
	keys = map(str,pyData.getColumnNames())
	
	for row in pyData:
	
		dictRow = {k:v for (k,v) in zip(keys,row)}
		ret.append(dictRow)
		
	return ret







		

		

