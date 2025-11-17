"""
2D visualization components for the Blasting Overview application.
"""
import plotly.graph_objects as go
import numpy as np

def create_2d_top_view(length, width, num_holes, hole_radii, hole_positions, burden=None, spacing=None, pattern="staggered", show_labels=False):
    """
    Creates a 2D top view visualization of the blasting area.
    
    Args:
        length: Length of the blasting area
        width: Width of the blasting area
        num_holes: Number of holes to display
        hole_radii: List of hole radii
        hole_positions: Tuple of (hole_positions_x, hole_positions_y)
        burden: Burden distance (for auto mode) or None
        spacing: Spacing distance (for auto mode) or None
        pattern: "staggered" or "square"
        show_labels: Whether to show labels
        
    Returns:
        fig: Plotly figure with 2D top view
    """
    fig = go.Figure()
    
    # Extract x and y positions from hole_positions
    if isinstance(hole_positions, tuple) and len(hole_positions) == 2:
        hole_positions_x, hole_positions_y = hole_positions
    else:
        # Handle unexpected format
        return fig  # Return empty figure
    
    # Add a rectangle representing the blasting area
    fig.add_shape(
        type="rect",
        x0=0,
        y0=0,
        x1=length,
        y1=width,
        line=dict(color="white", width=2),
        fillcolor="lightgrey",
    )
    
    # Add burden and spacing lines if provided
    if burden is not None and spacing is not None:
        num_rows = max(1, int(width / burden))
        num_holes_per_row_odd = max(1, int((length - spacing/2) / spacing) + 1)
        num_holes_per_row_even = max(1, int((length - spacing) / spacing) + 1)
        
        # Create grid lines based on burden and spacing
        # For Square pattern: holes at intersections of grid lines
        # For Staggered pattern: odd rows at intersections, even rows offset
        
        # Create burden lines (horizontal) - start from 0 for grid
        y_positions = np.linspace(0, width, num_rows + 1)
        for y_pos in y_positions:
            fig.add_shape(
                type="line",
                x0=0,
                y0=y_pos,
                x1=length,
                y1=y_pos,
                line=dict(color="green", width=1, dash="dash"),
            )
        
        # Add spacing lines (vertical) - start from 0 for grid
        x_positions = np.linspace(0, length, int(length/spacing) + 1)
        for x_pos in x_positions:
            fig.add_shape(
                type="line",
                x0=x_pos,
                y0=0,
                x1=x_pos,
                y1=width,
                line=dict(color="green", width=1, dash="dash"),
            )
        
        # Position holes at intersections (corners) of squares for square pattern
        # For staggered, odd rows at intersections, even rows offset
        hole_positions_x = []
        hole_positions_y = []
        
        if pattern == "staggered":
            for row_idx, y_pos in enumerate(y_positions[:-1]):  # Skip the last grid line
                # Calculate x positions differently for odd and even rows
                if row_idx % 2 == 0:  # Odd rows (index 0 is first row)
                    # Holes at intersections (grid corners)
                    row_x_positions = x_positions[:-1]  # Skip the last grid line
                else:  # Even rows
                    # Offset for staggered pattern - position between odd row holes
                    row_x_positions = x_positions[:-1] + spacing/2
                
                # Add holes for this row
                for x_pos in row_x_positions:
                    # Check if within boundary
                    if 0 <= x_pos <= length and 0 <= y_pos <= width:
                        hole_positions_x.append(x_pos)
                        hole_positions_y.append(y_pos)
                        
                        # Limit to the specified number of holes
                        if len(hole_positions_x) >= num_holes:
                            break
                
                # Break outer loop if we've reached the max number of holes
                if len(hole_positions_x) >= num_holes:
                    break
        else:
            # Square pattern - holes at grid corners
            for y_pos in y_positions[:-1]:  # Skip the last grid line
                for x_pos in x_positions[:-1]:  # Skip the last grid line
                    hole_positions_x.append(x_pos)
                    hole_positions_y.append(y_pos)
                    
                    # Limit to the specified number of holes
                    if len(hole_positions_x) >= num_holes:
                        break
                
                # Break outer loop if we've reached the max number of holes
                if len(hole_positions_x) >= num_holes:
                    break
        
        # Add burden and spacing labels
        if len(y_positions) > 1:
            fig.add_annotation(
                x=length/2,
                y=(y_positions[0] + y_positions[1])/2,
                text=f"burden={burden:.2f}m",
                showarrow=False,
                font=dict(color="green", size=12),
            )
        
        if len(x_positions) > 1:
            fig.add_annotation(
                x=(x_positions[0] + x_positions[1])/2,
                y=width/2,
                text=f"spacing={spacing:.2f}m",
                showarrow=False,
                font=dict(color="green", size=12),
            )
    
    # Add circles for each hole
    for i in range(min(num_holes, len(hole_positions_x))):
        x_pos = hole_positions_x[i]
        y_pos = hole_positions_y[i]
        radius = hole_radii[i % len(hole_radii)]
        
        # Add circle for hole
        fig.add_shape(
            type="circle",
            x0=x_pos - radius,
            y0=y_pos - radius,
            x1=x_pos + radius,
            y1=y_pos + radius,
            line=dict(color="yellow", width=2),
            fillcolor="black",  # Fill with black to represent a hole
        )
        
        # Add hole number
        fig.add_annotation(
            x=x_pos,
            y=y_pos,
            text=f"{i+1}",
            showarrow=False,
            font=dict(color="white", size=10),
        )
    
    # Update layout
    pattern_text = "Staggered Pattern" if pattern == "staggered" else "Square Pattern"
    fig.update_layout(
        title=f"Top View - {pattern_text}",
        xaxis_title="Length (m)",
        yaxis_title="Width (m)",
        xaxis_range=[-5, length+5],
        yaxis_range=[-5, width+5],
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),
        autosize=False,
        width=600,
        height=400,
        margin=dict(l=50, r=50, b=50, t=50),
        showlegend=False,
    )
    
    # Make axes equal to prevent distortion
    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
    )

    return fig


