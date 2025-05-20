#!/usr/bin/env python3
"""
Command-line interface for the TOPS pallet parser.
"""

import argparse
import sys
from pathlib import Path

from tops_parser.parser import TopsParser
from tops_parser.visualizer import PalletVisualizer


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Visualize TOPS pallet data from a file.")
    parser.add_argument("file_path", type=str, help="Path to the TOPS file to visualize")

    # Parse arguments
    args = parser.parse_args()

    # Validate file exists
    file_path = Path(args.file_path)
    if not file_path.exists():
        print(f"Error: File '{file_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    try:
        # Parse the TOPS file
        tops_parser = TopsParser(str(file_path))
        data = tops_parser.parse()

        # Create and show visualization
        visualizer = PalletVisualizer(data)
        visualizer.plot_boxes()
        visualizer.show()
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
