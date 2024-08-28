import re
import csv
import os
from StringIO import StringIO





def parseReportForTags(reportString):

	# --- any tag ---
	# tag:"..."
	tagRegex = re.compile(r'tag:"[-:<>_\\\.\w]+"')
	tags = tagRegex.findall(reportString)
	
	return tags
	
	
	
	
	
def parseReportForKepwareTags(reportString):
	

	# --- kepware tag pattern ---
	# tag:"\\10.5.206.26\Kepware.KEPServerEX.V6\C-JanssBooster.JanssBooster.Global.Pump_1.HOA_In_Auto"
	# tag:"\\10.5.206.26\Kepware.KEPServerEX.V6\C-JanssBooster.JanssBooster._System._FailedConnection"
	# tag:"\\10.5.206.26\Kepware.KEPServerEX.V6\C-Moorpark.Moorpark.UPS_BATT_LOW_ALM"
	kepwareRegex = re.compile(r'\\([.\w]+)\\([.\w]+)\\([-_ #\w]+).([-_ #\w]+).([.-_ #\w]+)')
	
	
	kepwareTags = []
	
	
	gdfNameRegex = re.compile(r'\\([-_ \w]+).gdf')
	gdfName = ''
	
	lines = reportString.splitlines()
	for line in lines:
	
		# update gdf file name
		result = gdfNameRegex.search(line)
		if result:
			gdfName = result.groups()[0]
	

		# find all kepware tags
		tags = kepwareRegex.findall(line)
		
		for i, tag in enumerate(tags):
		
			kepwareTags.append( {	
							'iconicsPage': gdfName,
							'ip':tag[0],
							'server':tag[1],
							'channel':tag[2],
							'device':tag[3],
							'tagPath':tag[4]
							})
			
	return kepwareTags





def parseAliasesForKepwareTags(aliasesString, filename):

	kepwareRegex = re.compile(r'\\\\([.\w]+)\\([.\w]+)\\([-_ #\w]+).([-_ #\w]+).([.-_ #\w]+)')
	#kepwareRegex = re.compile(r'(Ke)')
	
	paramRegex = re.compile(r'[\w]+\t')
	
	
	kepwareTags = []
	
	
	descRegex = re.compile(r'\$"([-_#\(\) \w]+)"\$')
	descName = ''
	
	lines = aliasesString.splitlines()
	for line in lines:
	
		# update gdf file name
		result = descRegex.search(line)
		if result:
			descName = result.groups()[0]

		# find all kepware tags
		tags = kepwareRegex.findall(line)
		
		for i, tag in enumerate(tags):
			
			param = line.split('\t')[0]
			
			if not descName:
				descName = filename
			
			kepwareTags.append( {	
							'iconicsPage': 'Aliases: ' + descName + '(' + param + ')',
							'ip':tag[0],
							'server':tag[1],
							'channel':tag[2],
							'device':tag[3],
							'tagPath':tag[4]
							})
			
	return kepwareTags






def generateCSV(tags):
	data = []
	header = ["IconicsPage", "IP", "Server", "Channel", "Device", "Tag Path"]
	
	for tag in tags:
		if 	'BristolBabcock' not in tag['server'] and 'AlarmServer' not in tag['server'] and  not tag['tagPath'].startswith('_System') and 'Simulator' not in tag['server']:
			if [tag['iconicsPage'], tag['ip'], tag['server'], tag['channel'], tag['device'], tag['tagPath']] not in data:
				data.append([tag['iconicsPage'], tag['ip'], tag['server'], tag['channel'], tag['device'], tag['tagPath']] )
	
	sortedData = sorted(data, key=lambda x : (x[0], x[3], x[4]))

	return system.dataset.toCSV(system.dataset.toDataSet(header, sortedData))
	
	
	




