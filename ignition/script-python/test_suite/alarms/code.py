import com.inductiveautomation.ignition.common.model.values.QualityCode as QualityCode




#commissioningReportPath = 'C:/VM Shared Drive/Ventura/Ventura/TestReports/TagReport/Commissioning_Alarm_Report.xlsx'
#
#alarmTagReport = test_suite.alarms.alarmTagReport(rootTagPath)
#alarmTagFormatDS = test_suite.alarms.alarmTagAnalysis(alarmTagReport)
#
#
#sheetsData = [	{'dataset':alarmTagReport, 'formatDataset': alarmTagFormatDS, 'sheetName': 'Alarm Tag Report'}
#]
#
#dataset_editor.export.toExcelWithFormating(sheetsData, commissioningReportPath)






def alarmCoverageReport(existingAlarmsDS, rootTagPath):
	pass
	
	
def alarmCoverageAnalysis(reportDS):
	pass




















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
			
			alarmValueSource, alarmValueProperty, alarmValueQuality, alarmValue = test_suite.util.getTagProperties(alarmPath+'/Alarm')
			alarmPriority = system.tag.readBlocking(alarmPath+'/Alarm/Alarms/Alarm.Priority')[0].value
			alarmPipeline = system.tag.readBlocking(alarmPath+'/Alarm/Alarms/Alarm.ActivePipeline')[0].value
			alarmLabel = system.tag.readBlocking(alarmPath+'/Alarm/Alarms/Alarm.Label')[0].value
			alarmNotes = system.tag.readBlocking(alarmPath+'/Alarm/Alarms/Alarm.Notes')[0].value
			enableValueSource, enabledValueProperty, enableValueQuality, enableValue = test_suite.util.getTagProperties(alarmPath+'/Enable')
			if enableValueQuality == QualityCode.Bad_Disabled:
				enableValueSource = ''
				enabledValueProperty = ''
				enableValue = ''
			
			setpointValueSource, setpointValueProperty, setpointValueQuality, setpointValue = test_suite.util.getTagProperties(alarmPath+'/Setpoint')
			if setpointValueQuality == QualityCode.Bad_Disabled:
				setpointValueSource = ''
				setpointValueProperty = ''
				setpointValue = ''
			
			delayValueSource, delayValueProperty, delayValueQuality, delayValue = test_suite.util.getTagProperties(alarmPath+'/Delay')
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
			
		if row['EnableValueQuality'] == 'Good':
			format['EnableValueQuality'] = 'Good'
		elif row['EnableValueQuality'] == 'Bad_Disabled':
			format['EnableValueQuality'] = 'Normal'
		else:
			format['EnableValueQuality'] = 'Bad'

		if row['SetpointValueQuality'] == 'Good':
			format['SetpointValueQuality'] = 'Good'
		elif row['SetpointValueQuality'] == 'Bad_Disabled':
			format['SetpointValueQuality'] = 'Normal'
		else:
			format['SetpointValueQuality'] = 'Bad'
			
		if row['DelayValueQuality'] == 'Good':
			format['DelayValueQuality'] = 'Good'
		elif row['DelayValueQuality'] == 'Bad_Disabled':
			format['DelayValueQuality'] = 'Normal'
		else:
			format['DelayValueQuality'] = 'Bad'

			
		return format



	formatDataset = dataset_editor.operation.formatDataset(reportDS, conditional=checkAlarmQuality, formatDataset=None)
	
	
	return formatDataset