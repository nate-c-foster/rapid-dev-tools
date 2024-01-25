"""Generate function definitions

This script is where tag generator functions are defined for the Functional Tag Editor.
Every function must return a list of tags where a tag is a dict with keys {'tagPath':str, 'tagType':str, 'tagConfig':str}.
For efficiency reasons 'tagConfig' will be empty string until a transformation is performed.
See below for examples.

Todo:
	* Generate all alarm tags under a given root tag path
	* Generate all historized tags under a given root tag path

"""



#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Jan 2023
#*****************************************************************************************************		
def getTags(rootTagPath, recursive=False):
	"""Generate all tags (atomic and udt instances) under a given root tag path.
	
	Args:
		rootTagPath (str): Root tag path.
		
	Returns:
		List of tags where a tag is a dict with keys {'tagPath':str, 'tagType':str, 'tagConfig':str}
	"""
	
	tags = []
	results = system.tag.browse(rootTagPath, {'recursive':recursive})
	
	# include the root tag
	tagType = str(system.tag.readBlocking(rootTagPath + '.tagType')[0].value)
	if tagType == 'UdtInstance' or tagType == 'UdtInstance':
		tags.append({'tagPath':rootTagPath, 'tagType':tagType, 'tagConfig':""})
	
	for result in results:
		tagType = str(result['tagType'])
		if tagType == 'AtomicTag' or tagType == 'UdtInstance':
			tagPath = str(result['fullPath'])
			tags.append({'tagPath':tagPath, 'tagType':tagType, 'tagConfig':""})
			
	return tags
	
	



#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Jan 2023
#*****************************************************************************************************		
def getAtomicTags(rootTagPath, recursive=False):
	"""Generate all atom tags under a given root tag path.
	
	Args:
		rootTagPath (str): Root tag path.
		
	Returns:
		List of tags where a tag is a dict with keys {'tagPath':str, 'tagType':str, 'tagConfig':str}
	"""
	
	tags = []
	results = system.tag.browse(rootTagPath, {'recursive':recursive, 'tagType': 'AtomicTag'})
	
	# include root tag
	tagType = str(system.tag.readBlocking(rootTagPath + '.tagType')[0].value)
	if tagType == 'AtomicTag':
		tags.append({'tagPath':rootTagPath, 'tagType':tagType, 'tagConfig':""})
	
	for result in results:
		tagType = str(result['tagType'])
		tagPath = str(result['fullPath'])
		if tagType == 'AtomicTag':
			tags.append({'tagPath':tagPath, 'tagType':tagType, 'tagConfig':""})
			
	return tags
	
	
	
	
	
#*****************************************************************************************************
# Author:         Nate Foster
# Company:        A.W. Schultz
# Date:           Jan 2023
#*****************************************************************************************************		
def getUdtTags(rootTagPath, typeId = "", recursive=False):
	"""Generate all udt instances under a given root tag path.
	
	Args:
		rootTagPath (str): Root tag path.
		typeID (str): UDT type id filter.
		
	Returns:
		List of tags where a tag is a dict with keys {'tagPath':str, 'tagType':str, 'tagConfig':str}      
	"""

	tags = []
	
	try:
	
	
		results = system.tag.browse(rootTagPath, {'recursive':recursive, 'tagType': 'UdtInstance'})
		
#		if rootTagPath:
#			if typeId:
#				results = system.tag.browse(rootTagPath, {'recursive':True, 'tagType': 'UdtInstance', 'typeId':typeId})
#			else:
#				results = system.tag.browse(rootTagPath, {'recursive':True, 'tagType': 'UdtInstance'})
#		else:
#			return []
		
		# include root tag
		tagType = str(system.tag.readBlocking(rootTagPath + '.tagType')[0].value)
		if tagType == 'UdtInstance':	
			if not typeId or typeId in str(result['typeId']):
				tags.append({'tagPath':rootTagPath, 'tagType':tagType, 'tagConfig':""})

		
		for result in results:
			tagType = str(result['tagType'])
			tagPath = str(result['fullPath'])
			if tagType == 'UdtInstance':
				if not typeId or typeId in str(result['typeId']):
					tags.append({'tagPath':tagPath, 'tagType':tagType, 'tagConfig':""})
				
	except:
		print 'Error: getUdtTags()'
			
			
	return tags
	
	
	


	
	
	