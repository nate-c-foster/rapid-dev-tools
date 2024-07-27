



def getAlarmReport(rootTagPath):
	"""Generates an alarm tag report based on the 'Components/Alarm' UDT
	
	Args:
		rootTagPath (str): Root tag path for the report
		
	Returns:
		CSV
	"""

	typeId = 'Components/Alarm'
	

	results = system.tag.browse(rootTagPath, {'recursive': True, 'tagType':'UdtInstance'})
	
	alarmTags = []
	for result in results:
		tagPath = str(result['fullPath'])
		if typeId in Tags.udt.getType(tagPath) or typeId in Tags.udt.getParentType(tagPath):
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
			setpointValueSource, setpointValueProperty, setpointValueQuality, setpointValue = test_suite.util.getTagProperties(alarmPath+'/Setpoint')
			delayValueSource, delayValueProperty, delayValueQuality, delayValue = test_suite.util.getTagProperties(alarmPath+'/Delay')
			
			data.append([	alarmPath,
							description,
							alarmValueSource,
							str(alarmValueProperty),
							str(alarmValueQuality),
							str(alarmValue),
							alarmPriority,
							alarmPipeline,
							alarmLabel,
							alarmNotes,
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