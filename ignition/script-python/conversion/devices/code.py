

# devices file is currently created manually
# headers: Name, KepwareChannel, KepwareDevice, Driver, Model, PLCType, IgnitionDriver, ID, IP, TagCount





# ------------- Create Ignition devices ------------------------
#import csv
#filePath = 'C:\VM Shared Drive\Ventura\Ventura\Kepware\devices.csv'  # devices file is currently made manually
#
#with open(filePath) as csvFile:
#	reader = csv.DictReader(csvFile)
#	for row in reader:
#
#		deviceName = row['\xef\xbb\xbfName']
#		deviceType = row['IgnitionDriver']
#		hostname = row['IP']
#		
#		print deviceName + '   ' + deviceType + '   ' + hostname
#		
#		system.device.addDevice(	deviceName=deviceName,
#									deviceType=deviceType, 
#									deviceProps={'HostName':hostname})