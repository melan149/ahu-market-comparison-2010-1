import streamlit as st
import pandas as pd
from PIL import Image
import io
import numpy as np

# Streamlit app: Market Analysis Competitor Comparison
# Expects a data file named "Data_Market analysis_2025_9.xlsx" or ".csv" in the same folder
# Expects an "images/" folder containing country flags and brand logos referenced in the data file.

st.set_page_config(layout="wide")

@st.cache_data
def load_data(path_xlsx="Data_Market analysis_2025_9.xlsx", path_csv="Data_Market analysis_2025_9.csv"):
    # Try Excel first, then CSV
    try:
        df = pd.read_excel(path_xlsx, engine="openpyxl")
        return df
    except Exception:
        try:
            # Fallback to CSV for the market analysis data
            df = pd.read_csv(path_csv)
            return df
        except Exception as e:
            st.error(f"Could not load data. Make sure '{path_xlsx}' or '{path_csv}' exists. Error: {e}")
            return pd.DataFrame()

def get_col(df, options):
    for o in options:
        if o in df.columns:
            return o
    return None

# Load dataframe
df = load_data()
if df.empty:
    st.stop()

# --- Column Mappings ---
# These variables map the user-friendly column names to the actual DataFrame column names.
col_brand_name = get_col(df, ["Brand name", "Brand name", "Brand"])
col_unit_name = get_col(df, ["Unit name", "Unit name", "Unit Name"])
col_country_flag = get_col(df, ["Country Flag", "Country Flag", "Country_Flag"])
col_brand_logo = get_col(df, ["Brand logo", "Brand logo", "Brand Logo"])
col_unit_photo = get_col(df, ["Unit photo", "Unit photo", "Unit Photo", "Unit Photo Name"])
col_recovery = get_col(df, ["Recovery type", "Recovery Type", "Recovery_type"])
col_unit_size = get_col(df, ["Unit size", "Unit Size"])
col_airflow_min = get_col(df, ["Minimum airflow [CMH]", "Min airflow [CMH]"])
col_airflow_max = get_col(df, ["Maximum airflow (CCOL) [CMH]", "Max airflow [CMH]"])

# Duct/Internal Dimensions (required for the rename/deduplication logic)
col_int_width = get_col(df, ["Internal Width (Supply Filter) [mm]", "Internal Width [mm]"])
col_int_height = get_col(df, ["Internal Height (Supply Filter) [mm]", "Internal Height [mm]"])
col_duct_width = get_col(df, ["Duct connection Width [mm]", "Duct connection Width"])
col_duct_height = get_col(df, ["Duct connection Height [mm]", "Duct connection Height"])
col_duct_diameter = get_col(df, ["Duct connection Diameter [mm]", "Duct connection Diameter"])

# Recovery Material/Efficiency (required for conditional hiding logic)
col_rrg_material = get_col(df, ["Rotary wheel. Material", "Rotary wheel Material"])
col_rrg_efficiency = get_col(df, ["Rotary wheel. Efficiency [%]", "Rotary wheel Efficiency [%]"])
col_hex_material = get_col(df, ["PCR/HEX material", "HEX material"])
col_hex_efficiency = get_col(df, ["PCR/HEX. Efficiency [%]", "HEX Efficiency [%]"])

# Fallback column names for parameters not explicitly defined above
def get_val(s, col):
    if col and not s['row'].empty and col in s['row'].columns and pd.notna(s['row'][col].iloc[0]):
        return str(s['row'][col].iloc[0])
    return "-"

st.title("AHU Competitor Comparison")
st.markdown("Use the selectors below to compare up to three AHU units.")

# --- Selection Logic ---
num_units = 3
selections = []

# Create a list of all unique brands for the first dropdown
all_brands = df[col_brand_name].unique().tolist() if col_brand_name in df.columns else []
all_brands.insert(0, "(choose)")

# Selection columns (Side-by-side dropdowns)
sel_cols = st.columns(num_units)

