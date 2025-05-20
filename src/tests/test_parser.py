import pytest
import os
from src.tops_parser.parser import TopsParser


@pytest.fixture
def test_file():
    # Create a temporary test file with known metadata and box data
    test_file = "test_tops.txt"
    with open(test_file, "w") as f:
        # Write metadata
        f.write('[Ship Case],"","RSC (FEFCO 0201)",9.9375,8.0625,5.8125\n')
        f.write('[Pallet],"CHEP Pallet",40.0,48.0,5.625\n')
        # Write box data
        f.write("1,-15.1875,-19.8750,5.6250,0,\n")
        f.write("1,-5.0625,-19.8750,5.6250,0,\n")
        f.write("2,-15.1875,-19.8750,11.4375,0,\n")
        f.write("2,-5.0625,-19.8750,11.4375,0,\n")

    yield test_file

    # Clean up the test file
    if os.path.exists(test_file):
        os.remove(test_file)


def test_metadata_parsing(test_file):
    parser = TopsParser(test_file)
    result = parser.parse()

    # Test pallet_id
    assert result["pallet_id"] == "test_tops"

    # Test Ship Case metadata
    assert "ship_case" in result["metadata"]
    ship_case = result["metadata"]["ship_case"]
    assert ship_case["name"] == ""
    assert ship_case["spec"] == "RSC (FEFCO 0201)"
    assert ship_case["length"] == 9.9375
    assert ship_case["width"] == 8.0625
    assert ship_case["height"] == 5.8125

    # Test Pallet metadata
    assert "pallet" in result["metadata"]
    pallet = result["metadata"]["pallet"]
    assert pallet["name"] == "CHEP Pallet"
    assert pallet["length"] == 40.0
    assert pallet["width"] == 48.0
    assert pallet["height"] == 5.625


def test_box_parsing(test_file):
    parser = TopsParser(test_file)
    result = parser.parse()

    # Test boxes list
    assert "boxes" in result
    assert len(result["boxes"]) == 4  # We have 4 boxes in our test file

    # Test first box
    first_box = result["boxes"][0]
    assert first_box["layer"] == 1
    assert first_box["x"] == -15.1875
    assert first_box["y"] == -19.8750
    assert first_box["z"] == 5.6250
    assert first_box["orientation"] == 0

    # Test layers
    assert "layers" in result
    assert len(result["layers"]) == 2  # We have 2 layers in our test file

    # Test layer 1
    layer1 = result["layers"][1]
    assert len(layer1) == 2  # Layer 1 has 2 boxes
    assert layer1[0]["x"] == -15.1875
    assert layer1[1]["x"] == -5.0625

    # Test layer 2
    layer2 = result["layers"][2]
    assert len(layer2) == 2  # Layer 2 has 2 boxes
    assert layer2[0]["x"] == -15.1875
    assert layer2[1]["x"] == -5.0625

