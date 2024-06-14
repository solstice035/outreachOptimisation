Option Explicit

Sub Reporting_Outreach()

' Author: Nick Solly
' Language: VBA
' Created: 2024-05-08
' Description: VBA macro to create an email with KPIs on refresh with a copy of the pivot table data attached
' Privacy: Confidential
' Version: 1.0



With Application
    .EnableEvents = False
    .ScreenUpdating = False
    .calculation = xlCalculationManual
End With

' Declare Variables
Dim wb As Workbook
Dim ws As Worksheet
Dim wbNew As Workbook

' Pivot Tables and Ranges
Dim statusHead As Range
Dim statusPivot As PivotTable

' Email Variables
Dim rng As Range
Dim OutApp As Object
Dim OutMail As Object
Dim StrBody As String
Dim StrFoot As String

Set wb = ThisWorkbook

' Define the range for the email
Set rng = Nothing
On Error Resume Next

' Define the range for the email body 
' to include status table, KPIs and refresh dates with links


Set rng = Sheets("MetaData").Range("****TBC****").SpecialCells(xlCellTypeVisible)
' ToDo: Add range for email body
' ToDo: Add Meta data tab in source workbook
On Error GoTo 0

' Add Status Table
Set statusHead = Worksheets("Status").Range("A1:G1")
Set statusPivot = Worksheets("Status").PivotTables("pvStatus")

' Add new workbook
Set wbNew = Workbooks.Add

' Copy the status table to the new workbook
statusHead.Copy
With wbNew.Sheets(1)
    .Range("A1").PasteSpecial Paste:=xlPasteValues
End With
' Copy the status pivot table to the new workbook
statusPivot.TableRange1.Copy
With wbNew.Sheets(1)
    .Range("A2").PasteSpecial Paste:=xlPasteValues
End With

' Email the workbook
Set OutApp = CreateObject("Outlook.Application")
Set OutMail = OutApp.CreateItem(0)

' Define the email body
StrBody = "Hello," & vbNewLine & vbNewLine & _
    "Please find attached the latest KPIs for the Outreach Program." & vbNewLine & _
    "The data is refreshed daily and can be accessed via the links below:" & vbNewLine & _
    "Status Table: " & vbNewLine & _
    "KPIs: " & vbNewLine & _
    "Refresh Date: " & vbNewLine & _
    "Refresh Time: " & vbNewLine & vbNewLine & _
    "Kind Regards," & vbNewLine & _
    "ETC Outreach Team"

' Send the email
With OutMail
    .To = ""
    .CC = ""
    .Subject = "Outreach Program Status Update"
    .Body = StrBody
    .BodyFormat = olFormatHTML
    .HTMLBody = "<html><head></head><body>" & strBody & "</body></html>"
    .Attachments.Add wbNew.FullName
    .Display
End With


' Optimise code
Application.ScreenUpdating = True
Application.DisplayAlerts = True
Application.Calculation = xlCalculationAutomatic

End Sub
