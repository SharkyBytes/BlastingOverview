"""
Blasting Pattern Visualization - Main Application
"""

import streamlit as st
import numpy as np
import math
import json
import os
import datetime

# Import visualization functions
from visualizations.view_3d import create_cuboid_with_labeled_holes
from visualizations.view_2d import (
    create_2d_top_view,
    create_2d_side_view,
    create_2d_front_view,
    create_2d_cross_section,
    create_explosive_section_view
)

# Import model functions
from models.pattern_calculator import (
    calculate_square_pattern,
    calculate_staggered_pattern,
    calculate_manual_positions,
    calculate_burden_spacing
)

# Explosive density values (g/cm³)
EXPLOSIVE_DENSITIES = {
    "ANFO": 0.85,  # Average of 0.8-0.9
    "Heavy ANFO": 1.225,  # Average of 1.15-1.30
    "Slurry": 1.175,  # Average of 1.0-1.35
    "Emulsion": 1.3  # Average of 1.15-1.45
}

# Set page configuration
st.set_page_config(
    page_title="Blasting Pattern Visualization",
    page_icon="💥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for hole parameters if they don't exist
if 'hole_radii' not in st.session_state:
    st.session_state.hole_radii = [5.0] * 25  # Default radius for up to 25 holes
if 'hole_depths' not in st.session_state:
    st.session_state.hole_depths = [15.0] * 25  # Default depth for up to 25 holes
    
# Initialize session state for recent configurations
if 'recent_configs' not in st.session_state:
    st.session_state.recent_configs = []

# Function to save current configuration
def save_current_config():
    # Create a configuration dictionary with all parameters
    config = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "bench_height": bench_height,
        "hole_diameter": hole_diameter,
        "explosive_type": explosive_type,
        "explosive_selection_method": explosive_selection_method if 'explosive_selection_method' in locals() else "Manual selection",
        "water_condition": water_condition if 'water_condition' in locals() else "Dry",
        "rock_density": rock_density if 'rock_density' in locals() else 2.5,
        "p_wave_velocity": p_wave_velocity if 'p_wave_velocity' in locals() else 3.5,
        "cost_sensitivity": cost_sensitivity if 'cost_sensitivity' in locals() else "Medium",
        "pattern": pattern,
        "pattern_selection_method": pattern_selection_method if 'pattern_selection_method' in locals() else "Use recommended pattern",
        "rock_type": rock_type if 'rock_type' in locals() else "medium",
        "length": length,
        "width": width,
        "height": height,
        "calculated_burden": calculated_burden,
        "calculated_spacing": calculated_spacing,
        "default_stemming": calculated_stemming,
        "default_subdrilling": calculated_subdrilling,
        "hole_depth": calculated_hole_depth,
        "blast_volume": blast_volume,
        "blast_volume_option": blast_volume_option,
        "num_holes": num_holes,
        "charge_per_hole": charge_per_hole if 'charge_per_hole' in locals() else 0,
        "total_explosive": total_explosive if 'total_explosive' in locals() else 0,
        "powder_factor_vol_per_explosive": powder_factor_vol_per_explosive if 'powder_factor_vol_per_explosive' in locals() else 0,
        "powder_factor_explosive_per_vol": powder_factor_explosive_per_vol if 'powder_factor_explosive_per_vol' in locals() else 0
    }
    
    # Add to recent configurations
    if len(st.session_state.recent_configs) >= 5:  # Keep only the 5 most recent
        st.session_state.recent_configs.pop()
    
    # Add new config to the beginning of the list
    st.session_state.recent_configs.insert(0, config)
    
    # Return config name for display
    return f"Project {len(st.session_state.recent_configs)}"

# Function to load saved configuration
def load_config(config_index):
    if 0 <= config_index < len(st.session_state.recent_configs):
        return st.session_state.recent_configs[config_index]
    return None

# Page title and description
st.title("Blasting Pattern Visualization")
st.write("Configure your blasting pattern and generate interactive 3D and 2D visualizations.")

# Recent Configurations Section
if st.session_state.recent_configs:
    st.sidebar.header("⏰ Recent Configurations")
    
    for i, config in enumerate(st.session_state.recent_configs):
        if st.sidebar.button(f"Project {i+1} - {config['timestamp']}"):
            # Set session state to load this config
            st.session_state.load_config_index = i
            st.rerun()

# Check if we need to load a saved configuration
loaded_config = None
if 'load_config_index' in st.session_state:
    loaded_config = load_config(st.session_state.load_config_index)
    # Clear the load flag after loading
    del st.session_state.load_config_index

# Create a two-column layout
col1, col2 = st.columns([1, 2])

