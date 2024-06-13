Sub OutreachDataBackup()

' Author: Nick Solly
' Language: VBA
' Created: 2024-05-08
' Description: VBA macro to create a copy of the data in a new workbook and upload it to a SharePoint directory
' Source: ICG Diagnostic Engagement
' Privacy: Confidential
' Version: 1.0

' Declare variables
Dim ws As Worksheet
Dim wb As Workbook
Dim tbl As ListObject
Dim tblRows As Long
Dim newWb As Workbook
Dim strDate As String
Dim strTime As String
Dim strFileName As String
Dim strPath As String
Dim coverSheet As Worksheet
Dim OutlookApp As Object
Dim OutlookMail As Object

' Optimise code
Application.ScreenUpdating = False
Application.DisplayAlerts = False
Application.Calculation = xlCalculationManual

' Check if the "Consolidated" sheet and table exist
On Error Resume Next
Set wb = ThisWorkbook
Set ws = wb.Sheets("Sheet1")
Set tbl = ws.ListObjects("tblCons")
On Error GoTo 0

If ws Is Nothing Or tbl Is Nothing Then
    MsgBox "The 'Consolidated' sheet or table does not exist.", vbCritical
    Exit Sub
End If

' Define number of rows in the table
tblRows = tbl.ListRows.Count

' Define variables for the new workbook
strDate = Format(Now(), "yyyy-mm-dd")
strTime = Format(Now(), "hh-mm-ss")
strFileName = strDate & "_" & strTime & "_OutreachDataBackup.xlsx"

' Output folder SharePoint folder
strPath = "https://eygb.sharepoint.com/sites/Outreachoptimisation/Shared%20Documents/Data/03-Pilot/DataBackUp/"

' Create a new workbook
Set newWb = Workbooks.Add

' copy the headers to the new workbook
tbl.HeaderRowRange.Copy
With newWb.Sheets(1)
    .Range("A1").PasteSpecial Paste:=xlPasteValues
End With

' Copy the data to the new workbook
tbl.DataBodyRange.Copy

' Paste the data to the new workbook
With newWb.Sheets(1)
    .Range("A2").PasteSpecial Paste:=xlPasteValues
End With

' Clear the clipboard
Application.CutCopyMode = False

' Format the new workbook as a table
With newWb.Sheets(1)
    .ListObjects.Add(xlSrcRange, .UsedRange, , xlYes).Name = "tblOutreachBackup"
    .ListObjects("tblOutreachBackup").TableStyle = "TableStyleMedium2"
End With

' resize the sheet
newWb.Sheets(1).Columns.AutoFit

' rename the sheet
newWb.Sheets(1).Name = "OutreachDataBackup"

' Add a coversheet to the new workbook
Set coverSheet = Nothing
On Error Resume Next
Set coverSheet = newWb.Sheets(2)
On Error GoTo 0

If coverSheet Is Nothing Then
    Set coverSheet = newWb.Sheets.Add(After:=newWb.Sheets(newWb.Sheets.Count))
End If
coverSheet.Name = "CoverSheet" ' Moved outside the If statement to ensure the sheet is always renamed.

' Add a coversheet to the new workbook
With coverSheet
    .Cells(2, 2).Value = "Outreach Data Backup"
    .Cells(3, 2).Value = "Date: " & strDate
    .Cells(4, 2).Value = "Time: " & strTime
    ' Add the name of the user who created the workbook
    .Cells(5, 2).Value = "Created by: " & Environ("USERNAME")
    .Cells(7, 2).Value = "This workbook contains a backup of the Outreach data."
    .Cells(8, 2).Value = "Please do not edit this workbook."
    .Cells(9, 2).Value = "If you need to make changes, please contact the Outreach team."
    .Cells(12, 2).Value = "Password: Outreach01"
End With

' Lock the new workbook
newWb.Protect Password:="Outreach01", Structure:=True, Windows:=False

' Protect the coversheet
coverSheet.Protect Password:="Outreach01", DrawingObjects:=True, Contents:=True, Scenarios:=True

' Protect the data sheet
newWb.Sheets("OutreachDataBackup").Protect Password:="Outreach01", DrawingObjects:=True, Contents:=True, Scenarios:=True


' Save the new workbook
newWb.SaveAs Filename:=strPath & strFileName, FileFormat:=xlOpenXMLWorkbook

' Close the new workbook
newWb.Close SaveChanges:=False

' Notify the user that the backup has been created
MsgBox "The Outreach data has been backed up successfully.", vbInformation

' Create a new instance of Outlook
Set OutlookApp = CreateObject("Outlook.Application")

' Create a new email
Set OutlookMail = OutlookApp.CreateItem(0)

' Construct the body of the email
strBody = "The Outreach data has been backed up at " & strDate & " " & strTime & "<br><br>"
strBody = strBody & vbCrLf & vbCrLf & "Please find the attached file. <br><br>"
strBody = strBody & vbCrLf & vbCrLf & "A copy has been stored in the following location: <br>"
strBody = strBody & vbCrLf & vbCrLf & "<a href=" & strPath & strFileName & ">" & strPath & strFileName & "</a><br><br>"
strBody = strBody & vbCrLf & vbCrLf & "Regards,<br>" & vbCrLf & "ETC Outreach Team"

' Set the properties of the email
With OutlookMail
    .To = "UKFSConsultingOps.ETCOutreach@uk.ey.com"
    .Importance = olImportanceLow
    .Subject = "Outreach Data Backup"
    .Body = strBody
    .BodyFormat = 2
    .HTMLBody = "<html><head></head><body>" & strBody & "</body></html>"
    .Attachments.Add strPath & strFileName
    .Send ' Use .Send instead of .Display to send the email without displaying it
End With


' Optimise code
Application.ScreenUpdating = True
Application.DisplayAlerts = True
Application.Calculation = xlCalculationAutomatic

End Sub




