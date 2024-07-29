
import org.apache.poi.xssf.usermodel.XSSFWorkbook as Workbook
import org.apache.poi.xssf.usermodel.XSSFColor as XSSFColor
import org.apache.poi.xssf.usermodel.XSSFFont as XSSFFont
import org.apache.poi.ss.usermodel.FillPatternType as FillPatternType
import java.io.FileOutputStream as FileOutputStream
import java.io.File as File
import java.awt.Color as Color



def toCSV(dataset, filePath):

	csv = system.dataset.toCSV(dataset, showHeaders=True, forExport=False)
	system.file.writeFile(filePath, csv)
	
	

def toExcel(dataset, filePath):

	spreadsheet = system.dataset.toExcel(showHeaders=True, dataset=dataset, nullsEmpty=True)
	system.file.writeFile(filePath, spreadsheet)
	
	
	
	

def toExcelWithFormating(sheetsData, filePath):
	# sheetsData: {'dataset', 'formatDataset', 'sheetName'}
	
	# create workbook
	workbook = Workbook()

	# Header Style
	headerStyle = workbook.createCellStyle()
	headerFont = workbook.createFont()
	headerFont.setBold(True)
	headerStyle.setFont(headerFont)
	


	# Good Style
	goodStyle = workbook.createCellStyle()
	goodFillColor = XSSFColor(Color(198, 239, 206))
	goodStyle.setFillForegroundColor(goodFillColor)
	goodStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND)
	goodFont = workbook.createFont()
	goodFontColor = XSSFColor(Color(0, 97, 0))
	goodFont.setColor(goodFontColor)
	goodStyle.setFont(goodFont)
	
	# Bad Style
	badStyle = workbook.createCellStyle()
	badFillColor = XSSFColor(Color(255, 199, 206))
	badStyle.setFillForegroundColor(badFillColor)
	badStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND)
	badFont = workbook.createFont()
	badFontColor = XSSFColor(Color(156, 0, 6))
	badFont.setColor(badFontColor)
	badStyle.setFont(badFont)
	
	# Warning Style
	warningStyle = workbook.createCellStyle()
	warningFillColor = XSSFColor(Color(255, 235, 156))
	warningStyle.setFillForegroundColor(warningFillColor)
	warningStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND)
	warningFont = workbook.createFont()
	warningFontColor = XSSFColor(Color(156, 101, 0))
	warningFont.setColor(warningFontColor)
	warningStyle.setFont(warningFont)
	
	# OPC Style [purple]
	opcStyle = workbook.createCellStyle()
	opcFillColor = XSSFColor(Color(220, 190, 255))
	opcStyle.setFillForegroundColor(opcFillColor)
	opcStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND)
	opcFont = workbook.createFont()
	opcFontColor = XSSFColor(Color(0, 0, 0))
	opcFont.setColor(opcFontColor)
	opcStyle.setFont(opcFont)
	
	# Memory Style [blue]
	memoryStyle = workbook.createCellStyle()
	memoryFillColor = XSSFColor(Color(190, 190, 255))
	memoryStyle.setFillForegroundColor(memoryFillColor)
	memoryStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND)
	memoryFont = workbook.createFont()
	memoryFontColor = XSSFColor(Color(0, 0, 0))
	memoryFont.setColor(memoryFontColor)
	memoryStyle.setFont(memoryFont)
	
	
	
	
	
	for sheetData in sheetsData:
		dataset = sheetData['dataset']
		formatDataset = sheetData['formatDataset']
		sheetName = sheetData['sheetName']

		sheet = workbook.createSheet(sheetName)
		
		
	
		headers = system.dataset.getColumnHeaders(dataset)
	
		# header
		row = sheet.createRow(0)
		for columnIndex in range(len(headers)):
			cell = row.createCell(columnIndex) 
			cell.setCellValue(headers[columnIndex])
			cell.setCellStyle(headerStyle)
		
		# conditional data
		for rowIndex in range(dataset.getRowCount()):
			row = sheet.createRow(rowIndex + 1) # add 1 to skip header row
			for columnIndex in range(len(headers)):
				cell = row.createCell(columnIndex) 
				cell.setCellValue(dataset.getValueAt(rowIndex, columnIndex))
				
				try:
					format = formatDataset.getValueAt(rowIndex, columnIndex)
				except:
					format = ''
					
				if format == 'Good':
					cell.setCellStyle(goodStyle)
				elif format == 'Bad':
					cell.setCellStyle(badStyle)
				elif format == 'Warning':
					cell.setCellStyle(warningStyle)
				elif format == 'OPC':
					cell.setCellStyle(opcStyle)
				elif format == 'Memory':
					cell.setCellStyle(memoryStyle)
				else:
					pass
		
		# autosize the columns
		for columnIndex in range(len(headers)):
			sheet.autoSizeColumn(columnIndex)
			
			
	
	# write to file
	out = None
	try:
		out = FileOutputStream(File(filePath))
		workbook.write(out)
		out.close
	except:
		out.close