def create_2d_side_view(length, height, num_holes, hole_radii, hole_depths, hole_positions, explosive_lengths=None, burden=None, spacing=None, pattern="staggered"):
    """
    Creates a 2D side view visualization of the blasting area.
    
    Args:
        length: Length of the blasting area
        height: Height of the blasting area
        num_holes: Number of holes to display
        hole_radii: List of hole radii
        hole_depths: List of hole depths
        hole_positions: Tuple of (hole_positions_x, hole_positions_y)
        explosive_lengths: List of explosive lengths (optional)
        burden: Burden distance (for auto mode) or None
        spacing: Spacing distance (for auto mode) or None
        pattern: "staggered" or "square"
        
    Returns:
        fig: Plotly figure with 2D side view
    """
    fig = go.Figure()
    
    # Extract x and y positions from hole_positions
    if isinstance(hole_positions, tuple) and len(hole_positions) == 2:
        hole_positions_x, hole_positions_y = hole_positions
    else:
        # Handle unexpected format
        return fig  # Return empty figure
    
    # Add a rectangle representing the blasting area (side view) - positioned below zero level
    fig.add_shape(
        type="rect",
        x0=0,
        y0=0,
        x1=length,
        y1=-height,  # Use negative height to place below zero
        line=dict(color="white", width=2),
        fillcolor="lightgrey",
    )
    
    # Get unique x-positions - these will be used for the side view
    unique_x_positions = sorted(set(hole_positions_x[:num_holes]))
    
    # Add vertical lines for holes
    for i, x_pos in enumerate(unique_x_positions):
        if i >= num_holes:
            break
            
        # Use the matching hole's radius and depth
        matching_indices = [j for j, pos in enumerate(hole_positions_x[:num_holes]) if pos == x_pos]
        if matching_indices:
            idx = matching_indices[0]  # Take the first matching hole
            radius = hole_radii[idx % len(hole_radii)]
            depth = hole_depths[idx % len(hole_depths)]
            
            # Draw hole shaft
            fig.add_shape(
                type="rect",
                x0=x_pos - radius,
                y0=0,
                x1=x_pos + radius,
                y1=-depth,  # Use negative depth to extend downward
                line=dict(color="black", width=1),
                fillcolor="black",
            )
            
            # Draw explosive if available
            if explosive_lengths and len(explosive_lengths) > idx:
                explosive_length = explosive_lengths[idx]
                
                # Draw explosive at the bottom part of the hole
                fig.add_shape(
                    type="rect",
                    x0=x_pos - radius * 0.8,
                    y0=-depth,  # Start from the bottom of the hole
                    x1=x_pos + radius * 0.8,
                    y1=-depth + explosive_length,  # Extend upward from bottom
                    line=dict(color="red", width=1),
                    fillcolor="red",
                )
                
                # Add label for stemming at the top part of the hole
                stemming_length = depth - explosive_length
                if stemming_length > 0:
                    fig.add_annotation(
                        x=x_pos,
                        y=-(depth - stemming_length/2),  # Centered in stemming area
                        text="Stemming",
                        showarrow=False,
                        font=dict(color="orange", size=10),
                    )
                
                # Add label for explosive
                if explosive_length > 0:
                    fig.add_annotation(
                        x=x_pos,
                        y=-(depth - explosive_length/2),  # Centered in explosive area
                        text="Explosive",
                        showarrow=False,
                        font=dict(color="white", size=10),
                    )
            
            # Add hole number
            fig.add_annotation(
                x=x_pos,
                y=0,
                text=f"{idx+1}",
                showarrow=False,
                font=dict(color="white", size=10),
                yshift=15,  # Shift slightly above ground level
            )
    
    # Update layout
    pattern_text = "Staggered Pattern" if pattern == "staggered" else "Square Pattern"
    fig.update_layout(
        title=f"Side View (Length) - {pattern_text}",
        xaxis_title="Length (m)",
        yaxis_title="Height (m)",
        xaxis_range=[-5, length+5],
        yaxis_range=[-height-5, 5],  # Adjust range to show negative values (below ground)
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),
        autosize=False,
        width=600,
        height=400,
        margin=dict(l=50, r=50, b=50, t=50),
        showlegend=False,
    )
    
    return fig


