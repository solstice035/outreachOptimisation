let
    Source = SharePointList,
    removeCols= Table.SelectColumns(
        Source,{
            "Title", 
            "field_24", 
            "field_25", 
            "field_26", 
            "field_27", 
            "field_28", 
            "field_29", 
            "field_30", 
            "ExceptionSubmitterEmail"
            }),
            //rename columns
    renameCols = Table.RenameColumns(
        removeCols,
        {
            {"Title", "EngagementID"},
            {"field_24", "ExceptionCategory"},
            {"field_25", "ExceptionUntil"},
            {"field_26", "ExceptionExplanation"},
            {"field_27", "ExceptionReviewedbyPartner"},
            {"field_28", "ExceptionApprovedbyFinance"},
            {"field_29", "ExceptionDateApproved"},
            {"field_30", "Comments"}
            }
    ),
    // Count number of values in each row
    countValues = Table.AddColumn(
        renameCols,
        "Count",
        each List.Count(
            List.RemoveNulls(
                Record.FieldValues(
                    Record.SelectFields(_, {
                        "ExceptionCategory", 
                        "ExceptionUntil"
                    })
                )
            )
        ),
        Int64.Type
    ),
    // Remove rows with no values
    removeRows = Table.SelectRows(countValues, each [Count] > 0),
    // Remove the Count column
    removeCount = Table.RemoveColumns(removeRows, {"Count"})
in
    removeCount
