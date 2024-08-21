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



def parse(l5xString):

	l5xString = String(l5xString)

	xmlStream = ByteArrayInputStream(l5xString.getBytes(StandardCharsets.UTF_8))

	dbFactory = DocumentBuilderFactory.newInstance()
	dBuilder = dbFactory.newDocumentBuilder()
	doc = dBuilder.parse(xmlStream)
	doc.getDocumentElement().normalize()

	dataTypes = doc.getElementsByTagName("DataType")
	
	
	for i in range(dataTypes.getLength()):
		dataType = dataTypes.item(i)
		print '---------------   ' + str(dataType.getAttribute("Name")) + '  --------------------'
		
		if dataType.getNodeType() == Node.ELEMENT_NODE:

			# suppose to convert dataType to Element here?
			
			members = dataType.getElementsByTagName("Member")
			
			for j in range(members.getLength()):
				member = members.item(j)
				
				hidden = member.getAttribute("Hidden")
				
				if hidden == 'false':
					print member.getAttribute("Name")
					print member.getAttribute("DataType")