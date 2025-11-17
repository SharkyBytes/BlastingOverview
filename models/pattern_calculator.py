"""
Pattern calculation for blast hole layouts.
"""
import numpy as np


def calculate_square_pattern(length, width, burden, spacing, num_holes=None):
    """
    Calculate hole positions for a square pattern.
    
    Args:
        length (float): Length of the blasting area in meters.
        width (float): Width of the blasting area in meters.
        burden (float): Burden distance in meters.
        spacing (float): Spacing distance in meters.
        num_holes (int, optional): Maximum number of holes to generate. If None, generate all possible holes.
        
    Returns:
        tuple: (hole_positions_x, hole_positions_y, num_rows, holes_per_row)
    """
    if burden <= 0 or spacing <= 0:
        return [], [], 0, 0
        
    # Calculate number of rows and holes per row
    num_rows = max(1, int(width / burden))
    holes_per_row = max(1, int(length / spacing))
    
    # Calculate positions
    y_positions = np.linspace(burden/2, width - burden/2, num_rows)
    x_positions = np.linspace(spacing/2, length - spacing/2, holes_per_row)
    
    # Generate all hole positions
    hole_positions_x = []
    hole_positions_y = []
    
    for y_pos in y_positions:
        for x_pos in x_positions:
            hole_positions_x.append(x_pos)
            hole_positions_y.append(y_pos)
            
            # Limit to requested number of holes
            if num_holes is not None and len(hole_positions_x) >= num_holes:
                return hole_positions_x, hole_positions_y, num_rows, holes_per_row
    
    return hole_positions_x, hole_positions_y, num_rows, holes_per_row


def calculate_staggered_pattern(length, width, burden, spacing, num_holes=None):
    """
    Calculate hole positions for a staggered (triangular) pattern.
    
    Args:
        length (float): Length of the blasting area in meters.
        width (float): Width of the blasting area in meters.
        burden (float): Burden distance in meters.
        spacing (float): Spacing distance in meters.
        num_holes (int, optional): Maximum number of holes to generate. If None, generate all possible holes.
        
    Returns:
        tuple: (hole_positions_x, hole_positions_y, num_rows, holes_per_row_odd, holes_per_row_even)
    """
    if burden <= 0 or spacing <= 0:
        return [], [], 0, 0, 0
        
    # Calculate number of rows and holes per row
    num_rows = max(1, int(width / burden))
    
    # Calculate positions for each row
    y_positions = np.linspace(burden/2, width - burden/2, num_rows)
    
    # Calculate number of holes per row (different for odd and even rows)
    num_holes_per_row_odd = max(1, int((length - spacing/2) / spacing) + 1)
    num_holes_per_row_even = max(1, int((length - spacing) / spacing) + 1)
    
    # Generate all hole positions
    hole_positions_x = []
    hole_positions_y = []
    
    for row_idx, y_pos in enumerate(y_positions):
        # Calculate x positions differently for odd and even rows
        if row_idx % 2 == 0:  # Odd rows (index 0 is first row)
            # Start with half spacing from the edge
            x_positions = np.linspace(spacing/2, length - spacing/2, num_holes_per_row_odd)
        else:  # Even rows
            # Offset by spacing to create triangular pattern
            x_positions = np.linspace(spacing, length - spacing, num_holes_per_row_even)
            
        # Add all holes in this row
        for x_pos in x_positions:
            hole_positions_x.append(x_pos)
            hole_positions_y.append(y_pos)
            
            # Limit to requested number of holes
            if num_holes is not None and len(hole_positions_x) >= num_holes:
                return hole_positions_x, hole_positions_y, num_rows, num_holes_per_row_odd, num_holes_per_row_even
    
    return hole_positions_x, hole_positions_y, num_rows, num_holes_per_row_odd, num_holes_per_row_even


def calculate_manual_positions(length, width, num_holes_per_row, num_rows=1, pattern="square"):
    """
    Calculate hole positions for manual mode with specified number of holes per row.
    
    Args:
        length (float): Length of the blasting area in meters.
        width (float): Width of the blasting area in meters.
        num_holes_per_row (int): Number of holes per row.
        num_rows (int, optional): Number of rows. Defaults to 1.
        pattern (str, optional): "square" or "staggered". Defaults to "square".
        
    Returns:
        tuple: (hole_positions_x, hole_positions_y)
    """
    if num_holes_per_row <= 0 or num_rows <= 0:
        return [], []
    
    # Calculate step sizes
    x_step = length / (num_holes_per_row + 1)
    y_step = width / (num_rows + 1)
    
    # Generate hole positions
    hole_positions_x = []
    hole_positions_y = []
    
    for row_idx in range(num_rows):
        y_pos = y_step * (row_idx + 1)
        
        # Calculate x positions based on pattern
        if pattern == "staggered" and row_idx % 2 == 1:  # Even row (0-indexed) in staggered pattern
            # Offset x position by half spacing for even rows
            x_offset = x_step / 2
            
            # For the last row (if it's an even row), ensure it doesn't go off edge
            if row_idx == num_rows - 1:
                # Calculate end position with offset
                end_pos = x_step * num_holes_per_row + x_offset
                
                if end_pos > length * 0.85:  # If it would go too close to the edge
                    # Adjust x positions for an even number of holes
                    for hole_idx in range(num_holes_per_row):
                        x_pos = x_offset + x_step * hole_idx
                        if x_pos < length * 0.85:  # Make sure we don't exceed the boundary
                            hole_positions_x.append(x_pos)
                            hole_positions_y.append(y_pos)
                else:
                    # Regular case where holes fit within the boundary
                    for hole_idx in range(num_holes_per_row):
                        x_pos = x_offset + x_step * hole_idx
                        hole_positions_x.append(x_pos)
                        hole_positions_y.append(y_pos)
            else:
                # Regular case for even rows (not the last one)
                for hole_idx in range(num_holes_per_row):
                    x_pos = x_offset + x_step * hole_idx
                    hole_positions_x.append(x_pos)
                    hole_positions_y.append(y_pos)
        else:
            # Odd rows or square pattern - no offset
            for hole_idx in range(num_holes_per_row):
                x_pos = x_step * (hole_idx + 1)
                hole_positions_x.append(x_pos)
                hole_positions_y.append(y_pos)
    
    return hole_positions_x, hole_positions_y


def calculate_burden_spacing(num_holes, rock_type="medium", hole_diameter=76):
    """
    Calculate suggested burden and spacing based on rock type and hole diameter.
    
    Args:
        num_holes (int): Number of holes
        rock_type (str): Type of rock ("soft", "medium", "hard")
        hole_diameter (float): Hole diameter in mm
        
    Returns:
        tuple: (burden, spacing)
    """
    # Base calculations for medium rock
    # B = K * D where B is burden in meters, K is a constant, and D is hole diameter in mm
    if rock_type == "soft":
        k_factor = 0.045  # For soft rock
    elif rock_type == "hard":
        k_factor = 0.025  # For hard rock
    else:  # medium
        k_factor = 0.035  # For medium rock
        
    # Calculate burden in meters
    burden = k_factor * hole_diameter
    
    # Spacing is typically 1.2 to 1.4 times the burden
    spacing = burden * 1.3
    
    return burden, spacing 