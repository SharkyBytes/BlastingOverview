"""
3D visualization components for the Blasting Overview application.
"""
import plotly.graph_objects as go
import numpy as np
from utils.helper_functions import create_cylinder_surface

def add_hole_visualization(fig, x_pos, y_pos, r, d, height, count, explosive_length):
    """
    Helper function to add a single hole visualization to the figure
    
    Args:
        fig: The plotly figure to add the hole to
        x_pos: X position of the hole
        y_pos: Y position of the hole
        r: Radius of the hole
        d: Depth of the hole
        height: Height of the blasting area
        count: Hole index/count (for labeling)
        explosive_length: Length of the explosive charge
        
    Returns:
        None (modifies fig in-place)
    """
    # Create hole cylinder (black sides)
    x_cyl, y_cyl, z_cyl = create_cylinder_surface(x_pos, y_pos, r, height, height - d)

    fig.add_trace(go.Surface(
        x=x_cyl, y=y_cyl, z=z_cyl,
        surfacecolor=np.ones_like(z_cyl) * 0,  # Solid black
        colorscale=[[0, 'black'], [1, 'black']],
        showscale=False,
        opacity=1,
        lighting=dict(ambient=0.4, diffuse=0.6, specular=0.1, roughness=0.2)
    ))

    theta = np.linspace(0, 2*np.pi, 36)
    radius_vals = np.linspace(0, r, 10)
    theta_grid, r_grid = np.meshgrid(theta, radius_vals)
    x_cap = x_pos + r_grid * np.cos(theta_grid)
    y_cap = y_pos + r_grid * np.sin(theta_grid)

    # Bottom cap (black)
    z_bottom_cap = (height - d) * np.ones_like(x_cap)
    fig.add_trace(go.Surface(
        x=x_cap, y=y_cap, z=z_bottom_cap,
        colorscale=[[0, 'black'], [1, 'black']],
        showscale=False,
        opacity=1,
        lighting=dict(ambient=0.4, diffuse=0.6, specular=0.1, roughness=0.2)
    ))

    # Add yellow circle outline at the top
    fig.add_trace(go.Scatter3d(
        x=x_pos + r * np.cos(theta),
        y=y_pos + r * np.sin(theta),
        z=np.ones_like(theta) * height,
        mode='lines',
        line=dict(color='yellow', width=6),
        showlegend=False
    ))

    angle_offset = (count % 4) * (np.pi/2)

    # Add radius line
    fig.add_trace(go.Scatter3d(
        x=[x_pos, x_pos + r * np.cos(angle_offset)],
        y=[y_pos, y_pos + r * np.sin(angle_offset)],
        z=[height, height],
        mode='lines',
        line=dict(color='white', width=2),
        showlegend=False
    ))

    # Radius label
    label_dist = 1.1
    fig.add_trace(go.Scatter3d(
        x=[x_pos + r * label_dist * np.cos(angle_offset)],
        y=[y_pos + r * label_dist * np.sin(angle_offset)],
        z=[height + 2],
        mode='text',
        text=f"r{count+1}={r}",
        textfont=dict(color='white', size=10),
        showlegend=False
    ))

    # Depth dimension line
    depth_angle = angle_offset + np.pi/4
    offset_x = r * 1.2 * np.cos(depth_angle)
    offset_y = r * 1.2 * np.sin(depth_angle)

    fig.add_trace(go.Scatter3d(
        x=[x_pos + offset_x, x_pos + offset_x],
        y=[y_pos + offset_y, y_pos + offset_y],
        z=[height, height - d],
        mode='lines',
        line=dict(color='white', width=2),
        showlegend=False
    ))

    # Add explosive length label
    fig.add_trace(go.Scatter3d(
        x=[x_pos + offset_x * 1.2],
        y=[y_pos + offset_y * 1.2],
        z=[height - d/2 - 4],  # Position below depth label
        mode='text',
        text=f"explosive{count+1}={explosive_length}",
        textfont=dict(color='red', size=10),
        showlegend=False
    ))

    # Add depth label
    fig.add_trace(go.Scatter3d(
        x=[x_pos + offset_x * 1.2],
        y=[y_pos + offset_y * 1.2],
        z=[height - d / 2],
        mode='text',
        text=f"depth{count+1}={d}",
        textfont=dict(color='white', size=10),
        showlegend=False
    ))

    # Add explosive visualization
    if explosive_length > 0:
        # Make sure explosive doesn't exceed hole depth
        exp_length = min(explosive_length, d)
        
        # Create explosive cylinder surface
        exp_x, exp_y, exp_z = create_cylinder_surface(
            x_pos, y_pos, r * 0.95,  # Slightly smaller radius to avoid z-fighting
            height - d + exp_length,  # Start from bottom, go up by explosive length
            height - d                # Bottom of hole
        )
        
        # Add the explosive surface (red cylinder)
        fig.add_trace(go.Surface(
            x=exp_x,
            y=exp_y,
            z=exp_z,
            colorscale=[[0, 'red'], [1, 'darkred']],  # Red gradient
            showscale=False,
            opacity=1.0,
            lighting=dict(ambient=0.8, diffuse=0.9, specular=0.2, roughness=0.1)
        ))
        
        # Add top cap for explosive (red circle)
        exp_top_z = (height - d + exp_length) * np.ones_like(x_cap)
        fig.add_trace(go.Surface(
            x=x_cap, 
            y=y_cap, 
            z=exp_top_z,
            colorscale=[[0, 'red'], [1, 'red']],
            showscale=False,
            opacity=1.0,
            lighting=dict(ambient=0.8, diffuse=0.9, specular=0.2, roughness=0.1)
        ))


