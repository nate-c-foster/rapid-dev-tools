import java.io.File as File
import java.io.InputStream as InputStream
import java.io.ByteArrayInputStream as ByteArrayInputStream
import java.nio.charset.StandardCharsets as StandardCharsets
import java.lang.String as String
import javax.xml.parsers.DocumentBuilder as DocumentBuilder
import javax.xml.parsers.DocumentBuilderFactory as DocumentBuilderFactory
import org.w3c.dom.Document as Document
import org.w3c.dom.NodeList as NodeList
import org.w3c.dom.Node as Node
import org.w3c.dom.Element as Element


DATA_TYPE_MAPPING_PYTHON = {"BOOL":bool, "BIT":bool, "SINT":int, "INT":int, "DINT":int, "LINT": int, "REAL":float, "STRING":str}
DATA_TYPE_MAPPING_IGNITION = {"BOOL":"Boolean", "BIT":"Boolean", "SINT":"Int1", "INT":"Int2", "DINT":"Int4", "LINT":"Int8", "REAL":"Float4", "STRING":"String"}
DATA_TYPE_MAPPING_SIMULATION = {"BOOL":"Boolean", "BIT":"Boolean", "SINT":"Int16", "INT":"Int16", "DINT":"Int32", "LINT":"Int64", "REAL":"Float", "STRING":"String"}
DATA_TYPE_MAPPING_KEPWARE_TO_AB = {"Boolean":"BIT", "Word": "DINT", "DWord":"DINT",  "Float":"REAL"}
DEFAULT_SIMULATION = {"BOOL":"false", "BIT":"false", "SINT":"0", "INT":"0", "DINT":"0", "LINT": "0", "REAL":"0", "STRING":""}



# --- generate both SIM file and tags file

#deviceName = 'GRAFTON_ELEV_TANK'
#l5xFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Alton PLC Programs/Alton PLC Programs/PLC_Grafton_ET.L5X'
#simFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Alton PLC Programs/SIM/' + deviceName + '.csv'
#tagsFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Alton PLC Programs/Tags/' + deviceName + '.csv'
#l5xString = system.file.readFileAsString(l5xFilePath, 'UTF-8')
#
#
#dsSIM = conversion.L5X.generateSimulation(l5xString)
#dataset.export.toCSV(dsSIM, simFilePath)
#
#dsTags = conversion.L5X.getAllTags(l5xString,deviceName)
#dataset.export.toCSV(dsTags, tagsFilePath)















#l5xFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Alton PLC Programs/Alton PLC Programs/ControlLogix/UV/PLC-UV.L5X'
#tagsFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Alton PLC Programs/Tags/UV.csv'
#l5xString = system.file.readFileAsString(l5xFilePath, 'UTF-8')
#
#ds = conversion.L5X.getAllTags(l5xString,'UV')
#dataset.export.toCSV(ds, tagsFilePath)


def getAllTags(l5xString, deviceName):



	udts, globalTags = parse(l5xString)
	
	paths = []
	rows = []
	
	for tag in globalTags:
		paths = paths + conversion.L5X.getPaths(tag, udts, tag['data'])
		
	for path in paths:
		value = path['value']

	
		rows.append([deviceName, path['path'], path['dataType'],  path['value'], path['description']])
			
			
	headers = ['Device', 'Path', 'DataType', 'Value', 'Description']
	
	return system.dataset.toDataSet(headers, rows)
	



#l5xFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Alton PLC Programs/Alton PLC Programs/ControlLogix/Forest Homes Tank/Forest_Homes_Tank.L5X'
#tagsFilePath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Alton PLC Programs/Alton PLC Programs/ControlLogix/Forest Homes Tank/FORESTHOMES_TANKPLC_SIM.csv'
#l5xString = system.file.readFileAsString(l5xFilePath, 'UTF-8')
#
#ds = conversion.L5X.generateSimulation(l5xString)
#
#dataset.export.toCSV(ds, tagsFilePath)


	
def generateSimulation(l5xString):

	udts, globalTags = parse(l5xString)
		
	paths = []
	rows = []
	
	for tag in globalTags:
		paths = paths + conversion.L5X.getPaths(tag, udts, tag['data'])
		
	for path in paths:

		dataType = DATA_TYPE_MAPPING_SIMULATION[path['dataType']]
	
		value = simulationValue(path['value'], dataType)

		rows.append([0, path['path'], value, dataType])
	
	headers = ['Time Interval', 'Browse Path', 'Value Source', 'Data Type']
	
	return system.dataset.toDataSet(headers, rows)
	



