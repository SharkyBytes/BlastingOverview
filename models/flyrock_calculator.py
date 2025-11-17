"""
Roth Flyrock Model Calculator
Reference: Roth, J. (1979). A Model for the Determination of Flyrock Range Based on Shot Design
"""

import numpy as np
import math

class RothFlyrockCalculator:
    def __init__(self):
        self.g = 9.81  # acceleration due to gravity (m/s²)

    def calculate_initial_velocity(self, powder_factor, rock_density, explosive_density):
        """
        Calculate initial velocity of flyrock
        
        Parameters:
        -----------
        powder_factor : float
            Powder factor in kg/m³
        rock_density : float
            Rock density in kg/m³
        explosive_density : float
            Explosive density in kg/m³
            
        Returns:
        --------
        float : Initial velocity in m/s
        """
        return 27.4 * math.sqrt(powder_factor * explosive_density / rock_density)

    def calculate_max_distance(self, burden, powder_factor, rock_density, 
                             explosive_density, hole_diameter, stemming_length):
        """
        Calculate maximum flyrock distance using Roth's model
        
        Parameters:
        -----------
        burden : float
            Burden distance in meters
        powder_factor : float
            Powder factor in kg/m³
        rock_density : float
            Rock density in kg/m³
        explosive_density : float
            Explosive density in kg/m³
        hole_diameter : float
            Diameter of blast hole in meters
        stemming_length : float
            Length of stemming in meters
            
        Returns:
        --------
        dict : Dictionary containing:
            - max_distance: Maximum flyrock distance (m)
            - initial_velocity: Initial velocity of flyrock (m/s)
            - launch_angle: Optimal launch angle (degrees)
            - safety_factor: Recommended safety factor
        """
        # Calculate initial velocity
        v0 = self.calculate_initial_velocity(powder_factor, rock_density, explosive_density)
        
        # Optimal launch angle for maximum distance (45 degrees)
        angle = 45
        angle_rad = math.radians(angle)
        
        # Calculate maximum distance using projectile motion equation
        max_distance = (v0**2 * math.sin(2 * angle_rad)) / self.g
        
        # Apply correction factors based on burden and stemming
        stemming_factor = 1 - (stemming_length / (20 * hole_diameter))
        burden_factor = 1 + (burden / 10)  # Increased risk with larger burden
        
        # Apply correction
        corrected_distance = max_distance * stemming_factor * burden_factor
        
        # Add safety factor (typically 1.5 to 2.0)
        safety_factor = 1.5
        safe_distance = corrected_distance * safety_factor
        
        return {
            'max_distance': safe_distance,
            'initial_velocity': v0,
            'launch_angle': angle,
            'safety_factor': safety_factor,
            'uncorrected_distance': max_distance,
            'stemming_factor': stemming_factor,
            'burden_factor': burden_factor
        }

    def generate_safety_zones(self, max_distance):
        """
        Generate safety zone radii based on maximum flyrock distance
        
        Parameters:
        -----------
        max_distance : float
            Maximum calculated flyrock distance in meters
            
        Returns:
        --------
        dict : Dictionary containing different safety zone radii
        """
        return {
            'red_zone': max_distance,  # No access zone
            'yellow_zone': max_distance * 1.2,  # Limited access zone
            'green_zone': max_distance * 1.5  # Safe zone
        }