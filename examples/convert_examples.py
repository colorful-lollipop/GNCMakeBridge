#!/usr/bin/env python3
"""
Example conversion script for GNCMakeBridge.
Demonstrates bidirectional conversion between GN and CMake.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from gncmake_bridge import Converter, ConversionMode


def convert_gn_to_cmake_example():
    """Example: Convert GN to CMake."""
    print("=" * 60)
    print("Example: GN to CMake Conversion")
    print("=" * 60)

    gn_content = '''
executable("hello_world") {
  sources = [
    "main.cc",
    "utils.cc",
  ]
  deps = [
    ":utils",
  ]
  cflags = ["-Wall", "-O2"]
}

static_library("utils") {
  sources = [
    "string_utils.cc",
    "file_utils.cc",
  ]
  headers = [
    "string_utils.h",
    "file_utils.h",
  ]
  public_deps = [":base"]
}
'''

    converter = Converter()
    cmake_output = converter.convert(gn_content, ConversionMode.GN_TO_CMAKE)

    print("\nInput GN:")
    print(gn_content)
    print("\nOutput CMake:")
    print(cmake_output)
    print()

    return cmake_output


def convert_cmake_to_gn_example():
    """Example: Convert CMake to GN."""
    print("=" * 60)
    print("Example: CMake to GN Conversion")
    print("=" * 60)

    cmake_content = '''
add_executable(myapp
  main.cc
  app.cc
)

target_link_libraries(myapp PRIVATE
  lib1
  lib2
)

target_include_directories(myapp PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

target_compile_definitions(myapp PRIVATE DEBUG)
'''

    converter = Converter()
    gn_output = converter.convert(cmake_content, ConversionMode.CMAKE_TO_GN)

    print("\nInput CMake:")
    print(cmake_content)
    print("\nOutput GN:")
    print(gn_output)
    print()

    return gn_output


def roundtrip_example():
    """Example: Roundtrip conversion GN -> CMake -> GN."""
    print("=" * 60)
    print("Example: Roundtrip Conversion")
    print("=" * 60)

    original_gn = '''
executable("myapp") {
  sources = ["main.cc", "utils.cc"]
  deps = [":lib1", ":lib2"]
  cflags = ["-Wall", "-O3"]
  link_flags = ["-lpthread"]
}
'''

    converter = Converter()

    print("\nOriginal GN:")
    print(original_gn)

    cmake = converter.convert(original_gn, ConversionMode.GN_TO_CMAKE)
    print("\nConverted to CMake:")
    print(cmake)

    roundtrip_gn = converter.convert(cmake, ConversionMode.CMAKE_TO_GN)
    print("\nRoundtrip back to GN:")
    print(roundtrip_gn)

    return roundtrip_gn


def complex_example():
    """Example: Complex project with multiple targets."""
    print("=" * 60)
    print("Example: Complex Project Conversion")
    print("=" * 60)

    gn_content = '''
# Main executable
executable("server") {
  sources = ["server.cc", "connection.cc"]
  deps = [":core", ":network"]
  cflags = ["-O2", "-g"]
}

# Static library
static_library("core") {
  sources = ["core.cc", "thread.cc"]
  headers = ["core.h", "thread.h"]
  public_deps = [":utils"]
}

# Shared library
shared_library("network") {
  sources = ["socket.cc", "http.cc"]
  deps = [":utils"]
  link_flags = ["-lssl"]
}

# Source set for object files
source_set("utils") {
  sources = ["logger.cc", "config.cc"]
  headers = ["logger.h", "config.h"]
}

# Group for dependency grouping
group("all_libs") {
  deps = [":core", ":network", ":utils"]
}
'''

    converter = Converter()
    cmake = converter.convert(gn_content, ConversionMode.GN_TO_CMAKE)

    print("\nInput GN (complex project):")
    print(gn_content)
    print("\nOutput CMake:")
    print(cmake)
    print()

    return cmake


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("GNCMakeBridge - Example Conversions")
    print("=" * 60 + "\n")

    try:
        convert_gn_to_cmake_example()
        convert_cmake_to_gn_example()
        roundtrip_example()
        complex_example()

        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
