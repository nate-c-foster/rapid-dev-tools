

import com.inductiveautomation.ignition.common.model.values.QualityCode as QualityCode
import java.text.DecimalFormat as DecimalFormat



#iconicsToKepwarePath = 'C:/VM Shared Drive/Ventura/Ventura/TestReports/TagReport/iconics_to_kepware_csv.csv'
#commissioningReportPath = 'C:/VM Shared Drive/Ventura/Ventura/TestReports/TagReport/Tag_Report.xlsx'
#rootTagPath = '[SCADA]Ventura'
#
#existingTagDS = dataset.generate.fromStandardCSV(iconicsToKepwarePath)
#
## tag coverage
#tagCoverageReport = testing.tags.tagConverageReport(existingTagDS, rootTagPath)
#tagCoverageFormatDS = testing.tags.tagCoverageAnalysis(tagCoverageReport)
#
## atomic tag report
#atomicTagReport = testing.tags.atomicTagsReport(rootTagPath)
#atomicTagFormatDS = testing.tags.atomicTagsAnalysis(atomicTagReport)
#
## udt instances
#udtInstancesReport = testing.tags.udtInstancesReport(rootTagPath)
#udtInstancesFormatDS = testing.tags.udtInstancesAnalysis(udtInstancesReport)
#
## analog input report
#analogInputReport = testing.tags.analogInputReport(rootTagPath)
#analogInputFormatDS = testing.tags.analogInputAnalysis(analogInputReport)
#
#
#
#
#
#sheetsData = [	{'dataset':tagCoverageReport, 'formatDataset': tagCoverageFormatDS, 'sheetName': 'Tag Coverage Report'},
#				{'dataset':atomicTagReport, 'formatDataset': atomicTagFormatDS, 'sheetName': 'Atomic Tag Report'},
#				{'dataset':udtInstancesReport, 'formatDataset': udtInstancesFormatDS, 'sheetName': 'UDT Instances Report'},
#				{'dataset':analogInputReport, 'formatDataset': analogInputFormatDS, 'sheetName': 'Analog Input Report'}
#]
#
#dataset.export.toExcelWithFormating(sheetsData, commissioningReportPath)





# ------------ Tag Coverate Report --------------------------------------


# existingTagDS must have columns 'DeviceName', 'Address'
def tagConverageReport(existingTagDS, rootTagPath):
	print 'Starting Coverage Report'
	
	
	opcPaths = {}
	results = system.tag.browse(rootTagPath, {'recursive':True, 'tagType':'AtomicTag', 'valueSource':'opc'})
	for result in results:
		ignitionPath = str(result['fullPath'])
		opcPath = system.tag.readBlocking(ignitionPath + '.opcItemPath')[0].value
		if opcPath:
			opcPaths[opcPath.lower()] = (opcPath, ignitionPath)
	
	opcKeys = opcPaths.keys()
	

	headers = system.dataset.getColumnHeaders(existingTagDS)
	headers = headers + ['OpcPath', 'IgnitionPath']
	
	data = []
	pyds = system.dataset.toPyDataSet(existingTagDS)
	for row in pyds:
		device = row['DeviceName']
		address = row['Address']
		
		if device and address:
			opcTestPath = 'ns=1;s=[' + device + ']' + address
			opcTestPathLower = opcTestPath.lower()
			if opcTestPathLower in opcKeys:
				opcPath = opcPaths[opcTestPathLower][0]
				ignitionPath = opcPaths[opcTestPathLower][1]
			else:
				opcPath = ''
				ignitionPath = ''
				
		data.append(list(row) + [opcPath, ignitionPath])
		
		
	return system.dataset.toDataSet(headers, data)
	
	
	
	

def tagCoverageAnalysis(reportDS):
	print 'Starting Coverage Analysis'


	def checkOpcExists(row):
		format = {}
		ignitionPath = row['IgnitionPath']
		if ignitionPath:
			enabled = system.tag.readBlocking(ignitionPath + '.enabled')[0].value
		else:
			enabled = False
		if row['OpcPath'] and row['IgnitionPath'] and enabled:
			format['OpcPath'] = 'Good' 
			format['IgnitionPath'] = 'Good'
		else:
			format['OpcPath'] = 'Bad' 
			format['IgnitionPath'] = 'Bad'
			format['IconicsTagPath'] = 'Bad'
			
		return format

	formatDataset = dataset.operation.formatDataset(reportDS, conditional=checkOpcExists, formatDataset=None)
	
	
	return formatDataset







# ------------ UDT Instances Report --------------------------------------


