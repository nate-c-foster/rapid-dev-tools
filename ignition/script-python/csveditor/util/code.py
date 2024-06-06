
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