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
#conversion.L5X.parse(l5xString)



DATA_TYPE_MAPPING_PYTHON = {"BOOL":bool, "BIT":bool, "SINT":int, "INT":int, "DINT":int, "REAL":float, "STRING":str}
DATA_TYPE_MAPPING_IGNITION = {"BOOL":"Boolean", "BIT":"Boolean", "SINT":"Int1", "INT":"Int2", "DINT":"Int4", "REAL":"Float4", "STRING":"String"}
DATA_TYPE_MAPPING_SIMULATION = {"BOOL":"Boolean", "BIT":"Boolean", "SINT":"Int16", "INT":"Int16", "DINT":"Int32", "REAL":"Float", "STRING":"String"}
DEFAULT_SIMULATION = {"BOOL":"false", "BIT":"false", "SINT":"0", "INT":"0", "DINT":"0", "REAL":"0", "STRING":""}





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
				
				if dataFormat == 'Decorated':

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
			
			
			if dataNodeType == 'DataValue':
				dataType = childNode.getAttribute("DataType")
				return DATA_TYPE_MAPPING_PYTHON[dataType](childNode.getAttribute("Value"))
			
			
			elif dataNodeType == 'Array':
				dataType = childNode.getAttribute("DataType")
				elements = []
				elementNodes = childNode.getElementsByTagName("Element")
				for k in range(elementNodes.getLength()):
					elementNode = elementNodes.item(k)
					if elementNode.getNodeType() == Node.ELEMENT_NODE:
						if elementNode.hasAttribute("Value"):
							value = DATA_TYPE_MAPPING_PYTHON[dataType](elementNode.getAttribute("Value"))
							elements.append(value)
						else:
							elements.append(parseDataNode(elementNode))
							
				return elements
						
	
			elif dataNodeType == 'Structure':
				members = {}
				memberNodes = childNode.getElementsByTagName("DataValueMember")
				for k in range(memberNodes.getLength()):
					memberNode = memberNodes.item(k)
					if memberNode.getNodeType() == Node.ELEMENT_NODE:
						name = memberNode.getAttribute("Name")
						if memberNode.hasAttribute("Value"):
							dataType = memberNode.getAttribute("DataType")
							value = DATA_TYPE_MAPPING_PYTHON[dataType](memberNode.getAttribute("Value"))
							members[name] = value
						else:
							members[name] = parseDataNode(memberNode)
							
				return members
	
	
	
			else:
				return None









	
def getBuiltInUdts():

	udts = []
	
	# Add TIMER, COUNTER, PID, and CONTROL
	udt = {
	  "name": "TIMER",
	  "description": "Built-in timer",
	  "stringFamily": False,
	  "tags": [
		{
		  "name": "DN",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "EN",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "TT",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "PRE",
		  "description": "",
		  "dataType": "DINT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ACC",
		  "description": "",
		  "dataType": "DINT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		}
	  ]
	}
	udts.append(udt)
	
	udt = {
	  "name": "COUNTER",
	  "description": "Built-in counter",
	  "stringFamily": False,
	  "tags": [
		{
		  "name": "CD",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "CU",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "DN",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "OV",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "UN",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "PRE",
		  "description": "",
		  "dataType": "DINT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ACC",
		  "description": "",
		  "dataType": "DINT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		}
	  ]
	}
	udts.append(udt)
	

	udt = {
	  "name": "MESSAGE",
	  "description": "Built-in Message",
	  "stringFamily": False,
	  "tags": [
		{
		  "name": "Flags",
		  "description": "",
		  "dataType": "INT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "EW",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ER",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "DN",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "ST",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "TO",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "EN_CC",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ERR",
		  "description": "",
		  "dataType": "INT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "EXERR",
		  "description": "",
		  "dataType": "DINT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ERR_SRC",
		  "description": "",
		  "dataType": "SINT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "DN_LEN",
		  "description": "",
		  "dataType": "INT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "REQ_LEN",
		  "description": "",
		  "dataType": "INT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "DestinationLink",
		  "description": "",
		  "dataType": "INT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "DestinationNode",
		  "description": "",
		  "dataType": "INT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "SourceLink",
		  "description": "",
		  "dataType": "INT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "Class",
		  "description": "",
		  "dataType": "INT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "Attribute",
		  "description": "",
		  "dataType": "INT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "Instance",
		  "description": "",
		  "dataType": "DINT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "LocalIndex",
		  "description": "",
		  "dataType": "DINT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "Channel",
		  "description": "",
		  "dataType": "SINT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "Rack",
		  "description": "",
		  "dataType": "SINT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "Group",
		  "description": "",
		  "dataType": "SINT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "Slot",
		  "description": "",
		  "dataType": "SINT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "Path",
		  "description": "",
		  "dataType": "STRING",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "RemoteIndex",
		  "description": "",
		  "dataType": "DINT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "RemoteElement",
		  "description": "",
		  "dataType": "STRING",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "UnconnectedTimeout",
		  "description": "",
		  "dataType": "DINT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ConnectionRate",
		  "description": "",
		  "dataType": "DINT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "TimeoutMultiplier",
		  "description": "",
		  "dataType": "SINT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		}
	  ]
	}
	udts.append(udt)
	
	udt = {
	  "name": "CONTROL",
	  "description": "Built-in Control",
	  "stringFamily": False,
	  "tags": [
		{
		  "name": "LEN",
		  "description": "",
		  "dataType": "DINT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "POS",
		  "description": "",
		  "dataType": "DINT",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "EN",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "EU",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "DN",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"false",
		  "hidden": False
		},
		{
		  "name": "EM",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "ER",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "UL",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "IN",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		},
		{
		  "name": "FD",
		  "description": "",
		  "dataType": "BOOL",
		  "arrayLength":None,
		  "selected": True,
		  "simulationFunction":"0",
		  "hidden": False
		}
	  ]
	}
	udts.append(udt)
	
	return udts