with col1:
    # Configuration section
    st.header("Configuration")
    
    # Select configuration mode - REMOVED
    config_mode = "Auto calculate from Burden & Spacing"  # Default to auto mode
    
    # Area Dimensions
    st.subheader("Area Dimensions")
    length = st.number_input("Length (m)", min_value=10.0, max_value=500.0, 
                           value=loaded_config["length"] if loaded_config else 20.0, 
                           step=10.0)
    width = st.number_input("Width (m)", min_value=10.0, max_value=500.0, 
                          value=loaded_config["width"] if loaded_config else 20.0, 
                          step=10.0)
    height = st.number_input("Height (m)", min_value=1.0, max_value=100.0, 
                           value=loaded_config["height"] if loaded_config else 20.0, 
                           step=1.0)
    
    # Parameters section
    st.subheader("Parameters")
    bench_height = st.number_input("Bench Height (m)", min_value=1.0, max_value=float(height), 
                                 value=min(loaded_config["bench_height"] if loaded_config else 10.0, height), 
                                 step=1.0)
    
    # Check if bench height exceeds total height and show warning
    if bench_height > height:
        st.warning("Bench height cannot be greater than the total height. Please adjust the input.")
        bench_height = height  # Adjust the bench height to the maximum allowed
    
    # Volume to be Blasted - Moved after bench_height is defined
    st.subheader("Volume to be Blasted")
    blast_volume_option = st.radio(
        "Blast Volume Selection",
        ["Full Blast", "Manual Selection"],
        index=0 if not loaded_config else (0 if loaded_config.get("blast_volume_option") == "Full Blast" else 1)
    )
    
    if blast_volume_option == "Full Blast":
        # Use bench_height for volume calculation
        blast_volume = length * width * bench_height
        st.write(f"Total Volume: {blast_volume:.2f} m³")
    else:
        blast_volume = st.number_input("Enter Volume (m³)", 
                                     min_value=10.0, 
                                     max_value=float(length * width * height), 
                                     value=loaded_config.get("blast_volume", float(length * width * bench_height / 2)) if loaded_config else float(length * width * bench_height / 2),
                                     step=10.0)
    
    # Calculate optimal hole diameter based on bench height
    calculated_diameter = bench_height / 120 * 1000  # Convert to mm
    calculated_diameter_rounded = max(80, min(350, round(calculated_diameter)))
    
    # Add Hole Diameter slider with calculated default
    hole_diameter = st.slider(
        "Hole Diameter (D) (mm)", 
        min_value=80, 
        max_value=350, 
        value=loaded_config["hole_diameter"] if loaded_config else calculated_diameter_rounded, 
        step=1
    )
    
    st.warning("⚠️ Changing the hole diameter is not recommended as the default value is optimally calculated based on the bench height.")
    
    # Calculate optimal parameters based on hole diameter
    calculated_burden = 0.024 * hole_diameter + 0.85  # Updated formula
    
    # Determine which pattern is most suitable based on calculated burden and desired burden-to-spacing ratio
    # Typical ratios: Square (1:1), Staggered (1:1.15-1.4), Rectangular (1:>1)
    # We'll recommend based on factors like rock properties
    
    # Let's calculate spacing for each pattern type
    square_spacing = calculated_burden  # 1:1 ratio
    staggered_spacing = 1.15 * calculated_burden  # 1:1.15 ratio
    rectangular_spacing = 0.9 * calculated_burden + 0.91  # typically >1:1 ratio
    
    # Determine recommended pattern based on rock hardness (or other factors if available)
    # Higher rock density or p-wave velocity generally requires staggered pattern for better fragmentation
    if 'rock_density' in locals() and 'p_wave_velocity' in locals():
        # Hard rock should use staggered pattern
        if rock_density > 2.7 or p_wave_velocity > 4.5:
            recommended_pattern = "staggered"
            recommended_pattern_name = "Staggered"
            recommended_spacing = staggered_spacing
        # Medium rock can use rectangular pattern
        elif rock_density > 2.5 or p_wave_velocity > 3.5:
            recommended_pattern = "square"  # We use "square" as backend value for rectangular too
            recommended_pattern_name = "Square or Rectangular"
            recommended_spacing = rectangular_spacing
        # Soft rock can use square pattern
        else:
            recommended_pattern = "square"
            recommended_pattern_name = "Square or Rectangular"
            recommended_spacing = square_spacing
    else:
        # Default recommendation if rock properties not available
        recommended_pattern = "square"  # Backend value
        recommended_pattern_name = "Square or Rectangular"
        recommended_spacing = rectangular_spacing
    
    # Set the default calculated spacing based on recommendation
    calculated_spacing = recommended_spacing
    calculated_subdrilling = 0.4 * calculated_burden
    calculated_stemming = 1.0 * calculated_burden
    calculated_hole_depth = bench_height + calculated_subdrilling
    
    # Display info box based on calculated diameter
    if 83 <= hole_diameter <= 200:
        st.info("Small-scale operations detected.")
    elif 200 < hole_diameter <= 350:
        st.info("Large-scale operation detected.")
    
    # Explosive Type Selection
    st.subheader("Explosive Type")
    explosive_selection_method = st.radio(
        "Selection Method",
        ["Best according to conditions", "Manual selection"],
        index=0 if not loaded_config else (0 if loaded_config.get("explosive_selection_method") == "Best according to conditions" else 1)
    )
    
    if explosive_selection_method == "Best according to conditions":
        # Collect relevant parameters from the decision matrix
        st.write("Please provide details about your blasting conditions:")
        
        # Water conditions
        water_condition = st.select_slider(
            "Water Conditions",
            options=["Dry", "Damp", "Wet", "Very Wet"],
            value=loaded_config.get("water_condition", "Dry") if loaded_config else "Dry"
        )
        
        # Rock characterization
        st.write("**Rock Characterization**")
        
        # Rock density input
        rock_density = st.number_input(
            "Rock Density (g/cm³)",
            min_value=1.5,
            max_value=3.5,
            value=loaded_config.get("rock_density", 2.5) if loaded_config else 2.5,
            step=0.1,
            format="%.2f"
        )
        
        # P-wave velocity input
        p_wave_velocity = st.number_input(
            "P-wave Velocity (km/s)",
            min_value=1.0,
            max_value=7.0,
            value=loaded_config.get("p_wave_velocity", 3.5) if loaded_config else 3.5,
            step=0.1,
            format="%.2f"
        )
        
        # Determine rock hardness based on inputs
        if p_wave_velocity < 2.5 and rock_density < 2.2:
            rock_hardness = "Very Soft"
            rock_ucs_range = "<25 MPa"
            rock_examples = "Highly weathered rocks, soft sandstone"
        elif p_wave_velocity < 3.5 and rock_density < 2.5:
            rock_hardness = "Soft"
            rock_ucs_range = "25-50 MPa"
            rock_examples = "Sandstone, shale, coal"
        elif p_wave_velocity < 4.5 and rock_density < 2.7:
            rock_hardness = "Medium"
            rock_ucs_range = "50-100 MPa"
            rock_examples = "Limestone, dolomite"
        elif p_wave_velocity < 5.5 and rock_density < 2.9:
            rock_hardness = "Hard"
            rock_ucs_range = "100-200 MPa"
            rock_examples = "Granite, gabbro, basalt"
        else:
            rock_hardness = "Very Hard"
            rock_ucs_range = ">200 MPa"
            rock_examples = "Quartzite, dense basalt"
            
        # Display rock classification
        st.info(f"""
        **Rock Classification:** {rock_hardness}
        
        **Typical UCS Range:** {rock_ucs_range}
        
        **Examples:** {rock_examples}
        """)
        
        # Display rock classification matrix
        with st.expander("Rock Classification Matrix", expanded=False):
            st.table({
                "P-wave Velocity (km/s)": ["<2.5", "2.5-3.5", "3.5-4.5", "4.5-5.5", ">5.5"],
                "Rock Density (g/cm³)": ["<2.2", "2.2-2.5", "2.5-2.7", "2.7-2.9", ">2.9"],
                "Rock Strength": ["Very weak to weak", "Weak to medium strong", "Medium strong to strong", "Strong to very strong", "Very strong to extremely strong"],
                "Typical UCS Range (MPa)": ["<25", "25-50", "50-100", "100-200", ">200"],
                "Rock Type Examples": ["Highly weathered rocks, soft sandstone", "Sandstone, shale, coal", "Limestone, dolomite", "Granite, gabbro, basalt", "Quartzite, dense basalt"]
            })
        
        # Cost sensitivity
        cost_sensitivity = st.select_slider(
            "Cost Sensitivity",
            options=["Low (Performance Priority)", "Medium", "High (Cost Priority)"],
            value=loaded_config.get("cost_sensitivity", "Medium") if loaded_config else "Medium"
        )
        
        # Auto-select the best explosive type based on conditions
        if water_condition == "Dry":
            if rock_hardness in ["Very Soft", "Soft", "Medium"]:
                recommended_explosive = "ANFO"
            else:  # Hard or Very Hard
                if cost_sensitivity == "High (Cost Priority)":
                    recommended_explosive = "ANFO"
                else:
                    recommended_explosive = "Heavy ANFO"
        elif water_condition == "Damp":
            if cost_sensitivity == "High (Cost Priority)":
                recommended_explosive = "Heavy ANFO"
            else:
                recommended_explosive = "Heavy ANFO"
        elif water_condition == "Wet":
            if cost_sensitivity == "High (Cost Priority)":
                recommended_explosive = "Heavy ANFO"
            else:
                recommended_explosive = "Slurry"
        else:  # Very Wet
            if rock_hardness in ["Hard", "Very Hard"]:
                recommended_explosive = "Emulsion"
            elif cost_sensitivity == "High (Cost Priority)":
                recommended_explosive = "Slurry"
            else:
                recommended_explosive = "Emulsion"
        
        st.success(f"**Recommended Explosive Type: {recommended_explosive}**")
        explosive_type = recommended_explosive
        
        # Display decision matrix
        with st.expander("Explosive Selection Decision Matrix", expanded=False):
            st.table({
                "Explosive Type": ["ANFO", "Heavy ANFO", "Slurry", "Emulsion"],
                "Water Resistance": ["None", "Low to Moderate", "Good", "Excellent"],
                "Density (g/cm³)": ["0.8-0.9", "1.15-1.30", "1.0-1.35", "1.15-1.45"],
                "VOD (m/s)": ["2500-3500", "5000-5335", "4000-5800", "4400-5600"],
                "Relative Cost": ["Low", "Medium", "Medium-High", "High"],
                "Best For": ["Dry holes, soft rock", "Damp to wet, medium rock", "Wet holes, varied rock", "Very wet holes, hard rock"]
            })
    else:
        # Manual selection
        explosive_type = st.selectbox(
            "Select Explosive Type",
            ["ANFO", "Heavy ANFO", "Slurry", "Emulsion"],
            index=["ANFO", "Heavy ANFO", "Slurry", "Emulsion"].index(loaded_config["explosive_type"]) if loaded_config else 0
        )
    
    # Display info based on selected explosive type
    if explosive_type == "ANFO":
        st.info("""
        📘 **Notes on ANFO:**
        - Density: 0.8–0.9 g/cm³
        - Detonation velocity (VOD): 2500–3500 m/s
        - Water resistance: None
        - Suitable for: Dry holes, Low–medium strength rock
        - Cost factor: Low
        - Notes: Simple to mix, not suitable for wet conditions
        """)
    elif explosive_type == "Heavy ANFO":
        st.info("""
        📘 **Notes on Heavy ANFO (60:40 Emulsion:ANFO):**
        - Density: 1.15–1.30 g/cm³
        - Detonation velocity (VOD): 5000–5335 m/s
        - Water resistance: Low to Moderate
        - Suitable for: Damp to wet holes, Medium-hard rock
        - Cost factor: Medium
        - Notes: Good balance of cost and performance
        """)
    elif explosive_type == "Slurry":
        st.info("""
        📘 **Notes on Slurry Explosives:**
        - Density: 1.0–1.35 g/cm³
        - Detonation velocity (VOD): 4000–5800 m/s
        - Water resistance: Good
        - Suitable for: Wet holes, varied rock types
        - Cost factor: Medium–High
        - Notes: Higher bulk strength than ANFO, excellent for wet conditions
        """)
    elif explosive_type == "Emulsion":
        st.info("""
        📘 **Notes on Emulsion Explosives:**
        - Density: 1.15–1.45 g/cm³
        - Detonation velocity (VOD): 4400–5600 m/s
        - Water resistance: Excellent
        - Suitable for: Very wet holes, hard rock
        - Cost factor: High
        - Notes: Best performance in challenging conditions, most water resistant
        """)
    
    # Blasting Pattern Type
    st.subheader("Blasting Pattern Type")
    
    # Pattern selection method - set index based on loaded config if available
    pattern_selection_index = 0
    if loaded_config and 'pattern_selection_method' in loaded_config:
        if loaded_config['pattern_selection_method'] == "Manual selection":
            pattern_selection_index = 1
    
    pattern_selection_method = st.radio(
        "Selection Method",
        ["Use recommended pattern", "Manual selection"],
        index=pattern_selection_index
    )
    
    if pattern_selection_method == "Use recommended pattern":
        # Use recommended pattern calculated based on rock properties
        pattern = recommended_pattern  # Backend value (square or staggered)
        st.success(f"Using {recommended_pattern_name} pattern (recommended)")
    else:
        # Manual pattern selection
        pattern_index = 0
        if loaded_config:
            pattern_value = loaded_config.get("pattern")
            if pattern_value == "staggered":
                pattern_index = 1
        
        pattern_choice = st.radio(
            "Select Pattern", 
            ["Square or Rectangular", "Staggered"], 
            index=pattern_index
        )
        pattern = "square" if pattern_choice == "Square or Rectangular" else "staggered"  # Convert to lowercase for compatibility
    
    # Display Pattern Decision Matrix expander
    with st.expander("Pattern Selection Decision Matrix", expanded=False):
        # Calculate burden to spacing ratios for display
        square_ratio = 1.0
        staggered_ratio = round(staggered_spacing / calculated_burden, 2)
        rectangular_ratio = round(rectangular_spacing / calculated_burden, 2)
        
        st.info(f"""
        **Burden-Spacing Relationship**
        
        | Pattern Type | Burden-Spacing Ratio |
        |--------------|----------------------|
        | Square | 1:1 |
        | Staggered | 1:{staggered_ratio} |
        | Rectangular | 1:{rectangular_ratio} |
        
        The best suitable pattern based on the provided inputs is the {recommended_pattern_name} pattern.
        """)
    
    # Update spacing calculation based on selected pattern
    if pattern == "square":
        # Square pattern: S = B
        calculated_spacing = calculated_burden
    elif pattern == "staggered":
        # Staggered pattern: S = 1.15B
        calculated_spacing = 1.15 * calculated_burden
    # The default is Rectangular: S = 0.9B + 0.91 m (already calculated above)
    
    # Different inputs based on configuration mode
    if config_mode == "Auto calculate from Burden & Spacing":
        # Calculate number of rows and holes per row
        if pattern == "square":
            num_rows = max(1, int(width / calculated_burden))
            num_holes_per_row = max(1, int(length / calculated_spacing))
            geometric_holes = num_rows * num_holes_per_row
        else:  # staggered pattern
            num_rows = max(1, int(width / calculated_burden))
            num_holes_odd_row = max(1, int((length - calculated_spacing/2) / calculated_spacing) + 1)
            num_holes_even_row = max(1, int((length - calculated_spacing) / calculated_spacing) + 1)
            
            # Calculate total holes based on odd and even rows
            odd_row_count = math.ceil(num_rows / 2)  # number of odd rows (1st, 3rd, 5th...)
            even_row_count = num_rows - odd_row_count  # number of even rows (2nd, 4th, 6th...)
            
            geometric_holes = (odd_row_count * num_holes_odd_row) + (even_row_count * num_holes_even_row)
            num_holes_per_row = max(num_holes_odd_row, num_holes_even_row)
        
        # Calculate volume per hole for theoretical calculation
        volume_per_hole = calculated_burden * calculated_spacing * bench_height
        
        # Calculate number of holes based on blast volume
        if blast_volume_option == "Manual Selection":
            num_holes = max(1, round(blast_volume / volume_per_hole) if volume_per_hole > 0 else 1)
        else:
            # Use full geometric layout
            num_holes = geometric_holes
    else:
        # Manual configuration
        if pattern == "staggered":
            # For staggered pattern, place holes at grid intersections with offset on even rows
            hole_positions_x = []
            hole_positions_y = []
            
            # Create a grid of positions
            x_grid = np.linspace(0, length, int(length/calculated_spacing) + 1)
            y_grid = np.linspace(0, width, int(width/calculated_burden) + 1)
            
            # Place holes at grid intersections with offset on even rows
            for row_idx, y in enumerate(y_grid[:-1]):  # Skip last grid line
                if row_idx % 2 == 0:  # Odd rows (index 0 is first row)
                    # Holes at intersections (grid corners)
                    row_x_positions = x_grid[:-1]  # Skip the last grid line
                else:  # Even rows
                    # Offset for staggered pattern - position between odd row holes
                    row_x_positions = x_grid[:-1] + calculated_spacing/2
                
                for x in row_x_positions:
                    # Check if within boundary
                    if 0 <= x <= length:
                        hole_positions_x.append(x)
                        hole_positions_y.append(y)
                        
                        if len(hole_positions_x) >= num_holes:
                            break
                if len(hole_positions_x) >= num_holes:
                    break
        else:  # square pattern
            # For square pattern, place holes at grid intersections
            hole_positions_x = []
            hole_positions_y = []
            
            # Create a grid of positions
            x_grid = np.linspace(0, length, int(length/calculated_spacing) + 1)
            y_grid = np.linspace(0, width, int(width/calculated_burden) + 1)
            
            # Place holes at grid intersections
            for y in y_grid[:-1]:  # Skip last grid line
                for x in x_grid[:-1]:  # Skip last grid line
                    hole_positions_x.append(x)
                    hole_positions_y.append(y)
                    
                    if len(hole_positions_x) >= num_holes:
                        break
                if len(hole_positions_x) >= num_holes:
                    break
        
        # Limit to the requested number of holes
        hole_positions_x = hole_positions_x[:num_holes]
        hole_positions_y = hole_positions_y[:num_holes]
    
    # Hole parameters
    st.subheader("Hole Parameters")
    
    # Option to apply the same parameters to all holes
    apply_to_all = st.checkbox("Apply same parameters to all holes", value=True)
    
    # Only show hole configs if not applying the same to all
    if apply_to_all:
        cols = st.columns(2)
        
        # Display input for the first hole only
        cols[0].write("**All Holes**")
        # Use hole diameter / 2000 to convert from mm to m and get radius
        radius = cols[0].number_input(
            "Radius (m)",
            min_value=0.01,
            max_value=10.0,
            value=float(hole_diameter/2000),  # Convert hole diameter (mm) to radius (m)
            step=0.01,
            key=f"r_all",
            format="%.4f"
        )
        
        # Use calculated hole depth from bench height + subdrilling
        cols[1].write(f"**Hole Depth (L): {calculated_hole_depth:.2f} m**")
        
        # Update all holes - extend to 100 to handle larger numbers of holes
        st.session_state.hole_radii = [radius] * 100
        st.session_state.hole_depths = [calculated_hole_depth] * 100
    else:
        # Display inputs for each hole
        for i in range(0, min(num_holes, 12), 2):  # Show max 12 holes, 2 per row
            cols = st.columns(4)
            
            # First hole in the pair
            cols[0].write(f"**Hole #{i+1}**")
            radius = cols[0].number_input(
                "Radius (m)",
                min_value=0.01,
                max_value=10.0,
                value=float(hole_diameter/2000),  # Convert hole diameter (mm) to radius (m)
                step=0.01,
                key=f"r_{i}",
                format="%.4f",
                disabled=apply_to_all and i > 0
            )
            
            # Display fixed hole depth
            cols[1].write(f"**Hole Depth (L): {calculated_hole_depth:.2f} m**")
            
            # Update session state for first hole
            st.session_state.hole_radii[i] = radius
            st.session_state.hole_depths[i] = calculated_hole_depth
            
            # Second hole in the pair (if available)
            if i + 1 < num_holes:
                cols[2].write(f"**Hole #{i+2}**")
                radius2 = cols[2].number_input(
                    "Radius (m)",
                    min_value=0.01,
                    max_value=10.0,
                    value=float(hole_diameter/2000),  # Convert hole diameter (mm) to radius (m)
                    step=0.01,
                    key=f"r_{i+1}",
                    format="%.4f",
                    disabled=apply_to_all
                )
                
                # Display fixed hole depth for second hole
                cols[3].write(f"**Hole Depth (L): {calculated_hole_depth:.2f} m**")
                
                # Update session state for second hole
                st.session_state.hole_radii[i+1] = radius2
                st.session_state.hole_depths[i+1] = calculated_hole_depth
            
            # Add some spacing between rows
            st.write("")
    
    st.write("")  # Add some spacing

