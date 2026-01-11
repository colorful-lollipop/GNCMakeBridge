import pytest

from gncmake_bridge import GNParser, CMakeParser, Target, TargetType


class TestGNParser:
    def setup_method(self) -> None:
        self.parser = GNParser()

    def test_parse_executable(self) -> None:
        gn_content = '''
executable("hello") {
  sources = ["main.cc"]
  deps = [":lib1"]
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert targets[0].name == "hello"
        assert targets[0].type == TargetType.EXECUTABLE
        assert "main.cc" in targets[0].sources
        assert ":lib1" in targets[0].deps

    def test_parse_static_library(self) -> None:
        gn_content = '''
static_library("mylib") {
  sources = ["lib.cc"]
  headers = ["lib.h"]
  public_deps = [":dep1"]
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert targets[0].name == "mylib"
        assert targets[0].type == TargetType.STATIC_LIBRARY
        assert "lib.cc" in targets[0].sources
        assert "lib.h" in targets[0].headers
        assert ":dep1" in targets[0].public_deps

    def test_parse_shared_library(self) -> None:
        gn_content = '''
shared_library("myshared") {
  sources = ["shared.cc"]
  cflags = ["-Wall", "-O2"]
  ldflags = ["-lm"]
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert targets[0].type == TargetType.SHARED_LIBRARY
        assert "-Wall" in targets[0].compile_flags
        assert "-O2" in targets[0].compile_flags
        assert "-lm" in targets[0].link_flags

    def test_parse_source_set(self) -> None:
        gn_content = '''
source_set("mysources") {
  sources = ["a.cc", "b.cc", "c.cc"]
  deps = [":base"]
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert targets[0].type == TargetType.SOURCE_SET
        assert len(targets[0].sources) == 3

    def test_parse_multiple_targets(self) -> None:
        gn_content = '''
executable("app") {
  sources = ["app.cc"]
  deps = [":lib"]
}

static_library("lib") {
  sources = ["lib.cc"]
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 2


class TestCMakeParser:
    def setup_method(self) -> None:
        self.parser = CMakeParser()

    def test_parse_executable(self) -> None:
        cmake_content = '''
add_executable(hello
  main.cc
)

target_link_libraries(hello PRIVATE lib1)
'''
        targets = self.parser.parse(cmake_content)
        assert len(targets) == 1
        assert targets[0].name == "hello"
        assert targets[0].type == TargetType.EXECUTABLE
        assert "main.cc" in targets[0].sources
        assert "lib1" in targets[0].private_deps

    def test_parse_static_library(self) -> None:
        cmake_content = '''
add_library(mylib STATIC
  lib.cc
)

target_include_directories(mylib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
'''
        targets = self.parser.parse(cmake_content)
        assert len(targets) == 1
        assert targets[0].name == "mylib"
        assert targets[0].type == TargetType.STATIC_LIBRARY

    def test_parse_shared_library(self) -> None:
        cmake_content = '''
add_library(myshared SHARED
  shared.cc
)

target_compile_definitions(myshared PRIVATE -DDEBUG)
'''
        targets = self.parser.parse(cmake_content)
        assert len(targets) == 1
        assert targets[0].type == TargetType.SHARED_LIBRARY
        assert "-DDEBUG" in targets[0].defines

    def test_parse_link_libraries_visibility(self) -> None:
        cmake_content = '''
add_executable(app app.cc)

target_link_libraries(app PUBLIC lib1 PRIVATE lib2)
'''
        targets = self.parser.parse(cmake_content)
        assert len(targets) == 1
        assert "lib1" in targets[0].public_deps
        assert "lib2" in targets[0].private_deps

    def test_parse_output_name(self) -> None:
        cmake_content = '''
add_executable(myapp main.cc)

set_target_properties(myapp PROPERTIES OUTPUT_NAME "final_app")
'''
        targets = self.parser.parse(cmake_content)
        assert len(targets) == 1
        assert targets[0].output_name == "final_app"