for i in range(num_units):
    with sel_cols[i]:
        st.subheader(f"Unit {i+1}")
        
        # 1. Brand Selection
        selected_brand = st.selectbox(
            f"Select Brand {i+1}", 
            all_brands, 
            key=f"brand_sel_{i}"
        )

        current_selection = {'brand': selected_brand, 'size': '(choose)', 'row': pd.DataFrame()}

        if selected_brand != "(choose)":
            # Filter DataFrame by selected brand
            df_filtered_by_brand = df[df[col_brand_name] == selected_brand].copy()
            
            # 2. Unit/Size Selection
            if col_unit_size and col_unit_size in df_filtered_by_brand.columns:
                unit_options = df_filtered_by_brand[col_unit_size].unique().tolist()
                unit_options.sort()
                unit_options.insert(0, "(choose)")

                selected_unit_size = st.selectbox(
                    f"Select Size {i+1}", 
                    unit_options, 
                    key=f"size_sel_{i}"
                )

                if selected_unit_size != "(choose)":
                    # Filter by unit size to get the final row
                    final_row = df_filtered_by_brand[df_filtered_by_brand[col_unit_size] == selected_unit_size]
                    
                    if not final_row.empty:
                        current_selection['size'] = selected_unit_size
                        current_selection['row'] = final_row.iloc[[0]]
                        
                        # Display unit photo if available
                        photo_val = get_val(current_selection, col_unit_photo)
                        if photo_val != "-":
                            try:
                                # Assuming photos are in an 'images' folder
                                st.image(f"images/{photo_val}", caption=f"{selected_brand} - {selected_unit_size}", use_column_width=True)
                            except Exception:
                                st.caption(f"Image for {photo_val} not found.")

        selections.append(current_selection)

st.markdown("---")

# --- Comparison Table Generation ---

# A flat list defining the display structure (Column Name, Display Label)
# (None, "HEADER") is used for subheaders
all_ordered_params = [
    # General data
    (None, "General data"),
    (col_brand_name, "Brand name"),
    (col_country_flag, "Country Flag"),
    (col_brand_logo, "Brand logo"),
    (col_unit_name, "Unit name"),
    (col_unit_size, "Unit size"),
    (col_recovery, "Recovery type"),
    (col_airflow_min, "Minimum airflow [CMH]"),
    (col_airflow_max, "Maximum airflow (CCOL) [CMH]"),

    # Renamed Header: Change 1
    (None, "Overall dimensions"), # Original name, will be renamed in the loop
    (col_int_width, "Internal Width (Supply Filter) [mm]"),
    (col_int_height, "Internal Height (Supply Filter) [mm]"),
    (col_duct_width, "Duct connection Width [mm]"),
    (col_duct_height, "Duct connection Height [mm]"),
    (col_duct_diameter, "Duct connection Diameter [mm]"),

    # Silencer data (Duplicates removed: Change 2)
    (None, "Silencer data"),
    (get_col(df, ["Silencer material", "Silencer. Material"]), "Silencer material"),
    # Duct connections are intentionally omitted here (Change 2)
    
    # Recovery - Rotary wheel (RRG) - Conditional: Change 3
    (None, "Rotary wheel"),
    (col_rrg_material, "Material"),
    (col_rrg_efficiency, "Efficiency [%]"),

    # Recovery - Plate/Counterflow (HEX/PCR) - Conditional: Change 3
    (None, "PCR/HEX recovery exchanger"),
    (col_hex_material, "Material"),
    (col_hex_efficiency, "Efficiency [%]"),
    
    # ... Add more sections as needed (Filters, Fans, Heating/Cooling, etc.)
    (None, "Fan data"),
    (get_col(df, ["Fan type", "Fan Type"]), "Fan type"),
    (get_col(df, ["Fan drive type", "Fan Drive"]), "Fan drive type"),
]


# --- Filtering Logic for Comparison (Changes 1, 2, 3) ---

# 1. Determine the unique recovery types selected (excluding empty selections)
active_selections = [s for s in selections if not s['row'].empty]
recovery_types = [get_val(s, col_recovery) for s in active_selections]
unique_recovery_types = set(t for t in recovery_types if t != '-' and str(t).upper() not in ('NAN', 'NA', 'NOT DISCLOSED', 'NONE'))

