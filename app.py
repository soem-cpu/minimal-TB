import pandas as pd

def normalize(x):
    """Robust normalization: strip whitespace, remove hidden chars, title case."""
    if pd.isnull(x):
        return ""
    return str(x).strip().replace('\u200b', '').replace('\t', '').replace('\n', '').title()

def load_dropdowns(dropdown_df):
    # Parse first block: State_Region | Township (A1:B359)
    state_township = dropdown_df.iloc[0:359].dropna()
    state_township_dict = {}
    for _, row in state_township.iterrows():
        state = normalize(row[0])
        township = normalize(row[1])
        if state not in state_township_dict:
            state_township_dict[state] = set()
        state_township_dict[state].add(township)
    return state_township_dict

def load_service_points(service_df):
    # Service Point codes
    svc_set = set(service_df['Service_delivery_point_code'].apply(normalize))
    return svc_set

def check_state_region(df_screen, state_township_dict):
    """Any State_Region not in dropdown dict keys?"""
    return df_screen[~df_screen['State_Region'].apply(normalize).isin(state_township_dict.keys())]

def check_township(df_screen, state_township_dict):
    """Is Township valid for State_Region?"""
    invalid_rows = []
    for idx, row in df_screen.iterrows():
        state = normalize(row['State_Region'])
        township = normalize(row['Township'])
        if state in state_township_dict:
            if township not in state_township_dict[state]:
                invalid_rows.append(idx)
        else:
            # Already caught by check_state_region, but include for completeness
            invalid_rows.append(idx)
    return df_screen.loc[invalid_rows]

def check_service_point(df_screen, svc_set):
    """Is Service_delivery_point in Service Point codes?"""
    return df_screen[~df_screen['Service_delivery_point'].apply(normalize).isin(svc_set)]

def run_checks(xls_file):
    # Load sheets
    xls = pd.ExcelFile(xls_file)
    df_screen = xls.parse("Screening")
    df_dropdown = xls.parse("Dropdown")
    df_service = xls.parse("Service Point")

    # Load reference data
    state_township_dict = load_dropdowns(df_dropdown)
    svc_set = load_service_points(df_service)

    # Debug prints
    print("Dropdown States:", list(state_township_dict.keys())[:10])
    print("Dropdown Townships for 'Shan (South)':", state_township_dict.get("Shan (South)", set()))
    print("Service Point codes:", list(svc_set)[:10])
    print("Sample Screening State_Region:", df_screen['State_Region'].drop_duplicates().head(5).tolist())
    print("Sample Screening Township:", df_screen['Township'].drop_duplicates().head(5).tolist())
    print("Sample Screening Service_delivery_point:", df_screen['Service_delivery_point'].drop_duplicates().head(5).tolist())

    # Checks
    invalid_state = check_state_region(df_screen, state_township_dict)
    invalid_township = check_township(df_screen, state_township_dict)
    invalid_service_point = check_service_point(df_screen, svc_set)

    print(f"\nRows with invalid State_Region: {invalid_state.shape[0]}")
    print(f"Rows with invalid Township: {invalid_township.shape[0]}")
    print(f"Rows with invalid Service_delivery_point: {invalid_service_point.shape[0]}")

    return invalid_state, invalid_township, invalid_service_point