def create_2d_front_view(width, height, num_holes, hole_radii, hole_depths, hole_positions, explosive_lengths=None, burden=None, spacing=None, pattern="staggered"):
    """
    Creates a 2D front view visualization of the blasting area.
    
    Args:
        width: Width of the blasting area
        height: Height of the blasting area
        num_holes: Number of holes to display
        hole_radii: List of hole radii
        hole_depths: List of hole depths
        hole_positions: Tuple of (hole_positions_x, hole_positions_y)
        explosive_lengths: List of explosive lengths (optional)
        burden: Burden distance (for auto mode) or None
        spacing: Spacing distance (for auto mode) or None
        pattern: "staggered" or "square"
        
    Returns:
        fig: Plotly figure with 2D front view
    """
    fig = go.Figure()
    
    # Extract x and y positions from hole_positions
    if isinstance(hole_positions, tuple) and len(hole_positions) == 2:
        hole_positions_x, hole_positions_y = hole_positions
    else:
        # Handle unexpected format
        return fig  # Return empty figure
    
    # Add a rectangle representing the blasting area (front view) - positioned below zero level
    fig.add_shape(
        type="rect",
        x0=0,
        y0=0,
        x1=width,
        y1=-height,  # Use negative height to place below zero
        line=dict(color="white", width=2),
        fillcolor="lightgrey",
    )
    
    # Get unique y-positions - these will be used for the front view
    unique_y_positions = sorted(set(hole_positions_y[:num_holes]))
    
    # Add vertical lines for holes
    for i, y_pos in enumerate(unique_y_positions):
        if i >= num_holes:
            break
            
        # Use the matching hole's radius and depth
        matching_indices = [j for j, pos in enumerate(hole_positions_y[:num_holes]) if pos == y_pos]
        if matching_indices:
            idx = matching_indices[0]  # Take the first matching hole
            radius = hole_radii[idx % len(hole_radii)]
            depth = hole_depths[idx % len(hole_depths)]
            
            # Draw hole shaft
            fig.add_shape(
                type="rect",
                x0=y_pos - radius,
                y0=0,
                x1=y_pos + radius,
                y1=-depth,  # Use negative depth to extend downward
                line=dict(color="black", width=1),
                fillcolor="black",
            )
            
            # Draw explosive if available
            if explosive_lengths and len(explosive_lengths) > idx:
                explosive_length = explosive_lengths[idx]
                
                # Draw explosive at the bottom part of the hole
                fig.add_shape(
                    type="rect",
                    x0=y_pos - radius * 0.8,
                    y0=-depth,  # Start from the bottom of the hole
                    x1=y_pos + radius * 0.8,
                    y1=-depth + explosive_length,  # Extend upward from bottom
                    line=dict(color="red", width=1),
                    fillcolor="red",
                )
                
                # Add label for stemming at the top part of the hole
                stemming_length = depth - explosive_length
                if stemming_length > 0:
                    fig.add_annotation(
                        x=y_pos,
                        y=-(depth - stemming_length/2),  # Centered in stemming area
                        text="Stemming",
                        showarrow=False,
                        font=dict(color="orange", size=10),
                    )
                
                # Add label for explosive
                if explosive_length > 0:
                    fig.add_annotation(
                        x=y_pos,
                        y=-(depth - explosive_length/2),  # Centered in explosive area
                        text="Explosive",
                        showarrow=False,
                        font=dict(color="white", size=10),
                    )
            
            # Add hole number
            fig.add_annotation(
                x=y_pos,
                y=0,
                text=f"{idx+1}",
                showarrow=False,
                font=dict(color="white", size=10),
                yshift=15,  # Shift slightly above ground level
            )
    
    # Update layout
    pattern_text = "Staggered Pattern" if pattern == "staggered" else "Square Pattern"
    fig.update_layout(
        title=f"Front View (Width) - {pattern_text}",
        xaxis_title="Width (m)",
        yaxis_title="Height (m)",
        xaxis_range=[-5, width+5],
        yaxis_range=[-height-5, 5],  # Adjust range to show negative values (below ground)
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),
        autosize=False,
        width=600,
        height=400,
        margin=dict(l=50, r=50, b=50, t=50),
        showlegend=False,
    )
    
    return fig


