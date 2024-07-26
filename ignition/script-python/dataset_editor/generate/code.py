

import csv
import re
import os



def fromIgnitionCSV(filePath):

	csvString = system.file.readFileAsString(filePath)
	return system.dataset.fromCSV(csvString)



def fromStandardCSV(filePath):

	headers = []
	data = []
	with open(filePath) as csvfile:
		reader = csv.DictReader(csvfile)
		headers = reader.fieldnames
		for row in reader:
			data.append([row[key] for key in headers])
			
	return system.dataset.toDataSet(headers, data)


# unions multiple CSVs
def fromStandardCSVs(folderPath, addFileNameColumn=False):
	
	filePaths = [folderPath + '/' + fileName for fileName in os.listdir(folderPath) if fileName.endswith('.csv')]

	if filePaths > 0:
		ds = fromStandardCSV(filePaths[0])
		if addFileNameColumn:
			fileName = filePaths[0].split('/')[-1]
			fileName = fileName.split('.')[0]
			ds = system.dataset.addColumn(ds, 0, [fileName for row in range(ds.getRowCount())], 'FileName', str)

		for filePath in filePaths[1:]:
			dsRight = fromStandardCSV(filePath)
			if addFileNameColumn:
				fileName = filePath.split('/')[-1]
				fileName = fileName.split('.')[0]
				dsRight = system.dataset.addColumn(dsRight, 0, [fileName for row in range(dsRight.getRowCount())], 'FileName', str)
			
			ds = dataset_editor.operation.union(ds, dsRight)
			
	return ds

	
	
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
			
			alarmValueSource, alarmValueProperty, alarmValueQuality, alarmValue = dataset_editor.util.getTagProperties(alarmPath+'/Alarm')
			alarmPriority = system.tag.readBlocking(alarmPath+'/Alarm/Alarms/Alarm.Priority')[0].value
			alarmPipeline = system.tag.readBlocking(alarmPath+'/Alarm/Alarms/Alarm.ActivePipeline')[0].value
			alarmLabel = system.tag.readBlocking(alarmPath+'/Alarm/Alarms/Alarm.Label')[0].value
			alarmNotes = system.tag.readBlocking(alarmPath+'/Alarm/Alarms/Alarm.Notes')[0].value
			enableValueSource, enabledValueProperty, enableValueQuality, enableValue = dataset_editor.util.getTagProperties(alarmPath+'/Enable')
			setpointValueSource, setpointValueProperty, setpointValueQuality, setpointValue = dataset_editor.util.getTagProperties(alarmPath+'/Setpoint')
			delayValueSource, delayValueProperty, delayValueQuality, delayValue = dataset_editor.util.getTagProperties(alarmPath+'/Delay')
			
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
	
	




def parseIconicsForKepwareTags(reportFilePath):

	reportString = system.file.readFileAsString(reportFilePath)
	
	
	# --- kepware tags ---
	# tag:"\\10.5.206.26\Kepware.KEPServerEX.V6\C-JanssBooster.JanssBooster.Global.Pump_1.HOA_In_Auto"
	# tag:"\\10.5.206.26\Kepware.KEPServerEX.V6\C-JanssBooster.JanssBooster._System._FailedConnection"
	# tag:"\\10.5.206.26\Kepware.KEPServerEX.V6\C-Moorpark.Moorpark.UPS_BATT_LOW_ALM"

	headers = 	["IP", "Server", "Channel", "Device", "Tag Path"]
	data = []

	kepwareTagRegex = re.compile(r'\\\\([.\w]+)\\([.\w]+)\\([-_ #\w]+).([-_ #\w]+).([.-_ #\w]+)')
	tags = kepwareTagRegex.findall(reportString)
	
	for i, tag in enumerate(tags):
		ip = tag[0]
		server = tag[1]
		channel = tag[2]
		device = tag[3]
		tagPath = tag[4]
	
	
		# Kepware only, not BristolBabcock(different regex)
		if 'Kepware' in server and 'AlarmServer' not in server and  not tagPath.startswith('_System') and 'Simulator' not in server:
		
			# no repeats
			if [ip, server, channel, device, tagPath] not in data:
				data.append( [ip, server, channel, device, tagPath] )
	
	data = sorted(data, key=lambda x: (x[2], x[3], x[4]))
		
	return system.dataset.toDataSet(headers, data)







def generateCSV(tags):
	data = []
	header = ["IP", "Server", "Channel", "Device", "Tag Path"]
	
	for tag in tags:
		if 	'BristolBabcock' not in tag['server'] and 'AlarmServer' not in tag['server'] and  not tag['tagPath'].startswith('_System') and 'Simulator' not in tag['server']:
			if [tag['ip'], tag['server'], tag['channel'], tag['device'], tag['tagPath']] not in data:
				data.append( [tag['ip'], tag['server'], tag['channel'], tag['device'], tag['tagPath']] )
	
	sortedData = sorted(data, key=lambda x : (x[3], x[4]))

	return system.dataset.toCSV(system.dataset.toDataSet(header, sortedData))