def simulationValue(value, dataType):

		if dataType == 'Boolean':
			if value == 'false':
				value = 'FALSE'
			if value == 'true':
				value = 'TRUE'

		elif "Int" in dataType:
			try:
				value = str(int(value))
			except:
				value = '0'
				
		elif dataType == 'Float':
			try:
				value = str(float(value))
			except:
				value = '0.0'
				
		return value




def getPaths(tag, udts, data):
	# recursive magic to build full paths

	dimension = tag['dimension']
	
	# atomic
	if not dimension or dimension == [0]:
	
		dataType = tag['dataType']
		
		# atomic primative
		if isPrimative(dataType):
			return [{'path': tag['name'], 'dataType': tag['dataType'], 'description':tag['description'], 'value': data}]
			
		# atomic udt
		else:
			
			paths = []
			for udt in udts:
				if udt['name'] == dataType:
					udtTags = udt['tags']
					for udtTag in udtTags:

						if udtTag['name'] in data.keys():
							dataRecursive = data[udtTag['name']]
						else:
							if isPrimative(udtTag['dataType']):
								dataRecursive = DEFAULT_SIMULATION[udtTag['dataType']]
							else:
								dataRecursive = []

						paths = paths + getPaths(udtTag, udts, dataRecursive)
						
					paths = map(lambda x : {'path':tag['name'] + '.' + x['path'], 'dataType':x['dataType'], 'description':x['description'], 'value':x['value']}, paths)
					break
					
			return paths
					
		
	# array
	else:

		dataType = tag['dataType']
		
		fullPaths = []
		if len(dimension) == 1:
	
			# 1-dimensional array of primatives
			if isPrimative(dataType):
				fullPaths = [{'path': tag['name'] + '[' + str(i) + ']', 'dataType': tag['dataType'], 'description':tag['description'], 'value': data[i]} for i in range(dimension[0])]
	
	
			# 1-dimensional array of udts
			else:
				

				for udt in udts:
					if udt['name'] == dataType:
						udtTags = udt['tags']
						
						for i in range(int(dimension[0])):
						
							paths = []
							for udtTag in udtTags:
							
								if udtTag['name'] in data[i].keys():
									dataRecursive = data[i][udtTag['name']]
								else:
									if isPrimative(udtTag['dataType']):
										dataRecursive = DEFAULT_SIMULATION[udtTag['dataType']]
									else:
										dataRecursive = []
							
								paths = paths + getPaths(udtTag, udts, dataRecursive)
								
							fullPaths = fullPaths + map(lambda x : {'path':tag['name'] + '[' + str(i) + ']'+ '.' + x['path'], 'dataType':x['dataType'], 'description':x['description'], 'value':x['value']}, paths)
							
		if len(dimension) == 2:
	
			# 2-dimensional array of primatives
			if isPrimative(dataType):
				fullPaths = [{'path': tag['name'] + '[' + str(i) + ',' + str(j) + ']', 'dataType': tag['dataType'], 'description':tag['description'], 'value':data[i][j]} for i in range(dimension[0]) for j in range(dimension[1])]
	
			# 2-dimensional array of udts
			else:
				
				for udt in udts:
					if udt['name'] == dataType:
						udtTags = udt['tags']
						
						for i in range(dimension[0]):
							for j in range(dimension[1]):				

								paths = []
								for udtTag in udtTags:
				
									if udtTag['name'] in data[i][j].keys():
										dataRecursive = data[i][j][udtTag['name']]
									else:
										if isPrimative(udtTag['dataType']):
											dataRecursive = DEFAULT_SIMULATION[udtTag['dataType']]
										else:
											dataRecursive = []
								
									paths = paths + getPaths(udtTag, udts, dataRecursive)
							
								fullPaths = fullPaths + map(lambda x : {'path':tag['name'] + '[' + str(i) + ',' + str(j) + ']' +  '.' + x['path'], 'dataType':x['dataType'], 'description':x['description'], 'value':x['value']}, paths)

		if len(dimension) > 2:
			# currently unsupported
			pass

		
		return fullPaths