def create_2d_cross_section(length, width, height, hole_positions_x, hole_positions_y, hole_depths, explosive_lengths, hole_radii,
                           pattern="staggered", burden=None, spacing=None, selected_cross_section=None):
    """
    Creates a 2D cross-section view of the blast pattern.
    
    Args:
        length: Length of the blasting area
        width: Width of the blasting area
        height: Height of the blasting area
        hole_positions_x: List of hole x positions
        hole_positions_y: List of hole y positions
        hole_depths: List of hole depths
        explosive_lengths: List of explosive lengths
        hole_radii: List of hole radii
        pattern: "staggered" or "square"
        burden: Burden distance (for auto mode) or None
        spacing: Spacing distance (for auto mode) or None
        selected_cross_section: Index of the selected cross section or None
        
    Returns:
        fig: Plotly figure with 2D cross-section view
    """
    # Default to the first row if no selection is made
    if selected_cross_section is None or selected_cross_section < 0:
        selected_cross_section = 0
    
    # Get unique y-coordinates (rows) and sort them
    unique_rows = sorted(list(set(hole_positions_y)))
    
    # Ensure the selected cross section is within bounds
    if selected_cross_section >= len(unique_rows):
        selected_cross_section = len(unique_rows) - 1
    
    # Get the y-coordinate for the selected row
    selected_y = unique_rows[selected_cross_section]
    
    # Filter holes to only those in the selected row
    selected_indices = [i for i, y in enumerate(hole_positions_y) if abs(y - selected_y) < 0.001]
    
    if not selected_indices:
        return go.Figure()
    
    # Get x-positions, depths, and explosive lengths for the selected row
    cross_section_x = [hole_positions_x[i] for i in selected_indices]
    cross_section_depths = []
    cross_section_explosives = []
    cross_section_radii = []
    
    # Safely get values for depths, explosives, and radii
    for i in selected_indices:
        # Make sure we don't go out of bounds
        if i < len(hole_depths):
            cross_section_depths.append(hole_depths[i])
        else:
            cross_section_depths.append(15.0)  # Default depth
            
        if i < len(explosive_lengths):
            cross_section_explosives.append(explosive_lengths[i])
        else:
            cross_section_explosives.append(10.0)  # Default explosive length
            
        if i < len(hole_radii):
            cross_section_radii.append(hole_radii[i])
        else:
            cross_section_radii.append(5.0)  # Default radius
    
    # Create a new figure
    fig = go.Figure()
    
    # Add ground level
    fig.add_shape(
        type="line",
        x0=0,
        y0=0,
        x1=length,
        y1=0,
        line=dict(color="brown", width=2),
    )
    
    # Determine row type for staggered pattern
    row_index = unique_rows.index(selected_y)
    row_type = "Odd Row" if row_index % 2 == 0 else "Even Row"
    
    # Add the holes
    for i, (x, depth, explosive, radius) in enumerate(zip(cross_section_x, cross_section_depths, cross_section_explosives, cross_section_radii)):
        # Draw hole outline
        fig.add_shape(
            type="rect",
            x0=x - radius,
            y0=0,
            x1=x + radius,
            y1=-depth,
            line=dict(color="black", width=1),
            fillcolor="lightgrey",
        )
        
        # Draw explosive charge
        fig.add_shape(
            type="rect",
            x0=x - radius * 0.9,
            y0=-depth + explosive,
            x1=x + radius * 0.9,
            y1=-depth,
            line=dict(color="red", width=1),
            fillcolor="orange",
        )
        
        # Add hole number
        fig.add_annotation(
            x=x,
            y=5,  # Just above ground level
            text=f"H{selected_indices[i]+1}",
            showarrow=False,
            font=dict(size=10, color="black"),
        )
        
        # Add depth annotation
        fig.add_annotation(
            x=x,
            y=-depth/2,
            text=f"{depth:.1f}m",
            showarrow=False,
            font=dict(size=8, color="black"),
        )
    
    # Add spacing annotations if pattern data is available
    if pattern and spacing:
        if pattern == "staggered" and row_index % 2 != 0:  # Even row in staggered pattern
            # Show adjusted spacing for even rows
            for i in range(len(cross_section_x) - 1):
                midpoint = (cross_section_x[i] + cross_section_x[i+1]) / 2
                fig.add_shape(
                    type="line",
                    x0=midpoint,
                    y0=10,
                    x1=midpoint,
                    y1=20,
                    line=dict(color="blue", width=1, dash="dash"),
                )
                fig.add_annotation(
                    x=midpoint,
                    y=25,
                    text=f"Spacing: {spacing:.1f}m",
                    showarrow=False,
                    font=dict(size=8, color="blue"),
                )
        else:  # Odd row or square pattern
            for i in range(len(cross_section_x) - 1):
                midpoint = (cross_section_x[i] + cross_section_x[i+1]) / 2
                fig.add_shape(
                    type="line",
                    x0=midpoint,
                    y0=10,
                    x1=midpoint,
                    y1=20,
                    line=dict(color="blue", width=1, dash="dash"),
                )
                fig.add_annotation(
                    x=midpoint,
                    y=25,
                    text=f"Spacing: {spacing:.1f}m",
                    showarrow=False,
                    font=dict(size=8, color="blue"),
                )
    
    # Add title to indicate which row is being viewed
    if pattern == "staggered":
        fig.update_layout(
            title=f"Cross Section View - {row_type} (Row {row_index+1} of {len(unique_rows)})",
            xaxis_title="Length (m)",
            yaxis_title="Depth (m)",
            showlegend=False,
        )
    else:
        fig.update_layout(
            title=f"Cross Section View - Row {row_index+1} of {len(unique_rows)}",
            xaxis_title="Length (m)",
            yaxis_title="Depth (m)",
            showlegend=False,
        )
    
    # Set axis ranges
    if cross_section_depths:
        y_min = -max([depth for depth in cross_section_depths]) * 1.1  # Add some margin
    else:
        y_min = -20  # Default value if no depths are available
    fig.update_yaxes(range=[y_min, 30], zeroline=False)  # Extend above ground for annotations
    fig.update_xaxes(range=[0, length])
    
    # Add a dropdown for selecting different rows
    buttons = []
    for i, row_y in enumerate(unique_rows):
        row_name = f"Row {i+1}" if pattern != "staggered" else f"{'Odd' if i % 2 == 0 else 'Even'} Row {i+1}"
        buttons.append(dict(
            label=row_name,
            method="relayout",
            args=[{"title": f"Cross Section View - {row_name} of {len(unique_rows)}"}]
        ))
    
    # Add row selector to the layout
    if len(unique_rows) > 1:
        fig.update_layout(
            updatemenus=[dict(
                type="dropdown",
                showactive=True,
                buttons=buttons,
                x=0.1,
                y=1.15,
                xanchor="left",
                yanchor="top"
            )]
        )
    
    return fig 

