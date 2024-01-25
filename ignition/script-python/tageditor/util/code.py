#*****************************************************************************************************
#
# Author:         	Nate Foster
# Company:        	A.W. Schultz
# Date:           	March 2022		
# 
#  for the Rapid Tag Editor
#*****************************************************************************************************





# gets json string of tag config
# same as right clicking and copy JSON
# this will get replaced when Ignition adds this feature to scripting API


#def getTagConfigStr(tagPath):
#	return system.tag.exportTags(tagPaths = [tagPath])
	
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


	




#*****************************************************************************************************
#
# Author:         Nate Foster
# Company:        A.W. Schultz
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