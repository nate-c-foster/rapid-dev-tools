import com.inductiveautomation.ignition.common.model.values.QualityCode as QualityCode




# ----------- run report  -----------------------------------------------------------

#iconicsToKepwarePath = 'C:/VM Shared Drive/Ventura/Ventura/TestReports/AlarmReport/alarmworx_to_kepware_filtered.csv'
#commissioningReportPath = 'C:/VM Shared Drive/Ventura/Ventura/TestReports/AlarmReport/Alarm_Report.xlsx'
#rootTagPath = '[SCADA]Ventura'
#
#existingAlarmDS = dataset.generate.fromStandardCSV(iconicsToKepwarePath)
#
## alarm coverage
#alarmCoverageReport = alarms.alarmCoverageReport(existingAlarmDS, rootTagPath)
#alarmCoverageFormatDS = alarms.alarmCoverageAnalysis(alarmCoverageReport)
#
## alarm tag report
#alarmTagReport = alarms.alarmTagReport(rootTagPath)
#alarmTagFormatDS = alarms.alarmTagAnalysis(alarmTagReport)
#
#
#
#sheetsData = [	{'dataset':alarmCoverageReport, 'formatDataset': alarmCoverageFormatDS, 'sheetName': 'Alarm Coverage Report'},
#				{'dataset':alarmTagReport, 'formatDataset': alarmTagFormatDS, 'sheetName': 'Alarm Tag Report'}
#
#]
#
#dataset.export.toExcelWithFormating(sheetsData, commissioningReportPath)






# ----------- update enables and delays to match alarmworx  -----------------------------------------------------------

#alarmworxToIgnitionPath = 'C:/VM Shared Drive/Ventura/Ventura/TestReports/AlarmReport/alarmworx_to_ignition.csv'
#rootTagPath = '[SCADA]Ventura'
#
#alarmworxToIgnitionDS = dataset.generate.fromStandardCSV(alarmworxToIgnitionPath)
#pyds = system.dataset.toPyDataSet(alarmworxToIgnitionDS)
#
#for row in pyds:
#	ignitionPath = row['IgnitionPath']
#
#	iconicsDelay = row['IconicsDelay']
#	iconicsEnabled = row['IconicsEnabled']
#		
#	if ignitionPath.endswith('/Alarm'):
#		udtPath = ignitionPath[:-len('/Alarm')]
#		enabledPath = udtPath + '/Enable'
#		delayPath = udtPath + '/Delay'
#		
#		if system.tag.exists(enabledPath) and system.tag.readBlocking(enabledPath + '.enabled')[0].value and system.tag.readBlocking(enabledPath + '.valueSource')[0].value == 'memory':
#			enabledValue = system.tag.readBlocking(enabledPath)[0].value
#
#
#			if bool(enabledValue) != bool(int(iconicsEnabled)):
#				print udtPath
#				#system.tag.writeBlocking(enabledPath, bool(int(iconicsEnabled)))
#
#
#		if system.tag.exists(delayPath) and system.tag.readBlocking(delayPath + '.enabled')[0].value and system.tag.readBlocking(delayPath + '.valueSource')[0].value == 'memory':
#			delayValue = system.tag.readBlocking(delayPath)[0].value
#
#			if delayValue and iconicsDelay and float(delayValue) != float(iconicsDelay):
#				print udtPath
#				print float(iconicsDelay)
#				#system.tag.writeBlocking(delayPath, float(iconicsDelay))






# -----------  delays  ------------------------------------------------


#rootPath = '[SCADA]Ventura'
#rootPath = '[SCADA]_types_/User Defined/GE Booth'
#rootPath = '[SCADA]_types_/User Defined/Ventura MicoLogix'

#results = system.tag.browse(rootPath, {'recursive':True, 'tagType':'UdtInstance', 'typeId':'Components/Alarm'})
#
#
#for result in results:
#	tagPath = str(result['fullPath'])
#	
#
#	
#	valueSource = system.tag.readBlocking(tagPath + '/Delay.valueSource')[0].value
#	enabled = system.tag.readBlocking(tagPath + '.enabled')[0].value
#	if enabled: # and valueSource == 'opc':
#	
#		delayValue = system.tag.readBlocking(tagPath + '/Alarm/Alarms/Alarm.TimeOnDelaySeconds')[0].value
#		delayConfig = system.tag.getConfiguration(tagPath + '/Alarm', False)
#		
#		#if not delay:
#		print tagPath
#		print delayValue
#		print delayConfig[0]['alarms'][0]['timeOnDelaySeconds']
	
	
		#delayConfig[0]['alarms'][0]['timeOnDelaySeconds'] = {'bindType':'Tag', 'value':'[.]Delay'}
	
		#system.tag.configure(tagPath, delayConfig[0], "o")
	
