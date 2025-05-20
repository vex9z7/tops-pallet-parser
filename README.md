# TOPS Pallet Parser

A Python-based parser for TOPS exported pallet files. This tool helps in parsing and analyzing pallet data exported from TOPS (TOPS Software) industrial pallet design software.

## Demo

Check out the demo video to Ssee the TOPS Pallet Parser in action:

https://github.com/user-attachments/assets/fe38195c-1cc7-4f90-a0c9-ee84f7f614e0

## Features

- Parse TOPS exported files
- Extract pallet specifications and dimensions
- Visualize TOPS pack

## Installation

```bash
# Clone the repository
git clone https://github.com/vex9z7/tops-pallet-parser.git
cd tops-pallet-parser

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Usage

### Command Line Interface

The package provides a command-line tool for visualizing TOPS pallet data:

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Visualize a TOPS file
tops-visualize path/to/your/tops/file.txt
```

### Python API

You can use the package in your Python code for parsing and analyzing TOPS pallet data:

```python
from tops_parser.parser import TopsParser
from tops_parser.visualizer import PalletVisualizer

# Parse a TOPS file
parser = TopsParser("path/to/your/tops/file.txt")
data = parser.parse()

# Access parsed data
print(f"Total boxes: {data['total_boxes']}")
print(f"Pallet dimensions: {data['dimensions']}")
print(f"Number of layers: {len(data['layers'])}")

# Export data to different formats
parser.export_to_csv("output.csv")
parser.export_to_json("output.json")

# Visualize the pallet
visualizer = PalletVisualizer(data)
visualizer.plot_boxes()
visualizer.show()
```

The parser provides the following key features:

- Parse TOPS exported files and extract box positions, orientations, and layer information
- Access pallet metadata including ship case and pallet specifications
- Visualize the pallet layout in 3D

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
```

## License

MIT License
