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



#filepath = 'C:/VM Shared Drive/ILAW Alton WA/ILAW Alton WA/Alton PLC Programs/Alton PLC Programs/ControlLogix/UV/PLC-UV.L5X'
#l5xString = system.file.readFileAsString(filepath, 'UTF-8')
#
#udts, tags = conversion.L5X.parse(l5xString)
#
#print "--------------  UDTs  --------------"
#for udt in udts:
#	print udt['name']
#	print udt['tags']
#	
#	
#print "\n\n\n------------------ Tags ---------------------"
#for tag in tags:
#	print tag


DATA_TYPE_MAPPING_PYTHON = {"BOOL":bool, "BIT":bool, "SINT":int, "INT":int, "DINT":int, "LINT": int, "REAL":float, "STRING":str}
DATA_TYPE_MAPPING_IGNITION = {"BOOL":"Boolean", "BIT":"Boolean", "SINT":"Int1", "INT":"Int2", "DINT":"Int4", "REAL":"Float4", "STRING":"String"}
DATA_TYPE_MAPPING_SIMULATION = {"BOOL":"Boolean", "BIT":"Boolean", "SINT":"Int16", "INT":"Int16", "DINT":"Int32", "REAL":"Float", "STRING":"String"}
DEFAULT_SIMULATION = {"BOOL":"false", "BIT":"false", "SINT":"0", "INT":"0", "DINT":"0", "LINT": "0", "REAL":"0", "STRING":""}





def getAllTags(l5xString):
	udts, globalTags = parse(l5xString)
	
	
	for globalTag in globalTags:
		
		name = globalTag['name']
		description = globalTag['description']
		dataType = globalTag['dataType']
		dimension = globalTag['dimension']
		data = globalTag['data']


	
	# create dataset ['TagPath', 'DataType', 'Value']



def getPaths(tag, udts, data):
	# recursive magic to build full paths

	dimension = tag['dimension']
	
	# atomic
	if not dimension or dimension == [0]:
	
		dataType = tag['dataType']
		
		# atomic primative
		if isPrimative(dataType):
			return [{'path': tag['name'], 'dataType': tag['dataType'], 'value': data}]
			
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
						
					paths = map(lambda x : {'path':tag['name'] + '.' + x['path'], 'dataType':x['dataType'], 'value':x['value']}, paths)
					break
					
			return paths
					
		
	# array
	else:

		dataType = tag['dataType']
		
		fullPaths = []
		if len(dimension) == 1:
	
			# 1-dimensional array of primatives
			if isPrimative(dataType):
				fullPaths = [{'path': tag['name'] + '[' + str(i) + ']', 'dataType': tag['dataType'], 'value': data[i]} for i in range(dimension[0])]
	
	
			# 1-dimensional array of udts
			else:
				
				paths = []
				for udt in udts:
					if udt['name'] == dataType:
						udtTags = udt['tags']
						for udtTag in udtTags:
						
							for i in range(int(dimension[0])):
							
								if udtTag['name'] in data[i].keys():
									dataRecursive = data[i][udtTag['name']]
								else:
									if isPrimative(udtTag['dataType']):
										dataRecursive = DEFAULT_SIMULATION[udtTag['dataType']]
									else:
										dataRecursive = []
							
								paths = paths + getPaths(udtTag, udts, dataRecursive)
							
							
								fullPaths = fullPaths + map(lambda x : {'path':tag['name'] + '[' + str(i) + ']'+ '.' + x['path'], 'dataType':x['dataType'], 'value':x['value']}, paths)
							
		if len(dimension) == 2:
	
			# 2-dimensional array of primatives
			if isPrimative(dataType):
				fullPaths = [{'path': tag['name'] + '[' + str(i) + ',' + str(j) + ']', 'dataType': tag['dataType'], 'value':data[i][j]} for i in range(dimension[0]) for j in range(dimension[1])]
	
			# 2-dimensional array of udts
			else:
				
				paths = []
				for udt in udts:
					if udt['name'] == dataType:
						udtTags = udt['tags']
						for udtTag in udtTags:
						
							
							for i in range(dimension[0]):
								for j in range(dimension[1]):
								
									if udtTag['name'] in data[i][j].keys():
										dataRecursive = data[i][j][udtTag['name']]
									else:
										if isPrimative(udtTag['dataType']):
											dataRecursive = DEFAULT_SIMULATION[udtTag['dataType']]
										else:
											dataRecursive = []
								
									paths = paths + getPaths(udtTag, udts, dataRecursive)
							
									fullPaths = fullPaths + map(lambda x : {'path':tag['name'] + '[' + str(i) + ',' + str(j) + ']' +  '.' + x['path'], 'dataType':x['dataType'], 'value':x['value']}, paths)

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
				return childNode.getAttribute("Value")
			
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
	elementNodes = arrayNode.getElementsByTagName("Element")
	for k in range(elementNodes.getLength()):
		elementNode = elementNodes.item(k)
		if elementNode.getNodeType() == Node.ELEMENT_NODE:
		
			indexes = map(int, elementNode.getAttribute("Index").strip('[]').split(','))
			if elementNode.hasAttribute("Value"):
				
				value = elementNode.getAttribute("Value")
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
	memberNodes = structureNode.getElementsByTagName("DataValueMember")
	for k in range(memberNodes.getLength()):
		memberNode = memberNodes.item(k)
		if memberNode.getNodeType() == Node.ELEMENT_NODE:
			name = memberNode.getAttribute("Name")
			if memberNode.hasAttribute("Value"):
				dataType = memberNode.getAttribute("DataType")
				value = memberNode.getAttribute("Value")
				members[name] = value
			else:
				members[name] = parseDataNode(memberNode)
				
	arrayNodes = structureNode.getElementsByTagName("ArrayMember")
	for k in range(arrayNodes.getLength()):
		arrayNode = arrayNodes.item(k)
		if arrayNode.getNodeType() == Node.ELEMENT_NODE:
			name = arrayNode.getAttribute("Name")
			members[name] = parseArrayNode(arrayNode)
			
	structureMemberNodes = structureNode.getElementsByTagName("StructureMember")
	for k in range(structureMemberNodes.getLength()):
		structureMemberNode = structureMemberNodes.item(k)
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
		attributeValue = attributeNode.getNodeValue()
		parameters[attributeName] = attributeValue
		
	return parameters


def initializeList(shape, value):

	if shape == []:
		return value
	else:
		return [initializeList(shape[1:],value)] * shape[0]



	
def getBuiltInUdts():

	udts = []
	
	# Add TIMER, COUNTER, MESSAGE, CONTROL, ALARM_DIGITAL, ALARM_ANALOG
	
	
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