#		config = system.tag.getConfiguration(tagPath + '/Alarm', recursive=False)
#		if type(config[0]['alarms'][0]['timeOnDelaySeconds']) == float:
#			print tagPath






def alarmCoverageReport(existingAlarmsDS, rootTagPath):
	print 'Starting Alarm Coverage Report'
		
		
	opcPaths = {}
	results = system.tag.browse(rootTagPath, {'recursive':True, 'tagType':'AtomicTag', 'valueSource':'opc'})
	for result in results:
		ignitionPath = str(result['fullPath'])
		opcPath = system.tag.readBlocking(ignitionPath + '.opcItemPath')[0].value
		if opcPath:
			opcPaths[opcPath.lower()] = (opcPath, ignitionPath)
	
	opcKeys = opcPaths.keys()
	


	
	data = []
	pyds = system.dataset.toPyDataSet(existingAlarmsDS)
	for row in pyds:
		device = row['DeviceName']
		address = row['Address']
		
		if device and address:
			opcTestPath = 'ns=1;s=[' + device + ']' + address
			opcTestPathLower = opcTestPath.lower()
			if opcTestPathLower in opcKeys:
				opcPath = opcPaths[opcTestPathLower][0]
				ignitionPath = opcPaths[opcTestPathLower][1]
				
				if ignitionPath.endswith('/Alarm'):
					udtPath = ignitionPath[:-len('/Alarm')]
					descriptionPath = udtPath + '/Description'
					enabledPath = udtPath + '/Enable'
					delayPath = udtPath + '/Delay'
					
					if system.tag.readBlocking(descriptionPath + '.enabled')[0].value:
						description = str(system.tag.readBlocking(descriptionPath)[0].value)
					else:
						description = ''
						
					if system.tag.readBlocking(enabledPath + '.enabled')[0].value:
						enabled = str(system.tag.readBlocking(enabledPath)[0].value)
					else:
						enabled = ''
						
					if system.tag.readBlocking(delayPath + '.enabled')[0].value:
						delay = str(system.tag.readBlocking(delayPath)[0].value)
					else:
						delay = ''
				else:
					description = ''
					enabled = ''
					delay = ''
				
			else:
				opcPath = ''
				ignitionPath = ''
				description = ''
				enabled = ''
				delay = ''
				
		data.append(	list(row)[:-3] + 
						[opcPath, ignitionPath] +
						[row['Description'], description, row['Enabled'], enabled, row['Delay'], delay]
						)
		
	data = sorted(data, key=lambda x : (x[1],x[2]))
	
	headers = system.dataset.getColumnHeaders(existingAlarmsDS)
	headers = headers[:-3] + ['OpcPath', 'IgnitionPath'] + ['IconicsDescription', 'IgnitionDescription', 'IconicsEnabled','IgnitionEnabled','IconicsDelay','IgnitionDelay']
		
	return system.dataset.toDataSet(headers, data)


	
def alarmCoverageAnalysis(reportDS):
	print 'Starting Alarm Coverage Analysis'



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
			
		if row['IgnitionEnabled'] != '' and row['IgnitionEnabled'] != 'None' and bool(int(row['IconicsEnabled'])) != bool(row['IgnitionEnabled'] == 'True'):
			format['IconicsTagPath'] = 'Bad'
			format['IgnitionEnabled'] = 'Bad'
			
		if row['IgnitionDelay'] != '' and row['IgnitionDelay'] != 'None' and row['IconicsDelay'] != '' and row['IconicsDelay'] != 'None' and abs(float(row['IconicsDelay']) - float(row['IgnitionDelay'])) > 0.1:
			format['IconicsTagPath'] = 'Bad'
			format['IgnitionDelay'] = 'Bad'
			
			
			
		return format



	formatDataset = dataset.operation.formatDataset(reportDS, conditional=checkOpcExists, formatDataset=None)
	
	
	return formatDataset







