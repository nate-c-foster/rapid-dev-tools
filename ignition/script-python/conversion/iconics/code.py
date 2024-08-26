import re



# ------------------ parse iconics text report --------------------------------------------------------

#filepath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Development/iconics_report.txt'
# 
#reportString = system.file.readFileAsString(filepath)
#
#tags = conversion.iconics.parseReportForKepwareTags(reportString)
#
#tags = filter(lambda x : x['ip'].lower() == 'Ilaltscd01'.lower() and x['channel'] != 'Simulator' and not x['tagPath'].endswith('_ALARM_ACK') and not x['iconicsPage'].lower().endswith('_old'), tags)
#
#system.file.writeFile('C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Development/iconics_all_tags.csv', conversion.iconics.generateCSV(tags))






# ------------- create mapping file from iconics to kepware ------------------------
	
#iconicTagsFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Development/iconics_all_tags.csv'
#tagMappingFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Development/iconics_kepware_join.csv'
#deviceFilePathSuffix = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Iconics Backup - 4-24-2024/Kepware/Exports/'
# 
#newFieldNames = [	'IconicsPage',
#					'KepwareChannel',
#					'KepwareDevice', 
#					'KepwareTagPath', 
#					'KepwareAddress', 
#					'KepwareDataType',
#					'KepwareDescription'
#					] 
# 
#import csv
#
#with open(iconicTagsFilePath) as csvReaderFile, open(tagMappingFilePath, 'wb') as csvWriterFile:
#	reader = csv.DictReader(csvReaderFile)
#	writer = csv.DictWriter(csvWriterFile, fieldnames=newFieldNames)
#	writer.writeheader()
#	
#	for row in reader:
#		deviceFilePath = deviceFilePathSuffix + row['Channel'] + '__' + row['Device'] + '.csv'
#		with open(deviceFilePath) as deviceReaderFile:
#			deviceReader = csv.DictReader(deviceReaderFile)
#			
#			address = ''
#			dataType = ''
#			for deviceRow in deviceReader:
#				#print deviceRow
#				if deviceRow['\xef\xbb\xbfTag Name'].lower() == row['Tag Path'].lower():	
#					address = deviceRow['Address']
#					dataType = deviceRow['Data Type']
#					description = deviceRow['Description']
#					break
#			
#			writer.writerow({	'IconicsPage': row['IconicsPage'],
#								'KepwareChannel': row['Channel'],
#								'KepwareDevice':row['Device'], 
#								'KepwareTagPath':row['Tag Path'], 
#								'KepwareAddress':address, 
#								'KepwareDataType': dataType,
#								'KepwareDescription': description
#								})






# ------------- add Ignition device name ------------------------


#tagMappingFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Development/iconics_kepware_join.csv'
#tagMappingFileWithDevice = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Development/iconics_kepware_join_device.csv'
#devicesFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Development/devices.csv'
# 
#newFieldNames = [	'IconicsPage',
#					'KepwareChannel',
#					'KepwareDevice', 
#					'KepwareTagPath', 
#					'KepwareAddress', 
#					'KepwareDataType',
#					'KepwareDescription',
#					'IgnitionDevice'
#					] 
# 
# 
# 
#import csv
#
#with open(tagMappingFilePath) as csvReaderFile, open(tagMappingFileWithDevice, 'wb') as csvWriterFile:
#	reader = csv.DictReader(csvReaderFile)
#
#	writer = csv.DictWriter(csvWriterFile, fieldnames=newFieldNames)
#	writer.writeheader()
#	
#	for row in reader:
#		
#		
#		with  open(devicesFilePath) as deviceReaderFile:
#			deviceReader = csv.DictReader(deviceReaderFile)
#			ignitionDevice = ''
#			for deviceRow in deviceReader:
#	
#				if deviceRow['KepwareChannel'] == row['KepwareChannel'] and deviceRow['KepwareDevice'] == row['KepwareDevice']:	
#					ignitionDevice = deviceRow['\xef\xbb\xbfName']
#					break
#		
#			writer.writerow({	'IconicsPage': row['IconicsPage'],
#								'KepwareChannel': row['KepwareChannel'],
#								'KepwareDevice':row['KepwareDevice'], 
#								'KepwareTagPath':row['KepwareTagPath'], 
#								'KepwareAddress':row['KepwareAddress'], 
#								'KepwareDataType': row['KepwareDataType'],
#								'KepwareDescription': row['KepwareDescription'],
#								'IgnitionDevice': ignitionDevice
#								})





# ------------------  Update with PLC info and Ignition OPC path ----------------------------------

