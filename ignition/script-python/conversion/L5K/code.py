
import re



DATA_TYPE_MAPPING_IGNITION = {"BOOL":"Boolean", "BIT":"Boolean", "SINT":"Int1", "INT":"Int2", "DINT":"Int4", "REAL":"Float4", "STRING":"String"}
DATA_TYPE_MAPPING_SIMULATION = {"BOOL":"Boolean", "BIT":"Boolean", "SINT":"Int16", "INT":"Int16", "DINT":"Int32", "REAL":"Float", "STRING":"String"}
DEFAULT_SIMULATION = {"BOOL":"false", "BIT":"false", "SINT":"0", "INT":"0", "DINT":"0", "REAL":"0", "STRING":""}


def searchOne(regexStr, findStr, defaultStr=None, flags=re.DOTALL):
	regex = re.compile(regexStr, flags)
	res = regex.search(findStr)
	if res and res.groups():
		return res.group(1)
	else:
		return defaultStr
			
def search(regexStr, findStr, flags=re.DOTALL):
	regex = re.compile(regexStr, flags)
	res = regex.search(findStr)
	return res.groups()
	
def matchOne(regexStr, findStr, defaultStr=None, flags=re.DOTALL):
	regex = re.compile(regexStr, flags)
	res = regex.match(findStr)
	if res and res.groups():
		return res.group(1)
	else:
		return defaultStr
	
def findall(regexStr, findStr, flags=re.DOTALL):
	regex = re.compile(regexStr, flags)
	res = regex.findall(findStr)
	return res
	
def findallOne(regexStr, findStr, flags=re.DOTALL):
	regex = re.compile(regexStr, flags)
	res = regex.findall(findStr)
	return res[0]

def parseTags(tagsSection, allowHidden=False, selectTags=False, useStoredValues=True):
	tags = []
	for tagSection in tagsSection.split(";\r\n"):
		if len(tagSection.strip()) > 0:
			tagParts = search("(\w+)(\sOF\s)?", tagSection.strip())
			if tagParts[1] != None:
				tag = {
				  "name": tagParts[0],
				  "description": "",
				  "dataType": "BIT",
				  "arrayLength":None,
				  "selected": selectTags,
				  "simulationFunction":DEFAULT_SIMULATION.get("BIT", None),
				  "hidden": 0
				}
				tags.append(tag)
			else:
				parseTag(tags, tagSection, "tag", allowHidden, selectTags, useStoredValues)
	return tags
	
def parseTag(tags, tagSection, sectionType, allowHidden, selectTags, useStoredValues):
	if len(tagSection.strip()) > 0:		
		if sectionType == "dataType":
			tagParts = search("([a-zA-Z0-9_:]+)\s(\w+)(\[[\d+|\,]+\])?\s?(.+)?", tagSection.strip())
		else:
			try:
				tagParts = [val for val in search("([a-zA-Z0-9_:.]+)\sOF\s([a-zA-Z0-9_:.]+)\s(\[[\d+|\,]+\])?\s?(.+)?", tagSection.strip())]
				tagParts[1] = "BOOL"
			except:
				try:
					tagParts = search("([a-zA-Z0-9_:.]+)\s:\s(\w+)(\[[\d+|\,]+\])?\s?(.+)?", tagSection.strip())
				except:
					tagParts = []			
		
		if len(tagParts) > 1:
			if sectionType == "dataType":
				tagName = tagParts[1]
				tagDataType = tagParts[0]
			else:
				tagName = tagParts[0]
				tagDataType = tagParts[1]
				
			tagDescription = ""
			isHidden = 0
			isInOut = 0
			simulationFunction = None
			arrayLength = None
			
			# Look to see if there is an array
			if tagParts[2] != None:
				arrayLengthStr = tagParts[2][1:-1]
				if "," in arrayLengthStr:
					arrayLengthParts = arrayLengthStr.split(",")
					arrayLength = int(arrayLengthParts[0]) * int(arrayLengthParts[1])
				else:
					arrayLength = int(arrayLengthStr)
									
			# Check for the description and hidden fields, if exists
			if tagParts[3] != None:
				isHidden = int(searchOne("Hidden\s\:\=\s(.*?)(\)|\,)", tagParts[3], 0))
				tagDescription = searchOne("Description.*\"(.*?)\"", tagParts[3], "", 0)
                # added code to look for AOI InOut paramters, as they are not part of the UDT
				isInOut = (tagParts[3].find("InOut"))

				if useStoredValues:
					tagValueParts = tagParts[3].split(":=")
					tagValue = tagValueParts[-1].strip()
					
					if "$00" in tagValue:
						tagValue = tagValue.replace("$00", "")
										
					if "2#" in tagValue:
						tagValue = tagValue.replace("2#", "")
					
					simulationFunction = tagValue
			
			if simulationFunction == None:
				simulationFunction = DEFAULT_SIMULATION.get(tagDataType, None)
			
			# Only bring in tags that are not hidden
            # added condition to block InOut paramters from being added to UDT 
			if (not isHidden or allowHidden) and isInOut == -1:	
				tag = {
				  "name": tagName,
				  "description": tagDescription,
				  "dataType": tagDataType,
				  "arrayLength":arrayLength,
				  "selected": selectTags,
				  "simulationFunction":simulationFunction,
				  "hidden": isHidden
				}
				tags.append(tag)



