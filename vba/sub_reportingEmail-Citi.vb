Option Explicit

Sub Reporting_Outreach()

Dim wb As Workbook
Dim sh As Worksheet


    With Application
        .EnableEvents = False
        .ScreenUpdating = False
    End With

' ***** Declare Variable ******
    'New Workbook
        Dim wbNew As Workbook
        
    'Sheets and Pivots
        Dim Head_WG_Sum As Range
        Dim pvWg_Sum As PivotTable
        Dim Head_WG_Disp As Range
        Dim pvWg_Disp As PivotTable
        Dim Head_Prog_AU As Range
        Dim pvProg_AU As PivotTable
        Dim Head_Prog_Int As Range
        Dim pvProg_Int As PivotTable
 

    'Emails
        Dim rng As Range
        Dim OutApp As Object
        Dim OutMail As Object
        Dim MailTo As Range
        Dim MailCC As Range
        Dim StrBody As String
        Dim StrFoot As String

Set wb = ThisWorkbook

        Set MailTo = Worksheets("MetaData").Range("F13")
        Set MailCC = Worksheets("MetaData").Range("G13")

   Set rng = Nothing
    On Error Resume Next

    Set rng = Sheets("MetaData").Range("A3:B14").SpecialCells(xlCellTypeVisible)
    On Error GoTo 0

    If rng Is Nothing Then
        MsgBox "The selection is not a range or the sheet is protected" & _
               vbNewLine & "please correct and try again.", vbOKOnly
        Exit Sub
    End If

    'WorkingGroup-Summary
        Set Head_WG_Sum = Worksheets("Summary").Range("A1:I1")
        Set pvWg_Sum = Worksheets("Summary").PivotTables("pvWg_Sum")
    
    'WorkingGroup-Dispositions
        Set Head_WG_Disp = Worksheets("Dispositions").Range("A1:M1")
        Set pvWg_Disp = Worksheets("Dispositions").PivotTables("pvWg_Disp")
    
    'Progress_Detailed_AU
        Set Head_Prog_AU = Worksheets("AU_Progress").Range("A1:Z1")
        Set pvProg_AU = Worksheets("AU_Progress").PivotTables("pvProg_AU")
  
    'Progress_Detailed_Interaction
        Set Head_Prog_Int = Worksheets("Interaction_Progress").Range("A1:Z1")
        Set pvProg_Int = Worksheets("Interaction_Progress").PivotTables("pvProg_Int")

'******* Create the new workbook *******
    Set wbNew = Workbooks.Add

