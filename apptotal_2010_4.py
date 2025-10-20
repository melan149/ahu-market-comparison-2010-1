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
        st.error("Market analysis data file not found.")
        return pd.DataFrame()

@st.cache_data
def load_competitor_data():
    try:
        # FIX: Changed 'openypxl' to 'openpyxl'
        return pd.read_excel("Data_2025_2.xlsx", sheet_name="data", engine='openpyxl')
    except FileNotFoundError:
        st.error("Competitor details data file not found.")
        return pd.DataFrame()

df_market = load_market_data()
df_competitor = load_competitor_data()

# --- Helper Functions ---
def get_column_safe(df, name_options):
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
col_comp_type = get_column_safe(df_competitor, ["Type"])
col_comp_material = get_column_safe(df_competitor, ["Material"])
silencer_casing_col = get_column_safe(df_competitor, ["Silencer casing"])
base_frame_height_col = get_column_safe(df_competitor, ["Base frame/Feets height [mm]"])
cabling_col = get_column_safe(df_competitor, ["Cabling"])

# Chart-related columns
internal_height_supply_filter_col = get_column_safe(df_competitor, ["Internal Height (Supply Filter) [mm]"])
unit_cross_section_area_supply_fan_col = get_column_safe(df_competitor, ["Unit cross section area (Supply Fan) [m2]"])
duct_connection_height_col = get_column_safe(df_competitor, ["Duct connection Height [mm]"])
duct_connection_diameter_col = get_column_safe(df_competitor, ["Duct connection Diameter [mm]"])
capacity_range1_col = get_column_safe(df_competitor, ["Capacity range1 [kW]"])
capacity_range2_col = get_column_safe(df_competitor, ["Capacity range2 [kW]"])
capacity_range3_col = get_column_safe(df_competitor, ["Capacity range3 [kW]"])
heating_elements_type_col = get_column_safe(df_competitor, ["Heating elements type"])

coord_col_pairs_1_5 = [(get_column_safe(df_competitor, [f"x{i}"]), get_column_safe(df_competitor, [f"y{i}"])) for i in range(1, 6)]
coord_col_pairs_6_10 = [(get_column_safe(df_competitor, [f"x{i}"]), get_column_safe(df_competitor, [f"y{i}"])) for i in range(6, 11)]
coord_col_pairs_11_15 = [(get_column_safe(df_competitor, [f"x{i}"]), get_column_safe(df_competitor, [f"y{i}"])) for i in range(11, 16)]

# --- App Title ---
st.title("Combined Market & Competitor Analysis")

