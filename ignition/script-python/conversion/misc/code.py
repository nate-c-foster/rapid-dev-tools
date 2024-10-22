

def updateDesiredValues(rootTagPath):
	import math
	
	
	results = system.tag.browse(rootTagPath, {'recursive':True, 'tagType':'UdtInstance', 'typeId':'Components/Analog Input'})
	
	endToday = system.date.now()
	startToday = system.date.addDays(endToday, -3)
	
	
	for result in results:
		tagPath = str(result['fullPath'])
	
	
	
		histPaths = Trending.util.toHistPaths([tagPath + '/Control/DeviceStatus/Output'])
		calcToday = system.tag.queryTagCalculations(paths=histPaths, 
													calculations=['Minimum','Maximum'], 
													startDate = startToday, 
													endDat = endToday,
													noInterpolation=True)
		
		
		euMin = system.tag.readBlocking(tagPath + '/Engineering/EUMin')[0].value
		euMax = system.tag.readBlocking(tagPath + '/Engineering/EUMax')[0].value
		
		if system.tag.readBlocking(tagPath + '/Alarming/High/Setpoint.enabled')[0].value:
			highSP = system.tag.readBlocking(tagPath + '/Alarming/High/Setpoint')[0].value
		else:
			highSP = euMax
		
		if highSP > euMax:
			highSP = euMax
		
		if system.tag.readBlocking(tagPath + '/Alarming/Low/Setpoint.enabled')[0].value:
			lowSP = system.tag.readBlocking(tagPath + '/Alarming/Low/Setpoint')[0].value
		else:
			lowSP = euMin
			
		if lowSP < euMin:
			lowSP = euMin
		
		minToday = calcToday.getValueAt(0,1)
		maxToday = calcToday.getValueAt(0,2)
		
	
		
		desiredHigh = 0
		desiredLow = 0
		
		try:
			maxToday = math.ceil(maxToday)
			minToday = math.floor(minToday)
		except:
			maxToday = highSP
			minToday = lowSP
		
		if maxToday < highSP and maxToday > lowSP:
			desiredHigh = maxToday
		elif highSP != 1:
			desiredHigh = highSP
		else:
			desiredHigh = euMax
			
		if minToday < highSP and minToday > lowSP:
			desiredLow = minToday
		elif lowSP != 1:
			desiredLow = lowSP
		else:
			desiredLow = euMin
			
			
		if desiredHigh != None and desiredLow != None and desiredHigh < euMax and desiredLow > euMin and desiredHigh > desiredLow:
			print tagPath
			print euMax
			print highSP
			print 'H: ', desiredHigh
			print 'L: ', desiredLow
			print lowSP
			print euMin
			
	#		system.tag.writeBlocking(tagPath + '/Engineering/DesiredHigh', desiredHigh)
	#		system.tag.writeBlocking(tagPath + '/Engineering/DesiredLow', desiredLow)