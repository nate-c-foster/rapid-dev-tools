

import csv
import os




def fromIgnitionCSV(filePath):

	csvString = system.file.readFileAsString(filePath)
	return system.dataset.fromCSV(csvString)




def fromStandardCSV(filePath):

	headers = []
	data = []
	with open(filePath) as csvfile:
		reader = csv.DictReader(csvfile)
		headers = reader.fieldnames
		for row in reader:
			data.append([row[key] for key in headers])
			
	return system.dataset.toDataSet(headers, data)



# unions multiple CSVs
def fromStandardCSVs(folderPath, addFileNameColumn=False):
	
	filePaths = [folderPath + '/' + fileName for fileName in os.listdir(folderPath) if fileName.endswith('.csv')]

	if filePaths > 0:
		ds = fromStandardCSV(filePaths[0])
		if addFileNameColumn:
			fileName = filePaths[0].split('/')[-1]
			fileName = fileName.split('.')[0]
			ds = system.dataset.addColumn(ds, 0, [fileName for row in range(ds.getRowCount())], 'FileName', str)

		for filePath in filePaths[1:]:
			dsRight = fromStandardCSV(filePath)
			if addFileNameColumn:
				fileName = filePath.split('/')[-1]
				fileName = fileName.split('.')[0]
				dsRight = system.dataset.addColumn(dsRight, 0, [fileName for row in range(dsRight.getRowCount())], 'FileName', str)
			
			ds = dataset.operation.union(ds, dsRight)
			
	return ds

	

	
	





