import argparse
import sys
from pathlib import Path

from gncmake_bridge import Converter, ConversionMode


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GNCMakeBridge - Bidirectional converter between GN and CMake build systems"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    convert_parser = subparsers.add_parser("convert", help="Convert between GN and CMake")
    convert_parser.add_argument(
        "--mode",
        required=True,
        choices=["gn-to-cmake", "cmake-to-gn"],
        help="Conversion mode",
    )
    convert_parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Input file path",
    )
    convert_parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output file path",
    )

    args = parser.parse_args()

    if args.command == "convert":
        mode_map = {
            "gn-to-cmake": ConversionMode.GN_TO_CMAKE,
            "cmake-to-gn": ConversionMode.CMAKE_TO_GN,
        }
        mode = mode_map[args.mode]

        converter = Converter()
        converter.convert_file(args.input, args.output, mode)
        print(f"Successfully converted {args.input} to {args.output}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
