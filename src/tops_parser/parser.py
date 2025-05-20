"""
TOPS Pallet Parser Module

This module provides functionality to parse TOPS exported pallet files.
"""

import os
from typing import Dict, List
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class Box:
    """Represents a box in the pallet."""

    layer: int
    x: float
    y: float
    z: float
    orientation: int

    def to_dict(self) -> Dict:
        """Convert box to dictionary representation."""
        return {"layer": self.layer, "x": self.x, "y": self.y, "z": self.z, "orientation": self.orientation}


class TopsParser:
    """Parser for TOPS exported pallet files."""

    def __init__(self, file_path: str):
        """
        Initialize the TOPS parser.

        Args:
            file_path (str): Path to the TOPS exported file
        """
        self.file_path = file_path
        self.metadata: Dict[str, Dict] = {
            'ship_case': {},
            'pallet': {}
        }
        self.boxes: List[Box] = []
        self.layers: Dict[int, List[Box]] = defaultdict(list)

    def parse(self) -> Dict:
        """
        Parse the TOPS exported file.

        Returns:
            Dict: Parsed metadata including ship case and pallet information
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")

        self.metadata = {
            'ship_case': {},
            'pallet': {}
        }
        self.boxes = []
        self.layers = defaultdict(list)

        with open(self.file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue

                # Check for metadata lines
                if line.startswith('[Ship Case]'):
                    # Parse ship case metadata
                    parts = line.strip('[]').split(',')
                    self.metadata['ship_case'] = {
                        'name': parts[1].strip('"'),
                        'spec': parts[2].strip('"'),
                        'length': float(parts[3]),
                        'width': float(parts[4]),
                        'height': float(parts[5])
                    }
                    continue

                if line.startswith('[Pallet]'):
                    # Parse pallet metadata
                    parts = line.strip('[]').split(',')
                    self.metadata['pallet'] = {
                        'name': parts[1].strip('"'),
                        'length': float(parts[2]),
                        'width': float(parts[3]),
                        'height': float(parts[4])
                    }
                    continue

                # Parse box data
                try:
                    parts = line.strip(",").split(",")
                    if len(parts) >= 5:  # Ensure we have all required fields
                        box = Box(
                            layer=int(parts[0]),
                            x=float(parts[1]),
                            y=float(parts[2]),
                            z=float(parts[3]),
                            orientation=int(parts[4]),
                        )
                        self.boxes.append(box)
                        self.layers[box.layer].append(box)
                except (ValueError, IndexError) as e:
                    print(f"Warning: Could not parse line: {line}")
                    continue

        return {
            "pallet_id": os.path.basename(self.file_path).split(".")[0],
            "metadata": self.metadata,
            "boxes": [box.to_dict() for box in self.boxes],
            "layers": {
                layer_num: [box.to_dict() for box in layer_boxes] for layer_num, layer_boxes in self.layers.items()
            },
        }

