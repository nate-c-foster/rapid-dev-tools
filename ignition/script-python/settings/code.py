








def getValue(category, setting):
	"""Get a setting value.
	
	Args:
		category (str): The setting category. Same name as category folder in RapidDev.
		setting (str): The setting name.
		
	Returns:
		The setting value.     
	"""
	
	tagProvider = getTagProvider()
	return system.tag.readBlocking(tagProvider + 'RapidDev/' + category + '/Settings/' + setting)[0].value
	
	
def getPath(category, setting):
	"""Get the tag path for a setting.
	
	Args:
		category (str): The setting category. Same name as category folder in RapidDev.
		setting (str): The setting name.
		
	Returns:
		The setting tag path.     
	"""
	
	tagProvider = getTagProvider()
	return tagProvider + 'RapidDev/' + category + '/Settings/' + setting
	
	
	
	
def getTagProvider():
	"""Get the tag provider where RapidDev folder is located.
	
	Args:

		
	Returns:
		The tag provider.     
	"""
	providers = system.tag.browse('')
	for provider in providers:
		tagProvider = provider['fullPath']
		if system.tag.exists(str(tagProvider) + 'RapidDev'):
			return str(tagProvider)
			
	print 'RapidDev folder not found'
	return '[default]'