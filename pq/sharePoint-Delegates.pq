let
    Source = SharePointList,
    removeCols = Table.SelectColumns(
        Source,
        {
            "Title",
            "field_15",
            "field_16",
            "field_17",
            "field_18",
            "field_19",
            "field_20",
            "field_21",
            "field_22",
            "field_23"
        }
    ),
    renameCols = Table.RenameColumns(
        removeCols, {
            {"Title", "EngagementID"},
            {"field_15", "Delegate1"},
            {"field_16", "Delegate1Email"},
            {"field_17", "Delegate1Date"},
            {"field_18", "Delegate2Date"},
            {"field_19", "Delegate3Date"},
            {"field_20", "Delegate2"},
            {"field_21", "Delegate2Email"},
            {"field_22", "Delegate3"},
            {"field_23", "Delegate3Email"}
            }),
        // Count number of values in each row
    countValues = Table.AddColumn(
        renameCols,
        "Count",
        each List.Count(
            List.RemoveNulls(
                Record.FieldValues(
                    Record.SelectFields(_, {"Delegate1", "Delegate2", "Delegate3"})
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