with col2:
    # Create tabs for displaying calculated parameters and their formulas
    calc_tab, formula_tab, explosive_tab = st.tabs(["Calculations", "Formulas", "Explosive Parameters"])
    
    with calc_tab:
        # Calculate burden-to-spacing ratio and volume per hole
        burden_spacing_ratio = calculated_burden / calculated_spacing if calculated_spacing != 0 else 0
        volume_per_hole = calculated_burden * calculated_spacing * bench_height
        number_of_holes_calc = blast_volume / volume_per_hole if volume_per_hole != 0 else 0
        
        # Display calculated parameters in blue info box
        st.info(f"""
        **Optimal Design Parameters for This Blasting Round:**
        
        - Burden (B): {calculated_burden:.2f} m
        - Spacing (S): {calculated_spacing:.2f} m
        - Burden-to-Spacing Ratio: {burden_spacing_ratio:.2f}
        - Subdrilling Depth (J): {calculated_subdrilling:.2f} m
        - Stemming Length (T): {calculated_stemming:.2f} m
        - Hole Depth (L): {calculated_hole_depth:.2f} m
        - Volume per Hole: {volume_per_hole:.2f} m³
        - Number of Holes: {num_holes}
        - Number of rows: {num_rows}
        - Holes per row: {num_holes_per_row}
        - Blast Volume: {blast_volume:.2f} m³
        """)
    
    with formula_tab:
        # Show formulas based on selected pattern
        pattern_name = "Square or Rectangular" if pattern == "square" else "Staggered"
        spacing_formula = "S = B" if pattern == "square" else "S = 1.15B" if pattern == "staggered" else "S = 0.9B + 0.91"
        
        st.info(f"""
        **Formulas Used for Parameter Calculation:**
        
        - Optimal Hole Diameter (D) = Bench Height ÷ 120 × 1000 (mm)
        - Burden (B) = 0.024 × Hole Diameter + 0.85 (m) (using the Bench Crater Method)
        - Spacing (S) = {spacing_formula} (for {pattern_name} pattern)
        - Burden-to-Spacing Ratio = Burden ÷ Spacing
        - Subdrilling Depth (J) = 0.4 × Burden (m)
        - Stemming Length (T) = 1.0 × Burden (m)
        - Hole Depth (L) = Bench Height + Subdrilling (m)
        - Volume per Hole = Burden × Spacing × Bench Height (m³)
        - Number of Holes = Total Volume to be Blasted ÷ Volume per Hole
        
        **Explosive Charge Calculations:**
        - Charge per Hole (q) = Density of Explosive × Available Hole Volume
          = Density × (π × (Hole Diameter²) ÷ 4) × (Bench Height + Subdrill - Stemming)
        - Total Explosive (Q_total) = q × Number of Holes
        - Powder Factor (Volume/Explosive) = Blast Volume ÷ Total Explosive Used (m³/kg)
        - Powder Factor (Explosive/Volume) = Total Explosive Used ÷ Blast Volume (kg/m³)
        
        *Typical ranges:*
        - Hole Depth: 12–17 m for large operations, 8–12 m for medium-scale
        - Burden to Spacing ratio: 1:1.15 to 1:1.3
        - Powder Factor: 0.3-0.5 kg/m³ for medium-hard rock, 0.6-0.8 kg/m³ for hard rock
        """)
        
    with explosive_tab:
        # Calculate explosive charge per hole
        # Convert hole diameter from mm to meters
        hole_diameter_m = hole_diameter / 1000
        
        # Get explosive density in kg/m³ (convert from g/cm³)
        explosive_density = EXPLOSIVE_DENSITIES[explosive_type] * 1000  # Convert to kg/m³
        
        # Calculate the explosive column length (bench height + subdrill - stemming)
        explosive_column_length = bench_height + calculated_subdrilling - calculated_stemming
        
        # Calculate available hole volume in m³
        available_hole_volume = math.pi * (hole_diameter_m**2) / 4 * explosive_column_length
        
        # Calculate charge per hole in kg
        charge_per_hole = explosive_density * available_hole_volume
        
        # Calculate total explosive used
        total_explosive = charge_per_hole * num_holes
        
        # Calculate powder factor in both representations
        powder_factor_vol_per_explosive = blast_volume / total_explosive if total_explosive > 0 else 0  # m³/kg
        powder_factor_explosive_per_vol = total_explosive / blast_volume if blast_volume > 0 else 0  # kg/m³
        
        # Display explosive parameters in blue info box
        st.info(f"""
        **Explosive Parameters:**
        
        - Explosive Type: {explosive_type}
        - Explosive Density: {explosive_density:.2f} kg/m³
        - Explosive Column Length: {explosive_column_length:.2f} m
        - Available Hole Volume: {available_hole_volume:.4f} m³
        - Charge per Hole (q): {charge_per_hole:.2f} kg
        - Total Explosive Used (Q_total): {total_explosive:.2f} kg
        - Powder Factor (Volume/Explosive): {powder_factor_vol_per_explosive:.2f} m³/kg
        - Powder Factor (Explosive/Volume): {powder_factor_explosive_per_vol:.2f} kg/m³
        """)
    
    # Create tabs for 3D and 2D views
    view_3d_tab, view_2d_tab = st.tabs(["3D Visualization", "2D Views"])
    
    with view_3d_tab:
        # Add a generate button specifically for 3D visualization
        generate_3d_button = st.button("Visualize 3D", type="primary", use_container_width=True)
        
        # Display the 3D visualization if button is clicked
        if 'fig' in st.session_state and 'show_3d' in st.session_state and st.session_state.show_3d:
            if 'exceed_3d_limit' in st.session_state and st.session_state.exceed_3d_limit:
                st.warning("3D visualization currently supports up to 50 holes only. This limitation exists due to rendering constraints. Future versions will include advanced 3D rendering support using Blender.")
            st.plotly_chart(st.session_state.fig, use_container_width=True)
        else:
            st.info("Click 'Visualize 3D' to generate the 3D visualization.")
    
    with view_2d_tab:
        # Add a generate button specifically for 2D visualization
        generate_2d_button = st.button("Visualize 2D", type="primary", use_container_width=True)
        
        # Create sub-tabs for different 2D views
        top_view_tab, side_view_tab, front_view_tab, cross_section_tab = st.tabs(["Top View", "Side View", "Front View", "Cross-Section View"])
        
        # Display 2D views if the button is clicked
        if 'fig_2d_top' in st.session_state and 'show_2d' in st.session_state and st.session_state.show_2d:
            with top_view_tab:
                st.plotly_chart(st.session_state.fig_2d_top, use_container_width=True)
            
            with side_view_tab:
                st.plotly_chart(st.session_state.fig_2d_side, use_container_width=True)
            
            with front_view_tab:
                st.plotly_chart(st.session_state.fig_2d_front, use_container_width=True)
            
            with cross_section_tab:
                st.plotly_chart(st.session_state.fig_2d_cross, use_container_width=True)
                
            # Add Explosive Section View below the tabs - always visible when 2D views are shown
            st.subheader("Explosive Section View")
            st.plotly_chart(st.session_state.fig_2d_section, use_container_width=True)
        else:
            with top_view_tab:
                st.info("Click 'Visualize 2D' to generate the top view.")
            
            with side_view_tab:
                st.info("Click 'Visualize 2D' to generate the side view.")
            
            with front_view_tab:
                st.info("Click 'Visualize 2D' to generate the front view.")
            
            with cross_section_tab:
                st.info("Click 'Visualize 2D' to generate the cross-section view.")