#iconicsReportPath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Development/iconics_report.txt' # iconic report of all dynamic tags for all displays
#aliasesFolderPath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Iconics Backup - 4-24-2024/Popups' # contains aliases text files
#kepwareExportsFolderPath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Iconics Backup - 4-24-2024/Kepware/Exports/' # contains kepware device csv exports
#devicesFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Development/devices.csv' # manually created with headers ['Name', KepwareChannel', 'KepwareDevice', 'Driver', 'Model', 'PLCType', 'IgnitionDriver', 'ID', 'IP', 'TagCount']
#plcTagsFolderPath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Alton PLC Programs/Tags/' # contains parsed L5X tags
#outputFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Development/iconics_kepware_plc.csv' # output file with all tag mappings
#
#conversion.iconics.generateTagMapping(iconicsReportPath, aliasesFolderPath, kepwareExportsFolderPath,devicesFilePath, plcTagsFolderPath, outputFilePath)



def generateTagMapping(iconicsReportPath, aliasesFolderPath, kepwareExportsFolderPath, devicesFilePath, plcTagsFolderPath, outputFilePath):
	
	# ------------------ parse iconics text report and aliases files --------------------------------------------------------

	tags = []
	
	reportString = system.file.readFileAsString(iconicsReportPath)
	tags = tags + conversion.iconics.parseReportForKepwareTags(reportString)
	
	if aliasesFolderPath:
		aliasesFilePaths = [aliasesFolderPath + '/' + fileName for fileName in os.listdir(aliasesFolderPath) if fileName.endswith('.txt')]
		for aliasesFilePath in aliasesFilePaths:
			aliasesString = system.file.readFileAsString(aliasesFilePath,"UTF-16")
			tags = tags + conversion.iconics.parseAliasesForKepwareTags(aliasesString, aliasesFilePath.split('/')[-1].strip('.txt'))
	
	
	
	tags = filter(lambda x : x['ip'].lower() == 'Ilaltscd01'.lower() and x['channel'] != 'Simulator' and not x['tagPath'].endswith('_ALARM_ACK') and not x['iconicsPage'].lower().endswith('_old'), tags)

	iconicTagsCSV = StringIO(conversion.iconics.generateCSV(tags))



	# ------------- create mapping file from iconics to kepware ------------------------
	
	 
	newFieldNames = [	'IconicsPage',
						'KepwareChannel',
						'KepwareDevice', 
						'KepwareTagPath', 
						'KepwareAddress', 
						'KepwareDataType',
						'KepwareDescription'
						] 
	 
	
	reader = csv.DictReader(iconicTagsCSV)
	iconicsKepwareJoinCSV = StringIO()
	writer = csv.DictWriter(iconicsKepwareJoinCSV, fieldnames=newFieldNames)
	writer.writeheader()
	
	for row in reader:
		deviceFilePath = kepwareExportsFolderPath + row['Channel'] + '__' + row['Device'] + '.csv'
		with open(deviceFilePath) as deviceReaderFile:
			deviceReader = csv.DictReader(deviceReaderFile)
			
			address = ''
			dataType = ''
			for deviceRow in deviceReader:

				if deviceRow['\xef\xbb\xbfTag Name'].lower() == row['Tag Path'].lower():	
					address = deviceRow['Address']
					dataType = deviceRow['Data Type']
					description = deviceRow['Description']
					break
			
			writer.writerow({	'IconicsPage': row['IconicsPage'],
								'KepwareChannel': row['Channel'],
								'KepwareDevice':row['Device'], 
								'KepwareTagPath':row['Tag Path'], 
								'KepwareAddress':address, 
								'KepwareDataType': dataType,
								'KepwareDescription': description
								})


	# ------------- add Ignition device name ------------------------

	 
	newFieldNames = [	'IconicsPage',
						'KepwareChannel',
						'KepwareDevice', 
						'KepwareTagPath', 
						'KepwareAddress', 
						'KepwareDataType',
						'KepwareDescription',
						'IgnitionDevice'
						] 

	reader = csv.DictReader(StringIO(iconicsKepwareJoinCSV.getvalue()))
	iconicsKepwareDeviceJoinCSV = StringIO()
	writer = csv.DictWriter(iconicsKepwareDeviceJoinCSV, fieldnames=newFieldNames)
	writer.writeheader()
	
	for row in reader:
		
		
		with  open(devicesFilePath) as deviceReaderFile:
			deviceReader = csv.DictReader(deviceReaderFile)
			ignitionDevice = ''
			for deviceRow in deviceReader:
	
				if deviceRow['KepwareChannel'] == row['KepwareChannel'] and deviceRow['KepwareDevice'] == row['KepwareDevice']:	
					ignitionDevice = deviceRow['\xef\xbb\xbfName']
					break
		
			writer.writerow({	'IconicsPage': row['IconicsPage'],
								'KepwareChannel': row['KepwareChannel'],
								'KepwareDevice':row['KepwareDevice'], 
								'KepwareTagPath':row['KepwareTagPath'], 
								'KepwareAddress':row['KepwareAddress'], 
								'KepwareDataType': row['KepwareDataType'],
								'KepwareDescription': row['KepwareDescription'],
								'IgnitionDevice': ignitionDevice
								})


	# ------------------  Update with PLC info and Ignition OPC path ----------------------------------

	plcTagsDS = dataset.generate.fromStandardCSVs(plcTagsFolderPath, addFileNameColumn=False)
	
	
	newFieldNames = [	'IconicsPage',
						'KepwareChannel',
						'KepwareDevice', 
						'KepwareTagPath', 
						'KepwareAddress', 
						'KepwareDataType',
						'KepwareDescription',
						'PLCPath',
						'PLCDataType',
						'PLCValue',
						'PLCDescription',
						'IgnitionDevice',
						'IgnitionOpcPath'
						] 
	 
	
	with open(outputFilePath, 'wb') as csvWriterFile:
		reader = csv.DictReader(StringIO(iconicsKepwareDeviceJoinCSV.getvalue()))
		writer = csv.DictWriter(csvWriterFile, fieldnames=newFieldNames)
		writer.writeheader()
		
		for row in reader:
	
			plcPath = ''
			plcDataType = ''
			plcDescription = ''
			plcValue = ''
			IgnitionOpcPath = ''
			for plcRow in range(plcTagsDS.getRowCount()):
				
				if row['IgnitionDevice'] == plcTagsDS.getValueAt(plcRow,'Device'):
				
					if row['KepwareAddress'].lower() == plcTagsDS.getValueAt(plcRow,'Path').lower():
						plcPath = plcTagsDS.getValueAt(plcRow,'Path')
						plcDataType = plcTagsDS.getValueAt(plcRow,'DataType')
						plcDescription = plcTagsDS.getValueAt(plcRow,'Description')
						plcValue = plcTagsDS.getValueAt(plcRow,'Value')
						break
				
					# if using bit numbers from an int
					if row['KepwareAddress'].split('.')[-1].isdigit() and '.'.join(row['KepwareAddress'].split('.')[:-1]).lower() == plcTagsDS.getValueAt(plcRow,'Path').lower():
						bitNumber = row['KepwareAddress'].split('.')[-1]
						plcPath = plcTagsDS.getValueAt(plcRow,'Path') + '.' + bitNumber
						plcDataType = plcTagsDS.getValueAt(plcRow,'DataType')
						plcDescription = plcTagsDS.getValueAt(plcRow,'Description')
						plcValue = plcTagsDS.getValueAt(plcRow,'Value')
						break
				
			if not plcPath and row['KepwareAddress']:
				
				plcPath = row['KepwareAddress']
				plcDescription = '(PLC Tag Not Found)'
				plcDataType = conversion.L5X.DATA_TYPE_MAPPING_KEPWARE_TO_AB[row['KepwareDataType']]
				plcValue = 0 
				
					
			writer.writerow({	'IconicsPage': row['IconicsPage'],
								'KepwareChannel': row['KepwareChannel'],
								'KepwareDevice':row['KepwareDevice'], 
								'KepwareTagPath':row['KepwareTagPath'], 
								'KepwareAddress':row['KepwareAddress'], 
								'KepwareDataType': row['KepwareDataType'],
								'KepwareDescription': row['KepwareDescription'],
								'PLCPath':plcPath,
								'PLCDataType':plcDataType,
								'PLCValue':plcValue,
								'PLCDescription':plcDescription,
								'IgnitionDevice':row['IgnitionDevice'],
								'IgnitionOpcPath': 'ns=1;s=[' + row['IgnitionDevice'] + ']' + plcPath
								})
								
								
								
								






#alarmsFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Iconics Backup - 4-24-2024/AL Alarms.csv' # alarmwork csv export (format so it's a proper csv)
#kepwareExportsFolderPath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Iconics Backup - 4-24-2024/Kepware/Exports/' # contains kepware device csv exports
#devicesFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Development/devices.csv' # manually created with headers ['Name', KepwareChannel', 'KepwareDevice', 'Driver', 'Model', 'PLCType', 'IgnitionDriver', 'ID', 'IP', 'TagCount']
#plcTagsFolderPath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Alton PLC Programs/Tags/' # contains parsed L5X tags
#outputFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Development/alarms_kepware_plc.csv'
#
#conversion.iconics.generateAlarmMapping(alarmsFilePath, kepwareExportsFolderPath, devicesFilePath, plcTagsFolderPath, outputFilePath)


def generateAlarmMapping(alarmsFilePath, kepwareExportsFolderPath, devicesFilePath, plcTagsFolderPath, outputFilePath):

## ------------- create mapping file from alarmworx to kepware ------------------------
		
	newFieldNames = [	'KepwareChannel',
						'KepwareDevice', 
						'KepwareTagPath', 
						'KepwareAddress', 
						'KepwareDataType',
						'KepwareDescription',
						'AlarmName',
						'AlarmDescription',
						'HiHiSetpoint',
						'HiHiDescription',
						'HiSetpoint',
						'HiDescription',
						'LoSetpoint',
						'LoDescription',
						'LoLoSetpoint',
						'LoLoDescription',
						'LastModified',
						'Enabled',
						'Delay'
						] 
	 
	
	with open(alarmsFilePath) as csvReaderFile:
		reader = csv.DictReader(csvReaderFile)
		alarmMappingCsvFile = StringIO()
		writer = csv.DictWriter(alarmMappingCsvFile, fieldnames=newFieldNames)
		writer.writeheader()
		
		for row in reader:
		
			kepwarePath = row['Input1']
			kepwareChannel = kepwarePath.split('KEPServerEX.V6\\')[-1].split('.')[0]
			kepwareDevice = kepwarePath.split('KEPServerEX.V6\\')[-1].split('.')[1]
			kepwareTagPath = '.'.join(kepwarePath.split('KEPServerEX.V6\\')[-1].split('.')[2:])
			
			if 'Simulator' not in kepwareChannel:
				deviceFilePath = kepwareExportsFolderPath + kepwareChannel + '__' + kepwareDevice + '.csv'
				with open(deviceFilePath) as deviceReaderFile:
					deviceReader = csv.DictReader(deviceReaderFile)
					
					address = ''
					dataType = ''
					for deviceRow in deviceReader:
						#print deviceRow
						if deviceRow['\xef\xbb\xbfTag Name'].lower() == kepwareTagPath.lower():	
							address = deviceRow['Address']
							dataType = deviceRow['Data Type']
							description = deviceRow['Description']
							break
					
					writer.writerow({
										'KepwareChannel': kepwareChannel,
										'KepwareDevice':kepwareDevice, 
										'KepwareTagPath':kepwareTagPath, 
										'KepwareAddress':address, 
										'KepwareDataType': dataType,
										'KepwareDescription': description,
										'AlarmName': row['Name'],
										'AlarmDescription': row['Description'],
										'HiHiSetpoint': row['LIM_HIHI_Limit'],
										'HiHiDescription': row['LIM_HIHI_MsgText'],
										'HiSetpoint': row['LIM_HI_Limit'],
										'HiDescription': row['LIM_HI_MsgText'],
										'LoSetpoint': row['LIM_LO_Limit'],
										'LoDescription': row['LIM_LO_MsgText'],
										'LoLoSetpoint': row['LIM_LOLO_Limit'],
										'LoLoDescription': row['LIM_LOLO_MsgText'],
										'LastModified': row['LastModified'],
										'Enabled':row['Enabled'],
										'Delay':row['Delay']
										})
	
	
	
	
	# ------------ Filter for most recent only ------------------------------------
	
	alarmMappingDS = dataset.generate.fromStandardCSVString(alarmMappingCsvFile.getvalue())
	pyds = system.dataset.toPyDataSet(alarmMappingDS)
	
	data = []
	for row in pyds:
	
		lastModified = system.date.toMillis(system.date.parse(row['LastModified'], 'MM/dd/yyyy hh:mm')) if row['LastModified'] != '12:00:00 AM' else 0
	
		matches = []
		for row2 in pyds:
			if row['KepwareChannel'] == row2['KepwareChannel'] and row['KepwareDevice'] == row2['KepwareDevice'] and row['KepwareAddress'] == row2['KepwareAddress']:
				matches.append(row2)
				
		latest = True
	
		for match in matches:
			
			if lastModified < system.date.toMillis(system.date.parse(match['LastModified'], 'MM/dd/yyyy hh:mm')) if match['LastModified'] != '12:00:00 AM' else 0:
				latest = False
				
		if latest:
			data.append(row)
			
	
	headers = alarmMappingDS.getColumnNames()
	filteredDS = system.dataset.toDataSet(list(headers), data)
	filteredPyDS = system.dataset.toPyDataSet(filteredDS)
	


	# ------------- add Ignition device name ------------------------
	
	devicesFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Development/devices.csv'
	alarmMappingDeviceFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Development/alarms_kepware_device.csv'
	 
	newFieldNames = [	'KepwareChannel',
						'KepwareDevice', 
						'KepwareTagPath', 
						'KepwareAddress', 
						'KepwareDataType',
						'KepwareDescription',
						'IgnitionDevice',
						'AlarmName',
						'AlarmDescription',
						'HiHiSetpoint',
						'HiHiDescription',
						'HiSetpoint',
						'HiDescription',
						'LoSetpoint',
						'LoDescription',
						'LoLoSetpoint',
						'LoLoDescription',
						'LastModified',
						'Enabled',
						'Delay'
						] 
	 
	
	alarmMappingWithDeviceFile = StringIO()
	writer = csv.DictWriter(alarmMappingWithDeviceFile, fieldnames=newFieldNames)
	writer.writeheader()
	
	for row in filteredPyDS:
		
		
		with  open(devicesFilePath) as deviceReaderFile:
			deviceReader = csv.DictReader(deviceReaderFile)
			ignitionDevice = ''
			for deviceRow in deviceReader:
	
				if deviceRow['KepwareChannel'] == row['KepwareChannel'] and deviceRow['KepwareDevice'] == row['KepwareDevice']:	
					ignitionDevice = deviceRow['\xef\xbb\xbfName']
					break
		
			writer.writerow({	
								'KepwareChannel': row['KepwareChannel'],
								'KepwareDevice': row['KepwareDevice'], 
								'KepwareTagPath': row['KepwareTagPath'], 
								'KepwareAddress': row['KepwareAddress'], 
								'KepwareDataType': row['KepwareDataType'],
								'KepwareDescription': row['KepwareDescription'],
								'IgnitionDevice': ignitionDevice,
								'AlarmName': row['AlarmName'],
								'AlarmDescription': row['AlarmDescription'],
								'HiHiSetpoint': row['HiHiSetpoint'],
								'HiHiDescription': row['HiHiDescription'],
								'HiSetpoint': row['HiSetpoint'],
								'HiDescription': row['HiDescription'],
								'LoSetpoint': row['LoSetpoint'],
								'LoDescription': row['LoDescription'],
								'LoLoSetpoint': row['LoLoSetpoint'],
								'LoLoDescription': row['LoLoDescription'],
								'LastModified': row['LastModified'],
								'Enabled': row['Enabled'],
								'Delay': row['Delay']
								})


	
	# ------------------  Update with PLC info and Ignition OPC path ----------------------------------
	
	plcTagsDS = dataset.generate.fromStandardCSVs(plcTagsFolderPath, addFileNameColumn=False)
	
	newFieldNames =[	'KepwareChannel',
						'KepwareDevice', 
						'KepwareTagPath', 
						'KepwareAddress', 
						'KepwareDataType',
						'KepwareDescription',
						'PLCPath',
						'PLCDataType',
						'PLCValue',
						'PLCDescription',
						'IgnitionDevice',
						'IgnitionOpcPath',
						'AlarmName',
						'AlarmDescription',
						'HiHiSetpoint',
						'HiHiDescription',
						'HiSetpoint',
						'HiDescription',
						'LoSetpoint',
						'LoDescription',
						'LoLoSetpoint',
						'LoLoDescription',
						'LastModified',
						'Enabled',
						'Delay'
						] 
	
	
	
	with open(outputFilePath, 'wb') as csvWriterFile:
		csvReaderFile = StringIO(alarmMappingWithDeviceFile.getvalue())
		reader = csv.DictReader(csvReaderFile)
		writer = csv.DictWriter(csvWriterFile, fieldnames=newFieldNames)
		writer.writeheader()
		
		for row in reader:
	
			plcPath = ''
			plcDataType = ''
			plcDescription = ''
			plcValue = ''
			IgnitionOpcPath = ''
			for plcRow in range(plcTagsDS.getRowCount()):
				
				if row['IgnitionDevice'] == plcTagsDS.getValueAt(plcRow,'Device'):
				
					if row['KepwareAddress'].lower() == plcTagsDS.getValueAt(plcRow,'Path').lower():
						plcPath = plcTagsDS.getValueAt(plcRow,'Path')
						plcDataType = plcTagsDS.getValueAt(plcRow,'DataType')
						plcDescription = plcTagsDS.getValueAt(plcRow,'Description')
						plcValue = plcTagsDS.getValueAt(plcRow,'Value')
						break
				
					# if using bit numbers from an int
					if row['KepwareAddress'].split('.')[-1].isdigit() and '.'.join(row['KepwareAddress'].split('.')[:-1]).lower() == plcTagsDS.getValueAt(plcRow,'Path').lower():
						bitNumber = row['KepwareAddress'].split('.')[-1]
						plcPath = plcTagsDS.getValueAt(plcRow,'Path') + '.' + bitNumber
						plcDataType = plcTagsDS.getValueAt(plcRow,'DataType')
						plcDescription = plcTagsDS.getValueAt(plcRow,'Description')
						plcValue = plcTagsDS.getValueAt(plcRow,'Value')
						break
				
			if not plcPath and row['KepwareAddress']:
				
				plcPath = row['KepwareAddress']
				plcDescription = '(PLC Tag Not Found)'
				plcDataType = conversion.L5X.DATA_TYPE_MAPPING_KEPWARE_TO_AB[row['KepwareDataType']]
				plcValue = 0 
				
				
				
					
					
			writer.writerow({	
							'KepwareChannel': row['KepwareChannel'],
							'KepwareDevice': row['KepwareDevice'], 
							'KepwareTagPath': row['KepwareTagPath'], 
							'KepwareAddress': row['KepwareAddress'], 
							'KepwareDataType': row['KepwareDataType'],
							'KepwareDescription': row['KepwareDescription'],
							'PLCPath':plcPath,
							'PLCDataType':plcDataType,
							'PLCValue':plcValue,
							'PLCDescription':plcDescription,
							'IgnitionDevice':row['IgnitionDevice'],
							'IgnitionOpcPath':'ns=1;s=[' + row['IgnitionDevice'] + ']' + plcPath,
							'AlarmName': row['AlarmName'],
							'AlarmDescription': row['AlarmDescription'],
							'HiHiSetpoint': row['HiHiSetpoint'],
							'HiHiDescription': row['HiHiDescription'],
							'HiSetpoint': row['HiSetpoint'],
							'HiDescription': row['HiDescription'],
							'LoSetpoint': row['LoSetpoint'],
							'LoDescription': row['LoDescription'],
							'LoLoSetpoint': row['LoLoSetpoint'],
							'LoLoDescription': row['LoLoDescription'],
							'LastModified': row['LastModified'],
							'Enabled': row['Enabled'],
							'Delay': row['Delay']
							})
	
