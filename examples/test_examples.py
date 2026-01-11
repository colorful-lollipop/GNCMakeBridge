"""Test examples for GNCMakeBridge."""
import tempfile
from pathlib import Path

from gncmake_bridge import Converter, ConversionMode, GNParser, CMakeParser


def test_gn_to_cmake_file_conversion():
    """Test converting a GN file to CMake."""
    gn_path = Path(__file__).parent / "gn_to_cmake" / "BUILD.gn"
    if not gn_path.exists():
        print(f"Skipping: {gn_path} does not exist")
        return

    content = gn_path.read_text()
    parser = GNParser()
    targets = parser.parse(content)
    print(f"Parsed {len(targets)} targets from GN file")
    for target in targets:
        print(f"  - {target.name} ({target.type.value})")
        print(f"    Sources: {target.sources}")
        print(f"    Deps: {target.deps}")


def test_cmake_to_gn_file_conversion():
    """Test converting a CMake file to GN."""
    cmake_path = Path(__file__).parent / "cmake_to_gn" / "CMakeLists.txt"
    if not cmake_path.exists():
        print(f"Skipping: {cmake_path} does not exist")
        return

    content = cmake_path.read_text()
    parser = CMakeParser()
    targets = parser.parse(content)
    print(f"Parsed {len(targets)} targets from CMake file")
    for target in targets:
        print(f"  - {target.name} ({target.type.value})")
        print(f"    Sources: {target.sources}")


def test_full_conversion_cycle():
    """Test full conversion cycle: GN -> CMake -> GN."""
    gn_content = '''
executable("myapp") {
  sources = ["main.cc", "utils.cc"]
  deps = [":lib1", ":lib2"]
  cflags = ["-Wall", "-O2"]
}
'''
    converter = Converter()

    cmake = converter.convert(gn_content, ConversionMode.GN_TO_CMAKE)
    print("GN -> CMake:")
    print(cmake)

    roundtrip_gn = converter.convert(cmake, ConversionMode.CMAKE_TO_GN)
    print("\nCMake -> GN (roundtrip):")
    print(roundtrip_gn)

    assert 'executable("myapp")' in roundtrip_gn


def test_complex_project_conversion():
    """Test converting a complex project with multiple target types."""
    gn_content = '''
executable("server") {
  sources = ["server.cc"]
  deps = [":core"]
}

static_library("core") {
  sources = ["core.cc"]
  headers = ["core.h"]
}

shared_library("network") {
  sources = ["socket.cc"]
  deps = [":core"]
}

source_set("utils") {
  sources = ["logger.cc"]
}

group("all") {
  deps = [":core", ":network"]
}
'''
    converter = Converter()

    cmake = converter.convert(gn_content, ConversionMode.GN_TO_CMAKE)
    print("\nComplex project GN -> CMake:")
    print(cmake)

    assert "add_executable(server" in cmake
    assert "add_library(core STATIC" in cmake
    assert "add_library(network SHARED" in cmake
    assert "add_library(utils OBJECT" in cmake
    assert "add_library(all INTERFACE" in cmake


def main():
    """Run all example tests."""
    print("=" * 60)
    print("GNCMakeBridge Example Tests")
    print("=" * 60 + "\n")

    print("1. Testing GN file conversion:")
    test_gn_to_cmake_file_conversion()

    print("\n2. Testing CMake file conversion:")
    test_cmake_to_gn_file_conversion()

    print("\n3. Testing full conversion cycle:")
    test_full_conversion_cycle()

    print("\n4. Testing complex project conversion:")
    test_complex_project_conversion()

    print("\n" + "=" * 60)
    print("All example tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