# Handle the 3D visualization generation
if generate_3d_button:
    # Save the current configuration
    project_name = save_current_config()
    
    # Create explosive lengths array based on stemming length
    explosive_lengths = [calculated_hole_depth - calculated_stemming] * num_holes
    
    # Set a flag to track if we exceed the 3D visualization limit
    st.session_state.exceed_3d_limit = num_holes > 50
    
    # Limit the number of holes for 3D visualization to prevent rendering issues
    num_holes_3d = min(num_holes, 50)
    
    # Generate the 3D visualization
    if config_mode == "Auto calculate from Burden & Spacing":
        try:
            # Calculate hole positions based on burden and spacing
            if pattern == "square":
                # For square pattern, place holes at grid intersections
                hole_positions_x = []
                hole_positions_y = []
                
                # Create a grid of positions
                x_grid = np.linspace(0, length, int(length/calculated_spacing) + 1)
                y_grid = np.linspace(0, width, int(width/calculated_burden) + 1)
                
                # Place holes at grid intersections
                for y in y_grid[:-1]:  # Skip last grid line
                    for x in x_grid[:-1]:  # Skip last grid line
                        hole_positions_x.append(x)
                        hole_positions_y.append(y)
                        
                        if len(hole_positions_x) >= num_holes:
                            break
                    if len(hole_positions_x) >= num_holes:
                        break
                
                num_rows = len(y_grid) - 1
                holes_per_row = len(x_grid) - 1
            else:  # staggered pattern
                # For staggered pattern, place holes at grid intersections with offset on even rows
                hole_positions_x = []
                hole_positions_y = []
                
                # Create a grid of positions
                x_grid = np.linspace(0, length, int(length/calculated_spacing) + 1)
                y_grid = np.linspace(0, width, int(width/calculated_burden) + 1)
                
                # Place holes at grid intersections with offset on even rows
                for row_idx, y in enumerate(y_grid[:-1]):  # Skip last grid line
                    if row_idx % 2 == 0:  # Odd rows (index 0 is first row)
                        # Holes at intersections (grid corners)
                        row_x_positions = x_grid[:-1]  # Skip the last grid line
                    else:  # Even rows
                        # Offset for staggered pattern - position between odd row holes
                        row_x_positions = x_grid[:-1] + calculated_spacing/2
                    
                    for x in row_x_positions:
                        # Check if within boundary
                        if 0 <= x <= length:
                            hole_positions_x.append(x)
                            hole_positions_y.append(y)
                            
                            if len(hole_positions_x) >= num_holes:
                                break
                    if len(hole_positions_x) >= num_holes:
                        break
                
                # Calculate proper number of rows and holes per row
                num_rows = len(y_grid) - 1
                num_holes_odd_row = len(x_grid) - 1
                num_holes_even_row = len(x_grid) - 1
                
                num_holes_per_row = max(num_holes_odd_row, num_holes_even_row)
            
            # Limit to the calculated number of holes
            hole_positions_x = hole_positions_x[:num_holes]
            hole_positions_y = hole_positions_y[:num_holes]
            
            # Apply volume-based modification if manual selection
            if blast_volume_option == "Manual Selection":
                # We've already calculated num_holes based on volume, just trim the arrays
                hole_positions_x = hole_positions_x[:num_holes]
                hole_positions_y = hole_positions_y[:num_holes]
                num_holes_3d = min(num_holes, 50)  # Keep 3D visualization limit
            
            # For auto mode, pass burden and spacing
            fig = create_cuboid_with_labeled_holes(
                length=length,
                width=width,
                height=height,
                num_holes=num_holes_3d,
                hole_radii=st.session_state.hole_radii[:num_holes_3d],
                hole_depths=st.session_state.hole_depths[:num_holes_3d],
                explosive_lengths=explosive_lengths[:num_holes_3d],
                hole_positions=(hole_positions_x[:num_holes_3d], hole_positions_y[:num_holes_3d]),
                burden=calculated_burden,
                spacing=calculated_spacing,
                pattern=pattern,
                show_labels=False,
                original_num_holes=num_holes
            )
        except Exception as e:
            st.error(f"Error calculating hole positions: {e}")
            fig = None
    else:
        # Calculate hole positions for manual mode based on pattern
        if pattern == "staggered":
            holes_per_row = int(np.ceil(np.sqrt(num_holes * 2)))
            hole_positions_x, hole_positions_y = calculate_manual_positions(
                length=length,
                width=width,
                num_holes_per_row=holes_per_row,
                num_rows=int(np.ceil(num_holes / (holes_per_row / 2))),
                pattern="staggered"
            )
        else:  # square pattern
            holes_per_row = int(np.ceil(np.sqrt(num_holes)))
            hole_positions_x, hole_positions_y = calculate_manual_positions(
                length=length,
                width=width,
                num_holes_per_row=holes_per_row,
                num_rows=int(np.ceil(num_holes / holes_per_row)),
                pattern="square"
            )
        
        # Limit to the requested number of holes
        hole_positions_x = hole_positions_x[:num_holes]
        hole_positions_y = hole_positions_y[:num_holes]
        
        # For manual mode, don't pass burden and spacing
        fig = create_cuboid_with_labeled_holes(
            length=length,
            width=width,
            height=height,
            num_holes=num_holes_3d,
            hole_radii=st.session_state.hole_radii[:num_holes_3d],
            hole_depths=st.session_state.hole_depths[:num_holes_3d],
            explosive_lengths=explosive_lengths[:num_holes_3d],
            hole_positions=(hole_positions_x[:num_holes_3d], hole_positions_y[:num_holes_3d]),
            pattern=pattern,
            show_labels=False,
            original_num_holes=num_holes
        )
    
    # Store the figure in session state
    st.session_state.fig = fig
    st.session_state.show_3d = True
    
    # Show success message for saved configuration
    st.sidebar.success(f"✅ Configuration saved as {project_name}")
    
    # Rerun to display the figure
    st.rerun()