def parse(l5kFile, selectTags=False, allowHidden=False, useStoredValues=True):
	import re
 
	udts = []
	tags = []
	programs = []
	
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
 
	if l5kFile != None:		
		# Get the controller information including IP address and slot number, so we can potentially create the PLC connection
		commPath = searchOne("CommPath\s\:\=\s\"(.*?)\"", l5kFile)
		if commPath != None:
			commPathParts = commPath.split("\\")
			ipAddress = commPathParts[1]
			slotNumber = commPathParts[-1]
		else:
			ipAddress = None
			slotNumber = None
		
		# Find all of the data types so we can make UDT definitions
		for dataType in findall("DATATYPE(.*?)END_DATATYPE", l5kFile):
			dataTypeName = dataType[0:dataType.find("(")].strip()
			dataTypeDescription = searchOne("Description.*\"(.*?)\"", dataType, "", 0)
						
			udtTags = []
			tagsSection = dataType[dataType.find(")\r\n")+1:]
			for tagRow in tagsSection.split(";\r\n"):
				parseTag(udtTags, tagRow, "dataType", allowHidden, True, False)
			
			udt = {
			  "name": dataTypeName,
			  "description": dataTypeDescription,
			  "tags": udtTags,
			  "stringFamily": "FamilyType := StringFamily" in dataType
			}
			udts.append(udt)
		
		# Find all of the add on instructions so we can make UDT definitions
		for dataType in findall("ADD_ON_INSTRUCTION_DEFINITION\s(.*?)END_ADD_ON_INSTRUCTION_DEFINITION\r\n", l5kFile):
			dataTypeName = searchOne("(.*?)\s", dataType, "", 0)
			dataTypeDescription = ""
			
			udtTags = []
			tagsSection = findallOne("PARAMETERS\r\n(.*?)END_PARAMETERS\r\n", dataType)
			for tagRow in tagsSection.split(";\r\n"):
				parseTag(udtTags, tagRow, "tag", allowHidden, True, False)
			
			udt = {
			  "name": dataTypeName,
			  "description": dataTypeDescription,
			  "tags": udtTags,
			  "stringFamily": False
			}
			udts.append(udt)
					
		# Find all of the add on instructions so we can make UDT definitions
		for dataType in findall("ADD_ON_INSTRUCTION_DEFINITION,(.*?)END_ENCODED_DATA\r\n", l5kFile):
			dataTypeName = searchOne("Name.*\"(.*?)\"", dataType, "", 0)
			dataTypeDescription = searchOne("Description.*\"(.*?)\"", dataType, "", 0)
			
			udtTags = []
			tagsSection = findallOne("PARAMETERS\r\n(.*?)END_PARAMETERS\r\n", dataType)
			for tagRow in tagsSection.split(";\r\n"):
				parseTag(udtTags, tagRow, "tag", allowHidden, True, False)
			
			udt = {
			  "name": dataTypeName,
			  "description": dataTypeDescription,
			  "tags": udtTags,
			  "stringFamily": False
			}
			udts.append(udt)
			
		# Find all of the global tags
		try:
			globalSection = findallOne("CONTROLLER(.*?)END_TAG\r\n", l5kFile)
			tagsSection = findallOne("TAG\r\n(.*?)END_TAG\r\n", globalSection + "END_TAG\r\n")
			tags = parseTags(tagsSection, allowHidden, selectTags, useStoredValues)
		except:
			tags = []

		# Find all programs
		for programSection in findall("\tPROGRAM\s(.*?)END_PROGRAM\r\n", l5kFile):
			system.util.getLogger("L5K").info(programSection)
			programName = searchOne("(\w+)\s(.*?)", programSection, "")
			tagsSection = findallOne("TAG\r\n(.*?)END_TAG\r\n", programSection)
			programTags = parseTags(tagsSection, allowHidden, selectTags, useStoredValues)
			programs.append({
				"name": programName,
				"tags": programTags
			})
		
	return (udts, tags, programs)