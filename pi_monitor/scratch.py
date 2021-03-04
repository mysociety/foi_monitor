import pandas as pd


def group_to_other(df, values_col, years_col, labels_col, cut_off=2, agg_func="sum", other_label="Other"):
    """
    Group to get lowest values into an 'Other' category
    """
    pt = df.pivot_table(values_col, labels_col)
    values = pt[values_col]
    if len(values.unique()) < cut_off:
        return df
    top_sectors = values.sort_values(ascending=False)[:cut_off].index

    df["grouped_labels"] = df[labels_col]
    df.loc[~df[labels_col].isin(top_sectors), "grouped_labels"] = other_label

    gb = df.groupby(["grouped_labels", years_col]).agg({values_col: agg_func}).reset_index()
    gb.columns = [labels_col, years_col, values_col]
    print(gb)


sectors = ["A", "A", "B", "B", "C", "C", "D", "D"]
years = [1, 2, 1, 2, 1, 2, 1, 2]
values = [5, 6, 1, 2, 5, 5, 2, 2]

df = pd.DataFrame({"sectors": sectors, "years": years, "values": values})

result = group_to_other(df, "values", "years", "sectors")
print(result)