'******* Copy Paste in Sheets and Pivots *******
    
    'WSummary
            
            Head_WG_Sum.Copy
                wbNew.Worksheets(1).Range("A1").PasteSpecial Paste:=xlPasteValues
                wbNew.Worksheets(1).Range("A1").PasteSpecial Paste:=xlPasteFormats
                Application.CutCopyMode = False
            
            
            pvWg_Sum.ClearAllFilters
            pvWg_Sum.RepeatAllLabels xlRepeatLabels
            pvWg_Sum.TableRange1.Copy
                wbNew.Worksheets(1).Cells(Rows.Count, 1).End(xlUp).Offset(1, 0).PasteSpecial Paste:=xlPasteColumnWidths
                wbNew.Worksheets(1).Cells(Rows.Count, 1).End(xlUp).Offset(1, 0).PasteSpecial Paste:=xlPasteFormats
                wbNew.Worksheets(1).Cells(Rows.Count, 1).End(xlUp).Offset(1, 0).PasteSpecial Paste:=xlPasteValues
                
                Application.CutCopyMode = False
            
            pvWg_Sum.RepeatAllLabels xlDoNotRepeatLabels

            'Rename the Sheets
                Sheets("Sheet1").Name = "Summary"

            'Freeze Panes
                wbNew.Worksheets(1).Rows("3:3").Select
                ActiveWindow.FreezePanes = True
            
            'Add Autoflter
                wbNew.Worksheets(1).Rows("2:2").AutoFilter

            'Go to the top of the workbook
                wbNew.Worksheets(1).Range("A2").Select

    'Dispositions
        Sheets.Add(After:=Sheets(1)).Name = "Dispositions"

            Head_WG_Disp.Copy
                wbNew.Worksheets(2).Range("A1").PasteSpecial Paste:=xlPasteValues
                wbNew.Worksheets(2).Range("A1").PasteSpecial Paste:=xlPasteFormats
                Application.CutCopyMode = False

            pvWg_Disp.ClearAllFilters
            pvWg_Disp.RepeatAllLabels xlRepeatLabels
            pvWg_Disp.TableRange1.Copy
                wbNew.Worksheets(2).Cells(Rows.Count, 1).End(xlUp).Offset(1, 0).PasteSpecial Paste:=xlPasteColumnWidths
                wbNew.Worksheets(2).Cells(Rows.Count, 1).End(xlUp).Offset(1, 0).PasteSpecial Paste:=xlPasteFormats
                wbNew.Worksheets(2).Cells(Rows.Count, 1).End(xlUp).Offset(1, 0).PasteSpecial Paste:=xlPasteValues
                
                Application.CutCopyMode = False
            
            pvWg_Disp.RepeatAllLabels xlDoNotRepeatLabels

            'Freeze Panes
                wbNew.Worksheets(2).Rows("3:3").Select
                ActiveWindow.FreezePanes = True
            
            'Add Autoflter
                wbNew.Worksheets(2).Rows("2:2").AutoFilter

            'Go to the top of the workbook
                wbNew.Worksheets(2).Range("A3").Select

    'Progress_Detailed_SubSegment
        Sheets.Add(After:=Sheets(2)).Name = "Progress_By_AU"

            Head_Prog_AU.Copy
                wbNew.Worksheets(3).Range("A1").PasteSpecial Paste:=xlPasteValues
                wbNew.Worksheets(3).Range("A1").PasteSpecial Paste:=xlPasteFormats
                Application.CutCopyMode = False

            pvProg_AU.ClearAllFilters
            pvProg_AU.RepeatAllLabels xlRepeatLabels
            pvProg_AU.TableRange1.Copy
                wbNew.Worksheets(3).Cells(Rows.Count, 1).End(xlUp).Offset(1, 0).PasteSpecial Paste:=xlPasteColumnWidths
                wbNew.Worksheets(3).Cells(Rows.Count, 1).End(xlUp).Offset(1, 0).PasteSpecial Paste:=xlPasteFormats
                wbNew.Worksheets(3).Cells(Rows.Count, 1).End(xlUp).Offset(1, 0).PasteSpecial Paste:=xlPasteValues
                             
                Application.CutCopyMode = False
                
            pvProg_AU.RepeatAllLabels xlDoNotRepeatLabels    

            'Freeze Panes
                wbNew.Worksheets(3).Rows("3:3").Select
                ActiveWindow.FreezePanes = True
            
            'Add Autoflter
                wbNew.Worksheets(3).Rows("2:2").AutoFilter

    'Progress_Detailed_Interaction
        Sheets.Add(After:=Sheets(3)).Name = "Progress_at_Interaction"

            Head_Prog_Int.Copy
                wbNew.Worksheets(4).Range("A1").PasteSpecial Paste:=xlPasteValues
                wbNew.Worksheets(4).Range("A1").PasteSpecial Paste:=xlPasteFormats
                Application.CutCopyMode = False

            pvProg_Int.ClearAllFilters
            pvProg_Int.RepeatAllLabels xlRepeatLabels
            pvProg_Int.TableRange1.Copy
                wbNew.Worksheets(4).Cells(Rows.Count, 1).End(xlUp).Offset(1, 0).PasteSpecial Paste:=xlPasteColumnWidths
                wbNew.Worksheets(4).Cells(Rows.Count, 1).End(xlUp).Offset(1, 0).PasteSpecial Paste:=xlPasteFormats
                wbNew.Worksheets(4).Cells(Rows.Count, 1).End(xlUp).Offset(1, 0).PasteSpecial Paste:=xlPasteValues
                Application.CutCopyMode = False

            pvProg_Int.RepeatAllLabels xlDoNotRepeatLabels

            'Freeze Panes
                wbNew.Worksheets(4).Rows("3:3").Select
                ActiveWindow.FreezePanes = True
            
            'Add Autoflter and filter for <100% and Blank
                wbNew.Worksheets(4).Rows("2:2").Select
                    With Selection
                        .AutoFilter
                        .AutoFilter Field:=16, _
                            Criteria1:="<1", _
                            Operator:=xlOr, _
                            Criteria2:="=" 
                    End With

            'Go to the top of the workbook
                wbNew.Worksheets(4).Range("A3").Select
   
     

    'Go to sheet 1 so when the user opens it they are on the first tab

Application.GoTo (wbNew.Worksheets(1).Range("A2"))

' ******* Save the new workbook *******
'includes a time stamp
    wbNew.SaveAs Filename:="https://eygb.sharepoint.com/sites/Citi_ICG_Remediation/Shared%20Documents/02-Data/05-Diagnostic_Model/Email_Attachments_Sent/" & Format(Now(), "YYYYMMDD-HHMMSS") & "-ICG_Remediation-Daily_Report.xlsx"


     'For Tips see: http://www.rondebruin.nl/win/winmail/Outlook/tips.htm
        'Don't forget to copy the function RangetoHTML in the module.
        'Working in Excel 2000-2016
   
    Set OutApp = CreateObject("Outlook.Application")
    Set OutMail = OutApp.CreateItem(0)
    
    StrBody = "All" & "<br><br>" & _
              "Please see below and attached for today's detailed ICG Remediation Diagnostic reporting" & "<br><br>"

    StrFoot = "<br><br>" & "Please let me know if there are any  changes or enhancements to the reporting you would like to see included. " & _
                "<br><br>" & "Kind regards" & "<br>" & _
              "Nick" & _
              "<br><br><i>" & "(all times are GMT)" & "</i><br><br>"
    
    On Error Resume Next
    With OutMail
        .To = MailTo
        .CC = MailCC
        .Subject = "ICG Diagnostic: Daily Progress Reporting - " & Format(Now(), "DD-MMM")
        .Attachments.Add wbNew.FullName 'original line
        .HTMLBody = StrBody & RangetoHTML(rng) & StrFoot
        .Display
    End With
    On Error GoTo 0

    'Close the workbook
    wbNew.Close


    With Application
        .EnableEvents = True
        .ScreenUpdating = True
    End With

    Set OutMail = Nothing
    Set OutApp = Nothing

End Sub