def udtInstancesReport(rootTagPath):
	print 'Starting UDT Instances Report'

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
	print 'Starting UDT Instances Analysis'


	def checkParams(row):
		tagPath = row['TagPath']
		
		
		format = {}
		
		# check location name
		if system.tag.exists(tagPath + '/Parameters.locationName'):
		
			locationName = tageditor.util.getLocationName(tagPath)
			
			if row['locationName'] and row['locationName'] == locationName:
				format['locationName'] = 'Good'
			else:
				format['locationName'] =  'Bad'
				format['TagPath'] = 'Bad'
				
		else:
			format['locationName'] = 'Normal'
			
			
		# check units
		if 'AnalogInput' in tageditor.util.getType(tagPath) or 'AnalogInput' in tageditor.util.getParentType(tagPath):
			if row['output1Units']:
				format['output1Units'] = 'Good'
			else:
				format['output1Units'] = 'Bad'
				format['TagPath'] = 'Bad'
				
		
		
		# check for opc repeats (copy/paste error)
		opcParams = filter(lambda x : x.startswith('opc'), system.dataset.getColumnHeaders(reportDS))
		for opcParam in opcParams:
			opcParamValue = row[opcParam]
			if opcParamValue and opcParamValue.split(']')[-1]:
				matches = 0
				for rowIndex in range(reportDS.getRowCount()):
					if str(reportDS.getValueAt(rowIndex, opcParam)) == opcParamValue:
						matches = matches + 1
						
				if matches > 1:
					format[opcParam] = 'Bad'
					format['TagPath'] = 'Bad'
				
				
		return format
		

	formatDataset = dataset.operation.formatDataset(reportDS, conditional=checkParams, formatDataset=None)
	
	return formatDataset
	
	
	






def analogInputReport(rootTagPath):
	print 'Starting Analog Input Report'


	metaTags = [	{'name': 'Location', 'path':'/General/LocationName'},
					{'name': 'Component', 'path':'/General/CommonName'},
					{'name': 'Units', 'path':'/Parameters.output1Units'},
					{'name': 'FormatString', 'path':'/Parameters.output1FormatString'}]
	atomicTags = [ 	
					{'name': 'EU Max', 'path':'/Engineering/EUMax'},
					{'name': 'Display Max', 'path':'/Engineering/DisplayMax'},
					{'name': 'HiHi SP', 'path':'/Alarming/HighHigh/Setpoint'},
					{'name': 'Hi SP', 'path':'/Alarming/High/Setpoint'},
					{'name': 'Desired Hi', 'path':'/Engineering/DesiredHigh'},
					{'name': 'Desired Lo', 'path':'/Engineering/DesiredLow'},
					{'name': 'Lo SP', 'path':'/Alarming/Low/Setpoint'},
					{'name': 'LoLo SP', 'path':'/Alarming/LowLow/Setpoint'},
					{'name': 'Display Min', 'path':'/Engineering/DisplayMin'},
					{'name': 'EU Min', 'path':'/Engineering/EUMin'}
					]


	meta2Tags = [	
					{'name': 'Units 2', 'path':'/Parameters.output2Units'},
					{'name': 'FormatString 2', 'path':'/Parameters.output2FormatString'}]
	atomic2Tags = [ 	
					{'name': 'EU Max 2', 'path':'/Engineering/EUMax2'},
					{'name': 'Display Max 2', 'path':'/Engineering/DisplayMax2'},
					{'name': 'HiHi SP 2', 'path':'/Alarming/HighHigh2/Setpoint'},
					{'name': 'Hi SP 2', 'path':'/Alarming/High2/Setpoint'},
					{'name': 'Desired Hi 2', 'path':'/Engineering/DesiredHigh2'},
					{'name': 'Desired Lo 2', 'path':'/Engineering/DesiredLow2'},
					{'name': 'Lo SP 2', 'path':'/Alarming/Low2/Setpoint'},
					{'name': 'LoLo SP 2', 'path':'/Alarming/LowLow2/Setpoint'},
					{'name': 'Display Min 2', 'path':'/Engineering/DisplayMin2'},
					{'name': 'EU Min 2', 'path':'/Engineering/EUMin2'}
					]
	

	udts = system.tag.browse(rootTagPath, {	'recursive':True,
											'tagType':'UdtInstance'})
	
	rows = []
	for udt in udts:
		udtPath = str(udt['fullPath'])

		if 'AnalogInput' in tageditor.util.getType(udtPath) or 'AnalogInput' in tageditor.util.getParentType(udtPath):
			row = [udtPath]
			
			for metaTag in metaTags:
				tagPath = str(udt['fullPath']) + metaTag['path']
				value = system.tag.readBlocking(tagPath)[0].value
				row.append(value)
			
			
			for atomicTag in atomicTags:
				tagPath = str(udt['fullPath']) + atomicTag['path']
				
				if system.tag.readBlocking(tagPath + '.enabled')[0].value:
				
					formatString = system.tag.readBlocking(tagPath + '.formatString')[0].value
					df = DecimalFormat(formatString)
					
					value = system.tag.readBlocking(tagPath)[0].value
					valueString = df.format(value)  if isinstance(value,float) else str(value)
					
				else:
					valueString = ''

				row.append(valueString)
				
				
			for metaTag in meta2Tags:
				tagPath = str(udt['fullPath']) + metaTag['path']
				value = system.tag.readBlocking(tagPath)[0].value
				row.append(value)
			
			
			for atomicTag in atomic2Tags:
				tagPath = str(udt['fullPath']) + atomicTag['path']
				
				if system.tag.readBlocking(tagPath + '.enabled')[0].value:
				
					formatString = system.tag.readBlocking(tagPath + '.formatString')[0].value
					df = DecimalFormat(formatString)
					
					value = system.tag.readBlocking(tagPath)[0].value
					valueString = df.format(value)  if isinstance(value,float) else str(value)
					
				else:
					valueString = ''

				row.append(valueString)

			rows.append(row)

		
	headers = ['TagPath'] + [x['name'] for x in metaTags] + [x['name'] for x in atomicTags] + [x['name'] for x in meta2Tags] + [x['name'] for x in atomic2Tags]
	return system.dataset.toDataSet(headers, rows)
	
	
	