def parse(l5xString):

	l5xString = String(l5xString)

	xmlStream = ByteArrayInputStream(l5xString.getBytes(StandardCharsets.UTF_8))

	dbFactory = DocumentBuilderFactory.newInstance()
	dBuilder = dbFactory.newDocumentBuilder()
	doc = dBuilder.parse(xmlStream)
	doc.getDocumentElement().normalize()


	# ---------   get all data type tags ------------------
	dataTypeNodes = doc.getElementsByTagName("DataType")
	udts = getBuiltInUdts()
	
	for i in range(dataTypeNodes.getLength()):
		dataTypeNode = dataTypeNodes.item(i)
		dataTypeName = dataTypeNode.getAttribute("Name")
		dataTypeDescriptionNode = dataTypeNode.getElementsByTagName("Description").item(0)
		dataTypeDescription = dataTypeDescriptionNode.getTextContent().strip() if dataTypeDescriptionNode else ''
		dataTypeFamily = dataTypeNode.getAttribute("Family")
		
		if dataTypeNode.getNodeType() == Node.ELEMENT_NODE:

			memberNodes = dataTypeNode.getElementsByTagName("Member")
			
			tags = []
			for j in range(memberNodes.getLength()):
				memberNode = memberNodes.item(j)
				
				hidden = memberNode.getAttribute("Hidden")
				dimensionString = memberNode.getAttribute("Dimension")
				dimension = map(int, dimensionString.split(' ')) if dimensionString else [0]

				
				tags.append({		'name': memberNode.getAttribute("Name"),
									'description': memberNode.getTextContent().strip(),
									'dataType': memberNode.getAttribute("DataType"),
									'dimension': dimension,
									'selected': True,
									'hidden': True if hidden == 'true' else False
									})
										
		udts.append({		'name': dataTypeName,
							'description': dataTypeDescription,
							'tags': tags,
							'stringFamily': True if dataTypeFamily == 'StringFamily' else False
							})
							
							
	# ----------- get all AOI tags ----------------------------
	
	aoiNodes = doc.getElementsByTagName("AddOnInstructionDefinition")

	
	for i in range(aoiNodes.getLength()):
		aoiNode = aoiNodes.item(i)
		aoiName = aoiNode.getAttribute("Name")
		aoiDescriptionNode = aoiNode.getElementsByTagName("Description").item(0)
		aoiDescription = aoiDescriptionNode.getTextContent().strip() if aoiDescriptionNode else ''
	
		if aoiNode.getNodeType() == Node.ELEMENT_NODE:

			parameterNodes = aoiNode.getElementsByTagName("Parameter")
			
			tags = []
			for j in range(parameterNodes.getLength()):
				parameterNode = parameterNodes.item(j)
				
				parameterDescriptionNode = parameterNode.getElementsByTagName("Description").item(0)
				parameterDescription = parameterDescriptionNode.getTextContent().strip() if parameterDescriptionNode else ''
				
				tags.append({		'name': parameterNode.getAttribute("Name"),
									'description': parameterDescription,
									'dataType': parameterNode.getAttribute("DataType"),
									'dimension': [0],
									'selected': True,
									'hidden': False
									})
									
										
		udts.append({		'name': aoiName,
							'description': aoiDescription,
							'tags': tags,
							'stringFamily': False
							})
	
	
	# ----------- get all global tags ---------------------
	
	tagNodes = doc.getElementsByTagName("Tag")

	globalTags = []
	for i in range(tagNodes.getLength()):
		tagNode = tagNodes.item(i)
		tagName = tagNode.getAttribute("Name")
		#print tagName
		tagDescriptionNode = tagNode.getElementsByTagName("Description").item(0)
		tagDescription = tagDescriptionNode.getTextContent().strip() if tagDescriptionNode else ''
		tagDataType = tagNode.getAttribute("DataType")
		tagDimensionString = tagNode.getAttribute("Dimensions")
		tagDimension = map(int, tagDimensionString.split(' ')) if tagDimensionString else [0]
		
		data = None

		if tagNode.getNodeType() == Node.ELEMENT_NODE:

			dataNodes = tagNode.getElementsByTagName("Data")
			for j in range(dataNodes.getLength()):
				dataNode = dataNodes.item(j)
				dataFormat = dataNode.getAttribute("Format")
				
				if dataFormat == 'Decorated' or dataFormat == 'Message' or dataFormat == 'Alarm':
					data = parseDataNode(dataNode)
		
					
		globalTags.append({		'name': tagName,
								'description': tagDescription,
								'dataType': tagDataType,
								'dimension': tagDimension,
								'selected': True,
								'hidden': False,
								'data': data
								})
	
	
	# ----------- get all program tags ---------------------
	#        ^       TODO if needed        ^



	return (udts, globalTags)