#tagsFolderPath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Alton PLC Programs/Tags/'
#plcTagsDS = dataset.generate.fromStandardCSVs(tagsFolderPath, addFileNameColumn=False)
#
#tagMappingFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Development/iconics_kepware_join_device.csv'
#rosetaStonePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Development/iconics_kepware_plc.csv'
#
#newFieldNames = [	'IconicsPage',
#					'KepwareChannel',
#					'KepwareDevice', 
#					'KepwareTagPath', 
#					'KepwareAddress', 
#					'KepwareDataType',
#					'KepwareDescription',
#					'PLCPath',
#					'PLCDataType',
#					'PLCValue',
#					'PLCDescription',
#					'IgnitionDevice',
#					'IgnitionOpcPath'
#					] 
# 
#import csv
#
#with open(tagMappingFilePath) as csvReaderFile, open(rosetaStonePath, 'wb') as csvWriterFile:
#	reader = csv.DictReader(csvReaderFile)
#	writer = csv.DictWriter(csvWriterFile, fieldnames=newFieldNames)
#	writer.writeheader()
#	
#	for row in reader:
#
#		plcPath = ''
#		plcDataType = ''
#		plcDescription = ''
#		plcValue = ''
#		IgnitionOpcPath = ''
#		for plcRow in range(plcTagsDS.getRowCount()):
#			
#			if row['IgnitionDevice'] == plcTagsDS.getValueAt(plcRow,'Device'):
#			
#				if row['KepwareAddress'].lower() == plcTagsDS.getValueAt(plcRow,'Path').lower():
#					plcPath = plcTagsDS.getValueAt(plcRow,'Path')
#					plcDataType = plcTagsDS.getValueAt(plcRow,'DataType')
#					plcDescription = plcTagsDS.getValueAt(plcRow,'Description')
#					plcValue = plcTagsDS.getValueAt(plcRow,'Value')
#					break
#			
#				# if using bit numbers from an int
#				if row['KepwareAddress'].split('.')[-1].isdigit() and '.'.join(row['KepwareAddress'].split('.')[:-1]).lower() == plcTagsDS.getValueAt(plcRow,'Path').lower():
#					bitNumber = row['KepwareAddress'].split('.')[-1]
#					plcPath = plcTagsDS.getValueAt(plcRow,'Path') + '.' + bitNumber
#					plcDataType = plcTagsDS.getValueAt(plcRow,'DataType')
#					plcDescription = plcTagsDS.getValueAt(plcRow,'Description')
#					plcValue = plcTagsDS.getValueAt(plcRow,'Value')
#					break
#			
#		if not plcPath and row['KepwareAddress']:
#			
#			plcPath = row['KepwareAddress']
#			plcDescription = '(PLC Tag Not Found)'
#			plcDataType = conversion.L5X.DATA_TYPE_MAPPING_KEPWARE_TO_AB[row['KepwareDataType']]
#			plcValue = 0 
#			
#			
#			
#				
#				
#		writer.writerow({	'IconicsPage': row['IconicsPage'],
#							'KepwareChannel': row['KepwareChannel'],
#							'KepwareDevice':row['KepwareDevice'], 
#							'KepwareTagPath':row['KepwareTagPath'], 
#							'KepwareAddress':row['KepwareAddress'], 
#							'KepwareDataType': row['KepwareDataType'],
#							'KepwareDescription': row['KepwareDescription'],
#							'PLCPath':plcPath,
#							'PLCDataType':plcDataType,
#							'PLCValue':plcValue,
#							'PLCDescription':plcDescription,
#							'IgnitionDevice':row['IgnitionDevice'],
#							'IgnitionOpcPath': 'ns=1;s=[' + row['IgnitionDevice'] + ']' + plcPath
#							})




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
	kepwareRegex = re.compile(r'\\\\([.\w]+)\\([.\w]+)\\([-_ #\w]+).([-_ #\w]+).([.-_ #\w]+)')
	
	
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






def generateCSV(tags):
	data = []
	header = ["IconicsPage", "IP", "Server", "Channel", "Device", "Tag Path"]
	
	for tag in tags:
		if 	'BristolBabcock' not in tag['server'] and 'AlarmServer' not in tag['server'] and  not tag['tagPath'].startswith('_System') and 'Simulator' not in tag['server']:
			if [tag['iconicsPage'], tag['ip'], tag['server'], tag['channel'], tag['device'], tag['tagPath']] not in data:
				data.append([tag['iconicsPage'], tag['ip'], tag['server'], tag['channel'], tag['device'], tag['tagPath']] )
	
	sortedData = sorted(data, key=lambda x : (x[0], x[3], x[4]))

	return system.dataset.toCSV(system.dataset.toDataSet(header, sortedData))
	
	
	
