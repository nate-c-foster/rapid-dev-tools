import com.inductiveautomation.ignition.common.tags.config.model.TagReferenceQuery as TagReferenceQuery
from com.inductiveautomation.ignition.common.tags.paths import BasicTagPath


def getSubscriptions():

	context = system.util.getContext()
	
	print 'Context: ', context
	
	tagProvider = context.getTagManager().getTagProvider('SCADA')
	print 'TagProvider: ', tagProvider
	
	
	tagPath = BasicTagPath('SCADA', ['Ventura','Booster Stations','American Oaks Booster', 'Flow', 'Control', 'DeviceStatus', 'Output'])
	
	print 'TagPath: ', str(tagPath)
	tagReferenceQuery = TagReferenceQuery(tagPath, False, 0)
	
	references = tagProvider.getTagReferences(tagReferenceQuery).get()
	
	for reference in references:
		locations = reference.getReferencePath().getLocations()
		for location in locations:
			projectResourceId = location.getProjectResourceId()
			properties = location.getReferenceMap()
			resourcePath = projectResourceId.getResourcePath()
			projectName = projectResourceId.getProjectName()
			
			print projectName
			print resourcePath
			print properties.keySet()
			
			print properties.get('component')
			print properties.get('component-id')
			print properties.get('function')
			print properties.get('property')
	