def alarmTagReport(rootTagPath):
	"""Generates an alarm tag report based on the 'Components/Alarm' UDT
	
	Args:
		rootTagPath (str): Root tag path for the report
		
	Returns:
		CSV
	"""

	print 'Starting Alarm Report'

	typeId = 'Components/Alarm'
	

	results = system.tag.browse(rootTagPath, {'recursive': True, 'tagType':'UdtInstance'})
	
	alarmTags = []
	for result in results:
		tagPath = str(result['fullPath'])
		if typeId in tageditor.util.getType(tagPath) or typeId in tageditor.util.getParentType(tagPath):
			alarmTags.append(result)
			
	
	data = []
	for alarmTag in alarmTags:
		alarmPath =  str(alarmTag['fullPath'])
		
		if system.tag.readBlocking(alarmPath + '.enabled')[0].value and system.tag.readBlocking(alarmPath + '/Alarm.enabled')[0].value:
			
			
			description = system.tag.readBlocking(alarmPath + '/Description')[0].value
			
			alarmValueSource, alarmValueProperty, alarmValueQuality, alarmValue = util.getTagProperties(alarmPath+'/Alarm')
			alarmPriority = system.tag.readBlocking(alarmPath+'/Alarm/Alarms/Alarm.Priority')[0].value
			alarmPipeline = system.tag.readBlocking(alarmPath+'/Alarm/Alarms/Alarm.ActivePipeline')[0].value
			alarmLabel = system.tag.readBlocking(alarmPath+'/Alarm/Alarms/Alarm.Label')[0].value
			alarmNotes = system.tag.readBlocking(alarmPath+'/Alarm/Alarms/Alarm.Notes')[0].value
			enableValueSource, enabledValueProperty, enableValueQuality, enableValue = util.getTagProperties(alarmPath+'/Enable')
			if enableValueQuality == QualityCode.Bad_Disabled:
				enableValueSource = ''
				enabledValueProperty = ''
				enableValue = ''
			
			setpointValueSource, setpointValueProperty, setpointValueQuality, setpointValue = util.getTagProperties(alarmPath+'/Setpoint')
			if setpointValueQuality == QualityCode.Bad_Disabled:
				setpointValueSource = ''
				setpointValueProperty = ''
				setpointValue = ''
			
			delayValueSource, delayValueProperty, delayValueQuality, delayValue = util.getTagProperties(alarmPath+'/Delay')
			if delayValueQuality == QualityCode.Bad_Disabled:
				delayValueSource = ''
				delayValueProperty = ''
				delayValue = ''
			
			
			data.append([	alarmPath,
							description,
							alarmValueSource,
							str(alarmValueProperty),
							str(alarmValueQuality),
							str(alarmValue),
							str(alarmPriority),
							str(alarmPipeline),
							str(alarmLabel),
							str(alarmNotes),
							enableValueSource,
							str(enabledValueProperty),
							str(enableValueQuality),
							str(enableValue),
							setpointValueSource,
							str(setpointValueProperty),
							str(setpointValueQuality),
							str(setpointValue),
							delayValueSource,
							str(delayValueProperty),
							str(delayValueQuality),
							str(delayValue)
						])

						
	headers = [	'TagPath', 
				'Description',
				'AlarmValueSource', 
				'AlarmValueProperty',
				'AlarmValueQuality',
				'AlarmValue',
				'AlarmPriority',
				'AlarmPipeline',
				'AlarmLabel',
				'AlarmNotes',
				'EnableValueSource',
				'EnableValueProperty',
				'EnableValueQuality',
				'EnableValue',
				'SetpointValueSource',
				'SetpointValueProperty',
				'SetpointValueQuality',
				'SetpointValue',
				'DelayValueSource',
				'DelayValueProperty',
				'DelayValueQuality',
				'DelayValue'
				]



	return system.dataset.toDataSet(headers, data)
	
	
	
def alarmTagAnalysis(reportDS):
	print 'Starting Alarm Analysis'



	def checkAlarmQuality(row):
		format = {}
		
		if row['AlarmValueQuality'] == 'Good':
			format['AlarmValueQuality'] = 'Good'
		elif row['AlarmValueQuality'] == 'Bad_Disabled':
			format['AlarmValueQuality'] = 'Normal'
		else:
			format['AlarmValueQuality'] = 'Bad'
			format['TagPath'] = 'Bad'
			
		if row['EnableValueQuality'] == 'Good':
			format['EnableValueQuality'] = 'Good'
		elif row['EnableValueQuality'] == 'Bad_Disabled':
			format['EnableValueQuality'] = 'Normal'
		else:
			format['EnableValueQuality'] = 'Bad'
			format['TagPath'] = 'Bad'

		if row['SetpointValueQuality'] == 'Good':
			format['SetpointValueQuality'] = 'Good'
		elif row['SetpointValueQuality'] == 'Bad_Disabled':
			format['SetpointValueQuality'] = 'Normal'
		else:
			format['SetpointValueQuality'] = 'Bad'
			format['TagPath'] = 'Bad'
			
		if row['DelayValueQuality'] == 'Good':
			format['DelayValueQuality'] = 'Good'
		elif row['DelayValueQuality'] == 'Bad_Disabled':
			format['DelayValueQuality'] = 'Normal'
		else:
			format['DelayValueQuality'] = 'Bad'
			format['TagPath'] = 'Bad'

			
		return format



	formatDataset = dataset.operation.formatDataset(reportDS, conditional=checkAlarmQuality, formatDataset=None)
	
	
	return formatDataset