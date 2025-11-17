"""
Helper functions for the Blasting Overview application.
"""
import numpy as np

def create_cylinder_surface(x_center, y_center, radius, z_top, z_bottom):
    """
    Creates the coordinates for a cylinder surface.
    
    Args:
        x_center: X-coordinate of the cylinder center
        y_center: Y-coordinate of the cylinder center
        radius: Radius of the cylinder
        z_top: Z-coordinate of the cylinder top
        z_bottom: Z-coordinate of the cylinder bottom
        
    Returns:
        x_grid, y_grid, z_grid: 3D coordinate grids for the cylinder surface
    """
    theta = np.linspace(0, 2*np.pi, 36)
    z = np.linspace(z_bottom, z_top, 10)
    theta_grid, z_grid = np.meshgrid(theta, z)
    x_grid = x_center + radius * np.cos(theta_grid)
    y_grid = y_center + radius * np.sin(theta_grid)
    return x_grid, y_grid, z_grid 