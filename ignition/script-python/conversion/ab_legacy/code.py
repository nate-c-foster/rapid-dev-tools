
import csv
import re




# -------------  Generate SIM files ------------------------------------

#deviceNames = ['CHEM', 'FLTR1', 'FLTR3', 'FLTR5', 'GRAFTON_ELEV_TANK', 'HRLD', 'RAW', 'SP1', 'SP3']
#
#for deviceName in deviceNames:
#
#	l5xFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Alton PLC Programs/Exports/' + deviceName + '.L5X'
#	asciiFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Alton PLC Programs/Exports/' + deviceName + '.csv'
#	tagsFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Alton PLC Programs/Tags/' + deviceName + '.csv'
#	simFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Alton PLC Programs/SIM/' + deviceName + '.csv'
#	
#	
#	ds = conversion.ab_legacy.getAllTags(l5xFilePath, asciiFilePath, deviceName)
#	dataset.export.toCSV(ds, tagsFilePath)
#	
#	ds = conversion.ab_legacy.generateSimulation(l5xFilePath, asciiFilePath)
#	dataset.export.toCSV(ds, simFilePath)






# -------------  Add missing tags from tag mapper ------------------------------------

#deviceNames = ['CHEM', 'FLTR1', 'FLTR3', 'FLTR5', 'GRAFTON_ELEV_TANK', 'HRLD', 'RAW', 'SP1', 'SP3']
#
#for deviceName in deviceNames:
#
#	simFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Alton PLC Programs/SIM/' + deviceName + '.csv'
#	rosetaStonePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Development/iconics_kepware_plc.csv'
#	
#	simDS = dataset.generate.fromStandardCSV(simFilePath)
#	
#	rosetaStoneDS = dataset.generate.fromStandardCSV(rosetaStonePath)
#	rosetaStonePyDS = system.dataset.toPyDataSet(rosetaStoneDS)
#	
#	for tag in rosetaStonePyDS:
#		if tag['IgnitionDevice'] == deviceName and tag['PLCDescription'] == '(PLC Tag Not Found)':
#			print 'Device: ', deviceName
#			print 'Not Found: ', tag['PLCPath']
#			currentTagPaths = simDS.getColumnAsList(simDS.getColumnIndex("Browse Path"))
#			if not tag['PLCPath'] in currentTagPaths:
#				simDS = system.dataset.addRow(simDS, [0, tag['PLCPath'], tag['PLCValue'], conversion.L5X.DATA_TYPE_MAPPING_SIMULATION[tag['PLCDataType']]])
#			
#	
#	dataset.export.toCSV(simDS, simFilePath)





def readASCIIExportFile(filePath):

	data = []
	with open(filePath) as csvfile:
	    reader = csv.reader(csvfile, delimiter=',')
	    for row in reader:
	    	register = row[0]
	    	name = row[2]
	    	description = ' '.join([row[3], row[4], row[5], row[6], row[7]])
	    	
	      	if register:
	      		data.append([register, name, description])
	
	headers = ['Register', 'Name', 'Description']

	return system.dataset.toDataSet(headers, data)





# get ASCII csv file by getting database ASCII Export for "Addr/Symbol Desc."
# get L5X file by first saving legacy program as ACD and unchecking "Create Alias Tag in Logix .."
def getAllTags(l5xFilePath, asciiFilePath, deviceName):

	l5xString = system.file.readFileAsString(l5xFilePath, 'UTF-8')
	l5xTagsDS = conversion.L5X.getAllTags(l5xString,deviceName)  # headers ['Device', 'Path', 'DataType', 'Value', 'Description']
	l5xTagPyDS = system.dataset.toPyDataSet(l5xTagsDS)
	
	asciiDS = readASCIIExportFile(asciiFilePath) # headers ['Register', 'Name', 'Description']
	asciiPyDS = system.dataset.toPyDataSet(asciiDS)
	
	data = []
	for asciiRow in asciiPyDS:
		register = asciiRow['Register']
		l5xPath, bitSelector = registerToL5XPath(register)
		

		
		for l5xRow in l5xTagPyDS:
		
			dataType = l5xRow['DataType']
			value = conversion.L5X.DEFAULT_SIMULATION[dataType]
			
			if '/' in register:
				dataType = 'BIT'
		
			if l5xPath == l5xRow['Path']:
				l5xValue = l5xRow['Value']
				if isBitRegister(l5xPath) and l5xValue.startswith('2#'):
					value = convertToBitList(l5xValue)[bitSelector]
				else:
					value = conversion.L5X.valueTransform(l5xValue)
				break
		
		
		if not '[' in register and not 'FILE' in register and not register.startswith('U'):
			data.append([	l5xRow['Device'],
							register,
							dataType,
							str(value),
							asciiRow['Name'] + '  -  ' + asciiRow['Description'] if asciiRow['Name'] else asciiRow['Description']
							])
	
	headers = ['Device', 'Path', 'DataType', 'Value', 'Description']
		
	return system.dataset.toDataSet(headers, data)
		
		
		
		

def generateSimulation(l5xFilePath, asciiFilePath):

	tagsDS = getAllTags(l5xFilePath, asciiFilePath, '')
	tagsPyDS = system.dataset.toPyDataSet(tagsDS)

	data = []
	for row in tagsPyDS:
		
		dataType = conversion.L5X.DATA_TYPE_MAPPING_SIMULATION[row['DataType']]
		value = conversion.L5X.simulationValue(row['Value'], dataType)

		data.append([0, row['Path'], value, dataType])
	
	headers = ['Time Interval', 'Browse Path', 'Value Source', 'Data Type']
	
	return system.dataset.toDataSet(headers, data)


	
# B3:4/03 -> (b3[4], 3)
def registerToL5XPath(register):

	l5xPath = register.split('/')[0]
	l5xPath = re.sub(r':([\d]+)', r'[\g<1>]', l5xPath)
	
	
	bitSelector = register.split('/')[-1]
	if bitSelector.isdigit():
		bitSelector = int(bitSelector)
	else:
		bitSelector = -1
	
	return (l5xPath, bitSelector)



def isBitRegister(name):
	match = re.search(r'^B[\d]+', name)
	if match:
		return True
	else:
		return False

def isIntRegister(name):
	match = re.search(r'^N[\d]+', name)
	if match:
		return True
	else:
		return False
		

def isFloatRegister(name):
	match = re.search(r'^F[\d]+', name)
	if match:
		return True
	else:
		return False



# example 2#0000_1011  -> [1,1,0,1,0000]
def convertToBitList(bitString):
	bitString = bitString.strip('2#')
	bitString = bitString.replace('_','')
	
	bitList = [int(x) for x in bitString[::-1]]
	
	return bitList






def registerDataType(register):
	pass



# create export with
#	path, dataType, description



# create sim file