# --- Sidebar ---
with st.sidebar:
    st.header("Selections")
    num_units = st.slider("Number of comparisons", 2, 10, 2)
    
    selections = []
    filtered_dfs_market = []
    filtered_dfs_competitor = []

    # Common Filters
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
            if selected_brand != "(any)":
                df_comp_filtered = df_competitor[
                    (df_competitor[col_comp_brand] == selected_brand) &
                    (df_competitor[col_comp_year] == selected_year) &
                    (df_competitor[col_comp_quarter] == selected_quarter) &
                    (df_competitor[col_comp_region] == selected_region)
                ]

                available_units = sorted(df_comp_filtered[col_comp_unit_name].dropna().unique())
                selected_unit = st.selectbox(f"Unit name", available_units, key=f"unit_{i}")
                
                df_comp_filtered = df_comp_filtered[df_comp_filtered[col_comp_unit_name] == selected_unit]
                
                available_recovery = sorted(df_comp_filtered[col_comp_recovery].dropna().unique())
                selected_recovery = st.selectbox(f"Recovery type", available_recovery, key=f"recovery_{i}")

                df_comp_filtered = df_comp_filtered[df_comp_filtered[col_comp_recovery] == selected_recovery]

                available_sizes = sorted(df_comp_filtered[col_comp_size].dropna().unique())
                selected_size = st.selectbox(f"Unit size", available_sizes, key=f"size_{i}")
                
                df_competitor_selection = df_comp_filtered[df_comp_filtered[col_comp_size] == selected_size]

                # Conditional dropdowns for Rotary Wheel Type or Material
                selected_type = None
                selected_material = None
                if selected_recovery == "RRG" and col_comp_type:
                    available_types = sorted(df_competitor_selection[col_comp_type].dropna().unique())
                    selected_type = st.selectbox(f"Rotary wheel type", available_types, key=f"type_{i}")
                    df_competitor_selection = df_competitor_selection[df_competitor_selection[col_comp_type] == selected_type]
                elif selected_recovery in ["HEX", "PCR"] and col_comp_material:
                    available_materials = sorted(df_competitor_selection[col_comp_material].dropna().unique())
                    selected_material = st.selectbox(f"PCR/HEX lamels material", available_materials, key=f"material_{i}")
                    df_competitor_selection = df_competitor_selection[df_competitor_selection[col_comp_material] == selected_material]
            else:
                selected_unit, selected_recovery, selected_size, selected_type, selected_material = None, None, None, None, None
            
            # Storing selections
            selections.append({
                "country": selected_country, "brand": selected_brand,
                "unit": selected_unit, "recovery": selected_recovery, "size": selected_size,
                "type": selected_type, "material": selected_material
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
        "Compact units. Automatics / Controller": "Compact Unit Controls",
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
                                    st.image(f"images/{val}", width=60)
                                except Exception:
                                    st.write(val)
                            else:
                                st.write(val)
                        else:
                            st.write("-")
                    else:
                        st.write("-")


# --- Competitors Details Section ---
st.markdown("---")
st.header("Competitors Details")

if any(s['brand'] == "(any)" for s in selections):
    st.info("Select a brand for each comparison to see competitor details.")
else:
    # Brand Logos and Unit Photos
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
    
    header_triggers_map = {
        get_column_safe(df_competitor, ["Eurovent Certificate"]): "Certification data",
        get_column_safe(df_competitor, ["Supply"]): "Available configurations",
        get_column_safe(df_competitor, ["Insulation material"]): "Casing",
        get_column_safe(df_competitor, ["Minimum airflow [CMH]"]): "Airflows",
        get_column_safe(df_competitor, ["Internal Width (Supply Filter) [mm]"]): "Overall dimensions",
        get_column_safe(df_competitor, ["Type"]): "Rotary wheel",
        get_column_safe(df_competitor, ["Sens. efficiency at nominal balanced airflows_PCR/HEX [%]"]): "PCR/HEX recovery exchanger",
        get_column_safe(df_competitor, ["Motor type"]): "Fan section data",
        heating_elements_type_col: "Electrical heater",
        get_column_safe(df_competitor, ["Water heater_min rows"]): "Water heater",
        get_column_safe(df_competitor, ["Water cooler_min rows"]): "Water cooler",
        get_column_safe(df_competitor, ["DXH_min rows"]): "DX/DXH cooler",
        get_column_safe(df_competitor, ["Filter type_Supply"]): "Supply Filter",
        get_column_safe(df_competitor, ["Filter type_Exhaust"]): "Exhaust Filter",
        silencer_casing_col: "Silencer data"
    }

    # Table Header
    col_widths = [3] + [2] * num_units
    table_header_cols = st.columns(col_widths)
    table_header_cols[0].markdown("**Parameter**")
    for i, s in enumerate(selections):
        with table_header_cols[i+1]:
            st.markdown(f"**{s['brand']} - {s['unit']} - {s['size']}**")
    
    displayed_headers = set()
    construction_details_added = False

    all_cols_ordered = []
    
    # Logic to order columns and insert special sections
    for col_name in df_competitor.columns:
        if col_name == silencer_casing_col and not construction_details_added:
            all_cols_ordered.append({"type": "row", "col": col_name})
            all_cols_ordered.append({"type": "header", "title": "Construction details"})
            if base_frame_height_col: all_cols_ordered.append({"type": "row", "col": base_frame_height_col})
            if cabling_col: all_cols_ordered.append({"type": "row", "col": cabling_col})
            construction_details_added = True
            continue

        header_title = header_triggers_map.get(col_name)
        if header_title and header_title not in displayed_headers:
            all_cols_ordered.append({"type": "header", "title": header_title})
            displayed_headers.add(header_title)
        
        all_cols_ordered.append({"type": "row", "col": col_name})
        
        # Insert charts at specific points
        if col_name == internal_height_supply_filter_col: all_cols_ordered.append({"type": "chart", "name": "chart1"})
        if col_name == unit_cross_section_area_supply_fan_col: all_cols_ordered.append({"type": "chart", "name": "chart2"})
        if col_name == duct_connection_height_col: all_cols_ordered.append({"type": "chart", "name": "chart3"})
        if col_name == heating_elements_type_col: all_cols_ordered.append({"type": "chart", "name": "electrical_heater_chart"})

    excluded_cols = [
        col_comp_brand, col_comp_logo, col_comp_unit_photo, col_comp_year, col_comp_quarter, col_comp_region,
        col_comp_unit_name, col_comp_recovery, col_comp_size, col_comp_type, col_comp_material
    ]
    coord_cols = [c for pair in coord_col_pairs_1_5 + coord_col_pairs_6_10 + coord_col_pairs_11_15 for c in pair if c]
    excluded_cols.extend(coord_cols)
    
    colors = px.colors.qualitative.Plotly

    # Displaying rows, headers, and charts
    for item in all_cols_ordered:
        if item["type"] == "header":
            st.markdown(f'<h4 style="text-align: center; font-size: 1.2em; margin: 1em 0;">{item["title"]}</h4>', unsafe_allow_html=True)
        elif item["type"] == "row" and item["col"] not in excluded_cols:
            row_cols = st.columns(col_widths)
            row_cols[0].write(item["col"])
            for i in range(num_units):
                with row_cols[i+1]:
                    df_comp = filtered_dfs_competitor[i]
                    if not df_comp.empty and item["col"] in df_comp.columns:
                        val = df_comp[item["col"]].iloc[0]
                        color = colors[i % len(colors)]
                        st.markdown(f'<div style="text-align: center; color: {color};">{val}</div>', unsafe_allow_html=True)
        elif item["type"] == "chart":
            # Chart rendering logic...
            chart_name = item["name"]
            chart_data = []
            color_map = {}

            if chart_name == "chart1":
                for i, df_unit in enumerate(filtered_dfs_competitor):
                    if not df_unit.empty:
                        for j, (x_name, y_name) in enumerate(coord_col_pairs_1_5):
                            if x_name in df_unit and y_name in df_unit and pd.notna(df_unit[x_name].iloc[0]) and pd.notna(df_unit[y_name].iloc[0]):
                                chart_data.append({'X': df_unit[x_name].iloc[0], 'Y': df_unit[y_name].iloc[0], 'Label': f"Unit {i+1}", 'Order': j})
                if chart_data:
                    chart_df = pd.DataFrame(chart_data).sort_values(by=['Label', 'Order'])
                    fig = px.line(chart_df, x="X", y="Y", color="Label", title='Internal Cross Section area (Supply Filter)')
                    st.plotly_chart(fig, use_container_width=True)

            elif chart_name == "chart2":
                for i, df_unit in enumerate(filtered_dfs_competitor):
                    if not df_unit.empty:
                        for j, (x_name, y_name) in enumerate(coord_col_pairs_6_10):
                             if x_name in df_unit and y_name in df_unit and pd.notna(df_unit[x_name].iloc[0]) and pd.notna(df_unit[y_name].iloc[0]):
                                chart_data.append({'X': df_unit[x_name].iloc[0], 'Y': df_unit[y_name].iloc[0], 'Label': f"Unit {i+1}", 'Order': j})
                if chart_data:
                    chart_df = pd.DataFrame(chart_data).sort_values(by=['Label', 'Order'])
                    fig = px.line(chart_df, x="X", y="Y", color="Label", title='Internal Cross Section area (Supply Fan)')
                    st.plotly_chart(fig, use_container_width=True)
            
            elif chart_name == "chart3":
                fig = go.Figure()
                for i, df_unit in enumerate(filtered_dfs_competitor):
                    if not df_unit.empty:
                        is_circ = pd.notna(df_unit[duct_connection_diameter_col].iloc[0]) and df_unit[duct_connection_diameter_col].iloc[0] > 0
                        if is_circ:
                            diameter = df_unit[duct_connection_diameter_col].iloc[0]
                            radius = diameter / 2.0
                            # Adjusting coordinates for the circle shape
                            fig.add_shape(type="circle", x0=-radius, y0=-radius, x1=radius, y1=radius, line_color=colors[i % len(colors)], name=f"Unit {i+1}")
                        else: # Rectangular
                            x_vals, y_vals = [], []
                            for j, (x_name, y_name) in enumerate(coord_col_pairs_11_15):
                                if x_name in df_unit and y_name in df_unit and pd.notna(df_unit[x_name].iloc[0]) and pd.notna(df_unit[y_name].iloc[0]):
                                    x_vals.append(df_unit[x_name].iloc[0])
                                    y_vals.append(df_unit[y_name].iloc[0])
                            if x_vals and y_vals:
                                # FIX: Removed duplicate 'x=' -> go.Scatter(x=x_vals, ...)
                                fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name=f"Unit {i+1}", line=dict(color=colors[i % len(colors)])))
                fig.update_layout(title="Supply Duct Connection (mm)", xaxis_title="Width (mm)", yaxis_title="Height (mm)")
                fig.update_yaxes(scaleanchor="x", scaleratio=1)
                st.plotly_chart(fig, use_container_width=True)


            elif chart_name == "electrical_heater_chart":
                for i, df_unit in enumerate(filtered_dfs_competitor):
                    if not df_unit.empty and all(c in df_unit and pd.notna(df_unit[c].iloc[0]) for c in [capacity_range1_col, capacity_range2_col, capacity_range3_col]):
                        chart_data.append({"Capacity Range": "Range 1", "Value (kW)": df_unit[capacity_range1_col].iloc[0], "Selection": f"Unit {i+1}"})
                        chart_data.append({"Capacity Range": "Range 2", "Value (kW)": df_unit[capacity_range2_col].iloc[0], "Selection": f"Unit {i+1}"})
                        chart_data.append({"Capacity Range": "Range 3", "Value (kW)": df_unit[capacity_range3_col].iloc[0], "Selection": f"Unit {i+1}"})
                if chart_data:
                    chart_df = pd.DataFrame(chart_data)
                    fig = px.bar(chart_df, x="Capacity Range", y="Value (kW)", color="Selection", barmode="group", title='Electrical Heater Capacity (kW)')
                    st.plotly_chart(fig, use_container_width=True)
