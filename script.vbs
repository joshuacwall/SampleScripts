Dim args, objExcel

Set args = WScript.Arguments
Set objExcel = Createobject("Excel.Application")

objExcel.workbooks.Open args(0)
objExcel.Visible = False


objExcel.Run "Automation.get_data_auto"
objExcel.Run "Automation.auto_MasterMacro"


objExcel.ActiveWorkbook.Close(0)
objExcel.Quit