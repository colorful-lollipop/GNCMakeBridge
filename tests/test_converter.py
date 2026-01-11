from gncmake_bridge import ConversionMode, Converter


class TestConverter:
    def setup_method(self) -> None:
        self.converter = Converter()

    def test_convert_gn_to_cmake(self) -> None:
        gn_content = """
executable("hello") {
  sources = ["main.cc"]
  deps = [":lib"]
}

static_library("lib") {
  sources = ["lib.cc"]
}
"""
        result = self.converter.convert(gn_content, ConversionMode.GN_TO_CMAKE)
        assert "cmake_minimum_required" in result
        assert "project(gn_conversion)" in result
        assert "add_executable(hello" in result
        assert "add_library(lib STATIC" in result
        assert "main.cc" in result
        assert "lib.cc" in result

    def test_convert_cmake_to_gn(self) -> None:
        cmake_content = """
add_executable(hello
  main.cc
)

target_link_libraries(hello PRIVATE lib)
"""
        result = self.converter.convert(cmake_content, ConversionMode.CMAKE_TO_GN)
        assert 'executable("hello")' in result
        assert "main.cc" in result
        assert ":lib" in result

    def test_roundtrip(self) -> None:
        original_gn = """
executable("myapp") {
  sources = ["main.cc"]
  compile_flags = ["-Wall"]
  deps = [":mylib"]
}

static_library("mylib") {
  sources = ["lib.cc"]
  headers = ["lib.h"]
}
"""
        cmake = self.converter.convert(original_gn, ConversionMode.GN_TO_CMAKE)
        roundtrip_gn = self.converter.convert(cmake, ConversionMode.CMAKE_TO_GN)

        assert 'executable("myapp")' in roundtrip_gn
        assert "main.cc" in roundtrip_gn
        assert 'static_library("mylib")' in roundtrip_gn
