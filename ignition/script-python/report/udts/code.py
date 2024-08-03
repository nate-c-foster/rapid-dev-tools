import com.inductiveautomation.ignition.common.config.BoundValue as BoundValue


#udtReportPath = 'C:/VM Shared Drive/Ventura/Ventura/TestReports/UdtReport/Commissioning_UDT_Report.xlsx'
#
#folderPaths = [	'[SCADA]_types_/User Defined/GE Booth',
#				'[SCADA]_types_/User Defined/Ventura MicoLogix/Moorpark',
#				'[SCADA]_types_/User Defined/Ventura MicoLogix/Piru',
#				'[SCADA]_types_/User Defined/Ventura MicoLogix/Twenty Oaks',
#				'[SCADA]_types_/User Defined/Ventura MicoLogix/Warrick PRV'
#				]
#
#
#udtTypesReport = report.udts.udtTypesReport(folderPaths)
#udtConfigReport = report.udts.udtConfigReport(folderPaths)
#
#sheetsData = [	{'dataset':udtTypesReport, 'formatDataset': None, 'sheetName': 'UDT Types Report'},
#				{'dataset':udtConfigReport, 'formatDataset': None, 'sheetName': 'UDT Configs Report'}
#]
#
#dataset.export.toExcelWithFormating(sheetsData, udtReportPath)





def udtTypesReport(folderPaths):

	udts = []
	for folderPath in folderPaths:
		results = system.tag.browse(folderPath, {'recursive':False, 'tagType':'UdtType'})
		udts = udts + list(results)
		
	
	data = []
	for udt in udts:
		rootPath = str(udt['fullPath'])
		typeId = udt['typeId']
		udtName = udt['name']
		documentation = system.tag.readBlocking(rootPath + '.documentation')[0].value
		
		if rootPath.startswith('[SCADA]_types_/User Defined/'):
			udtSubPath = rootPath[len('[SCADA]_types_/User Defined/'):]
		elif rootPath.startswith('[SCADA]_types_/'):
			udtSubPath = rootPath[len('[SCADA]_types_/'):]
		else:
			udtSubPath = rootPath
			
		
	
		data.append([	str(typeId) if typeId else '',
						udtSubPath,
						documentation
						])
								
	
	headers = 	[	'ParentType',
					'UdtType',
					'Description'
					]
	
	data = sorted(data, key=lambda x : (x[0]=='', x[0], x[1]))
	return system.dataset.toDataSet(headers, data)

def udtTypesAnalysis(reportDS):
	# ?
	pass








def udtConfigReport(folderPaths):

	udts = []
	for folderPath in folderPaths:
		results = system.tag.browse(folderPath, {'recursive':False, 'tagType':'UdtType'})
		udts = udts + list(results)
		
	
	data = []
	for udt in udts:
		rootPath = str(udt['fullPath'])
		typeId = udt['typeId']
		udtName = udt['name']
		
		if rootPath.startswith('[SCADA]_types_/User Defined/'):
			udtSubPath = rootPath[len('[SCADA]_types_/User Defined/'):]
		elif rootPath.startswith('[SCADA]_types_/'):
			udtSubPath = rootPath[len('[SCADA]_types_/'):]
		else:
			udtSubPath = rootPath
			
		
		tags = system.tag.browse(rootPath, {'recursive':True, 'tagType':'AtomicTag'})
		for tag in tags:
			tagPath = str(tag['fullPath'])
			if system.tag.readBlocking(tagPath + '.enabled')[0].value:
				tagSubPath = tagPath[len(rootPath)+1:]
				
				valueSource, dataType, valueProperty = report.udts.getTagProperties(tagPath)
	
				data.append([	str(typeId) if typeId else '',
								udtSubPath,
								tagSubPath,
								str(dataType),
								valueSource,
								str(valueProperty)
								])
								
	
	headers = 	[	'ParentType',
					'UdtType',
					'TagPath',
					'DataType',
					'ValueSource',
					'ValueProperty'
					]
	
	data = sorted(data, key=lambda x : (x[0]=='', x[0], x[1], x[2]))
	return system.dataset.toDataSet(headers, data)

def udtConfigAnalysis(reportDS):
	# ?
	pass
	
	



	
def getTagProperties(tagPath):

	valueSource = system.tag.readBlocking(tagPath +'.valueSource')[0].value
	dataType = system.tag.readBlocking(tagPath + '.dataType')[0].value
	tagConfig = system.tag.getConfiguration(tagPath, recursive=True)[0]
	
	if valueSource == 'opc':
		if 'opcItemPath' in tagConfig.keys() and type(tagConfig['opcItemPath']) == BoundValue:
			valueProperty =  str(tagConfig['opcItemPath'].getBinding())
		else:
			valueProperty = system.tag.readBlocking(tagPath + '.opcItemPath')[0].value
	elif valueSource == 'memory':
		if 'value' in tagConfig.keys() and type(tagConfig['value']) == BoundValue:
			valueProperty =  str(tagConfig['value'].getBinding())
		elif 'value' in tagConfig.keys():
			valueProperty = tagConfig['value']
		else:
			valueProperty = ''
	elif valueSource == 'reference':
		if 'sourceTagPath' in tagConfig.keys() and type(tagConfig['sourceTagPath']) == BoundValue:
			valueProperty =  str(tagConfig['sourceTagPath'].getBinding())
		else:
			valueProperty = system.tag.readBlocking(tagPath + '.sourceTagPath')[0].value
	elif valueSource == 'derived':
		if 'sourceTagPath' in tagConfig.keys() and type(tagConfig['sourceTagPath']) == BoundValue:
			valueProperty =  str(tagConfig['sourceTagPath'].getBinding())
		else:
			valueProperty = system.tag.readBlocking(tagPath + '.sourceTagPath')[0].value
	elif valueSource == 'expression' or valueSource == 'expr':
		if 'expression' in tagConfig.keys() and type(tagConfig['expression']) == BoundValue:
			valueProperty =  str(tagConfig['expression'].getBinding())
		else:
			valueProperty = system.tag.readBlocking(tagPath + '.expression')[0].value
	else:
		valueProperty = 'BAD_VALUE_SOURCE'
		
	return (valueSource, dataType, valueProperty)