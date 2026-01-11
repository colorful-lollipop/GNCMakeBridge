from enum import Enum
from pathlib import Path
from typing import Any

from gncmake_bridge.ir import Target, Toolchain
from gncmake_bridge.parser import GNParser, CMakeParser
from gncmake_bridge.generator import GNGenerator, CMakeGenerator


class ConversionMode(Enum):
    GN_TO_CMAKE = "gn_to_cmake"
    CMAKE_TO_GN = "cmake_to_gn"


class Converter:
    def __init__(self) -> None:
        self._gn_parser = GNParser()
        self._cmake_parser = CMakeParser()
        self._gn_generator = GNGenerator()
        self._cmake_generator = CMakeGenerator()

    def convert_gn_to_cmake(self, gn_content: str) -> str:
        targets = self._gn_parser.parse(gn_content)
        cmake_lines = ["cmake_minimum_required(VERSION 3.20)", "project(gn_conversion)"]
        for target in targets:
            cmake_lines.append(self._cmake_generator.generate(target))
        return "\n\n".join(cmake_lines)

    def convert_cmake_to_gn(self, cmake_content: str) -> str:
        targets = self._cmake_parser.parse(cmake_content)
        gn_lines = []
        for target in targets:
            gn_lines.append(self._gn_generator.generate(target))
        return "\n\n".join(gn_lines)

    def convert_file(
        self, input_path: Path, output_path: Path, mode: ConversionMode
    ) -> None:
        content = input_path.read_text()

        if mode == ConversionMode.GN_TO_CMAKE:
            result = self.convert_gn_to_cmake(content)
        elif mode == ConversionMode.CMAKE_TO_GN:
            result = self.convert_cmake_to_gn(content)
        else:
            raise ValueError(f"Unknown conversion mode: {mode}")

        output_path.write_text(result)

    def convert(self, content: str, mode: ConversionMode) -> str:
        if mode == ConversionMode.GN_TO_CMAKE:
            return self.convert_gn_to_cmake(content)
        elif mode == ConversionMode.CMAKE_TO_GN:
            return self.convert_cmake_to_gn(content)
        else:
            raise ValueError(f"Unknown conversion mode: {mode}")