def create_explosive_section_view(hole_diameter, stemming_length, explosive_length, hole_depth, spacing=None):
    """
    Creates a detailed section view of a drill hole showing explosive, stemming, and dimensions.
    
    Args:
        hole_diameter: Diameter of the hole in mm
        stemming_length: Length of stemming in meters
        explosive_length: Length of explosive column in meters
        hole_depth: Total depth of the hole in meters
        spacing: Spacing between holes in meters (optional)
        
    Returns:
        fig: Plotly figure with explosive section view
    """
    fig = go.Figure()
    
    # Convert hole diameter from mm to meters for consistent units
    hole_diameter_m = hole_diameter / 1000
    
    # Define colors
    stemming_color = "gold"  # More yellow like in the reference image
    explosive_color = "red"
    ground_color = "brown"
    
    # Define the center line for the hole
    center_x = 0
    
    # Add ground level
    fig.add_shape(
        type="rect",
        x0=-2,
        y0=0,
        x1=2,
        y1=0.5,
        line=dict(color=ground_color, width=1),
        fillcolor=ground_color,
    )
    
    # Add hole
    fig.add_shape(
        type="rect",
        x0=center_x - hole_diameter_m/2,
        y0=0,
        x1=center_x + hole_diameter_m/2,
        y1=-hole_depth,
        line=dict(color="black", width=1),
        fillcolor="white",  # Changed to white for better visibility
    )
    
    # Add explosive column
    fig.add_shape(
        type="rect",
        x0=center_x - hole_diameter_m*0.4,
        y0=-hole_depth,
        x1=center_x + hole_diameter_m*0.4,
        y1=-stemming_length,  # Bottom of stemming
        line=dict(color="black", width=1),
        fillcolor=explosive_color,
    )
    
    # Add stemming
    fig.add_shape(
        type="rect",
        x0=center_x - hole_diameter_m*0.4,
        y0=-stemming_length,
        x1=center_x + hole_diameter_m*0.4,
        y1=0,
        line=dict(color="black", width=1),
        fillcolor=stemming_color,
    )
    
    # Add shock tube - curved line from top to center
    # First add a vertical line
    fig.add_shape(
        type="line",
        x0=center_x,
        y0=0,
        x1=center_x,
        y1=-stemming_length/2,
        line=dict(color="black", width=2),
    )
    
    # Then add a curve from above ground to the top of the hole
    x_curve = [center_x - hole_diameter_m, center_x - hole_diameter_m*0.8, center_x]
    y_curve = [0.4, 0.2, 0]
    
    fig.add_trace(go.Scatter(
        x=x_curve,
        y=y_curve,
        mode='lines',
        line=dict(color='black', width=2),
        showlegend=False
    ))
    
    # Add labels
    # Shock tube label
    fig.add_annotation(
        x=center_x - hole_diameter_m*1.5,
        y=0.4,
        text="Shock tube",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowcolor="black",
        ax=10,
        ay=0,
        font=dict(color="black", size=10),
    )
    
    # Blast hole label
    fig.add_annotation(
        x=center_x - hole_diameter_m*1.5,
        y=-(stemming_length + explosive_length/3),
        text=f"Blast hole<br>({hole_diameter}mm)",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowcolor="black",
        ax=10,
        ay=0,
        font=dict(color="black", size=10),
    )
    
    # Stemming column label
    fig.add_annotation(
        x=center_x + hole_diameter_m*1.5,
        y=-stemming_length/2,
        text=f"Stemming<br>column ({stemming_length:.2f}m)",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowcolor="black",
        ax=-10,
        ay=0,
        font=dict(color="black", size=10),
    )
    
    # Explosive column label
    fig.add_annotation(
        x=center_x + hole_diameter_m*1.5,
        y=-(stemming_length + explosive_length/2),
        text=f"Explosive column<br>({explosive_length:.2f}m)",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowcolor="black",
        ax=-10,
        ay=0,
        font=dict(color="black", size=10),
    )
    
    # Add spacing indication if provided
    if spacing is not None:
        # Add a second hole to illustrate spacing
        fig.add_shape(
            type="rect",
            x0=spacing - hole_diameter_m/2,
            y0=0,
            x1=spacing + hole_diameter_m/2,
            y1=-hole_depth/3,  # Partial depth for illustration
            line=dict(color="black", width=1),
            fillcolor="white",
        )
        
        # Add spacing dimension line
        fig.add_shape(
            type="line",
            x0=center_x,
            y0=0.3,
            x1=spacing,
            y1=0.3,
            line=dict(color="green", width=1, dash="solid"),
        )
        # Add vertical markers at ends of dimension line
        fig.add_shape(
            type="line",
            x0=center_x,
            y0=0.2,
            x1=center_x,
            y1=0.4,
            line=dict(color="green", width=1, dash="solid"),
        )
        fig.add_shape(
            type="line",
            x0=spacing,
            y0=0.2,
            x1=spacing,
            y1=0.4,
            line=dict(color="green", width=1, dash="solid"),
        )
        fig.add_annotation(
            x=(center_x + spacing)/2,
            y=0.3,
            text=f"Spacing: {spacing:.2f} m",
            showarrow=False,
            font=dict(color="green", size=10),
            yshift=15,
        )
    
    # Update layout
    fig.update_layout(
        title="Blast Hole Section View",
        xaxis_title="Width (m)",
        yaxis_title="Depth (m)",
        xaxis_range=[-3, spacing + 3 if spacing else 3],
        yaxis_range=[-hole_depth-1, 1],
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="black"),
        autosize=False,
        width=600,
        height=600,  # Increased height to match proportions in reference image
        margin=dict(l=50, r=50, b=50, t=50),
        showlegend=False,
    )
    
    # Make axes equal to prevent distortion
    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
    )
    
    return fig 