def isPrimative(dataType):
	primatives = ['BIT', 'BOOL', 'DINT', 'SINT', 'INT', 'LINT', 'REAL','STRING']
	return dataType in primatives
	
	



def parseDataNode(dataNode):


	childrenNodes = dataNode.getChildNodes()
	for j in range(childrenNodes.getLength()):
		childNode = childrenNodes.item(j)
		if childNode.getNodeType() == Node.ELEMENT_NODE:
			dataNodeType =  childNode.getNodeName()
			
			# return a single value
			if dataNodeType == 'DataValue':
				dataType = childNode.getAttribute("DataType")
				value = childNode.getAttribute("Value")
				return valueTransform(value)
			
			# return a list (recursive)
			elif dataNodeType == 'Array':
				
				return parseArrayNode(childNode)
				

			# return a dictionary (recursive)
			elif dataNodeType == 'Structure':
				return parseStructureNode(childNode)


			# return a dictionary of parameters
			# not that most of these parameters don't match the UDTs parameters
			
			elif dataNodeType == 'MessageParameters':
				return parseAttributesNode(childNode)
				
			# return a dictionary of parameters
			
			elif dataNodeType == 'AlarmAnalogParameters':
				return parseAttributesNode(childNode)
				
			# return a dictionary of parameters
			
			elif dataNodeType == 'AlarmDigitalParameters':
				return parseAttributesNode(childNode)


			else:
				return None
					
					
def parseArrayNode(arrayNode):

	dataType = arrayNode.getAttribute("DataType")
	dimensions = map(int,arrayNode.getAttribute("Dimensions").split(','))
	elements = initializeList(dimensions, '0')
	

	elementNodes = getChildByTagName(arrayNode, 'Element')
	for elementNode in elementNodes:

		if elementNode.getNodeType() == Node.ELEMENT_NODE:
		
			indexes = map(int, elementNode.getAttribute("Index").strip('[]').split(','))

			if elementNode.hasAttribute("Value"):
				
				value = valueTransform(elementNode.getAttribute("Value"))
				
				
				if len(indexes) == 1:
					elements[indexes[0]] = value
				elif len(indexes) == 2:
					elements[indexes[0]][indexes[1]] = value
				elif len(indexes) == 3:
					elements[indexes[0]][indexes[1]][indexes[2]] = value
					
			else:
				if len(indexes) == 1:
					elements[indexes[0]] = parseDataNode(elementNode)
				elif len(indexes) == 2:
					elements[indexes[0]][indexes[1]] = parseDataNode(elementNode)
				elif len(indexes) == 3:
					elements[indexes[0]][indexes[1]][indexes[2]] = parseDataNode(elementNode)
					
	return elements
	
	
	
	



def parseStructureNode(structureNode):
	members = {}
	
	
	memberNodes = getChildByTagName(structureNode, "DataValueMember")
	for memberNode in memberNodes:
		if memberNode.getNodeType() == Node.ELEMENT_NODE:
			name = memberNode.getAttribute("Name")
			if memberNode.hasAttribute("Value"):
				dataType = memberNode.getAttribute("DataType")
				value = valueTransform(memberNode.getAttribute("Value"))
				members[name] = value
			else:
				members[name] = parseDataNode(memberNode)
				
				
	arrayNodes = getChildByTagName(structureNode, "ArrayMember")
	for arrayNode in arrayNodes:
		if arrayNode.getNodeType() == Node.ELEMENT_NODE:
			name = arrayNode.getAttribute("Name")
			members[name] = parseArrayNode(arrayNode)
			
			
	structureMemberNodes = getChildByTagName(structureNode, "StructureMember")
	for structureMemberNode in structureMemberNodes:
		#structureMemberNode = structureMemberNodes.item(k)
		if structureMemberNode.getNodeType() == Node.ELEMENT_NODE:
			name = structureMemberNode.getAttribute("Name")
			members[name] = parseStructureNode(structureMemberNode)
				
	return members
	
	



