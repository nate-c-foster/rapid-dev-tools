
import csv
import re

# read file

#filePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Alton PLC Programs/Alton PLC Programs/PLC5/FILTR1_2.CSV'
#ds = conversion.ascii_export.readFile(filePath)



def readASCIIExportFile(filePath):

	data = []
	with open(filePath) as csvfile:
	    reader = csv.reader(csvfile, delimiter=',')
	    for row in reader:
	    	register = row[0]
	    	name = row[2]
	    	description = ' '.join([row[3], row[4], row[5], row[6], row[7]])
	      	print register + '     ' + name + '    ' + description
	      	
	      	if register:
	      		data.append([register, name, description])
	
	headers = ['Register', 'Name', 'Description']

	return system.dataset.toDataSet(headers, data)





# get ASCII csv file by getting database ASCII Export for "Addr/Symbol Desc."
# get L5X file by first saving legacy program as ACD and unchecking "Create Alias Tag in Logix .."
def getAllTags(l5xFilePath, asciiFilePath, deviceName):

	l5xString = system.file.readFileAsString(l5xFilePath, 'UTF-8')
	l5xTagsDS = conversion.L5X.getAllTags(l5xString,'FLTR1')  # headers ['Device', 'Path', 'DataType', 'Value', 'Description']
	l5xTagPyDS = system.dataset.toPyDataSet(l5xTagsDS)
	
	asciiDS = readASCIIExportFile(asciiFilePath) # headers ['Register', 'Name', 'Description']
	asciiPyDS = system.dataset.toPyDataSet(asciiDS)
	
	for asciiRow in asciiPyDS:
		register = asciiPyDS['Register']
		l5xPath, bitSelector = registerToL5XPath(register)
		
		for l5xRow in l5xTagPyDS:
			if l5xPath == l5xRow['Path']:
				# get value - tricky with bit string
				
				break
				
		# if value not found, use a default value
		
		# get data type based on register
		
		
	# return same format as getAllTags()
		
		
		
		

def generateSimulation(l5xString):
	pass





	
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




def registerDataType(register):
	pass



# create export with
#	path, dataType, description



# create sim file
