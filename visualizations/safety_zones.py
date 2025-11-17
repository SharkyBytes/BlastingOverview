"""
Flyrock Safety Zone Visualization
"""

import plotly.graph_objects as go
import numpy as np

def create_safety_zone_visualization(pattern_coords, safety_zones, hole_coordinates=None):
    """
    Create a visualization of safety zones around the blast pattern
    
    Parameters:
    -----------
    pattern_coords : dict
        Dictionary containing pattern boundaries
    safety_zones : dict
        Dictionary containing radii for different safety zones
    hole_coordinates : list, optional
        List of hole coordinates [(x1,y1), (x2,y2),...]
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    fig = go.Figure()
    
    # Calculate center point of the pattern
    center_x = (pattern_coords['x_min'] + pattern_coords['x_max']) / 2
    center_y = (pattern_coords['y_min'] + pattern_coords['y_max']) / 2
    
    # Create circles for each safety zone
    theta = np.linspace(0, 2*np.pi, 100)
    
    # Red Zone (No Access)
    x_red = center_x + safety_zones['red_zone'] * np.cos(theta)
    y_red = center_y + safety_zones['red_zone'] * np.sin(theta)
    fig.add_trace(go.Scatter(
        x=x_red, y=y_red,
        fill='toself',
        fillcolor='rgba(255,0,0,0.2)',
        line=dict(color='red'),
        name='No Access Zone'
    ))
    
    # Yellow Zone (Limited Access)
    x_yellow = center_x + safety_zones['yellow_zone'] * np.cos(theta)
    y_yellow = center_y + safety_zones['yellow_zone'] * np.sin(theta)
    fig.add_trace(go.Scatter(
        x=x_yellow, y=y_yellow,
        fill='toself',
        fillcolor='rgba(255,255,0,0.2)',
        line=dict(color='yellow'),
        name='Limited Access Zone'
    ))
    
    # Green Zone (Safe Zone)
    x_green = center_x + safety_zones['green_zone'] * np.cos(theta)
    y_green = center_y + safety_zones['green_zone'] * np.sin(theta)
    fig.add_trace(go.Scatter(
        x=x_green, y=y_green,
        fill='toself',
        fillcolor='rgba(0,255,0,0.1)',
        line=dict(color='green'),
        name='Safe Zone'
    ))
    
    # Add blast holes if provided
    if hole_coordinates:
        x_holes, y_holes = zip(*hole_coordinates)
        fig.add_trace(go.Scatter(
            x=x_holes, y=y_holes,
            mode='markers',
            marker=dict(
                size=8,
                color='black',
                symbol='circle'
            ),
            name='Blast Holes'
        ))
    
    # Update layout
    fig.update_layout(
        title='Blast Pattern Safety Zones',
        xaxis_title='Distance (m)',
        yaxis_title='Distance (m)',
        showlegend=True,
        width=800,
        height=800
    )
    
    # Make the plot aspect ratio equal
    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1
    )
    
    return fig