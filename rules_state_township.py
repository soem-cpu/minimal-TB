import pandas as pd

def normalize(x):
    """Normalize for comparison: strip, lower, remove hidden chars, no casing change."""
    if pd.isnull(x):
        return ""
    return str(x).strip().replace('\u200b', '').replace('\t', '').replace('\n', '')

def load_dropdowns(dropdown_df):
    # Get valid State_Region and townships from single Variable/Value table
    state_regions = set()
    state_township_dict = {}
    for _, row in dropdown_df.iterrows():
        var = normalize(row['Variable'])
        val = normalize(row['Value'])
        if var.lower() == "state_region":
            state_regions.add(val)
        else:
            # var is a State_Region, val is a township for that
            state = var
            township = val
            if state not in state_township_dict:
                state_township_dict[state] = set()
            state_township_dict[state].add(township)
    return state_regions, state_township_dict

def check_state_region(df, state_regions, col="State_Region"):
    # Normalize and check State_Region validity
    return df[~df[col].apply(normalize).isin(state_regions)]

def check_township(df, state_township_dict, state_col="State_Region", township_col="Township"):
    # Check if township is valid for the given state
    invalid_rows = []
    for idx, row in df.iterrows():
        state = normalize(row[state_col])
        township = normalize(row[township_col])
        if state in state_township_dict:
            if township not in state_township_dict[state]:
                invalid_rows.append(idx)
        else:
            # State itself is invalid, already caught by state check
            invalid_rows.append(idx)
    return df.loc[invalid_rows]

def run_state_township_checks(xls_file, sheet_name="Screening"):
    # Load sheets
    xls = pd.ExcelFile(xls_file)
    df_target = xls.parse(sheet_name)
    df_dropdown = xls.parse("Dropdown")

    # Load reference data
    state_regions, state_township_dict = load_dropdowns(df_dropdown)

    # Debug prints
    print("Valid State_Region:", sorted(list(state_regions)))
    print("Sample township for 'Shan (South)':", state_township_dict.get("Shan (South)", set()))
    print("Sample uploaded State_Region:", df_target['State_Region'].drop_duplicates().head().tolist())
    print("Sample uploaded Township:", df_target['Township'].drop_duplicates().head().tolist())

    invalid_state = check_state_region(df_target, state_regions, "State_Region")
    invalid_township = check_township(df_target, state_township_dict, "State_Region", "Township")

    print(f"\nRows with invalid State_Region: {invalid_state.shape[0]}")
    print(f"Rows with invalid Township: {invalid_township.shape[0]}")

    return invalid_state, invalid_township
