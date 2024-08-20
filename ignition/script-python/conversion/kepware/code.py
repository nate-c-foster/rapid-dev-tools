# -- run scripts

#filepath = 'C:/VM Shared Drive/Ventura/Ventura/Kepware/exports/Dos_Vientos_Bstr.csv'
# 
#csvString = system.file.readFileAsString(filepath)
#
#tags = conversion.kepware.parse(csvString)
#
#system.file.writeFile('C:/VM Shared Drive/Ventura/Ventura/Kepware/simulation_files/Dos_Vientos_Bstr.csv', conversion.kepware.generateSimulationCSV(tags))


import random



DATA_TYPE_MAPPING_SIMULATION = {"Boolean":"Boolean", "Char":"UInt16", "Short":"Int16", "Long":"Int32", "Float":"Float", "String":"String"}

DEFAULT_SIMULATION = {"Boolean":"false", "Char":"0", "Short":"0", "Long":"0", "Float":"0.0", "String":""}

PUMP_SIMULATION = { 	'.Call_Out':'false',
						'.HOA_In_Auto':'true',
						'.HOA_Inhibit':'false',
						'.Level_Control_Start':'false',
						'.Level_Control_Stop':'true',
						'.Model':'0',
						'.PB_Operator_Start':'false',
						'.PB_Operator_Stop':'false',
						'.Power_Raw':'3200',
						'.Power_Raw_Zero':'4000',
						'.Power_Raw_Span':'20000',
						'.Power_Zero':'0',
						'.Power_Span':'5',
						'.Pump_Order': '1',
						'.Reset_Alarm':'false',
						'.Reset_Delay':'0.01',
						'.Run':'false',
						'.Run_Inhibit':'false',
						'.Run_On':'false',
						'.Run_SP':'0.0',
						'.Run_Time_L':'0.0',
						'.Start':'false',
						'.Start_Delay': '0.01',
						'.Stop':'false',
						'.Stop_Delay': '0.01',
						'.Time_Control_Start':'false',
						'.Time_Control_Stop':'true',
						'.TOF':'false',
						'.VFD_Hz_Eng_Span':'60.0',
						'.VFD_Hz_Eng_Zero':'0.0',
						'.VFD_Hz_Raw':'0.0',
						'.Vfd_Hz_Raw_Span':'0.0',
						'.VFD_Hz_Raw_Zero':'0.0',
						}
						
						

def parse(csvString, selectTags=False):

	tags = []
	
	csvReader = CSV.util.dictReaderFromString(csvString)

	for row in csvReader:
	
		# remove prefix 'Global.'
		tagName = row['\xef\xbb\xbfTag Name']
		tagName = tagName[len('Global.'):] if tagName.startswith('Global.') else tagName
		
		address = row['Address']
		
		# convert the address case so it matches the tagName case
		for i in range(len(tagName)):
			if i < len(address) and tagName[i].lower() ==  address[i].lower():
				address = address[:i] + tagName[i] + address[i+1:]
		
		
		if 'String' not in row['Data Type']:
		
			tags.append( {
				"tagName": tagName,
				"address": address,
				"dataType": row['Data Type'],
				"selected": selectTags,
				"simulationFunction": simulatorValue(tagName, address, row['Data Type']),
				})
	
	return tags


def generateSimulationCSV(tags):
	simulationData = []
	simulationHeader = ["Time Interval", "Browse Path", "Value Source", "Data Type"]
	
	for tag in tags:
		simulationData.append([0,tag['address'], tag['simulationFunction'], DATA_TYPE_MAPPING_SIMULATION[tag['dataType']]])
		
	return system.dataset.toCSV(system.dataset.toDataSet(simulationHeader, simulationData))



def isPump(tagName, address, dataType):

	if 'Pump' in tagName:
		choices = [('true','sine(2.7,3.5,1000,true)','sine(78,84,1000,true)','sine(48,52,1000,true)'), ('false', '0.0', '0.0', '0.0'), ('true','sine(3.8,4.6,1000,true)','sine(93,97,1000,true)','sine(55,59,1000,true)'), ('false', '0.0', '0.0', '0.0')]
		if '1' in tagName:
			choice = choices[0]
		elif '2' in tagName:
			choice = choices[1]
		elif '3' in tagName:
			choice = choices[2]
		else:
			choice = choices[3]
			
		if tagName.endswith('.Run_Status'):
			return (True, choice[0])	
		elif tagName.endswith('.Power_Eng'):
			return (True, choice[1])	
		elif tagName.endswith('.VFD_Percent_Out'):
			return (True, choice[2])	
		elif tagName.endswith('.VFD_Hz_Eng'):
			return (True, choice[3])	
		else:
			keys = PUMP_SIMULATION.keys()
			for key in keys:
				if tagName.endswith(key):
					return (True, PUMP_SIMULATION[key])
				
	return (False, None)	
	
