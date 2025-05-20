"""
TOPS Pallet Visualizer Module

This module provides functionality to visualize TOPS pallet data in 3D using PyVista.
"""

import pyvista as pv
from typing import Dict
import numpy as np

# Color constants
COLOR_BOX_ORIENTATION_0 = "#4a90e2"  # Soft blue for orientation 0
COLOR_BOX_ORIENTATION_1 = "#e27474"  # Soft red for orientation 1
COLOR_EDGE = "black"
COLOR_BACKGROUND = "#f5f5f5"  # Light gray background


class PalletVisualizer:
    """Visualizer for TOPS pallet data."""

    def __init__(self, data: Dict):
        """
        Initialize the visualizer.

        Args:
            data (Dict): Parsed pallet data from TopsParser
        """
        self.data = data
        self.plotter = pv.Plotter()

        # Get box dimensions from metadata
        try:
            ship_case = data["metadata"]["ship_case"]
            self.box_length = ship_case["length"]
            self.box_width = ship_case["width"]
            self.box_height = ship_case["height"]
        except KeyError:
            raise ValueError("Missing required box dimensions in metadata.ship_case")

    def plot_boxes(self):
        """Plot all boxes in 3D."""
        # Clear previous plot
        self.plotter.clear()

        # Calculate pallet bounds
        boxes = self.data["boxes"]

        # Calculate bounds considering orientation
        x_min = min(box["x"] for box in boxes)
        x_max = max(box["x"] + (self.box_width if box["orientation"] == 1 else self.box_length) for box in boxes)
        y_min = min(box["y"] for box in boxes)
        y_max = max(box["y"] + (self.box_length if box["orientation"] == 1 else self.box_width) for box in boxes)
        z_min = min(box["z"] for box in boxes)
        z_max = max(box["z"] + self.box_height for box in boxes)

        # Plot each box
        for box in boxes:
            # Get dimensions based on orientation
            dx = self.box_width if box["orientation"] == 1 else self.box_length
            dy = self.box_length if box["orientation"] == 1 else self.box_width
            dz = self.box_height

            # Create box bounds
            x, y, z = box["x"], box["y"], box["z"]
            bounds = (x, x + dx, y, y + dy, z, z + dz)

            # Create box mesh
            box_mesh = pv.Box(bounds=bounds)

            # Add box to plotter with color based on orientation
            color = COLOR_BOX_ORIENTATION_0 if box["orientation"] == 0 else COLOR_BOX_ORIENTATION_1
            self.plotter.add_mesh(
                box_mesh,
                color=color,
                opacity=1.0,  # Fully opaque
                show_edges=True,
                edge_color=COLOR_EDGE,
                line_width=1,
            )

        # Set title
        self.plotter.add_text(f"Pallet {self.data['pallet_id']}", font_size=20, position="upper_edge")

        # Set background color
        self.plotter.set_background(COLOR_BACKGROUND)

        # Calculate center of pallet
        center = [(x_min + x_max) / 2, (y_min + y_max) / 2, (z_min + z_max) / 2]

        # Calculate camera distance based on pallet size
        size = max(x_max - x_min, y_max - y_min, z_max - z_min)
        distance = size * 2  # Adjust this multiplier to change how much of the pallet is visible

        # Set camera position
        camera_position = [
            center[0] - distance,  # Camera x
            center[1] - distance,  # Camera y
            center[2] + distance,  # Camera z
        ]
        focus_point = center
        up = [0, 0, 1]  # Keep Z-axis pointing up

        self.plotter.camera_position = [camera_position, focus_point, up]

    def show(self):
        """Display the plot."""
        self.plotter.show()

    def save(self, filename: str):
        """
        Save the plot to a file.

        Args:
            filename (str): Path where to save the plot
        """
        self.plotter.screenshot(filename)
        self.plotter.close()