def analogInputAnalysis(reportDS):
	print 'Starting Analog Input Analysis'


	atomicTags = [ 	
					{'name': 'EU Max', 'path':'/Engineering/EUMax'},
					{'name': 'Display Max', 'path':'/Engineering/DisplayMax'},
					{'name': 'HiHi SP', 'path':'/Alarming/HighHigh/Setpoint'},
					{'name': 'Hi SP', 'path':'/Alarming/High/Setpoint'},
					{'name': 'Desired Hi', 'path':'/Engineering/DesiredHigh'},
					{'name': 'Desired Lo', 'path':'/Engineering/DesiredLow'},
					{'name': 'Lo SP', 'path':'/Alarming/Low/Setpoint'},
					{'name': 'LoLo SP', 'path':'/Alarming/LowLow/Setpoint'},
					{'name': 'Display Min', 'path':'/Engineering/DisplayMin'},
					{'name': 'EU Min', 'path':'/Engineering/EUMin'}
					]


	atomic2Tags = [ 	
					{'name': 'EU Max 2', 'path':'/Engineering/EUMax2'},
					{'name': 'Display Max 2', 'path':'/Engineering/DisplayMax2'},
					{'name': 'HiHi SP 2', 'path':'/Alarming/HighHigh2/Setpoint'},
					{'name': 'Hi SP 2', 'path':'/Alarming/High2/Setpoint'},
					{'name': 'Desired Hi 2', 'path':'/Engineering/DesiredHigh2'},
					{'name': 'Desired Lo 2', 'path':'/Engineering/DesiredLow2'},
					{'name': 'Lo SP 2', 'path':'/Alarming/Low2/Setpoint'},
					{'name': 'LoLo SP 2', 'path':'/Alarming/LowLow2/Setpoint'},
					{'name': 'Display Min 2', 'path':'/Engineering/DisplayMin2'},
					{'name': 'EU Min 2', 'path':'/Engineering/EUMin2'}
					]
					
					

	def checkValueSource(row):
		format = {}
		for atomicTag in (atomicTags + atomic2Tags):
			tagPath = row['TagPath'] + atomicTag['path']
			valueSource = system.tag.readBlocking(tagPath + '.valueSource')[0].value
			enabled = system.tag.readBlocking(tagPath + '.enabled')[0].value
			quality = system.tag.readBlocking(tagPath + '.quality')[0].value
			
			if enabled:
				if quality == QualityCode.Good:
					if valueSource == 'opc':
						format[atomicTag['name']] = 'OPC'
					elif valueSource == 'memory':
						format[atomicTag['name']] = 'Memory'
					else:
						format[atomicTag['name']] = 'Memory'
				else:
					format[atomicTag['name']] = 'Bad'
			else:
				format[atomicTag['name']] = 'Normal'
		
		return format



	formatDataset = dataset.operation.formatDataset(reportDS, conditional=checkValueSource, formatDataset=None)
	
	
	return formatDataset








# ------------ Atomic Tag Report --------------------------------------



def atomicTagsReport(rootTagPath):
	print 'Starting Atomic Tag Report'

	results = system.tag.browse(rootTagPath, {'recursive': True, 'tagType':'AtomicTag'})
	
	data = []
	
	for result in results:
		quality = result['value'].quality
		if quality != QualityCode.Bad_Disabled:
		
			tagPath = str(result['fullPath'])
			dataType = result['dataType']
			attributes = result['attributes']
			
			if not '/General/' in tagPath and not '/Alarming/' in tagPath:

				valueSource, valueProperty, valueQuality, value = testing.util.getTagProperties(tagPath)
		
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
	print 'Starting Atomic Tag Analysis'


	def checkQuality(row):
		if row['ValueQuality'] == 'Good':
			return {'ValueQuality':'Good'}
		else:
			return {'TagPath': 'Bad', 'ValueQuality': 'Bad'}


	formatDataset = dataset.operation.formatDataset(reportDS, conditional=checkQuality, formatDataset=None)
	
	
	return formatDataset










