def isSensor(tagName, address, dataType):
	if 'Flow' in tagName:
		if tagName.endswith('.Eng_Value'):
			return (True, 'sine(600,800,1000,true)')
		if tagName.endswith('.Flow_Eng'):
			return (True, 'sine(600,800,1000,true)')
		elif tagName.endswith('.Eng_Span'):
			return (True, '2000')	
		elif tagName.endswith('.SP_HH_Alm'):
			return (True, '900')	
		elif tagName.endswith('.SP_H_Alm'):
			return (True, '850')	
		elif tagName.endswith('.SP_L_Alm'):
			return (True, '0')	
		elif tagName.endswith('.SP_LL_Alm'):
			return (True, '0')
		elif tagName.endswith('.SP_Hi_Hi_Alm'):
			return (True, '900')	
		elif tagName.endswith('.SP_Hi_Alm'):
			return (True, '850')	
		elif tagName.endswith('.SP_Lo_Alm'):
			return (True, '0')	
		elif tagName.endswith('.SP_Lo_Lo_Alm'):
			return (True, '0')
		elif tagName.endswith('_Today'):
			return (True, '.0254')
		elif tagName.endswith('_Yesterday'):
			return (True, '.493')
		elif tagName.endswith('_This_Month'):
			return (True, '5.29')
		elif tagName.endswith('_Last_Month'):
			return (True, '7.82')
		elif tagName.endswith('_This_Year'):
			return (True, '28.45')
		elif tagName.endswith('_Last_Year'):
			return (True, '43.37')
			

	elif 'Press' in tagName:
		if tagName.endswith('.Eng_Value'):
			return (True, 'sine(54,87,1000,true)')
		elif tagName.endswith('.Eng_Span'):
			return (True, '250')	
		elif tagName.endswith('.SP_HH_Alm'):
			return (True, '150')	
		elif tagName.endswith('.SP_H_Alm'):
			return (True, '93')	
		elif tagName.endswith('.SP_L_Alm'):
			return (True, '10')	
		elif tagName.endswith('.SP_LL_Alm'):
			return (True, '10')
			
			
	return (False, None)
	

def isT1Type(tagName, address, dataType):
	return (False, None)


def isTankType(tagName, address, dataType):
	if 'Tank' in tagName or 'TK_01' in tagName:
		if tagName.endswith('.Level_Eng'):
			return (True, 'sine(31,38,1000,true)')
		elif tagName.endswith('.Rng_Eng_Tank_Height'):
			return (True, '52')	
		elif tagName.endswith('.SP_Hi_Hi_Alm'):
			return (True, '100')	
		elif tagName.endswith('.SP_Hi_Alm'):
			return (True, '47')	
		elif tagName.endswith('.SP_Lo_Alm'):
			return (True, '24')	
		elif tagName.endswith('.SP_Lo_Lo_Alm'):
			return (True, '20')
		elif tagName.endswith('.Rng_Eng_Level_Span'):
			return (True, '579.5')
		elif tagName.endswith('.Rng_Eng_Volume_Max'):
			return (True, '6')
		elif tagName.endswith('.Rng_Eng_Volume'):
			return (True, 'sine(3.5,4.3,1000,true)')

	return (False, None)
	





def simulatorValue(tagName, address, dataType):

	isPumpTag, pumpTagValue = isPump(tagName, address, dataType)
	isSensorTag, sensorTagValue = isSensor(tagName, address, dataType)	
	isT1TypeTag, t1TypeTagValue = isT1Type(tagName, address, dataType)
	isTankTypeTag, tankTypeTagValue = isTankType(tagName, address, dataType)	
	
	if isPumpTag:
		return pumpTagValue 
	elif isSensorTag:
		return sensorTagValue
	elif isT1TypeTag:
		return t1TypeTagValue
	elif isTankTypeTag:
		return tankTypeTagValue
	else:
		return DEFAULT_SIMULATION[dataType]