# 2. Determine which sections to skip based on Change 3
# Skip if all active units share the same type AND there is only one type (i.e., no mixed types)
skip_rotary = (len(unique_recovery_types) == 1 and 'RRG' in unique_recovery_types)
# Covers both 'HEX' and 'PCR' if they are the only type selected
skip_hex = (len(unique_recovery_types) == 1 and any(t.upper() in ('HEX', 'PCR') for t in unique_recovery_types))

# 3. Build the final list of parameters
final_params = []
header_internal_dimensions = "Internal dimensions & Duct connections"
is_in_rotary_section = False
is_in_hex_section = False

for col_name, display_name in all_ordered_params:
    
    # Check for Headers
    if col_name is None:
        
        # Apply Change 1: Rename the "Overall dimensions" header
        if display_name == "Overall dimensions":
            display_name = header_internal_dimensions
        
        # Track current section for conditional removal
        is_in_rotary_section = (display_name == "Rotary wheel")
        is_in_hex_section = (display_name == "PCR/HEX recovery exchanger")
        
        # Apply Change 3: Conditional Header Removal
        if (is_in_rotary_section and skip_rotary) or (is_in_hex_section and skip_hex):
            continue # Skip the header
        
        final_params.append((None, display_name))
        continue
    
    # Check for Data Rows
    
    # Data row handling (Change 3: Conditional removal of data rows)
    if (is_in_rotary_section and skip_rotary) or (is_in_hex_section and skip_hex):
        continue
        
    final_params.append((col_name, display_name))


# --- Rendering the Final Table ---
st.header("Technical Comparison")

if not active_selections:
    st.info("Please select at least one unit above to start the comparison.")
else:
    # Get column names for the Streamlit table: one column for the parameter label, plus one for each selection
    column_widths = [2] + [1] * len(active_selections)
    
    # Header row with Brand Name and Size
    header_cols = st.columns(column_widths)
    with header_cols[0]:
        st.markdown("**Parameter**")
    for i, s in enumerate(active_selections):
        with header_cols[i + 1]:
            st.markdown(f"**{s['brand']}**")
            st.caption(f"Size: {s['size']}")


    # Iterate through final_params (filtered and renamed list) to create rows
    for col_name, display_name in final_params:
        
        # Subheader row
        if col_name is None:
            st.markdown(f"---")
            subheader_cols = st.columns(column_widths)
            with subheader_cols[0]:
                st.markdown(f"### {display_name}")
            # Do not draw values for the header row
            continue
            
        # Data rows
        row_cols = st.columns(column_widths)
        with row_cols[0]:
            st.markdown(f"**{display_name}**")
            
        for i, s in enumerate(active_selections):
            with row_cols[i + 1]:
                if col_name == col_country_flag or col_name == col_brand_logo or col_name == col_unit_photo:
                    # show image if possible
                    val = get_val(s, col_name)
                    if val != "-":
                        try:
                            # Note: This requires an 'images' folder with the assets
                            img = Image.open(f"images/{val}")
                            st.image(img, width=120, use_container_width=True)
                        except Exception:
                            st.write(val)
                    else:
                        st.write("-")
                else:
                    st.write(get_val(s, col_name))

# --- CSV download of comparison ---
st.markdown("---")
export_df = pd.DataFrame()
for i, s in enumerate(selections):
    label = s['brand'] if s['brand'] != "(choose)" else f"Competitor_{i+1}"
    if not s['row'].empty:
        row_flat = s['row'].copy()
        # Rename columns to reflect the selection brand/size
        row_flat.columns = [f"{label} - {s.get('size', '')} - {c}" for c in row_flat.columns]
        export_df = pd.concat([export_df, row_flat.reset_index(drop=True)], axis=1)

csv_bytes = export_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Full Comparison Data as CSV",
    data=csv_bytes,
    file_name='ahu_comparison_data.csv',
    mime='text/csv',
)
