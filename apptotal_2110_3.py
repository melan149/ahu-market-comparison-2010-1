import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go 
import numpy as np

# --- Page Configuration ---
st.set_page_config(layout="wide")

# --- Data Loading ---
@st.cache_data
def load_market_data():
    try:
        # Assuming Data_Market analysis_2025_9.xlsx is in the same directory
        return pd.read_excel("Data_Market analysis_2025_9.xlsx", engine='openpyxl')
    except FileNotFoundError:
        st.error("Market analysis data file not found. Please ensure 'Data_Market analysis_2025_9.xlsx' is available.")
        return pd.DataFrame()

@st.cache_data
def load_competitor_data():
    try:
        return pd.read_excel("Data_2025_2.xlsx", sheet_name="data", engine='openpyxl')
    except FileNotFoundError:
        st.error("Competitor details data file not found. Please ensure 'Data_2025_2.xlsx' is available.")
        return pd.DataFrame()

df_market = load_market_data()
df_competitor = load_competitor_data()

# --- Helper Functions ---
def get_column_safe(df, name_options):
    """Finds the first matching column name in the DataFrame."""
    for name in name_options:
        if name in df.columns:
            return name
    return None

# --- Column Mappings for Market Data ---
col_market_quarter = get_column_safe(df_market, ["Quarter"])
col_market_year = get_column_safe(df_market, ["Year"])
col_market_region = get_column_safe(df_market, ["Region"])
col_market_country = get_column_safe(df_market, ["Country"])
col_market_brand = get_column_safe(df_market, ["Brand name"])
col_country_flag = get_column_safe(df_market, ["Country Flag"])
col_brand_logo_market = get_column_safe(df_market, ["Brand logo"])


# --- Column Mappings for Competitor Data ---
col_comp_unit_name = get_column_safe(df_competitor, ["Unit name"])
col_comp_region = get_column_safe(df_competitor, ["Region"])
col_comp_year = get_column_safe(df_competitor, ["Year"])
col_comp_quarter = get_column_safe(df_competitor, ["Quarter"])
col_comp_recovery = get_column_safe(df_competitor, ["Recovery type"])
col_comp_size = get_column_safe(df_competitor, ["Unit size"])
col_comp_brand = get_column_safe(df_competitor, ["Brand name"])
col_comp_logo = get_column_safe(df_competitor, ["Brand logo"])
col_comp_unit_photo = get_column_safe(df_competitor, ["Unit photo"])

# NEW COLUMNS FOR GENERAL INFO
col_comp_unit_type = get_column_safe(df_competitor, ["Unit type"])
col_comp_execution = get_column_safe(df_competitor, ["Execution"])
col_comp_unit_size_quantity = get_column_safe(df_competitor, ["Unit size quantity"])

# Chart-related columns
internal_width_supply_filter_col = get_column_safe(df_competitor, ["Internal Width (Supply Filter) [mm]"])
internal_height_supply_filter_col = get_column_safe(df_competitor, ["Internal Height (Supply Filter) [mm]"])
unit_cross_section_area_supply_filter_area_col = get_column_safe(df_competitor, ["Unit cross section area (Supply Filter) [m2]"])
unit_cross_section_area_supply_fan_col = get_column_safe(df_competitor, ["Unit cross section area (Supply Fan) [m2]"])
duct_connection_height_col = get_column_safe(df_competitor, ["Duct connection Height [mm]"])
duct_connection_diameter_col = get_column_safe(df_competitor, ["Duct connection Diameter [mm]"])
capacity_range1_col = get_column_safe(df_competitor, ["Capacity range1 [kW]"])
capacity_range2_col = get_column_safe(df_competitor, ["Capacity range2 [kW]"])
capacity_range3_col = get_column_safe(df_competitor, ["Capacity range3 [kW]"])
heating_elements_type_col = get_column_safe(df_competitor, ["Heating elements type"])

# Special columns
col_comp_type = get_column_safe(df_competitor, ["Type"])
col_comp_material = get_column_safe(df_competitor, ["Material"])
silencer_casing_col = get_column_safe(df_competitor, ["Silencer casing"])
base_frame_height_col = get_column_safe(df_competitor, ["Base frame/Feets height [mm]"])
cabling_col = get_column_safe(df_competitor, ["Cabling"])

