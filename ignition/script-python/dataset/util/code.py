
import csv

def csvToMap(filePath, keyName, valueName):
	"""Turns two columns of a csv file into a dictionary mapping
	
	Args:
		filePath (str): Path to file (use '/')
		keyName (str): Column name to be used as dictionary key
		keyName (str): Column name to be used as dictionary value
		
	Returns:
		Python dictionary
	"""
	dictMap = {}
	with open(filePath) as csvfile:
		reader = csv.DictReader(csvfile)
		tagMap = {row['keyName']:row['valueName'] for row in reader}
		
	dictMap
	
	
	
	
	
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
	elif valueSource == 'expression':
		valueProperty = system.tag.readBlocking(tagPath + '.expression')[0].value
	else:
		valueProperty = 'BAD_VALUE_SOURCE'
		
	return (valueSource, valueProperty, valueQuality, value)