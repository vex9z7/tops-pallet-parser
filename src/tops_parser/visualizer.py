"""
TOPS Pallet Visualizer Module

This module provides functionality to visualize TOPS pallet data in 3D using PyVista.
"""

import pyvista as pv
from typing import Dict, List, Optional
import numpy as np
from pyvista.plotting.opts import PickerType

# Color constants
COLOR_BOX_ORIENTATION_0 = "#4a90e2"  # Soft blue for orientation 0
COLOR_BOX_ORIENTATION_1 = "#e27474"  # Soft red for orientation 1
COLOR_EDGE = "black"
COLOR_HIGHLIGHT = "#ffd700"  # Gold color for highlighting


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
        self.box_meshes: List[pv.PolyData] = []  # Store box meshes for interaction

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
        self.box_meshes.clear()

        # Calculate pallet bounds
        boxes = self.data["boxes"]

        # Calculate bounds considering orientation
        x_min = min(box["x"] for box in boxes)
        x_max = max(
            box["x"] + (self.box_width if box["orientation"] == 1 else self.box_length)
            for box in boxes
        )
        y_min = min(box["y"] for box in boxes)
        y_max = max(
            box["y"] + (self.box_length if box["orientation"] == 1 else self.box_width)
            for box in boxes
        )
        z_min = min(box["z"] for box in boxes)
        z_max = max(box["z"] + self.box_height for box in boxes)

        # Plot each box
        for i, box in enumerate(boxes):
            # Get dimensions based on orientation
            dx = self.box_width if box["orientation"] == 1 else self.box_length
            dy = self.box_length if box["orientation"] == 1 else self.box_width
            dz = self.box_height

            # Create box bounds
            x, y, z = box["x"], box["y"], box["z"]
            bounds = (x, x + dx, y, y + dy, z, z + dz)

            # Create box mesh
            box_mesh = pv.Box(bounds=bounds)
            self.box_meshes.append(box_mesh)

            # Add box to plotter with color based on orientation
            color = (
                COLOR_BOX_ORIENTATION_0
                if box["orientation"] == 0
                else COLOR_BOX_ORIENTATION_1
            )

            # Add mesh with a unique name
            self.plotter.add_mesh(
                box_mesh,
                color=color,
                opacity=1.0,  # Fully opaque
                show_edges=True,
                edge_color=COLOR_EDGE,
                line_width=1,
                name=f"box_{i}",  # Give each box a unique name
            )

        # Calculate center of pallet
        center = [(x_min + x_max) / 2, (y_min + y_max) / 2, (z_min + z_max) / 2]

        # Calculate camera distance based on pallet size
        size = max(x_max - x_min, y_max - y_min, z_max - z_min)
        distance = (
            size * 2
        )  # Adjust this multiplier to change how much of the pallet is visible

        # Set camera position
        camera_position = [
            center[0] - distance,  # Camera x
            center[1] - distance,  # Camera y
            center[2] + distance,  # Camera z
        ]
        focus_point = center
        up = [0, 0, 1]  # Keep Z-axis pointing up

        self.plotter.camera_position = [camera_position, focus_point, up]

        self.plotter.enable_mesh_picking(
            left_clicking=True,
            color=COLOR_HIGHLIGHT,
            picker=PickerType.POINT,
        )

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
