"""Generate function definitions

This script is where tag generator functions are defined for the Functional Tag Editor.
Every function must return a list of tags where a tag is a dict with keys {'tagPath':str, 'tagType':str, 'tagConfig':str}.
For efficiency reasons 'tagConfig' will be empty string until a transformation is performed.
See below for examples.

Todo:
	* Generate all alarm tags under a given root tag path
	* Generate all historized tags under a given root tag path

"""


registeredFunctions = [	
{
	'name':"UDT instances",
	'description':"Generate all UDT instances under a root tag path",
	'functionPath':"tageditor.generate.getUdtTags",
	'kwargs':{"rootTagPath":"","typeId":"","recursive":"", "inheritance":""},
	'dockPaths':{"rootTagPath":"Global Components/Functions/Docks/Tag Path Selector"},
	'dropdownPaths':{"typeId": "Global Components/Functions/Dropdowns/UDT Type Id","recursive":"Global Components/Functions/Dropdowns/Boolean Value","inheritance":"Global Components/Functions/Dropdowns/Boolean Value"},
	'order':1,
	'kwargsOrder':{u'recursive': 3, u'typeId': 2, u'rootTagPath': 1, "inheritance":4}
	},
	{
	'name':"Atomic Tags",
	'description':"Generate all atomic tags under a root tag path",
	'functionPath':"tageditor.generate.getAtomicTags",
	'kwargs':{"rootTagPath":"","recursive":""},
	'dockPaths':{"rootTagPath":"Global Components/Functions/Docks/Tag Path Selector"},
	'dropdownPaths':{"recursive":"Global Components/Functions/Dropdowns/Boolean Value"},
	'order':2,
	'kwargsOrder':{u'recursive': 2, u'rootTagPath': 1}
	},
	{
	'name':"All Tags",
	'description':"Generate all tags (atomic and udt instances) under a root tag path",
	'functionPath':"tageditor.generate.getTags",
	'kwargs':{"rootTagPath":"","recursive":""},
	'dockPaths':{"rootTagPath":"Global Components/Functions/Docks/Tag Path Selector"},
	'dropdownPaths':{"recursive":"Global Components/Functions/Dropdowns/Boolean Value"},
	'order':3,
	'kwargsOrder':{u'recursive': 2, u'rootTagPath': 1}
	}
]



#*****************************************************************************************************
# Author:         Nate Foster
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
# Date:           Jan 2023
#*****************************************************************************************************		
def getUdtTags(rootTagPath, typeId = "", recursive=False, inheritance=False):
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
		
		
		# include root tag
		tagType = str(system.tag.readBlocking(rootTagPath + '.tagType')[0].value)
		if tagType == 'UdtInstance':	
			if not typeId or typeId in str(result['typeId']):
				tags.append({'tagPath':rootTagPath, 'tagType':tagType, 'tagConfig':""})

		
		for result in results:
			tagType = str(result['tagType'])
			tagPath = str(result['fullPath'])
			if tagType == 'UdtInstance':
				if inheritance:
					if typeId in tageditor.util.getType(tagPath) or typeId in tageditor.util.getParentType(tagPath):
						tags.append({'tagPath':tagPath, 'tagType':tagType, 'tagConfig':""})
				else:
					if not typeId or typeId in str(result['typeId']):
						tags.append({'tagPath':tagPath, 'tagType':tagType, 'tagConfig':""})
				
	except:
		print 'Error: getUdtTags()'
			
			
	return tags
	
	
	


	
	
	