def parseAttributesNode(attributesNode):
	parameters = {}

	attributeNodes = attributesNode.getAttributes()
	for a in range(attributeNodes.getLength()):
		attributeNode = attributeNodes.item(a)
		attributeName = attributeNode.getNodeName()
		attributeValue = valueTransform(attributeNode.getNodeValue())
		parameters[attributeName] = attributeValue
		
	return parameters



def getChildByTagName(node, tagName):
	
	nodes = []
	childNodes = node.getChildNodes()
	for i in range(childNodes.getLength()):
		childNode = childNodes.item(i)
		if childNode.getNodeName() == tagName:
			nodes.append(childNode)
			
	return nodes




def initializeList(shape, value):

	if shape == []:
		return value
	else:
		return [initializeList(shape[1:],value)] * shape[0]




def valueTransform(value):
	if "DT#" in str(value):
		value = '0'
	elif str(value).startswith('$'):
		value = '0'
	elif str(value).startswith('16#'):
		value = str(int(value.replace('16#', '0x'),0))
	return value


	
def getBuiltInUdts():

	udts = []
	
	# Add TIMER, COUNTER, PID, MESSAGE, CONTROL, ALARM_DIGITAL, ALARM_ANALOG
	
	
	#--------------------- TIMER --------------------------------------------
	udt = {
	  "name": "TIMER",
	  "description": "Built-in timer",
	  "stringFamily": False,
	  "tags": [
		{
		  "name": "DN",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "EN",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "TT",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "PRE",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ACC",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		}
	  ]
	}
	udts.append(udt)
	
	
	
	
	#--------------------- COUNTER --------------------------------------------
	udt = {
	  "name": "COUNTER",
	  "description": "Built-in counter",
	  "stringFamily": False,
	  "tags": [
		{
		  "name": "CD",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "CU",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "DN",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "OV",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "UN",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "PRE",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ACC",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		}
	  ]
	}
	udts.append(udt)
	





	#--------------------- PID --------------------------------------------
	udt = {
	  "name": "PID",
	  "description": "Built-in counter",
	  "stringFamily": False,
	  "tags": [
		{
		  "name": "CTL",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "EN",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "CT",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "CL",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "PVT",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "DOE",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "SWM",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "CA",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "MO",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "PE",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "NDF",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "NOBC",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "NOZC",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "INI",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "SPOR",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "OLL",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "OLH",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "EWD",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "DVNA",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "DVPA",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "PVLA",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "PVHA",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "SP",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "KP",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "KI",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "KD",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "BIAS",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "MAXS",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "MINS",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "DB",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "SO",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "MAXO",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "MINO",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "UPD",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "PV",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ERR",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "OUT",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "PVH",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "PVL",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "DVP",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "DVN",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "PVDB",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "DVDB",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "MAXI",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "MINI",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "TIE",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "MAXCV",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "MINCV",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "MINTIE",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "MAXTIE",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "DATA",
		  "description": "",
		  "dataType": "REAL[17]",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		}
	  ]
	}
	udts.append(udt)










	#--------------------- MESSAGE --------------------------------------------
	udt = {
	  "name": "MESSAGE",
	  "description": "Built-in Message",
	  "stringFamily": False,
	  "tags": [
		{
		  "name": "Flags",
		  "description": "",
		  "dataType": "INT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "EW",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ER",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "DN",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ST",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "TO",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "EN_CC",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ERR",
		  "description": "",
		  "dataType": "INT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "EXERR",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ERR_SRC",
		  "description": "",
		  "dataType": "SINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "DN_LEN",
		  "description": "",
		  "dataType": "INT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "REQ_LEN",
		  "description": "",
		  "dataType": "INT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "DestinationLink",
		  "description": "",
		  "dataType": "INT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "DestinationNode",
		  "description": "",
		  "dataType": "INT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "SourceLink",
		  "description": "",
		  "dataType": "INT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "Class",
		  "description": "",
		  "dataType": "INT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "Attribute",
		  "description": "",
		  "dataType": "INT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "Instance",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "LocalIndex",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "Channel",
		  "description": "",
		  "dataType": "SINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "Rack",
		  "description": "",
		  "dataType": "SINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "Group",
		  "description": "",
		  "dataType": "SINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "Slot",
		  "description": "",
		  "dataType": "SINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "Path",
		  "description": "",
		  "dataType": "STRING",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "RemoteIndex",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "RemoteElement",
		  "description": "",
		  "dataType": "STRING",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "UnconnectedTimeout",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ConnectionRate",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "TimeoutMultiplier",
		  "description": "",
		  "dataType": "SINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		}
	  ]
	}
	udts.append(udt)
	
	
	
	
	#--------------------- CONTROL --------------------------------------------
	udt = {
	  "name": "CONTROL",
	  "description": "Built-in Control",
	  "stringFamily": False,
	  "tags": [
		{
		  "name": "LEN",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "POS",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "EN",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "EU",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "DN",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "EM",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ER",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "UL",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "IN",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "FD",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		}
	  ]
	}
	udts.append(udt)
	
	
	
	
	
	
	

	#--------------------- ALARM_DIGITAL --------------------------------------------
	udt = {
	  "name": "ALARM_DIGITAL",
	  "description": "Built-in Control",
	  "stringFamily": False,
	  "tags": [
		{
		  "name": "EnableIn",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "In",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "InFault",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "Condition",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "AckRequired",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "Latched",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ProgAck",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "OperAck",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ProgReset",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "OperReset",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ProgSuppress",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "OperSuppress",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ProgUnsuppress",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "OperUnsuppress",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "OperShelve",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ProgUnshelve",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "OperUnshelve",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ProgDisable",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "OperDisable",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ProgEnable",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "OperEnable",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "AlarmCountReset",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "UseProgTime",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ProgTime",
		  "description": "",
		  "dataType": "LINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "Severity",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "MinDurationPRE",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ShelveDuration",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "MaxShelveDuration",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "EnableOut",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "InAlarm",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "Acked",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "InAlarmUnack",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "Suppressed",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "Shelved",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "Disabled",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "Commissioned",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "MinDurationACC",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "AlarmCount",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "InAlarmTime",
		  "description": "",
		  "dataType": "LINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "AckTime",
		  "description": "",
		  "dataType": "LINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "RetToNormalTime",
		  "description": "",
		  "dataType": "LINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "AlarmCountResetTime",
		  "description": "",
		  "dataType": "LINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ShelveTime",
		  "description": "",
		  "dataType": "LINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "UnshelveTime",
		  "description": "",
		  "dataType": "LINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "Status",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "InstructFault",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "InFaulted",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "SeverityInv",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		}
	  ]
	}
	udts.append(udt)





	
	
	
	#--------------------- ALARM_ANALOG --------------------------------------------
	udt = {
	  "name": "ALARM_ANALOG",
	  "description": "Built-in ALARM_ANALOG",
	  "stringFamily": False,
	  "tags": [
		{
		  "name": "EnableIn",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"true",
		  "hidden": False
		},
		{
		  "name": "In",
		  "description": "",
		  "dataType": "Real",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "InFault",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HHEnabled",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HEnabled",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "LEnabled",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "LLEnabled",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "AckRequired",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ProgAckAll",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "OperAckAll",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HHProgAck",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HHOperAck",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HProgAck",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HOperAck",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "LProgAck",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "LOperAck",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "LLProgAck",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "LLOperAck",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ROCPosProgAck",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ROCPosOperAck",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ROCNegProgAck",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ROCNegOperAck",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ProgSuppress",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "OperSuppress",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ProgUnsuppress",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "OperUnsuppress",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HHOperShelve",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HOperShelve",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "LOperShelve",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "LLOperShelve",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ROCPosOperShelve",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ROCNegOperShelve",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ProgUnshelveAll",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HHOperUnshelve",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HOperUnshelve",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "LOperUnshelve",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "LLOperUnshelve",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ROCPosOperUnshelve",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ROCNegOperUnshelve",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ProgDisable",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "OperDisable",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ProgEnable",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "OperEnable",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "AlarmCountReset",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HHMinDurationEnable",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HMinDurationEnable",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "LMinDurationEnable",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "LLMinDurationEnable",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HHLimit",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "HLimit",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "LLimit",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "LLLimit",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "HHSeverity",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "HSeverity",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "LSeverity",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "LLSeverity",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "MinDurationPRE",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ShelveDuration",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "MaxShelveDuration",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "Deadband",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ROCPosLimit",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ROCPosSeverity",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ROCNegLimit",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ROCNegSeverity",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ROCPeriod",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "EnableOut",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "InAlarm",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "AnyInAlarmUnack",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HHInAlarm",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HInAlarm",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "LInAlarm",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "LLInAlarm",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ROCPosInAlarm",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ROCNegInAlarm",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ROC",
		  "description": "",
		  "dataType": "REAL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HHAcked",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HAcked",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "LAcked",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "LLAcked",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ROCPosAcked",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ROCNegAcked",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HHInAlarmUnack",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HInAlarmUnack",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "LInAlarmUnack",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "LLInAlarmUnack",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ROCPosInAlarmUnack",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ROCNegInAlarmUnack",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "Suppressed",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HHShelved",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "HShelved",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "LShelved",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "LLShelved",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ROCPosShelved",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ROCNegShelved",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "Disabled",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "Commissioned",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "MinDurationACC",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "HHInAlarmTime",
		  "description": "",
		  "dataType": "LINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "HInAlarmTime",
		  "description": "",
		  "dataType": "LINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "LInAlarmTime",
		  "description": "",
		  "dataType": "LINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "LLInAlarmTime",
		  "description": "",
		  "dataType": "LINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "HHAlarmCount",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "HAlarmCount",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "LAlarmCount",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "LLAlarmCount",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ROCPosInAlarmTime",
		  "description": "",
		  "dataType": "LINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ROCNegInAlarmTime",
		  "description": "",
		  "dataType": "LINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ROCPosAlarmCount",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ROCNegAlarmCount",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "AckTime",
		  "description": "",
		  "dataType": "LINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "RetToNormalTime",
		  "description": "",
		  "dataType": "LINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "AlarmCountResetTime",
		  "description": "",
		  "dataType": "LINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ShelveTime",
		  "description": "",
		  "dataType": "LINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "UnshelveTime",
		  "description": "",
		  "dataType": "LINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "Status",
		  "description": "",
		  "dataType": "DINT",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "InstructFault",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "InFaulted",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "SeverityInv",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "AlarmLimitsInv",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "DeadbandInv",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ROCPosLimitInv",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ROCNegLimitInv",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ROCPeriodInv",
		  "description": "",
		  "dataType": "BOOL",
		  "dimension":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		}
	  ]
	}
	udts.append(udt)
	
	return udts











# ------------------------- Testing -----------------------------------------------------------------------------------



#filepath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Alton PLC Programs/Alton PLC Programs/ControlLogix/UV/PLC-UV.L5X'
#l5xString = system.file.readFileAsString(filepath, 'UTF-8')
#
#udts, tags = conversion.L5X.parse(l5xString)
#
#
#paths = []
#for i, tag in enumerate(tags):
#	print tag
#	paths = paths + conversion.L5X.getPaths(tag, udts, tag['data'])
#
#print "--------------  UDTs  --------------"
#for udt in udts:
#	print udt['name']
#	print udt['tags']
#	
#	
#print "\n\n\n------------------ Tags ---------------------"
#for i, tag in enumerate(tags):
#	print tag
#	if tag['name'] == 'UV2_DAILY_REPORT_DATA':
#		print i
#	
#	
#	
#print tags[24] # simple atomic
#print tags[26] # array atomic
#print tags[84] # multi dim array
#print tags[46] # simple udt
#print tags[0] # alarm analog
#print tags[3] # alarm digital
#print tags[48] # message
#print tags[28] # array of udts
#print tags[63]
#
#print tags[71]
#print tags[71]['name']
#print tags[71]['data']
#paths = conversion.L5X.getPaths(tags[71], udts, tags[71]['data'])
#
#for path in paths:
#	print path