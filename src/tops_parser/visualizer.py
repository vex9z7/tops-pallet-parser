"""
TOPS Pallet Visualizer Module

This module provides functionality to visualize TOPS pallet data in 3D using PyVista.
"""

import pyvista as pv
from typing import Dict, List, Optional, Tuple
import numpy as np
from pyvista.plotting.opts import PickerType

# Color constants
COLOR_BOX_ORIENTATION_0 = "#4a90e2"  # Soft blue for orientation 0
COLOR_BOX_ORIENTATION_1 = "#e27474"  # Soft red for orientation 1
COLOR_EDGE = "black"
COLOR_HIGHLIGHT = "#ffd700"  # Gold color for highlighting
COLOR_PALLET = "#8B4513"  # Brown color for pallet base
COLOR_GAP = "#ff0000"  # Bright red color for gap indicators


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
        self.info_text = None  # Store the text actor

        # Get box dimensions from metadata
        try:
            ship_case = data["metadata"]["ship_case"]
            self.box_length = ship_case["length"]
            self.box_width = ship_case["width"]
            self.box_height = ship_case["height"]
        except KeyError:
            raise ValueError("Missing required box dimensions in metadata.ship_case")

    def _box_click_callback(self, mesh, event=None):
        """Callback function for box click events."""
        if mesh is None:
            return

        # Find the clicked box by matching the mesh with our stored meshes
        try:
            box_index = self.box_meshes.index(mesh)
            box = self.data["boxes"][box_index]

            # Get bounds in a more readable format
            x1, x2, y1, y2, z1, z2 = mesh.bounds

            # Create info text
            info = f"Box Information\n"
            info += f"---------------\n"
            info += f"Box Number: {box_index + 1}\n\n"
            info += f"Dimensions:\n"
            info += f"  Length: {self.box_length:.2f}\n"
            info += f"  Width: {self.box_width:.2f}\n"
            info += f"  Height: {self.box_height:.2f}\n"
            info += f"---------------\n"
            info += f"Position:\n"
            info += f"  X: {box['x']:.2f}\n"
            info += f"  Y: {box['y']:.2f}\n"
            info += f"  Z: {box['z']:.2f}\n\n"
            info += f"Bounds:\n"
            info += f"  X: [{x1:.4f}, {x2:.4f}]\n"
            info += f"  Y: [{y1:.4f}, {y2:.4f}]\n"
            info += f"  Z: [{z1:.4f}, {z2:.4f}]\n\n"
            info += f"Orientation: {box['orientation']}"

            # Remove old text and add new text
            if self.info_text:
                self.plotter.remove_actor(self.info_text)

            self.info_text = self.plotter.add_text(
                info,
                position="upper_right",
                font_size=14,
                color="black",
                shadow=True,
                name="info_text",
                viewport=True,
            )

        except (ValueError, IndexError):
            # If we can't find the box, just ignore the click
            pass

    def _find_layer_gaps(self) -> List[Tuple[float, float]]:
        """
        Find gaps between layers in the pallet.

        Returns:
            List[Tuple[float, float]]: List of (bottom_height, top_height) tuples representing gaps
        """
        # Get all unique heights where boxes are placed
        heights = sorted(set(box["z"] for box in self.data["boxes"]))

        # Get pallet height from metadata
        pallet_height = self.data["metadata"]["pallet"]["height"]

        gaps = []

        # Check gap between pallet and first layer
        if heights and heights[0] > pallet_height:
            gaps.append((pallet_height, heights[0]))

        # Check gaps between layers
        for i in range(len(heights) - 1):
            current_height = heights[i]
            next_height = heights[i + 1]
            # Add box height to current layer height to find actual top
            current_layer_top = current_height + self.box_height
            height_diff = next_height - current_layer_top

            # If there's a gap of more than 1mm between layers
            if height_diff > 0.001:
                gaps.append((current_layer_top, next_height))

        return gaps

    def plot_boxes(self):
        """Plot all boxes in 3D."""
        # Clear previous plot
        self.plotter.clear()
        self.box_meshes.clear()

        # Calculate pallet bounds
        boxes = self.data["boxes"]

        # Get pallet dimensions from metadata
        pallet = self.data["metadata"]["pallet"]
        pallet_length = pallet["length"]
        pallet_width = pallet["width"]
        pallet_height = pallet["height"]

        # Create and add pallet base
        pallet_bounds = (-pallet_length / 2, pallet_length / 2, -pallet_width / 2, pallet_width / 2, 0, pallet_height)
        pallet_mesh = pv.Box(bounds=pallet_bounds)
        self.plotter.add_mesh(
            pallet_mesh,
            color=COLOR_PALLET,
            opacity=0.3,  # Semi-transparent
            show_edges=True,
            edge_color=COLOR_EDGE,
            line_width=1,
        )

        # Find and visualize gaps between layers
        gaps = self._find_layer_gaps()
        for bottom_height, top_height in gaps:
            # Create a semi-transparent plane to show the gap
            gap_plane = pv.Plane(
                center=(0, 0, (bottom_height + top_height) / 2),
                direction=(0, 0, 1),
                i_size=pallet_length,
                j_size=pallet_width,
            )

            self.plotter.add_mesh(
                gap_plane,
                color=COLOR_GAP,
                opacity=1,  # Increased opacity
                show_edges=True,
                edge_color=COLOR_GAP,
                line_width=3,  # Thicker edges
                style="surface",  # Solid surface
                render_lines_as_tubes=True,  # Make lines more visible
            )

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
            bounds = (
                x - dx / 2,
                x + dx / 2,
                y - dy / 2,
                y + dy / 2,
                z,
                z + dz,
            )

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
            callback=self._box_click_callback,
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