# Coordinates for shape plots (Excluded from main table rendering)
coord_col_pairs_1_5 = [(get_column_safe(df_competitor, [f"x{i}"]), get_column_safe(df_competitor, [f"y{i}"])) for i in range(1, 6)]
coord_col_pairs_6_10 = [(get_column_safe(df_competitor, [f"x{i}"]), get_column_safe(df_competitor, [f"y{i}"])) for i in range(6, 11)]
coord_col_pairs_11_15 = [(get_column_safe(df_competitor, [f"x{i}"]), get_column_safe(df_competitor, [f"y{i}"])) for i in range(11, 16)]
coord_cols = [c for pair in coord_col_pairs_1_5 + coord_col_pairs_6_10 + coord_col_pairs_11_15 for c in pair if c]


# --- App Title ---
st.title("Market & Competitor Analysis")

# --- Sidebar ---
with st.sidebar:
    st.header("Selections")
    num_units = st.slider("Number of comparisons", 2, 10, 2)
    
    selections = []
    filtered_dfs_market = []
    filtered_dfs_competitor = []

    # Common Filters (Used globally and for the new Area vs Size chart)
    available_years = sorted(df_market[col_market_year].dropna().unique())
    selected_year = st.selectbox("Year", available_years)
    
    df_filtered_by_year = df_market[df_market[col_market_year] == selected_year]
    available_quarters = sorted(df_filtered_by_year[col_market_quarter].dropna().unique())
    selected_quarter = st.selectbox("Quarter", available_quarters)

    df_filtered_by_quarter = df_filtered_by_year[df_filtered_by_year[col_market_quarter] == selected_quarter]
    available_regions = sorted(df_filtered_by_quarter[col_market_region].dropna().unique())
    selected_region = st.selectbox("Region", available_regions)

    df_filtered_by_region = df_filtered_by_quarter[df_filtered_by_quarter[col_market_region] == selected_region]

    for i in range(num_units):
        st.markdown("---")
        with st.expander(f"Comparison {i+1}"):
            
            # --- Interconnected Country and Brand Filters ---
            all_countries = sorted(df_filtered_by_region[col_market_country].dropna().unique())
            all_brands = sorted(df_filtered_by_region[col_market_brand].dropna().unique())

            selected_country = st.selectbox(f"Country", ["(any)"] + all_countries, key=f"country_{i}")
            
            if selected_country != "(any)":
                brands_in_country = sorted(df_filtered_by_region[df_filtered_by_region[col_market_country] == selected_country][col_market_brand].dropna().unique())
                selected_brand = st.selectbox(f"Brand name", ["(any)"] + brands_in_country, key=f"brand_{i}")
            else:
                selected_brand = st.selectbox(f"Brand name", ["(any)"] + all_brands, key=f"brand_{i}")

            df_market_selection = df_filtered_by_region.copy()
            if selected_country != "(any)":
                df_market_selection = df_market_selection[df_market_selection[col_market_country] == selected_country]
            if selected_brand != "(any)":
                df_market_selection = df_market_selection[df_market_selection[col_market_brand] == selected_brand]
                if selected_country == "(any)":
                    countries_for_brand = sorted(df_market_selection[col_market_country].dropna().unique())
                    st.info(f"'{selected_brand}' is available in: {', '.join(countries_for_brand)}")


            # --- Competitor Detail Filters (based on brand selection) ---
            df_competitor_selection = pd.DataFrame()
            selected_unit = None
            selected_recovery = None
            selected_size = None
            selected_type = None
            selected_material = None
            
            if selected_brand != "(any)":
                df_comp_filtered = df_competitor[
                    (df_competitor[col_comp_brand] == selected_brand) &
                    (df_competitor[col_comp_year] == selected_year) &
                    (df_competitor[col_comp_quarter] == selected_quarter) &
                    (df_competitor[col_comp_region] == selected_region)
                ]

                available_units = sorted(df_comp_filtered[col_comp_unit_name].dropna().unique())
                if available_units:
                    selected_unit = st.selectbox(f"Unit name", available_units, key=f"unit_{i}")
                    df_comp_filtered = df_comp_filtered[df_comp_filtered[col_comp_unit_name] == selected_unit]
                
                available_recovery = sorted(df_comp_filtered[col_comp_recovery].dropna().unique())
                if available_recovery:
                    selected_recovery = st.selectbox(f"Recovery type", available_recovery, key=f"recovery_{i}")
                    df_comp_filtered = df_comp_filtered[df_comp_filtered[col_comp_recovery] == selected_recovery]

                available_sizes = sorted(df_comp_filtered[col_comp_size].dropna().unique())
                if available_sizes:
                    selected_size = st.selectbox(f"Unit size", available_sizes, key=f"size_{i}")
                    
                    # This df_competitor_selection is the SINGLE ROW for the table details
                    df_competitor_selection = df_comp_filtered[df_comp_filtered[col_comp_size] == selected_size]

                    # Conditional dropdowns for Rotary Wheel Type or Material
                    if selected_recovery == "RRG" and col_comp_type and not df_competitor_selection.empty:
                        available_types = sorted(df_competitor_selection[col_comp_type].dropna().unique())
                        if df_competitor_selection[col_comp_type].iloc[0] in available_types:
                            default_type = df_competitor_selection[col_comp_type].iloc[0]
                        else:
                            default_type = available_types[0] if available_types else None
                            
                        if available_types:
                            selected_type = st.selectbox(f"Rotary wheel type", available_types, index=available_types.index(default_type) if default_type in available_types else 0, key=f"type_{i}")
                            df_competitor_selection = df_competitor_selection[df_competitor_selection[col_comp_type] == selected_type]
                        
                    elif selected_recovery in ["HEX", "PCR"] and col_comp_material and not df_competitor_selection.empty:
                        available_materials = sorted(df_competitor_selection[col_comp_material].dropna().unique())
                        if df_competitor_selection[col_comp_material].iloc[0] in available_materials:
                            default_material = df_competitor_selection[col_comp_material].iloc[0]
                        else:
                            default_material = available_materials[0] if available_materials else None

                        if available_materials:
                            selected_material = st.selectbox(f"PCR/HEX lamels material", available_materials, index=available_materials.index(default_material) if default_material in available_materials else 0, key=f"material_{i}")
                            df_competitor_selection = df_competitor_selection[df_competitor_selection[col_comp_material] == selected_material]
            
            # Storing selections
            selections.append({
                "country": selected_country, "brand": selected_brand,
                "unit": selected_unit, "recovery": selected_recovery, "size": selected_size,
                "type": selected_type, "material": selected_material,
                # Store the global filters as well for use in the Area chart's query
                "year": selected_year, "quarter": selected_quarter, "region": selected_region
            })
            # Ensure the market selection is narrowed down correctly (taking the first row if multiple match, as market data is usually high level)
            filtered_dfs_market.append(df_market_selection.iloc[0:1])
            filtered_dfs_competitor.append(df_competitor_selection)