# Handle the 2D visualization generation
if generate_2d_button:
    # Save the current configuration
    project_name = save_current_config()
    
    # Create explosive lengths array based on stemming length
    explosive_lengths = [calculated_hole_depth - calculated_stemming] * num_holes
    
    # Set a flag to track if we exceed the 3D visualization limit
    st.session_state.exceed_3d_limit = num_holes > 50
    
    # Generate the 2D visualizations
    if config_mode == "Auto calculate from Burden & Spacing":
        try:
            # Calculate hole positions based on burden and spacing
            if pattern == "square":
                # For square pattern, place holes at grid intersections
                hole_positions_x = []
                hole_positions_y = []
                
                # Create a grid of positions
                x_grid = np.linspace(0, length, int(length/calculated_spacing) + 1)
                y_grid = np.linspace(0, width, int(width/calculated_burden) + 1)
                
                # Place holes at grid intersections
                for y in y_grid[:-1]:  # Skip last grid line
                    for x in x_grid[:-1]:  # Skip last grid line
                        hole_positions_x.append(x)
                        hole_positions_y.append(y)
                        
                        if len(hole_positions_x) >= num_holes:
                            break
                    if len(hole_positions_x) >= num_holes:
                        break
                
                num_rows = len(y_grid) - 1
                holes_per_row = len(x_grid) - 1
            else:  # staggered pattern
                # For staggered pattern, place holes at grid intersections with offset on even rows
                hole_positions_x = []
                hole_positions_y = []
                
                # Create a grid of positions
                x_grid = np.linspace(0, length, int(length/calculated_spacing) + 1)
                y_grid = np.linspace(0, width, int(width/calculated_burden) + 1)
                
                # Place holes at grid intersections with offset on even rows
                for row_idx, y in enumerate(y_grid[:-1]):  # Skip last grid line
                    if row_idx % 2 == 0:  # Odd rows (index 0 is first row)
                        # Holes at intersections (grid corners)
                        row_x_positions = x_grid[:-1]  # Skip the last grid line
                    else:  # Even rows
                        # Offset for staggered pattern - position between odd row holes
                        row_x_positions = x_grid[:-1] + calculated_spacing/2
                    
                    for x in row_x_positions:
                        # Check if within boundary
                        if 0 <= x <= length:
                            hole_positions_x.append(x)
                            hole_positions_y.append(y)
                            
                            if len(hole_positions_x) >= num_holes:
                                break
                    if len(hole_positions_x) >= num_holes:
                        break
                
                # Calculate proper number of rows and holes per row
                num_rows = len(y_grid) - 1
                num_holes_odd_row = len(x_grid) - 1
                num_holes_even_row = len(x_grid) - 1
                
                num_holes_per_row = max(num_holes_odd_row, num_holes_even_row)
            
            # Limit to the calculated number of holes
            hole_positions_x = hole_positions_x[:num_holes]
            hole_positions_y = hole_positions_y[:num_holes]
            
            # Apply volume-based modification if manual selection
            if blast_volume_option == "Manual Selection":
                # We've already calculated num_holes based on volume, just trim the arrays
                hole_positions_x = hole_positions_x[:num_holes]
                hole_positions_y = hole_positions_y[:num_holes]
        except Exception as e:
            st.error(f"Error calculating hole positions: {e}")
            st.rerun()
    else:
        # Calculate hole positions for manual mode based on pattern
        if pattern == "staggered":
            holes_per_row = int(np.ceil(np.sqrt(num_holes * 2)))
            hole_positions_x, hole_positions_y = calculate_manual_positions(
                length=length,
                width=width,
                num_holes_per_row=holes_per_row,
                num_rows=int(np.ceil(num_holes / (holes_per_row / 2))),
                pattern="staggered"
            )
        else:  # square pattern
            holes_per_row = int(np.ceil(np.sqrt(num_holes)))
            hole_positions_x, hole_positions_y = calculate_manual_positions(
                length=length,
                width=width,
                num_holes_per_row=holes_per_row,
                num_rows=int(np.ceil(num_holes / holes_per_row)),
                pattern="square"
            )
        
        # Limit to the requested number of holes
        hole_positions_x = hole_positions_x[:num_holes]
        hole_positions_y = hole_positions_y[:num_holes]
    
    # Create 2D top view - ensure we show all holes
    hole_positions_x_full = hole_positions_x[:num_holes] 
    hole_positions_y_full = hole_positions_y[:num_holes]
    
    fig_2d_top = create_2d_top_view(
        length=length,
        width=width,
        num_holes=num_holes,
        hole_radii=st.session_state.hole_radii[:num_holes],
        hole_positions=(hole_positions_x_full, hole_positions_y_full),
        burden=calculated_burden if config_mode == "Auto calculate from Burden & Spacing" else None,
        spacing=calculated_spacing if config_mode == "Auto calculate from Burden & Spacing" else None,
        pattern=pattern,
        show_labels=True
    )
    
    # Ensure arrays are of proper length for all 2D views
    hole_depths_safe = st.session_state.hole_depths.copy()
    while len(hole_depths_safe) < num_holes:
        hole_depths_safe.append(st.session_state.hole_depths[0])  # Add default depth
        
    hole_radii_safe = st.session_state.hole_radii.copy()
    while len(hole_radii_safe) < num_holes:
        hole_radii_safe.append(st.session_state.hole_radii[0])  # Add default radius
        
    explosive_lengths_safe = explosive_lengths[:num_holes]
    
    # Create 2D side view with full set of holes
    fig_2d_side = create_2d_side_view(
        length=length,
        height=height,
        num_holes=num_holes,
        hole_radii=hole_radii_safe,
        hole_depths=hole_depths_safe,
        hole_positions=(hole_positions_x_full, hole_positions_y_full),
        explosive_lengths=explosive_lengths_safe,
        burden=calculated_burden if config_mode == "Auto calculate from Burden & Spacing" else None,
        spacing=calculated_spacing if config_mode == "Auto calculate from Burden & Spacing" else None,
        pattern=pattern
    )
    
    # Create 2D front view with full set of holes
    fig_2d_front = create_2d_front_view(
        width=width,
        height=height,
        num_holes=num_holes,
        hole_radii=hole_radii_safe,
        hole_depths=hole_depths_safe,
        hole_positions=(hole_positions_x_full, hole_positions_y_full),
        explosive_lengths=explosive_lengths_safe,
        burden=calculated_burden if config_mode == "Auto calculate from Burden & Spacing" else None,
        spacing=calculated_spacing if config_mode == "Auto calculate from Burden & Spacing" else None,
        pattern=pattern
    )
    
    # Create 2D cross-section view with full set of holes
    fig_2d_cross = create_2d_cross_section(
        length=length,
        width=width,
        height=height,
        hole_positions_x=hole_positions_x_full,
        hole_positions_y=hole_positions_y_full,
        hole_depths=hole_depths_safe,
        explosive_lengths=explosive_lengths_safe,
        hole_radii=hole_radii_safe,
        burden=calculated_burden if config_mode == "Auto calculate from Burden & Spacing" else None,
        spacing=calculated_spacing if config_mode == "Auto calculate from Burden & Spacing" else None,
        pattern=pattern
    )
    
    # Create explosive section view
    fig_2d_section = create_explosive_section_view(
        hole_diameter=hole_diameter,
        stemming_length=calculated_stemming,
        explosive_length=explosive_column_length,
        hole_depth=calculated_hole_depth,
        spacing=calculated_spacing
    )
    
    # Store the figures in session state
    st.session_state.fig_2d_top = fig_2d_top
    st.session_state.fig_2d_side = fig_2d_side
    st.session_state.fig_2d_front = fig_2d_front
    st.session_state.fig_2d_cross = fig_2d_cross
    st.session_state.fig_2d_section = fig_2d_section
    st.session_state.show_2d = True
    
    # Show success message for saved configuration
    st.sidebar.success(f"✅ Configuration saved as {project_name}")
    
    # Rerun to display the figures
    st.rerun()

