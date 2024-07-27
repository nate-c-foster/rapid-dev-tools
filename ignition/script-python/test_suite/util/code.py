
import re








def parseIconicsForKepwareTags(reportFilePath):

	reportString = system.file.readFileAsString(reportFilePath)
	
	
	# --- kepware tags ---
	# tag:"\\10.5.206.26\Kepware.KEPServerEX.V6\C-JanssBooster.JanssBooster.Global.Pump_1.HOA_In_Auto"
	# tag:"\\10.5.206.26\Kepware.KEPServerEX.V6\C-JanssBooster.JanssBooster._System._FailedConnection"
	# tag:"\\10.5.206.26\Kepware.KEPServerEX.V6\C-Moorpark.Moorpark.UPS_BATT_LOW_ALM"

	headers = 	["IP", "Server", "Channel", "Device", "TagPath", "FullPath"]
	data = []

	kepwareTagRegex = re.compile(r'\\\\([.\w]+)\\([.\w]+)\\([-_ #\w]+).([-_ #\w]+).([.-_ #\w]+)')
	tags = kepwareTagRegex.finditer(reportString)
	
	for i, tag in enumerate(tags):
		
		
		
		ip = tag.group(1)
		server = tag.group(2)
		channel = tag.group(3)
		device = tag.group(4)
		tagPath = tag.group(5)
		
		fullPath = tag.group()

		# remove ip
		if fullPath.startswith('\\\\' + ip + '\\'):
			fullPath = fullPath[len('\\\\' + ip + '\\'):]


		# Kepware only, not BristolBabcock(different regex)
		if 'Kepware' in server and 'AlarmServer' not in server and  not tagPath.startswith('_System') and 'Simulator' not in server:
		
			# no repeats
			if [ip, server, channel, device, tagPath, fullPath] not in data:
				data.append( [ip, server, channel, device, tagPath, fullPath] )
	
	data = sorted(data, key=lambda x: (x[2], x[3], x[4]))
		
	return system.dataset.toDataSet(headers, data)
	




#inputFilePath = 'C:/VM Shared Drive/Ventura/Ventura/TestReports/TagReport/iconics_kepware_join_csv.csv'
#outputFilePath = 'C:/VM Shared Drive/Ventura/Ventura/TestReports/TagReport/iconics_to_ignition_csv.csv'
#
#dataset = dataset_editor.generate.fromStandardCSV(inputFilePath)
#
#
#def transform(row):
#
#	address = row['right_Address']
#	device = row['left_Device']
#	devicePath = row['left_TagPath']
#	
#	tagPath = devicePath[len('Global.'):] if devicePath.startswith('Global.') else devicePath
#	
#	# use tagPath case
#	if tagPath.lower() == address.lower():
#		address = tagPath
#
#	return {	'KepwarePath': row['left_FullPath'],
#				'DeviceName': device,
#				'DevicePath': devicePath,
#				'Address': address,
#				'OpcPath': 'ns=1;s=[' + row['left_Device'] + ']' + address if address else ''
#				}
#
#ds = dataset_editor.operation.datsetMap(dataset, transform, ['KepwarePath','DeviceName','DevicePath','Address','OpcPath'])
#dataset_editor.export.toCSV(ds, outputFilePath)







	
	
	
	
def getTagProperties(tagPath):

	valueSource = system.tag.readBlocking(tagPath +'.valueSource')[0].value
	valueQuality = system.tag.readBlocking(tagPath +'.quality')[0].value
	value = system.tag.readBlocking(tagPath)[0].value
	
	if valueSource == 'opc':
		valueProperty = system.tag.readBlocking(tagPath + '.opcItemPath')[0].value
	elif valueSource == 'memory':
		valueProperty = system.tag.readBlocking(tagPath + '.value')[0].value
	elif valueSource == 'reference':
		valueProperty = system.tag.readBlocking(tagPath + '.sourceTagPath')[0].value
	elif valueSource == 'derived':
		valueProperty = system.tag.readBlocking(tagPath + '.sourceTagPath')[0].value
	elif valueSource == 'expression' or valueSource == 'expr':
		valueProperty = system.tag.readBlocking(tagPath + '.expression')[0].value
	else:
		valueProperty = 'BAD_VALUE_SOURCE'
		
	return (valueSource, valueProperty, valueQuality, value)