# --- Main Window ---

# --- Market Overview Section ---
st.markdown("---")
show_market_overview = st.toggle("Show Market Overview", True)
if show_market_overview:
    st.header("Market Overview")
    
    market_cols_to_show = {
        col_market_country: "Country", col_country_flag: "Flag",
        col_market_brand: "Brand", col_brand_logo_market: "Logo",
        "Market information": "Market Information", "Technical demand": "Technical Demand",
        "Company profile": "Company Profile", "Factories": "Factories",
        "Factory in domestic market": "Local Factory", "Sales structure": "Sales Structure",
        "Own sales structure in domestic market": "Local Sales Office",
        "Yearly sales & product value": "Yearly Sales", "Product types": "Product Types",
        "Compact units": "Compact Units", "Compact units. Technical information": "Compact Unit Details",
        "Compact units. Automatics / Controller": "Compact units. Automatics / Controller",
        "Compact units. Certifications & Standards": "Compact Unit Certs.",
        "After sales / Service": "After Sales/Service", "Own service in domestic market": "Local Service",
        "Comments": "Comments", "Technical barriers": "Technical Barriers", "Trade fairs": "Trade Fairs"
    }

    # Header
    overview_cols = st.columns([2] + [1] * num_units)
    overview_cols[0].markdown("**Parameter**")
    for i in range(num_units):
        with overview_cols[i+1]:
            s = selections[i]
            st.markdown(f"**{s['brand']}**" if s['brand'] != "(any)" else f"**Comparison {i+1}**")

    # Data Rows
    for col, display_name in market_cols_to_show.items():
        if col in df_market.columns:
            row_cols = st.columns([2] + [1] * num_units)
            row_cols[0].markdown(f"**{display_name}**")
            for i in range(num_units):
                with row_cols[i+1]:
                    df_sel = filtered_dfs_market[i]
                    if not df_sel.empty and col in df_sel.columns:
                        val = df_sel[col].iloc[0]
                        if pd.notna(val):
                            if col in [col_country_flag, col_brand_logo_market]:
                                try:
                                    # Note: Assumes images are available locally in an 'images/' folder
                                    st.image(f"images/{val}", width=60)
                                except Exception:
                                    st.write(val)
                            else:
                                st.write(val)
                        else:
                            st.write("-")
                    else:
                        st.write("-")