def create_cuboid_with_labeled_holes(length, width, height, num_holes, hole_radii, hole_depths, 
                                   explosive_lengths, hole_positions=None, burden=None, spacing=None, 
                                   pattern="staggered", show_labels=False, original_num_holes=None):
    """
    Creates a 3D visualization of the blasting area with labeled holes.
    
    Args:
        length: Length of the blasting area
        width: Width of the blasting area
        height: Height of the blasting area
        num_holes: Number of holes to display
        hole_radii: List of hole radii
        hole_depths: List of hole depths
        explosive_lengths: List of explosive lengths
        hole_positions: Tuple of (x_positions, y_positions) or None
        burden: Burden distance or None
        spacing: Spacing distance or None
        pattern: "staggered" or "square"
        show_labels: Whether to show labels
        original_num_holes: Total number of holes (for display)
        
    Returns:
        fig: Plotly figure with the 3D visualization
    """
    fig = go.Figure()

    # We'll create the cuboid with separate faces to allow for hole cutouts
    # Define the vertices of the cuboid
    vertices = np.array([
        [0, 0, 0],  # 0: bottom-left-front
        [length, 0, 0],  # 1: bottom-right-front
        [length, width, 0],  # 2: bottom-right-back
        [0, width, 0],  # 3: bottom-left-back
        [0, 0, height],  # 4: top-left-front
        [length, 0, height],  # 5: top-right-front
        [length, width, height],  # 6: top-right-back
        [0, width, height]  # 7: top-left-back
    ])
    
    # Create the 5 visible faces (excluding the top face which will have holes)
    # Bottom face
    fig.add_trace(go.Mesh3d(
        x=[vertices[0, 0], vertices[1, 0], vertices[2, 0], vertices[3, 0]],
        y=[vertices[0, 1], vertices[1, 1], vertices[2, 1], vertices[3, 1]],
        z=[vertices[0, 2], vertices[1, 2], vertices[2, 2], vertices[3, 2]],
        i=[0], j=[1], k=[2],
        color='white',
        opacity=0.9,
        flatshading=True,
        showlegend=False
    ))
    
    fig.add_trace(go.Mesh3d(
        x=[vertices[0, 0], vertices[2, 0], vertices[3, 0]],
        y=[vertices[0, 1], vertices[2, 1], vertices[3, 1]],
        z=[vertices[0, 2], vertices[2, 2], vertices[3, 2]],
        i=[0], j=[1], k=[2],
        color='white',
        opacity=0.9,
        flatshading=True,
        showlegend=False
    ))
    
    # Front face
    fig.add_trace(go.Mesh3d(
        x=[vertices[0, 0], vertices[1, 0], vertices[5, 0], vertices[4, 0]],
        y=[vertices[0, 1], vertices[1, 1], vertices[5, 1], vertices[4, 1]],
        z=[vertices[0, 2], vertices[1, 2], vertices[5, 2], vertices[4, 2]],
        i=[0], j=[1], k=[2],
        color='white',
        opacity=0.9,
        flatshading=True,
        showlegend=False
    ))
    
    fig.add_trace(go.Mesh3d(
        x=[vertices[0, 0], vertices[4, 0], vertices[5, 0]],
        y=[vertices[0, 1], vertices[4, 1], vertices[5, 1]],
        z=[vertices[0, 2], vertices[4, 2], vertices[5, 2]],
        i=[0], j=[1], k=[2],
        color='white',
        opacity=0.9,
        flatshading=True,
        showlegend=False
    ))
    
    # Back face
    fig.add_trace(go.Mesh3d(
        x=[vertices[2, 0], vertices[3, 0], vertices[7, 0], vertices[6, 0]],
        y=[vertices[2, 1], vertices[3, 1], vertices[7, 1], vertices[6, 1]],
        z=[vertices[2, 2], vertices[3, 2], vertices[7, 2], vertices[6, 2]],
        i=[0], j=[1], k=[2],
        color='white',
        opacity=0.9,
        flatshading=True,
        showlegend=False
    ))
    
    fig.add_trace(go.Mesh3d(
        x=[vertices[2, 0], vertices[6, 0], vertices[7, 0]],
        y=[vertices[2, 1], vertices[6, 1], vertices[7, 1]],
        z=[vertices[2, 2], vertices[6, 2], vertices[7, 2]],
        i=[0], j=[1], k=[2],
        color='white',
        opacity=0.9,
        flatshading=True,
        showlegend=False
    ))
    
    # Left face
    fig.add_trace(go.Mesh3d(
        x=[vertices[0, 0], vertices[3, 0], vertices[7, 0], vertices[4, 0]],
        y=[vertices[0, 1], vertices[3, 1], vertices[7, 1], vertices[4, 1]],
        z=[vertices[0, 2], vertices[3, 2], vertices[7, 2], vertices[4, 2]],
        i=[0], j=[1], k=[2],
        color='white',
        opacity=0.9,
        flatshading=True,
        showlegend=False
    ))
    
    fig.add_trace(go.Mesh3d(
        x=[vertices[0, 0], vertices[4, 0], vertices[7, 0]],
        y=[vertices[0, 1], vertices[4, 1], vertices[7, 1]],
        z=[vertices[0, 2], vertices[4, 2], vertices[7, 2]],
        i=[0], j=[1], k=[2],
        color='white',
        opacity=0.9,
        flatshading=True,
        showlegend=False
    ))
    
    # Right face
    fig.add_trace(go.Mesh3d(
        x=[vertices[1, 0], vertices[2, 0], vertices[6, 0], vertices[5, 0]],
        y=[vertices[1, 1], vertices[2, 1], vertices[6, 1], vertices[5, 1]],
        z=[vertices[1, 2], vertices[2, 2], vertices[6, 2], vertices[5, 2]],
        i=[0], j=[1], k=[2],
        color='white',
        opacity=0.9,
        flatshading=True,
        showlegend=False
    ))
    
    fig.add_trace(go.Mesh3d(
        x=[vertices[1, 0], vertices[5, 0], vertices[6, 0]],
        y=[vertices[1, 1], vertices[5, 1], vertices[6, 1]],
        z=[vertices[1, 2], vertices[5, 2], vertices[6, 2]],
        i=[0], j=[1], k=[2],
        color='white',
        opacity=0.9,
        flatshading=True,
        showlegend=False
    ))

    # If hole_positions is provided, use that directly
    if hole_positions is not None:
        hole_positions_x, hole_positions_y = hole_positions
    else:
        # Otherwise, calculate positions based on pattern and mode
        hole_positions_x = []
        hole_positions_y = []
        
        # Positioning holes
        if burden is not None and spacing is not None:
            # Auto mode: Use provided burden and spacing for organized grid
            num_rows = max(1, int(width / burden))
            num_holes_per_row_odd = max(1, int((length - spacing/2) / spacing) + 1)
            num_holes_per_row_even = max(1, int((length - spacing) / spacing) + 1)
            
            # Create positions based on burden and spacing
            y_positions = np.linspace(burden/2, width - burden/2, num_rows)
            
            # Add burden lines (horizontal)
            for y_pos in y_positions:
                fig.add_shape(
                    type="line",
                    x0=0,
                    y0=y_pos,
                    x1=length,
                    y1=y_pos,
                    line=dict(color="green", width=1, dash="dash"),
                )
            
            # Add spacing lines (vertical) - adjust for staggered pattern if needed
            if pattern == "staggered":
                for row_idx, y_pos in enumerate(y_positions):
                    # Calculate x positions differently for odd and even rows
                    if row_idx % 2 == 0:  # Odd rows (index 0 is first row)
                        # Start with half spacing from the edge
                        x_positions = np.linspace(spacing/2, length - spacing/2, num_holes_per_row_odd)
                    else:  # Even rows
                        # For even rows, shift by exactly half spacing to create triangular pattern
                        # This creates equal spacing between all holes as shown in the diagram
                        x_positions = np.linspace(spacing, length - spacing, num_holes_per_row_even)
                    
                    # Add hole markers
                    for x_pos in x_positions:
                        fig.add_trace(go.Scatter(
                            x=[x_pos],
                            y=[y_pos],
                            mode='markers',
                            marker=dict(
                                size=10,
                                color='blue',
                                symbol='circle',
                                line=dict(color='black', width=1)
                            ),
                            showlegend=False
                        ))
                        
                        # Add hole labels if requested
                        if show_labels:
                            hole_idx = len(hole_positions_x)
                            fig.add_trace(go.Scatter(
                                x=[x_pos],
                                y=[y_pos],
                                text=f'H{hole_idx+1}',
                                mode='text',
                                textposition='top center',
                                showlegend=False
                            ))
                        
                        # Store hole positions
                        hole_positions_x.append(x_pos)
                        hole_positions_y.append(y_pos)
                        
                        # Limit to the specified number of holes
                        if len(hole_positions_x) >= num_holes:
                            break
                    
                    # Break outer loop if we've reached the max number of holes
                    if len(hole_positions_x) >= num_holes:
                        break
            else:
                # Standard square pattern
                x_positions = np.linspace(spacing/2, length - spacing/2, num_holes_per_row_odd)
                for x_pos in x_positions:
                    fig.add_shape(
                        type="line",
                        x0=x_pos,
                        y0=0,
                        x1=x_pos,
                        y1=width,
                        line=dict(color="green", width=1, dash="dash"),
                    )
            
            # Add burden and spacing labels
            fig.add_annotation(
                x=length/2,
                y=y_positions[0] + burden/2 if len(y_positions) > 1 else width/2,
                text=f"burden={burden:.2f}m",
                showarrow=False,
                font=dict(color="green", size=12),
            )
            
            fig.add_annotation(
                x=x_positions[0] + spacing/2 if len(x_positions) > 1 else length/2,
                y=width/2,
                text=f"spacing={spacing:.2f}m",
                showarrow=False,
                font=dict(color="green", size=12),
            )
            
            # Place holes in organized grid
            count = 0
            for y_pos in y_positions:
                for x_pos in x_positions:
                    if count < num_holes:
                        hole_positions_x.append(x_pos)
                        hole_positions_y.append(y_pos)
                        count += 1
        else:
            # Manual mode: Use original placement logic
            holes_per_row = int(np.ceil(np.sqrt(num_holes)))
            x_positions = np.linspace(length*0.15, length*0.85, holes_per_row)
            y_positions = np.linspace(width*0.15, width*0.85, holes_per_row)
            
            if pattern == "staggered" and holes_per_row > 1:
                # Create staggered pattern for manual mode
                hole_positions_x = []
                hole_positions_y = []
                count = 0
                
                # Calculate the horizontal and vertical spacing between holes
                x_step = (length*0.7) / (holes_per_row - 1) if holes_per_row > 1 else length*0.7
                y_step = (width*0.7) / (holes_per_row - 1) if holes_per_row > 1 else width*0.7
                
                # Calculate grid positions
                for row_idx in range(holes_per_row):
                    # Calculate y position for this row
                    y_pos = width*0.15 + row_idx * y_step
                    
                    # Determine number of holes in this row
                    # For more consistent spacing, we might have fewer holes in even rows
                    if row_idx % 2 == 1 and row_idx == holes_per_row - 1:  # Last even row
                        row_holes = holes_per_row - 1  # One fewer hole in the last even row
                    else:
                        row_holes = holes_per_row
                    
                    # Calculate x positions for this row
                    if row_idx % 2 == 0:  # Odd rows (index 0, 2, 4...)
                        # Start from x=0.15*length
                        for col_idx in range(row_holes):
                            x_pos = length*0.15 + col_idx * x_step
                            
                            if count < num_holes:
                                hole_positions_x.append(x_pos)
                                hole_positions_y.append(y_pos)
                                count += 1
                    else:  # Even rows (index 1, 3, 5...)
                        # Shift by half of horizontal spacing to create triangular pattern
                        # This ensures equal spacing between all adjacent holes
                        for col_idx in range(row_holes):
                            x_pos = length*0.15 + x_step/2 + col_idx * x_step
                            
                            if count < num_holes and x_pos <= length*0.85:
                                hole_positions_x.append(x_pos)
                                hole_positions_y.append(y_pos)
                                count += 1
            else:
                # Place holes in original pattern
                count = 0
                for x_pos in x_positions:
                    for y_pos in y_positions:
                        if count < num_holes:
                            hole_positions_x.append(x_pos)
                            hole_positions_y.append(y_pos)
                            count += 1

    # Place holes at the calculated or provided positions
    for i in range(min(num_holes, len(hole_positions_x))):
        x_pos = hole_positions_x[i]
        y_pos = hole_positions_y[i]
        r = hole_radii[i % len(hole_radii)]
        d = min(hole_depths[i % len(hole_depths)], height)
        
        # Add hole visualization
        add_hole_visualization(fig, x_pos, y_pos, r, d, height, i, explosive_lengths[i % len(explosive_lengths)])

    # Update layout
    pattern_text = "Staggered Pattern" if pattern == "staggered" else "Square Pattern"
    
    # Create title based on whether we're showing all holes or a limited number
    if original_num_holes is not None and num_holes < original_num_holes:
        title = f'Blasting Area ({length}×{width}×{height}) - Showing {num_holes} of {original_num_holes} Holes - {pattern_text}'
    else:
        title = f'Blasting Area ({length}×{width}×{height}) with {num_holes} Holes - {pattern_text}'
    
    fig.update_layout(
        scene=dict(
            xaxis_title='X: Length',
            yaxis_title='Y: Width',
            zaxis_title='Z: Height',
            aspectmode='data',
            camera=dict(
                eye=dict(x=2.0, y=2.0, z=1.5),
                up=dict(x=0, y=0, z=1)
            )
        ),
        title=title,
        margin=dict(l=0, r=0, b=0, t=40)
    )

    return fig 