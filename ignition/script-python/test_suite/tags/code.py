

import com.inductiveautomation.ignition.common.model.values.QualityCode as QualityCode


def udtConfigReport(rootPath):
	# ?
	pass



def udtConfigAnalysis(reportDS):
	# ?
	pass






# ------------ UDT Instances Report --------------------------------------


def udtInstancesReport(rootTagPath):

	allParameterSet = set([])
	data = []

	udts = system.tag.browse(rootTagPath, {'recursive': True, 'tagType':'UdtInstance'})


	for udt in udts:
		tagPath = str(udt['fullPath'])
		tagConfig = tageditor.util.getTagConfigObj(tagPath)

		parentPath = '/'.join(tagPath.split('/')[:-1])
		parentOfParentPath = '/'.join(parentPath.split('/')[:-1])
		
		parentType = tageditor.util.getTagConfigObj(parentPath)['tagType']
		parentOfParentType = tageditor.util.getTagConfigObj(parentOfParentPath)['tagType']
		
		# ignore Udt composition
		if parentType != 'UdtInstance' and parentOfParentType != 'UdtInstance':

			parameters = {}
			if 'parameters' in tagConfig.keys():
				parameters = tagConfig['parameters']
				allParameterSet = allParameterSet.union(set(parameters.keys()))
				
				data.append([	tagPath,
								tageditor.util.getType(tagPath),
								tageditor.util.getParentType(tagPath),
								parameters
								])
								
	allParams = sorted(list(allParameterSet))
	
	headers = [	'TagPath',
				'TagType',
				'ParentType' ] + allParams
				
	# spread parameters
	updatedData = []
	for item in data:
		updatedData.append([item[0], item[1], item[2]] + [str(item[3][param]['value']) if param in item[3].keys() else '' for param in allParams])
		
	
	return system.dataset.toDataSet(headers, updatedData)
	


def udtInstancesAnalysis(reportDS):
	# check location id param
	# check opc path devices
	# check each AI has units
	pass










# ------------ Atomic Tag Report --------------------------------------



def atomicTagsReport(rootTagPath):

	results = system.tag.browse(rootTagPath, {'recursive': True, 'tagType':'AtomicTag'})
	
	data = []
	
	for result in results:
		quality = result['value'].quality
		if quality != QualityCode.Bad_Disabled:
		
			tagPath = str(result['fullPath'])
			dataType = result['dataType']
			attributes = result['attributes']
			
			if not '/General/' in tagPath and not '/Alarming/' in tagPath:

				valueSource, valueProperty, valueQuality, value = test_suite.util.getTagProperties(tagPath)
		
				data.append([	tagPath,
								str(dataType),
								str(attributes),
								str(valueSource),
								str(valueProperty),
								str(valueQuality),
								str(value)
								])
							
	headers = [	'TagPath',
				'DataType',
				'Attributes',
				'ValueSource',
				'ValueProperty',
				'ValueQuality',
				'Value'
				]
	
	return system.dataset.toDataSet(headers, data)
	
	
def atomicTagsAnalysis(reportDS):


	def checkQuality(row):
		if row['ValueQuality'] == 'Good':
			return {'ValueQuality':'Good'}
		else:
			return {'ValueQuality': 'Bad'}


	formatDataset = dataset_editor.operation.formatDataset(reportDS, conditional=checkQuality, formatDataset=None)
	
	
	return formatDataset


#filePath = 'C:/VM Shared Drive/Ventura/Ventura/TestReports/TagReport/test_atomic.xlsx'
#
#rootTagPath = '[SCADA]Ventura/Booster Stations/Dos Vientos Booster/Pump 1'
#reportDS = test_suite.tags.atomicTagsReport(rootTagPath)
#formatDS = test_suite.tags.atomicTagsAnalysis(reportDS)
#
#sheetsData = [{'dataset':reportDS, 'formatDataset':formatDS, 'sheetName':'AtomicTags'}]
#
#dataset_editor.export.toExcelWithFormating(sheetsData, filePath)









# ------------ Tag Coverate Report --------------------------------------


def tagConverageReport(existingTagsDS):

	pass

def tagCoverageAnalysis(reportDS):

	pass