# --- Technical Details Section ---
st.markdown("---")
st.header("Technical Details")

if any(s['brand'] == "(any)" for s in selections):
    st.info("Select a brand for each comparison to see technical details.")
else:
    # Brand Logos and Unit Photos (Keep visible for context)
    st.subheader("Brand Logos")
    logo_cols = st.columns(num_units)
    for i in range(num_units):
        with logo_cols[i]:
            df_comp = filtered_dfs_competitor[i]
            if not df_comp.empty and pd.notna(df_comp[col_comp_logo].iloc[0]):
                try:
                    st.image(f"images/{df_comp[col_comp_logo].iloc[0]}", width=150)
                except Exception:
                    st.write("Logo not found")
    
    st.subheader("Unit Photos")
    photo_cols = st.columns(num_units)
    for i in range(num_units):
        with photo_cols[i]:
            df_comp = filtered_dfs_competitor[i]
            if not df_comp.empty and pd.notna(df_comp[col_comp_unit_photo].iloc[0]):
                try:
                    st.image(f"images/{df_comp[col_comp_unit_photo].iloc[0]}", use_container_width=True)
                except Exception:
                    st.write("Photo not found")

    # Detailed Comparison Table
    st.subheader("Technical Comparison")
    
    # Helper for rendering data rows inside expanders
    def render_data_row(cols, col_name, df_list, num_units, colors):
        row_cols = st.columns(cols)
        row_cols[0].write(col_name)
        for i in range(num_units):
            with row_cols[i+1]:
                df_comp = df_list[i]
                if not df_comp.empty and col_name in df_comp.columns:
                    val = df_comp[col_name].iloc[0]
                    color = colors[i % len(colors)]
                    st.markdown(f'<div style="text-align: center; color: {color};">{val}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div style="text-align: center;">-</div>', unsafe_allow_html=True)


    sections_config = [
        # NEW SECTION (Change 3 & 4)
        {
            "title": "General information",
            "rows": [col_comp_unit_type, col_comp_execution, col_comp_unit_size_quantity],
            "charts": ["chart_area_vs_size"] # Chart now nested here
        },
        {
            "title": "Certification data",
            "rows": [
                get_column_safe(df_competitor, ["Eurovent Certificate"]),
                get_column_safe(df_competitor, ["Eurovent Model Box"]),
                get_column_safe(df_competitor, ["Casing Strength (Eurovent)"]),
                get_column_safe(df_competitor, ["Casing leakage, negative pressure (Eurovent)"]),
                get_column_safe(df_competitor, ["Casing leakage, positive pressure (Eurovent)"]),
                get_column_safe(df_competitor, ["Filter mounting leakage (Eurovent)"]),
                get_column_safe(df_competitor, ["Thermal isolation (Eurovent)"]),
                get_column_safe(df_competitor, ["Thermal bridges (Eurovent)"]),
                get_column_safe(df_competitor, ["VDI 6022-1 certification"])
            ],
            "charts": []
        },
        {
            "title": "Available configurations",
            "rows": [
                get_column_safe(df_competitor, ["Supply"]),
                get_column_safe(df_competitor, ["Exhaust"]),
                get_column_safe(df_competitor, ["Supply/Exhaust without recovery"]),
                get_column_safe(df_competitor, ["Supply/Exhaust with RRG"]),
                get_column_safe(df_competitor, ["Supply/Exhaust with PCR (HEX)"]),
                get_column_safe(df_competitor, ["Supply/Exhaust with glycol"])
            ],
            "charts": []
        },
        {
            "title": "Casing",
            "rows": [
                get_column_safe(df_competitor, ["Insulation material"]),
                get_column_safe(df_competitor, ["Insulation thickness [mm]"]),
                get_column_safe(df_competitor, ["Metal sheet (Internal)"]),
                get_column_safe(df_competitor, ["Metal sheet thickness (Internal) [mm]"]),
                get_column_safe(df_competitor, ["Metal sheet (External)"]),
                get_column_safe(df_competitor, ["Metal sheet thickness (External) [mm]"])
            ],
            "charts": []
        },
        {
            "title": "Airflows",
            "rows": [
                get_column_safe(df_competitor, ["Minimum airflow [CMH]"]),
                get_column_safe(df_competitor, ["Maximum airflow (CCOL) [CMH]"]),
                get_column_safe(df_competitor, ["Optimal airflow (ErP2018) [CMH]"]),
                get_column_safe(df_competitor, ["Air speed on Filter at opt airflow (ErP) [m/s]"])
            ],
            "charts": []
        },
        {
            "title": "Overall dimensions",
            "rows": [
                internal_width_supply_filter_col,
                internal_height_supply_filter_col
            ],
            "charts": ["chart1"] # Internal Cross Section Area (Supply Filter) Shape
        },
        {
            "title": "Rotary wheel",
            "rows": [
                col_comp_type,
                get_column_safe(df_competitor, ["Efficiency-RRG"]),
                get_column_safe(df_competitor, ["Fan power-RRG"]),
                get_column_safe(df_competitor, ["Rotor diameter [mm]"]),
                get_column_safe(df_competitor, ["Rotor length [mm]"])
            ],
            "charts": []
        },
        {
            "title": "PCR/HEX recovery exchanger",
            "rows": [
                col_comp_material,
                get_column_safe(df_competitor, ["Sens. efficiency at nominal balanced airflows_PCR/HEX [%]"]),
                get_column_safe(df_competitor, ["Efficiency-HEX/PCR"]),
                get_column_safe(df_competitor, ["Fan power-HEX/PCR"])
            ],
            "charts": []
        },
        {
            "title": "Fan section data",
            "rows": [
                get_column_safe(df_competitor, ["Motor type"]),
                get_column_safe(df_competitor, ["Air speed on Fan at opt airflow (ErP) [m/s]"]),
                unit_cross_section_area_supply_fan_col
            ],
            "charts": ["chart2"] # Internal Cross Section Area (Supply Fan) Shape
        },
        {
            "title": "Electrical heater",
            "rows": [
                heating_elements_type_col
            ],
            "charts": ["electrical_heater_chart"] # Electrical Heater Capacity (kW)
        },
        {
            "title": "Water heater",
            "rows": [
                get_column_safe(df_competitor, ["Water heater_min rows"]),
                get_column_safe(df_competitor, ["Water heater_max rows"])
            ],
            "charts": []
        },
        {
            "title": "Water cooler",
            "rows": [
                get_column_safe(df_competitor, ["Water cooler_min rows"]),
                get_column_safe(df_competitor, ["Water cooler_max rows"])
            ],
            "charts": []
        },
        {
            "title": "DX/DXH cooler",
            "rows": [
                get_column_safe(df_competitor, ["DXH_min rows"]),
                get_column_safe(df_competitor, ["DXH_max rows"])
            ],
            "charts": []
        },
        {
            "title": "Supply Filter",
            "rows": [
                get_column_safe(df_competitor, ["Filter type_Supply"]),
                get_column_safe(df_competitor, ["Filter size_Supply [mm]"]),
                get_column_safe(df_competitor, ["Media area_Supply [m2]"]),
                get_column_safe(df_competitor, ["Weight_Supply [kg]"])
            ],
            "charts": []
        },
        {
            "title": "Exhaust Filter",
            "rows": [
                get_column_safe(df_competitor, ["Filter type_Exhaust"]),
                get_column_safe(df_competitor, ["Filter size_Exhaust [mm]"]),
                get_column_safe(df_competitor, ["Media area_Exhaust [m2]"]),
                get_column_safe(df_competitor, ["Weight_Exhaust [kg]"])
            ],
            "charts": []
        },
        {
            "title": "Silencer data",
            "rows": [
                silencer_casing_col,
                get_column_safe(df_competitor, ["Silencer length [mm]"]),
                get_column_safe(df_competitor, ["Duct connection Width [mm]"]),
                duct_connection_height_col,
                duct_connection_diameter_col
            ],
            "charts": ["chart3"] # Supply Duct Connection Shape
        },
        {
            "title": "Construction details",
            "rows": [
                base_frame_height_col,
                cabling_col
            ],
            "charts": []
        }
    ]
    
    col_widths = [3] + [2] * num_units
    colors = px.colors.qualitative.Plotly

    # Table Header (Visible always)
    table_header_cols = st.columns(col_widths)
    table_header_cols[0].markdown("---")
    table_header_cols[0].markdown("**Parameter**")
    for i, s in enumerate(selections):
        with table_header_cols[i+1]:
            st.markdown(f"**{s['brand']} - {s['unit']} - {s['size']}**") 
    table_header_cols[0].markdown("---")

    # Loop through sections and create expanders (Change 5: default collapsed)
    for section in sections_config:
        st.markdown(f'<h4 style="text-align: center; font-size: 1.2em; margin: 1em 0;">{section["title"]}</h4>', unsafe_allow_html=True)
        
        # All sections are collapsed by default
        with st.expander(f"Show {section['title']} details", expanded=False): 
            
            # Render Rows for the Section
            for col_name in section["rows"]:
                if col_name in df_competitor.columns and col_name not in coord_cols:
                    render_data_row(col_widths, col_name, filtered_dfs_competitor, num_units, colors)

            # Render Charts for the Section
            for chart_name in section["charts"]:
                
                # --- CHART: Unit Cross Section Area (Supply Filter) vs Unit Size (Scatter) ---
                if chart_name == "chart_area_vs_size":
                    # This chart is specifically requested to be between Unit size quantity and Certification data
                    full_chart_data = []
                    unique_y_labels = []

                    for i, s in enumerate(selections):
                        brand = s.get('brand')
                        unit = s.get('unit')
                        recovery = s.get('recovery')
                        
                        if brand and brand != "(any)" and unit and recovery:
                            temp_df = df_competitor[
                                (df_competitor[col_comp_brand] == brand) &
                                (df_competitor[col_comp_unit_name] == unit) &
                                (df_competitor[col_comp_recovery] == recovery) &
                                (df_competitor[col_comp_year] == s.get('year')) &
                                (df_competitor[col_comp_quarter] == s.get('quarter')) & # <-- FIXED TYPO
                                (df_competitor[col_comp_region] == s.get('region'))     # <-- FIXED TYPO
                            ].copy()
                            
                            if recovery == "RRG" and s.get('type'):
                                temp_df = temp_df[temp_df[col_comp_type] == s.get('type')]
                            elif recovery in ["HEX", "PCR"] and s.get('material'):
                                temp_df = temp_df[temp_df[col_comp_material] == s.get('material')]
                            
                            
                            if not temp_df.empty and unit_cross_section_area_supply_filter_area_col in temp_df.columns and col_comp_size in temp_df.columns:
                                unique_sizes_df = temp_df.drop_duplicates(subset=[col_comp_size, unit_cross_section_area_supply_filter_area_col])

                                for _, row in unique_sizes_df.iterrows():
                                    area_val_raw = row[unit_cross_section_area_supply_filter_area_col]
                                    area_val = pd.to_numeric(area_val_raw, errors='coerce')
                                    
                                    unit_size = row[col_comp_size]
                                    y_label = f"{brand} - {unit_size}"
                                    
                                    if pd.notna(area_val) and area_val > 0:
                                        full_chart_data.append({
                                            "Y-Label": y_label, 
                                            "Area (m²)": area_val, 
                                            "Brand": brand,
                                            "Unit Size": unit_size
                                        })
                                        if y_label not in unique_y_labels:
                                            unique_y_labels.append(y_label)

                    
                    if full_chart_data:
                        chart_df = pd.DataFrame(full_chart_data)
                        unique_y_labels.reverse() 
                        
                        fig = px.scatter(
                            chart_df, 
                            x="Area (m²)", 
                            y="Y-Label", 
                            color="Brand", 
                            hover_data={"Unit Size": True, "Area (m²)": ":.3f"},
                            title='Unit Cross Section Area (Supply Filter) vs Unit Size',
                            color_discrete_sequence=colors
                        )

                        fig.update_traces(marker=dict(size=10, opacity=0.8), mode='markers')
                        
                        fig.update_layout(
                            yaxis={
                                'categoryorder': 'array', 
                                'categoryarray': unique_y_labels
                            },
                            xaxis=dict(range=[0, chart_df['Area (m²)'].max() * 1.15], title='Area (m²)'),
                            height=200 + 30 * len(unique_y_labels)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No Unit Cross Section Area (Supply Filter) data available for plotting under the current brand/unit selections.")


                # --- CHART 1: Internal Cross Section Area (Supply Filter) Shape ---
                elif chart_name == "chart1":
                    # This chart is nested under Overall dimensions
                    fig = go.Figure()
                    all_x, all_y = [], []
                    
                    for i, df_unit in enumerate(filtered_dfs_competitor):
                        if not df_unit.empty:
                            x_vals, y_vals = [], []
                            label = f"Unit {i+1}: {selections[i]['brand']} - {selections[i]['size']}"
                            for x_name, y_name in coord_col_pairs_1_5:
                                if x_name in df_unit and y_name in df_unit and pd.notna(df_unit[x_name].iloc[0]) and pd.notna(df_unit[y_name].iloc[0]):
                                    x_vals.append(df_unit[x_name].iloc[0])
                                    y_vals.append(df_unit[y_name].iloc[0])
                            
                            if x_vals and y_vals:
                                all_x.extend(x_vals)
                                all_y.extend(y_vals)
                                fig.add_trace(go.Scatter(
                                    x=x_vals, y=y_vals, mode='lines+markers', 
                                    name=label, 
                                    line=dict(color=colors[i % len(colors)]),
                                    marker=dict(size=6)
                                ))
                    
                    if fig.data:
                        max_x = max(all_x) if all_x else 1
                        max_y = max(all_y) if all_y else 1

                        fig.update_yaxes(scaleanchor="x", scaleratio=1)
                        fig.update_layout(
                            title='Internal Cross Section Area (Supply Filter) [mm]', 
                            xaxis_title='Width (mm)', 
                            yaxis_title='Height (mm)',
                            xaxis=dict(range=[0, max_x * 1.15]), 
                            yaxis=dict(range=[0, max_y * 1.15]), 
                            hovermode="closest"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No coordinate data available for Internal Cross Section Area (Supply Filter).")


                # --- CHART 2: Internal Cross Section Area (Supply Fan) Shape ---
                elif chart_name == "chart2":
                    # This chart is nested under Fan section data
                    fig = go.Figure()
                    all_x, all_y = [], []
                    
                    for i, df_unit in enumerate(filtered_dfs_competitor):
                        if not df_unit.empty:
                            x_vals, y_vals = [], []
                            label = f"Unit {i+1}: {selections[i]['brand']} - {selections[i]['size']}"
                            for x_name, y_name in coord_col_pairs_6_10:
                                if x_name in df_unit and y_name in df_unit and pd.notna(df_unit[x_name].iloc[0]) and pd.notna(df_unit[y_name].iloc[0]):
                                    x_vals.append(df_unit[x_name].iloc[0])
                                    y_vals.append(df_unit[y_name].iloc[0])

                            if x_vals and y_vals:
                                all_x.extend(x_vals)
                                all_y.extend(y_vals)
                                fig.add_trace(go.Scatter(
                                    x=x_vals, y=y_vals, mode='lines+markers', 
                                    name=label, 
                                    line=dict(color=colors[i % len(colors)]),
                                    marker=dict(size=6)
                                ))

                    if fig.data:
                        max_x = max(all_x) if all_x else 1
                        max_y = max(all_y) if all_y else 1
                        
                        fig.update_yaxes(scaleanchor="x", scaleratio=1)
                        fig.update_layout(
                            title='Internal Cross Section Area (Supply Fan) [mm]', 
                            xaxis_title='Width (mm)', 
                            yaxis_title='Height (mm)',
                            xaxis=dict(range=[0, max_x * 1.15]), 
                            yaxis=dict(range=[0, max_y * 1.15]), 
                            hovermode="closest"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No coordinate data available for Internal Cross Section Area (Supply Fan).")

                # --- CHART 3: Supply Duct Connection Shape ---
                elif chart_name == "chart3":
                    # This chart is nested under Silencer data
                    fig = go.Figure()
                    max_x = 0
                    max_y = 0

                    for i, df_unit in enumerate(filtered_dfs_competitor):
                        if not df_unit.empty:
                            is_circ = pd.notna(df_unit[duct_connection_diameter_col].iloc[0]) and df_unit[duct_connection_diameter_col].iloc[0] > 0
                            
                            label = f"Unit {i+1}: {selections[i]['brand']} - {selections[i]['size']}"

                            if is_circ:
                                diameter = df_unit[duct_connection_diameter_col].iloc[0]
                                radius = diameter / 2.0
                                color = colors[i % len(colors)]
                                
                                x_center = radius
                                y_center = radius
                                
                                max_x = max(max_x, x_center + radius)
                                max_y = max(max_y, y_center + radius)
                                
                                fig.add_shape(
                                    type="circle", 
                                    x0=0, y0=0, x1=diameter, y1=diameter, 
                                    line=dict(color=color), 
                                    name=label, 
                                    xref='x', yref='y'
                                )
                                fig.add_trace(go.Scatter(
                                    x=[x_center], y=[y_center], 
                                    mode='markers', 
                                    name=f"{label} (D={diameter})",
                                    marker=dict(size=10, color=color, symbol='circle')
                                ))

                            else: # Rectangular/Polygon
                                x_vals, y_vals = [], []
                                for j, (x_name, y_name) in enumerate(coord_col_pairs_11_15):
                                    if x_name in df_unit and y_name in df_unit and pd.notna(df_unit[x_name].iloc[0]) and pd.notna(df_unit[y_name].iloc[0]):
                                        x_vals.append(df_unit[x_name].iloc[0])
                                        y_vals.append(df_unit[y_name].iloc[0])
                                if x_vals and y_vals:
                                    max_x = max(max_x, max(x_vals))
                                    max_y = max(max_y, max(y_vals))
                                    fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines+markers', name=label, line=dict(color=colors[i % len(colors)]), marker=dict(size=6)))
                    
                    if fig.data or fig.layout.shapes:
                        max_x = max_x if max_x > 0 else 100
                        max_y = max_y if max_y > 0 else 100
                        
                        fig.update_layout(
                            title="Supply Duct Connection (mm)", 
                            xaxis_title="Width (mm)", 
                            yaxis_title="Height (mm)",
                            xaxis=dict(range=[0, max_x * 1.15]), 
                            yaxis=dict(range=[0, max_y * 1.15])
                        )
                        fig.update_yaxes(scaleanchor="x", scaleratio=1)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No coordinate data available for Supply Duct Connection.")


                # --- CHART 4: Electrical Heater Capacity (kW) ---
                elif chart_name == "electrical_heater_chart":
                    # This chart is nested under Electrical heater
                    chart_data = []
                    for i, df_unit in enumerate(filtered_dfs_competitor):
                        if not df_unit.empty and all(c in df_unit and pd.notna(df_unit[c].iloc[0]) for c in [capacity_range1_col, capacity_range2_col, capacity_range3_col]):
                            label = f"Unit {i+1}: {selections[i]['brand']} - {selections[i]['size']}"
                            
                            val1 = pd.to_numeric(df_unit[capacity_range1_col].iloc[0], errors='coerce')
                            val2 = pd.to_numeric(df_unit[capacity_range2_col].iloc[0], errors='coerce')
                            val3 = pd.to_numeric(df_unit[capacity_range3_col].iloc[0], errors='coerce')

                            if pd.notna(val1): chart_data.append({"Capacity Range": "Range 1", "Value (kW)": val1, "Selection": label})
                            if pd.notna(val2): chart_data.append({"Capacity Range": "Range 2", "Value (kW)": val2, "Selection": label})
                            if pd.notna(val3): chart_data.append({"Capacity Range": "Range 3", "Value (kW)": val3, "Selection": label})

                    if chart_data:
                        chart_df = pd.DataFrame(chart_data)
                        fig = px.bar(chart_df, x="Capacity Range", y="Value (kW)", color="Selection", barmode="group", title='Electrical Heater Capacity (kW)')
                        fig.update_yaxes(range=[0, chart_df['Value (kW)'].max() * 1.15 if not chart_df.empty else 1])
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No Electrical Heater Capacity data available for plotting.")
