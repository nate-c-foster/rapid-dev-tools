



def innerJoin(dataset1, dataset2, joinPredicate, columns1, columns2):
	
	
	selectHeaders = columns1 + columns2
	data = []
	
	allHeaders = system.dataset.getColumnHeaders(dataset1) + system.dataset.getColumnHeaders(dataset2)
	
	pyds1 = system.dataset.toPyDataSet(dataset1)
	pyds2 = system.dataset.toPyDataSet(dataset2)
	
	for row1 in pyds1:
		for row2 in pyds2:
			if joinPredicate(row1, row2):
				data.append( list(row1) + list(row2))
				
	return filterColumns(system.dataset.toDataSet(allHeaders, data), selectHeaders)
	
def leftOuterJoint(dataset1, dataset2, joinPredicate, columns1, columns2):
	selectHeaders = ['left_' + columnName for columnName in columns1] + ['right_' + columnName for columnName in columns2]
	data = []
	
	leftHeaders = ['left_' + columnName for columnName in system.dataset.getColumnHeaders(dataset1)]
	rightHeaders = ['right_' + columnName for columnName in system.dataset.getColumnHeaders(dataset2)]
	
	allHeaders = leftHeaders + rightHeaders 
	
	pyds1 = system.dataset.toPyDataSet(dataset1)
	pyds2 = system.dataset.toPyDataSet(dataset2)
	
	for row1 in pyds1:
	
		match = False
		for row2 in pyds2:
			if joinPredicate(row1, row2):
				match = True
				data.append( list(row1) + list(row2))
				
		# right row empty if no match
		if not match:
			data.append( list(row1) + ['' for header in rightHeaders])
				
	return filterColumns(system.dataset.toDataSet(allHeaders, data), selectHeaders)




def union(dataset1, dataset2):
	return system.dataset.appendDataset(dataset1, dataset2)

	
	
def columnMap(dataset, columnName, transform):
	pass
	
	
	
	
def filterColumns(dataset, columns):
	return system.dataset.filterColumns(dataset, columns)
	
	
	
	
def filterRows(dataset, predicate):
	pass


def renameColumns(dataset, columnNames):
	
	pyds = system.dataset.toPyDataSet(dataset)
	data = [list(row) for row in pyds]
	return system.dataset.toDataSet(columnNames, data)


def formatDataset(dataset, conditional, formatDataset=None):
	"""
	Generates a format dataset, used for conditional highlighting when exporting to Excel
	
	Args:
		dataset (dataset):
		conditional ( dict -> dict ): Takes dataset row as dict and returns a dict with the format names as values
		formatDataset (dataset): if there is alread a formatDataset for this dataset then pass it in here
		
	Returns:
		formatDataset (dataset) - dataset with same shape as input datset but with format names
	"""
	
	
	headers = system.dataset.getColumnHeaders(dataset)
	
	# create blank formatDataset if is doen't exist
	if not formatDataset:
		data = []
		for row in range(dataset.getRowCount()):
			data.append(['' for header in headers])
			
		formatDataset = system.dataset.toDataSet(headers, data)
	
	
	pyds = system.dataset.toPyDataSet(dataset)
	
	data = []
	for i, row in enumerate(pyds):
		formatDataset = system.dataset.updateRow(formatDataset, i, conditional(row))
	
	return formatDataset
	