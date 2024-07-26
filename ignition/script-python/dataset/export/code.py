
import org.apache.poi.xssf.usermodel.XSSFWorkbook as Workbook
import org.apache.poi.xssf.usermodel.XSSFColor as XSSFColor
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
	
	
def toExcelWithFormating(dataset, formatDataset, filePath):
	
	# create workbook
	workbook = Workbook()
	sheet = workbook.createSheet('test-sheet') #XSSFSheet
	row = sheet.createRow(0) #XSSFRow
	cell = row.createCell(0) #XSSFCell
	cell.setCellValue('A')
	
	
	
	goodStyle = workbook.createCellStyle()
	goodFillColor = XSSFColor(Color(198, 239, 206))
	goodStyle.setFillForegroundColor(goodFillColor)
	goodStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND)
	goodFont = workbook.createFont()
	goodFontColor = XSSFColor(Color(0, 97, 0))
	goodFont.setColor(goodFontColor)
	goodStyle.setFont(goodFont)
	cell2 = row.createCell(1)
	cell2.setCellValue("B")
	cell2.setCellStyle(goodStyle)
	
	
	badStyle = workbook.createCellStyle()
	badFillColor = XSSFColor(Color(255, 199, 206))
	badStyle.setFillForegroundColor(badFillColor)
	badStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND)
	badFont = workbook.createFont()
	badFontColor = XSSFColor(Color(156, 0, 6))
	badFont.setColor(badFontColor)
	badStyle.setFont(badFont)
	cell3 = row.createCell(2)
	cell3.setCellValue("C")
	cell3.setCellStyle(badStyle)
	
	
	warningStyle = workbook.createCellStyle()
	warningFillColor = XSSFColor(Color(255, 235, 156))
	warningStyle.setFillForegroundColor(warningFillColor)
	warningStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND)
	warningFont = workbook.createFont()
	warningFontColor = XSSFColor(Color(156, 101, 0))
	warningFont.setColor(warningFontColor)
	warningStyle.setFont(warningFont)
	cell3 = row.createCell(3)
	cell3.setCellValue("D")
	cell3.setCellStyle(warningStyle)
	
	

	# write to file
	out = None
	try:
		out = FileOutputStream(File(filePath))
		workbook.write(out)
		out.close
	except:
		out.close


def toExcelSheets(datasets, sheetNames, filePath):

	spreadsheet = system.dataset.toExcel(showHeaders=True, dataset=datasets, nullsEmpty=True, sheetNames=sheetNames)
	system.file.writeFile(filePath, spreadsheet)